PATH_TO_WEIGHTS = r"wght"
EXISTENCE_THRESHOLD = 0.4
V3_LIST26 = {1: "staff", 2: "clefCAlto", 3: "clefCTenor", 4: "clefG", 5: "clefF"}
V3_LIST52 = {
    1: 'ledgerLine',
    2: 'repeatDot',
    3: 'clef8', 4: 'clef15',
    5: 'slur',
    6: 'beam',
    7: 'timeSig0', 8: 'timeSig1', 9: 'timeSig2', 10: 'timeSig3', 11: 'timeSig4',
    12: 'timeSig5', 13: 'timeSig6', 14: 'timeSig7', 15: 'timeSig8', 16: 'timeSig9',
    17: 'timeSigCommon', 18: 'timeSigCutCommon',
    19: 'noteheadBlackOnLine', 20: 'noteheadBlackInSpace',
    21: 'noteheadHalfOnLine', 22: 'noteheadHalfInSpace',
    23: 'noteheadWholeOnLine', 24: 'noteheadWholeInSpace',
    25: 'noteheadDoubleWholeOnLine', 26: 'noteheadDoubleWholeInSpace',
    27: 'augmentationDot',
    28: 'tie',
    29: 'tremolo1', 30: 'tremolo2', 31: 'tremolo3', 32: 'tremolo4',
    33: 'flag8thUp', 34: 'flag16thUp', 35: 'flag32ndUp', 36: 'flag64thUp', 37: 'flag128thUp',
    38: 'flag8thDown', 39: 'flag16thDown', 40: 'flag32ndDown', 41: 'flag64thDown', 42: 'flag128thDown',
    43: 'accidentalFlat', 44: 'accidentalNatural', 45: 'accidentalSharp',
    46: 'accidentalDoubleSharp', 47: 'accidentalDoubleFlat',
    48: 'keyFlat', 49: 'keyNatural', 50: 'keySharp',
    51: 'articAccentAbove', 52: 'articAccentBelow', 53: 'articStaccatoAbove', 54: 'articStaccatoBelow',
    55: 'articTenutoAbove', 56: 'articTenutoBelow', 57: 'articStaccatissimoAbove', 58: 'articStaccatissimoBelow',
    59: 'articMarcatoAbove', 60: 'articMarcatoBelow',
    61: 'tuplet3', 62: 'tuplet6',
    63: 'restHBar', 64: 'restDoubleWhole', 65: 'restWhole', 66: 'restHalf', 67: 'restQuarter',
    68: 'rest8th', 69: 'rest16th', 70: 'rest32nd', 71: 'rest64th', 72: 'rest128th',
    73: 'dynamicP', 74: 'dynamicM', 75: 'dynamicF', 76: 'dynamicS', 77: 'dynamicZ', 78: 'dynamicR',
    79: 'ornamentTrill', 80: 'ornamentTurn', 81: 'ornamentTurnInverted', 82: 'ornamentMordent',
    83: 'stringsDownBow', 84: 'stringsUpBow',
    85: 'arpeggiato',
    86: 'tupletBracket',
    87: 'fingering0', 88: 'fingering1', 89: 'fingering2', 90: 'fingering3', 91: 'fingering4', 92: 'fingering5',
    93: 'tuplet1', 94: 'tuplet7', 95: 'tuplet8', 96: 'tuplet9'}

IMAGE_SIZE = (416, 416)
STOP_FIND_LIST = ["ledgerLine", "stem"]