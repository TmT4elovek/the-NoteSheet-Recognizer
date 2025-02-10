import torch
from torch import nn



class Convolutional(nn.Module):  # DBL
  def __init__(self, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1, padding=1, bias=False):
    super().__init__()
    self._stack = nn.Sequential(
        nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding, bias=bias),
        nn.BatchNorm2d(out_channels),
        nn.LeakyReLU(0.1),
    )
  def forward(self, x):
    return self._stack(x)
  
class Detection(nn.Module):
  def __init__(self, in_channels: int, C, B):  # where A is number of anchors
    super().__init__()
    out_channels = in_channels // 2
    self.stack = nn.Sequential(
        Convolutional(in_channels=in_channels, out_channels=out_channels, kernel_size=1, padding=0),
        Convolutional(in_channels=out_channels, out_channels=in_channels, kernel_size=3),
        nn.Conv2d(in_channels=in_channels, out_channels=((B * 5) + C), kernel_size=1, padding=0)
    )

  def forward(self, x):
    out = self.stack(x)
    # print(out.shape)
    out = out.reshape(-1, out.shape[2], out.shape[2], out.shape[1])
    return out

class FPN(nn.Module):
  def __init__(self, in_channels, out_channels):
    super().__init__()
    self.conv1 = Convolutional(in_channels=in_channels, out_channels=out_channels, kernel_size=1, padding=0)
    self.up = nn.ConvTranspose2d(out_channels, out_channels, kernel_size=2, stride=2)
    self.conv3 = Convolutional(in_channels=(out_channels * 2), out_channels=out_channels, kernel_size=3)

  def forward(self, x, skip):
    x = self.conv1(x)
    x = self.up(x)
    out = torch.cat([x, skip], dim=1)
    out = self.conv3(out)
    return out

class DBLx5(nn.Module):
  def __init__(self, in_channels):
    super().__init__()
    out_channels = in_channels // 2
    self.stack = nn.Sequential(
        Convolutional(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1),
        Convolutional(in_channels=out_channels, out_channels=in_channels, kernel_size=3, stride=1),
        Convolutional(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1),
        Convolutional(in_channels=out_channels, out_channels=in_channels, kernel_size=3, stride=1),
        Convolutional(in_channels=in_channels, out_channels=in_channels, kernel_size=1, stride=1)
    )

  def forward(self, x):
    out = self.stack(x)
    return x
  
class Residual(nn.Module):  # ResUnit
  def __init__(self, in_channels: int):
    super().__init__()
    self._conv_stack = nn.Sequential(
        Convolutional(in_channels=in_channels, out_channels=(in_channels // 2), kernel_size=1, padding=0),
        Convolutional(in_channels=(in_channels // 2), out_channels=in_channels, kernel_size=3, padding=1),
    )

  def forward(self, x):
    out = self._conv_stack(x)
    return x + out
# ----------------------------------------------------------------------------
class Darknet(nn.Module):
  def __init__(self, is_train=False, weights=None, C:int =None):
    super().__init__()
    # Res11
    self.stack_list1 = nn.Sequential(
        Convolutional(in_channels=3, out_channels=32, kernel_size=3),
        Convolutional(in_channels=32, out_channels=64, kernel_size=3, stride=2),
        Residual(64),
        Convolutional(in_channels=64, out_channels=128, kernel_size=3, stride=2),
        *[Residual(128) for _ in range(2)],
        Convolutional(in_channels=128, out_channels=256, kernel_size=3, stride=2),
        *[Residual(256) for _ in range(8)],
    )
    # Res 8
    self.stack_list2 = nn.Sequential(
        Convolutional(in_channels=256, out_channels=512, kernel_size=3, stride=2),
        *[Residual(512) for _ in range(8)],
    )
    # Res4
    self.stack_list3 = nn.Sequential(
        Convolutional(in_channels=512, out_channels=1024, kernel_size=3, stride=2),
        *[Residual(1024) for _ in range(4)],
    )
    if is_train:
      self._is_train = is_train
      self._bottom = nn.Sequential(
          nn.AdaptiveAvgPool2d((1, 1)),
          nn.Lenear(in_features=496, out_features=C),
          nn.Softmax(),
      )
    else:
      self._is_train = False
      pass

  def _load_weights(self, weights):
    self.load_state_dict(weights, weights_only=True)

  def forward(self, x):
    out1 = self.stack_list1(x)
    out2 = self.stack_list2(out1)
    out3 = self.stack_list3(out2)
    if self._is_train:
      y = self._bottom(out3)
      return y
    return out1, out2, out3
# ----------------------------YOLOv3-------------------------------------- 
class YOLOv3(nn.Module):
  def __init__(self, C, B=2):
    super().__init__()
    self.darknet = Darknet()  # out size 19x19
    self.dbl5_1 = DBLx5(1024)
    self.dbl5_2 = DBLx5(512)
    self.dbl5_3 = DBLx5(256)
    self.detection_1 = Detection(1024, C, B)
    self.detection_2 = Detection(512, C, B)
    self.detection_3 = Detection(256, C, B)
    self.fpn_1 = FPN(1024, 512)
    self.fpn_2 = FPN(512, 256)

  def forward(self, x):
    # x1 - 256x256
    # x2 - 512x512
    # x3 - 1024x1024
    x1, x2, x3 = self.darknet(x)
    out1 = self.dbl5_1(x3)

    out2 = self.fpn_1(out1, x2)
    out2 = self.dbl5_2(out2)

    out3 = self.fpn_2(out2, x1)
    out3 = self.dbl5_3(out3)

    # out1 = self.detection_1(out1)
    out2 = self.detection_2(out2)
    out3 = self.detection_3(out3)

    return out2, out3  
