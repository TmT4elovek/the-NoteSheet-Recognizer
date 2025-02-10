import os
from music21 import *
from PIL import Image
from sqlalchemy import create_engine
from backend.static.Entity import SQLALCHEMY_DATABASE_URL

from backend.music21_release import recognize
from backend.neural_network_utils import utils


yolov3_m, yolov3_l = utils.import_models()
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

images = list()
music_sheets = ["1.png", "2.png"]
for j in music_sheets:
    path = os.path.join(r"PATH", j)
    img = Image.open(path)
    images.append(img)
mp3 = recognize(images, yolov3_m, yolov3_l)