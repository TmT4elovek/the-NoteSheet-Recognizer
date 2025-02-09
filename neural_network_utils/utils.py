import os

import torch
from torch import nn
import torchvision.transforms as tr

from nns_module import YOLOv3
from parametrs import *  # parametrs



# ------------------------ CONVERT OUT ------------------------------
def cell2coords(box, S: int, i: int, j: int):
  flag = False
  xc_cell, yc_cell, w_cell, h_cell = box.tolist()
  delta_c = IMAGE_SIZE[0] / S
  yc = (yc_cell + i) * delta_c
  xc = (xc_cell + j) * delta_c
  w = w_cell * delta_c
  h = h_cell * delta_c
  # TO CORNERS
  x0 = (xc - (w / 2))
  y0 = (yc - (h / 2))
  x1 = (w + x0)
  y1 = (y0 + h)
  if x0 > x1 or y0 > y1:
    # print(f"Wrong x0 x1 y0 y1. Depicting changed results. \n Real pred: {x0}, {y0}, {x1}, {y1}.")
    flag = True
    x0 = min(x0, x1)
    x1 = max(x0, x1)
    y0 = min(y0, y1)
    y1 = max(y0, y1)
  return flag, [x0, y0, x1, y1]

def translate_output(pred, x, S: int, C: int):  # x - original pic
  # for B = 2
  B = 2

  batch_size = pred.shape[0]
  pred = pred.reshape(batch_size, S, S, ((5 * B) + C))
  box_1 = pred[... , 0:4]
  box_2 = pred[... , 5:9]
  confidence = torch.cat((pred[... , 4].unsqueeze(0), pred[... , 9].unsqueeze(0)), dim=0)
  bestb_idxs = confidence.argmax(0).unsqueeze(-1)
  confidence = (1 - bestb_idxs) * pred[... , 4:5] + bestb_idxs * pred[... , 9:10]
  bestb = (1 - bestb_idxs) * box_1 + bestb_idxs * box_2
  labels_ids = pred[... , (B * 5):].argmax(-1).unsqueeze(-1)
  # OUT
  out = dict()
  for idx in range(batch_size):
    labels = list()
    boxes = list()
    for i in range(S):
      for j in range(S):
        flag, coord_box = cell2coords(bestb[idx, i, j], S, i, j)
        if not flag:
          label = labels_ids[idx, i, j].item() + 1
          if label != 0 and confidence[idx, i, j].item() >= EXISTENCE_THRESHOLD:
            labels.append(label)
            boxes.append(coord_box)
        else:
          # print(f"Model predicted wrong box coords at pic №{idx}.")
          pass
    out[idx] = dict()
    out[idx]["y"] = dict()
    out[idx]["y"]["labels"] = torch.Tensor(labels)
    out[idx]["y"]["boxes"] = torch.Tensor(boxes)
    out[idx]["x"] = x[idx]
  return out
# ------------------------ POSITION ---------------------------------
def area(x0: int, y0: int, x1: int, y1: int, intersection=False) -> int:
  height = x1 - x0
  width = y1 - y0
  if intersection:
    height = height.clamp(0)
    width = width.clamp(0)
  area = height * width
  return area

def intersection(box1: torch.Tensor, box2: torch.Tensor):
  # Expecting box with corners' coordinates
  b1x0 = box1[..., 0]
  b1x1 = box1[..., 2]
  b1y0 = box1[..., 1]
  b1y1 = box1[..., 3]

  b2x0 = box2[..., 0]
  b2x1 = box2[..., 2]
  b2y0 = box2[..., 1]
  b2y1 = box2[..., 3]

  x0, y0 = torch.max(b1x0, b2x0), torch.max(b1y0, b2y0)
  x1, y1 = torch.min(b1x1, b2x1), torch.min(b1y1, b2y1)

  intersection_area = area(x0, y0, x1, y1, intersection=True)
  return intersection_area

def find_dublicates(boxes: torch.Tensor, allowed_error: int=0):
  result_boxes = boxes.clone()
  for idx in range(0, boxes.shape[0]):
    current_box = boxes[idx].unsqueeze(0)
    if (idx + 2) <= result_boxes.shape[0]:
      for idx_box in range((idx + 1), result_boxes.shape[0]):
        if (idx_box + 2) <= result_boxes.shape[0]:
          box = result_boxes[idx_box].unsqueeze(0)
          if intersection(box, current_box) >= allowed_error:
            result_boxes[idx] = torch.mean(torch.cat((box, current_box), dim=0), dim = 0, keepdim=False)
            result_boxes = torch.cat((result_boxes[:idx_box], result_boxes[idx_box + 1:]), axis=0)
  return result_boxes

def check_existance(boxes: torch.Tensor, notes: torch.Tensor, threshold: int=1) -> torch.Tensor:
  exist_idx = list()
  for box in boxes:
    existance_score = 0
    for note in notes:
      if intersection(box.unsqueeze(0), note.unsqueeze(0)) != 0:
        existance_score += 1
    if existance_score >= threshold:
      exist_idx.append([True, True, True, True])
    else:
      exist_idx.append([False, False, False, False])
  return torch.Tensor.bool(torch.Tensor(exist_idx))

def find_by_box(box, obj_list):
  for idx in range(len(obj_list)):
    obj = obj_list[idx]["y"]["boxes"]
    for idx2 in range(obj.shape[0]):
      cbox = obj[idx2].unsqueeze(0)
      if torch.equal(cbox, box):
        return obj_list[idx]["y"]["labels"][idx2]


def search_obj_in_area(obj_list, center_obj: torch.Tensor, environment: torch.Tensor, delta: int):
  result = list()
  center_obj[1], center_obj[3] = center_obj[1] - delta, center_obj[3] + delta

  for note in environment:
    if intersection(note.unsqueeze(0), center_obj.unsqueeze(0)) != 0:
      label = V3_LIST52[find_by_box(note.unsqueeze(0), obj_list).item()]
      if label not in STOP_FIND_LIST:
        result.append((label, note.tolist()))
  return result

def find_staff_lines(obj_list, pred_note_tensor: torch.Tensor, pred_staff_tensor: torch.Tensor, delta: int=1.5, img_size: int=416, dinamic_delta: bool=True):
  ALLOWED_ERROR = 2
  readed_notes = dict()
  # "Delta" is how much we expand the boxes due to the error

  note_dict = translate_output(pred_note_tensor[1].unsqueeze(0), pred_note_tensor[0].unsqueeze(0), 52, len(V3_LIST52))
  staff_dict = translate_output(pred_staff_tensor[1].unsqueeze(0), pred_staff_tensor[0].unsqueeze(0), 26, len(V3_LIST26))

  # staff_tensor = staff_dict[0]["y"]["boxes"]
  note_tensor = note_dict[0]["y"]["boxes"]
  staff_tensor = list()
  for label_idx in range(len(staff_dict[0]["y"]["labels"])):
    label = staff_dict[0]["y"]["labels"][label_idx]
    label = V3_LIST26[label.item()]
    if label == "staff":
      staff = staff_dict[0]["y"]["boxes"][label_idx].tolist()
      staff_tensor.append(staff)
  staff_tensor = torch.Tensor(staff_tensor)
  staff_tensor = find_dublicates(staff_tensor, ALLOWED_ERROR)
  exist_mask = check_existance(staff_tensor, note_tensor, 2)
  staff_tensor[~exist_mask] = False
  top_note, top_note_idx = torch.min(note_tensor[..., 1].unsqueeze(-1), dim=0)
  bottom_note = note_tensor[top_note_idx, 3]
  top_staff, top_staff_idx = torch.min(staff_tensor[..., 1].unsqueeze(-1), dim=0)
  bottom_staff = staff_tensor[top_staff_idx, 3]
  note_label = V3_LIST52[find_by_box(note_tensor[top_note_idx], obj_list).item()]
  # CHECK ERROR
  if (bottom_staff + delta) < (top_note - delta):
    print("Unreadible coordinates")
    return
  if (bottom_note + delta) < (top_staff - delta):
    note_tensor_topfinder = note_tensor.clone()
  while (bottom_note + delta) < (top_staff - delta) or note_label in STOP_FIND_LIST:
     note_tensor_topfinder =  torch.cat((note_tensor_topfinder[:top_note_idx], note_tensor_topfinder[top_note_idx + 1:]), axis=0)
     top_note, top_note_idx = torch.min(note_tensor_topfinder[..., 1].unsqueeze(-1), dim=0)
     bottom_note = note_tensor_topfinder[top_note_idx, 3].item()
     note_label = V3_LIST52[find_by_box(note_tensor[top_note_idx], obj_list).item()]

  for staff_idx in range(staff_tensor.shape[0]):
    staff = staff_tensor[staff_idx]
    if dinamic_delta:
      delta = (staff[3].item() - staff[1].item()) * 0.5
    staff_notes = search_obj_in_area(obj_list, staff, note_tensor, delta)
    readed_notes[staff_idx] = staff_notes

  return readed_notes

# ------------------------- LOAD -----------------------------------

def load_chekpoint(device, model: nn.Module, file_name: str, optim=None):
  state = torch.load(os.path.join(PATH_TO_WEIGHTS, file_name), map_location=torch.device(device))
  model.load_state_dict(state["model"])
  if optim:
    optim.load_state_dict(state["optimizer"])
  model.eval()

# -------------------------------------------------------------------

def import_models():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # Import models
    yolov3_m = YOLOv3(len(V3_LIST26)).to(device)
    yolov3_l = YOLOv3(len(V3_LIST52)).to(device)
    # Load weights
    load_chekpoint(device, yolov3_m, "YOLOv3_medium_params_ep34.pt")
    load_chekpoint(device, yolov3_l, "YOLOv3_large_params_ep114.pt")
    return yolov3_m, yolov3_l

def process_img(imgs, yolov3_m, yolov3_l):
  # DATA: list of pil imgs
  yolov3_m.eval()
  yolov3_l.eval()
   
  image_tr = tr.Compose([
    tr.Grayscale(num_output_channels=3),
    tr.Resize((416, 416)),
    tr.ToTensor(),
  ])
  imgs_input = torch.stack([image_tr(el) for el in imgs])  # imgs_input.shape -> (len(imgs), 3, 416, 416)
  pred_staffs, _ = yolov3_m(imgs_input)
  _, pred_symbols = yolov3_l(imgs_input)
  symbols_translations = translate_output(pred_symbols, imgs_input, 52, len(V3_LIST52))
  notes_on_staff = find_staff_lines(symbols_translations, pred_symbols, pred_staffs)

  return notes_on_staff
