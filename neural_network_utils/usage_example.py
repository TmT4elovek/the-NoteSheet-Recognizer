import os

import torchvision.transforms as tr
from PIL import Image

import utils


yolov3_m, yolov3_l = utils.import_models()
file_nemes = ["0.png", "1.png", "2.png"]
path = r"test_dataset"
imgs = list()
for idx in range(len(file_nemes)):
    current_img = file_nemes[idx]
    path_to_img = os.path.join(path, current_img)
    pil_img = Image.open(path_to_img)
    imgs.append(pil_img)
result = utils.process_img(imgs, yolov3_m, yolov3_l)
print(result)