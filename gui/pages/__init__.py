import cv2
import platform
from glob import glob

LOGO_PATH = "gui/logo.png"
MODEL_PATH = "ai/Models/Jitted_MobileNetV2.pth"
ARDUINO_EXIST = False
FPS = 60
DETECTION_FPS = 5
MIN_STEPS = -20000 
MAX_STEPS = 20000
STEP_SIZE = 20
MICRO_DELAY = 1000
BAUD_RATE = 9600


if platform.system() == 'Windows':
    DEVICE = 'pc'
elif platform.system() == 'Linux' or platform.release() == 'ubuntu':
    DEVICE = 'pi'


if DEVICE == "pc":
    PORT_PATH = 'COM6'
    CV_CAP = cv2.CAP_DSHOW
    CAM_ID = 0
else:
    path_list = glob('/dev/ttyUSB*')
    PORT_PATH = path_list[0]
    CV_CAP = cv2.CAP_V4L
    CAM_ID = "/dev/video0"

CAPTURE = cv2.VideoCapture(CAM_ID, CV_CAP)
# 'dev/ttyUSB0' for linux, 'COM{id}' for windows
