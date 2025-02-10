from music21 import *
import torch
import matplotlib.pyplot as plt

from neural_network_utils.utils import *

V3_LIST_TRANSLATOR26 = dict()
for k in (V3_LIST26.keys()):
  item = V3_LIST26[k]
  V3_LIST_TRANSLATOR26[item] = k

V3_LIST_TRANSLATOR52 = dict()
for k in (V3_LIST52.keys()):
  item = V3_LIST52[k]
  V3_LIST_TRANSLATOR52[item] = k

V3_LIST_KEYS26 = V3_LIST_TRANSLATOR26.keys()
V3_LIST_KEYS52 = V3_LIST_TRANSLATOR52.keys()

def clamp(num, border) -> float:
  if num < border or num > border:
    num = border
  return num

def area_ntn(x0, y0, x1, y1, intersection=False):
  height = x1 - x0
  width = y1 - y0
  if intersection:
    if height < 0 or width < 0:
      height, width = 0, 0
  area = height * width
  return area

def staff_lines(staff_coord: list, num: int=4) -> list:
  lines = list()
  x1, y1, x2, y2 = map(round, staff_coord)
  lines_Dy = (y2-y1) / num
  for i in range(-4, num+4):
    line_y1 = y1+lines_Dy*i
    lines.append((x1, line_y1, x2, line_y1+lines_Dy))
  return lines

def intersection_int(box1: tuple, box2: tuple) -> int:
  # Expecting box with corners' coordinates
  b1x0 = box1[0]
  b1x1 = box1[2]
  b1y0 = box1[1]
  b1y1 = box1[3]

  b2x0 = box2[0]
  b2x1 = box2[2]
  b2y0 = box2[1]
  b2y1 = box2[3]

  x0, y0 = max(b1x0, b2x0), max(b1y0, b2y0)
  x1, y1 = min(b1x1, b2x1), min(b1y1, b2y1)

  intersection_area = area_ntn(x0, y0, x1, y1, intersection=True)
  return intersection_area

def find_note_oct(note_coord: tuple, lines: list, key: str) -> str:

  line_tone = {
      -0.5: {'G': 'G6', 'F': 'B4'},
      0:    {'G': 'F6', 'F': 'A4'},
      0.5:  {'G': 'E6', 'F': 'G4'},
      1:    {'G': 'D6', 'F': 'F4'},
      1.5:  {'G': 'C6', 'F': 'E4'},
      2:    {'G': 'B5', 'F': 'D4'},
      2.5:  {'G': 'A5', 'F': 'C4'},
      3:    {'G': 'G5', 'F': 'B3'},
      3.5:  {'G': 'F5', 'F': 'A3'},
      4:    {'G': 'E5', 'F': 'G3'},
      4.5:  {'G': 'D5', 'F': 'F3'},
      5:    {'G': 'C5', 'F': 'E3'},
      5.5:  {'G': 'B4', 'F': 'E3'},
      6:    {'G': 'A4', 'F': 'C3'}, # данная линия направляет stem вверх, все что находится ниже, также направляет stem вверх, а то что выше - вниз
      6.5:  {'G': 'G4', 'F': 'B2'},
      7:    {'G': 'F4', 'F': 'A2'},
      7.5:  {'G': 'E4', 'F': 'G2'},
      8:    {'G': 'D4', 'F': 'F2'},
      8.5:  {'G': 'C4', 'F': 'E2'},
      9:    {'G': 'B3', 'F': 'D2'},
      9.5:  {'G': 'A3', 'F': 'C2'},
      10:   {'G': 'G3', 'F': 'B1'},
      10.5: {'G': 'F3', 'F': 'A1'},
      11:   {'G': 'E3', 'F': 'G1'},
      11.5: {'G': 'D3', 'F': 'F1'},
  }

  note_area = area_ntn(*note_coord)
  # print('note area:', note_area)
  id = 0
  while id <= 10:
    # print('id:', id)
    line = lines[id]
    inters = intersection_int(note_coord, line)
    # print('intersection:', inters)
    if inters >= note_area * 0.9:
      return line_tone[id][key[-1]]
    elif inters >= note_area * 0.3:
      return line_tone[id+0.5][key[-1]]
    id += 1
  return line_tone[-0.5][key[-1]]

def expand_note_box(coord: tuple, dx: int, dy: int) -> tuple:
  x1, y1, x2, y2 = coord
  res = tuple()
  x1 -= dx
  if x1 < 0: x1 = 0
  x2 += dx
  y1 -= dy
  if y1 < 0: y1 = 0
  y2 += dy

  return (x1, y1, x2, y2)

def find_note_elems(note_coord: tuple, elems_on_staff: list) -> list:
  list_of_note_elems = list()
  expanded_note_coord = expand_note_box(note_coord, 3, 30)
  beam_count = 0
  for label, coord in elems_on_staff:
    if coord != note_coord:
      if intersection_int(coord, expanded_note_coord) != 0:
        list_of_note_elems.append((label, coord))
        if label == 'beam':
          beam_count += 1
  return list_of_note_elems, beam_count

def find_dynamics_near(dyn: tuple, elems_on_staff: list, used_dyn: list, delta: int) -> list:
  dyn_label, dyn_coord = dyn
  res_dyn = list()
  used_dyn.append(dyn_coord)
  res_dyn.append(dyn)
  dyn_coord[2] += delta
  dyn_area = area_ntn(*dyn_coord)
  for label, coord in elems_on_staff:
    if dyn_coord != coord:
      if intersection_int(dyn_coord, coord) != 0:
        res_dyn.append((label, coord))
        used_dyn.append(coord)
  # print(res_dyn)
  return res_dyn, used_dyn


trill = expressions.Trill()
turn = expressions.Turn()
inverted_turn = expressions.InvertedTurn()
mord = expressions.Mordent()


def recognize(imgs, yolov3_m, yolov3_l):
  recognized_music_sheets = []
  next_tremolo = None
  next_accidental = None
  next_inveted_turn = None
  next_mordent = None
  next_trill = None
  next_turn = None
  is_tie_cont = False
  g_part = stream.Part([clef.GClef()])
  f_part = stream.Part([clef.FClef()])

  #По всем листам
  # for id in range(len(staff_data)): # оставить в итоговом варианте
  for id in [0, 100]:  # для тестов

    in_list = translate_output(st[1].unsqueeze(0), nt[0].unsqueeze(0), 26, len(V3_LIST26))[0]['y']
    in_list_labels = list(zip([V3_LIST26[i.item()] for i in in_list["labels"]], in_list['boxes'].tolist()))

    notes_in_staffs = process_img(imgs, yolov3_m, yolov3_l)
    # print('-'*15)
    
    # Удаление из списка brace
    list_labels_sort = list(filter(lambda i: i[0] != 'brace', in_list_labels))

    # По всем staff на листе
    for staff_id in range(len(notes_in_staffs)):
      symbs_in_staff = notes_in_staffs[staff_id]
      symbs_in_staff = list(sorted(symbs_in_staff, key=lambda i: [i[1][0], i[1][1]]))

      lines = staff_lines(list_labels_sort[2 * staff_id + 1][1]) # координаты линий на staff
      key_symb = list_labels_sort[2 * staff_id][0] # music key
      # print('---------------\nKEY:', key_symb, '\n-----------------')
      time_sigs = [] # то, что идедт после ключа(4/4 или 2/4 и тд)
      symbols = list() # количество нот и пауз на нотном листе
      dynamics_list = list()
      used_dyn = list()
      key_sigs = list()
      next_accidental = None
      next_tremolo = None

      is_g_part = ('G' in key_symb)
      m = stream.Measure()

      # по всем элементам на staff
      elem_id = 0
      for label, coord in symbs_in_staff:
        # print('-------')
        # print("Iter label:", label, coord)
        # print('symbols:', len(symbols) )
        if 'key' in label:
          key_sigs.append(label)
        # Определение метрики
        elif 'timeSig' in label:
          if 'Common' in label:
            m.append(meter.TimeSignature('4/4'))
          else:
            time_sigs.append((label[-1], coord))
            if len(time_sigs) == 2:
              time_sigs = list(sorted(time_sigs, key=lambda x: x[1][1]))
              m.append(meter.TimeSignature(f'{time_sigs[0][0]}/{time_sigs[1][0]}'))
              time_sigs = list()
        # Определение пауз
        elif 'rest' in label:
          if 'DoubleWhole' in label:
            symbols.append(note.Rest(1*2*2*2))
          elif 'Whole' in label:
            symbols.append(note.Rest(1*2*2))
          elif 'Half' in label:
            symbols.append(note.Rest(1*2))
          elif 'Quarter' in label:
            symbols.append(note.Rest(1))
          elif '8th' in label:
            symbols.append(note.Rest(1/2))
          elif '16th' in label:
            symbols.append(note.Rest(1/2/2))
          elif '32th' in label:
            symbols.append(note.Rest(1/2/2/2))
          elif '64th' in label:
            symbols.append(note.Rest(1/2/2/2/2))
          elif '128th' in label:
            symbols.append(note.Rest(1/2/2/2/2/2))
        # Определение динамики
        elif 'dynamic' in label:
          if coord not in used_dyn:
            dyns, used_dyn = find_dynamics_near((label, coord), symbs_in_staff, used_dyn, 16)
            dynamics_list.append(((len(symbols) - 1) * 0.5, dynamics.Dynamic(''.join([elem[0][-1].lower() for elem in dyns]))))
            # print('Dynamic pos:', (len(symbols) - 1) * 0.5)
        # Опеределение ноты
        elif 'notehead' in label:
          note_tone = find_note_oct(coord, lines, key_symb)
          symbs_in_note, beam_count = find_note_elems(coord, symbs_in_staff)
          symbs_in_note_labels = [elem[0] for elem in symbs_in_note]
          # print('Symbs in note:', symbs_in_note)
          # Параметры ноты
          note_elems = {
              'step': note_tone[0],
              'accidental': '',
              'octave': int(note_tone[1]),
              'type': 1,
              'dots': len(list(filter(lambda i: i == 'augmentationDot', symbs_in_note_labels))),
              'tremolo': None
          }
          # print('Dots:', note_elems['dots'])
          # головы
          if 'Black' in label:
            # хвостики
            if list(filter(lambda i: i == 'flag', symbs_in_note_labels)) or beam_count != 0: # 'flag' in symbs_in_note_labels не рабочая тема
              try:
                flag = list(filter(lambda i: i == 'flag', symbs_in_note_labels))[0]
              except IndexError:
                flag = ''
              if '128' in flag or beam_count == 5:
                note_elems['type'] = 1 / 2 / 2 / 2 / 2 / 2
                # print('Beams:', beam_count, ' Flag:', flag)
              elif '64' in flag or beam_count == 4:
                note_elems['type'] = 1 / 2 / 2 / 2 / 2
                # print('Beams:', beam_count, ' Flag:', flag)
              elif '32' in flag or beam_count == 3:
                note_elems['type'] = 1 / 2 / 2 / 2
                # print('Beams:', beam_count, ' Flag:', flag)
              elif '16' in flag or beam_count == 2:
                note_elems['type'] = 1 / 2 / 2
                # print('Beams:', beam_count, ' Flag:', flag)
              elif '8' in flag or beam_count == 1:
                note_elems['type'] = 1 / 2
                # print('Beams:', beam_count, ' Flag:', flag)
            else:
              note_elems['type'] = 1
          elif 'Half' in label:
            note_elems['type'] = 1 * 2
          elif 'Whole' in label:
            note_elems['type'] = 1 * 2 * 2
          elif 'DoubleWhole' in label:
            note_elems['type'] = 1 * 2 * 2 * 2

          if next_accidental:
            note_elems['accidental'] = next_accidental
            next_accidental = None
          # Tremolo
          elif list(filter(lambda i: i == 'tremolo', symbs_in_note_labels)):
            trem_lab = list(filter(lambda i: i == 'tremolo', symbs_in_note_labels))[0]
            if '1' in trem_lab:
              next_tremolo = expressions.Trem()
              next_tremolo.numberOfMarks = 1
              note_elems['tremolo'] = next_tremolo
            elif '2' in trem_lab:
              next_tremolo = expressions.Trem()
              next_tremolo.numberOfMarks = 2
              note_elems['tremolo'] = next_tremolo
            elif '3' in trem_lab:
              next_tremolo = expressions.Trem()
              next_tremolo.numberOfMarks = 3
              note_elems['tremolo'] = next_tremolo
            elif '4' in trem_lab:
              next_tremolo = expressions.Trem()
              next_tremolo.numberOfMarks = 4
              note_elems['tremolo'] = next_tremolo

          elif list(filter(lambda i: i == 'trill', symbs_in_note_labels)):
            next_trill = True

          note_ready = note.Note(
              f"{note_elems['step']}{note_elems['accidental']}{note_elems['octave']}", # Example 'C#4'
              quarterLength=note_elems['type'] # Duration
                          )
          # note_ready.duration.dots = note_elems['dots']
          # В самом конце
          if note_elems['tremolo']:
            symbols.extend(note_elems['tremolo'].realize(note_ready)[0])
          if next_trill:
            symbols.extend(trill.realize(note_ready)[0])
            next_trill = None
          elif next_inveted_turn:
            symbols.extend(inverted_turn.realize(note_ready)[-1])
            next_inveted_turn = None
          elif next_turn:
            symbols.extend(turn.realize(note_ready)[-1])
            next_turn = None
          elif next_mordent:
            symbols.extend(mord.realize(note_ready)[0])
            symbols.append(mord.realize(note_ready)[1])
            next_mordent = None
          else:
            symbols.append(note_ready)

        elif 'accidental' in label:
          if 'Double' in label:
            if 'Flat' in label:
              next_accidental = '--'
            elif 'Sharp' in label:
              next_accidental = '##'
          elif 'flat' in label:
            next_accidental = '-'
          elif 'sharp' in label:
            next_accidental = '#'
          elif 'natural' in label:
            next_accidental = 'natural'
        elif 'ornament' in label:
          if 'Trill' in label:
            next_trill = True
          elif 'TurnInverted' in label:
            next_inveted_turn = True
          elif 'Turn' in label:
            next_turn = True
          elif 'Mordent' in label:
            next_mordent = True

        elem_id += 1


      if len(key_sigs):
        m.append(key.KeySignature(len(key_sigs) if 'Sharp' in key_sigs[0] else -len(key_sigs)))

      m.append(symbols)
      for indx, dyn in dynamics_list:
        m.insert(indx, dyn)

      if is_g_part:
        g_part.append(m)
      else:
        f_part.append(m)

    parts = [g_part, f_part]

  # print(recognized_music_sheets)
  s = stream.Score()
  s.append(parts)
  s.show()
  s.show('text')
  s.show('midi')
  s.write() #! TODO: придумать как соединить этот файл и main

#recognize(dataset, dataset352)