import numpy as np
import pandas as pd
import torch
# torch.backends.quantized.engine = 'qnnpack'
from torchvision import models
import torchvision.transforms as transforms
import time
from cv2 import imread, resize, imshow, waitKey
import os
import warnings
from roboflow import Roboflow

warnings.simplefilter(action='ignore', category=FutureWarning)
from glob import glob
from firebase.databasev2 import base64, datetime


class Quant_MobileNetv3_Large(torch.nn.Module):
    def __init__(self, n_classes):
        super().__init__()
        self.net = models.quantization.mobilenet_v3_large(quantize=False)
        self.last_layer = torch.nn.Linear(1000, n_classes)
        self.dropout = torch.nn.Dropout(p=0.5)

    def forward(self, x):
        x = self.net(x)
        # print(x.shape)
        x = self.dropout(x)
        x = self.last_layer(x)
        # print(x.shape)
        return x


class Jitted_MobileNetv2(torch.nn.Module):
    def __init__(self, n_classes=3, quantization=False):
        super().__init__()
        self.net = models.quantization.mobilenet_v2(pretrained=True,
                                                    quantize=quantization)
        self.last_layer = torch.nn.Linear(1000, n_classes)
        self.dropout = torch.nn.Dropout(p=0.5)

    def forward(self, x):
        x = self.net(x)
        x = self.dropout(x)
        x = self.last_layer(x)
        return x


def load_model(model_path: str, n_classes: int = 3, optimized: int = 0):
    model = None
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    if not optimized:
        model = Jitted_MobileNetv2(n_classes, quantization=False)
        model.load_state_dict(torch.load(model_path,
                                         map_location=torch.device(device)))
        model.to(device)
        model.eval()
        return model

    if optimized:
        model = Jitted_MobileNetv2(n_classes, quantization=False)
        model.load_state_dict(torch.load(model_path,
                                         map_location=torch.device(device)))

        # quantized_model = torch.quantization.quantize_dynamic(model,
        #                                                      {torch.nn.Linear},
        #                                                      dtype=torch.qint8)

        # temp_input = torch.rand(1,3,299,299)
        # traced_model = torch.jit.trace(model, temp_input)

        model.to(device)

        return model


@torch.no_grad()
def img_forward(model, img_path, verbose: int = 0, model_optimized: int = 0, track_performance: int = 0):
    total_since = int(round(time.time() * 1000)) if verbose else None
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    class_map = {0: "Normal", 1: "Implant", 2: "Fracture"}
    img_ready = transforms.Compose([
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        transforms.Lambda(lambda x: x.to(device))])

    img = None
    if type(img_path) == str:
        img = imread(img_path)
        img = resize(img, (299, 299))
    else:
        img = img_path
        img = resize(img, (299, 299))

    img_tensor = torch.from_numpy(img)
    img_tensor = img_tensor.permute(2, 0, 1)
    img_tensor = img_tensor.float()
    img_tensor = img_ready(img_tensor)
    img_tensor = torch.unsqueeze(img_tensor, 0)
    model.eval()

    ttime_elapsed = None
    total_elapsed = None
    max_index = None
    confidence = None
    row = None
    if verbose:
        tsince = int(round(time.time() * 1000))
        output = model(img_tensor)
        ttime_elapsed = int(round(time.time() * 1000)) - tsince
        total_elapsed = int(round(time.time() * 1000)) - total_since
        max_index = torch.argmax(output).item()
        confidence = torch.softmax(output, 1)[0].max().item()
        # flops, params = profile(model, inputs=(img_tensor,)) \ clever_format(flops) -> 435.80M
        print(f"Prediction: {class_map[max_index]}\nConfidence Score: {confidence:.3f}\nInference Time:\
 {ttime_elapsed}ms\nTotal Time: {total_elapsed}ms\nFLOPs: 435.80M")

    if not verbose:
        output = model(img_tensor)
        max_index = torch.argmax(output).item()
        confidence = torch.softmax(output, 1)[0].max().item()
        print(f"Prediction: {class_map[max_index]}\nConfidence Score: {confidence:.3f}")

    ## Verbose=1 inference time FLOP device
    # imshow("image",img)
    # waitKey(0)

    if track_performance:
        csv_path = "Metrics/performance_metrics_default.csv"
        columns = ["Is Optimized", "Prediction", "Confidence Score", "Inference Time (ms)", "Total Time (ms)"]

        row = [model_optimized, class_map[max_index], round(confidence, 3), ttime_elapsed, total_elapsed]
        if not os.path.exists(csv_path):
            df = pd.DataFrame(columns=columns)
            df.to_csv(csv_path, index=False)
        df = pd.read_csv(csv_path)
        df2 = pd.concat([df, pd.DataFrame([row], columns=df.columns)], ignore_index=True)
        df2.to_csv(csv_path, index=False)

    return img_tensor, row


def object_detection(folder_path, save_folder):
    rf = Roboflow(api_key="DljH1huWx0HJuSYMtdhZ")
    project = rf.workspace("deniz-mcj5w").project("aisam-detection")
    # dataset = project.version(1).download("yolov8")
    model = project.version(1).model

    image_files = glob(os.path.join(folder_path, "*.png"))
    response_list = list()
    now = datetime.now()
    dt = now.strftime(r"%d/%m/%Y--%H:%M")

    for idx, image_file in enumerate(image_files):
        image_name = os.path.basename(image_file)
        save_path = os.path.join(save_folder, image_name)
        results = model.predict(image_file, confidence=20, overlap=30)
        response = results.json()
        results.save(save_folder + "/" + image_name)

        patient_id, i, j = image_name.split(".")[0].split("_")
        if not response["predictions"]:
            response_list.append({"patient_id": patient_id,
                                  f"confidence_{i}_{j}": 0,
                                  f"diagnosed_disease{i}_{j}": "Normal",
                                  "date_time": dt,
                                  "is_diagnosed": False,
                                  f"image_{i}_{j}": io_operation(image_file)})
            continue
        else:
            print(response["predictions"])
            response = response["predictions"][0]
            temp = {"patient_id": patient_id,
                    f"confidence_{i}_{j}": round(response["confidence"], 3),
                    f"diagnosed_disease_{i}_{j}": response["class"],
                    "date_time": dt,
                    "is_diagnosed": True,
                    f"image_{i}_{j}": io_operation(image_file)}
            response_list.append(temp)

        # {'predictions': [{'x': 380.0, 'y': 217.0, 'width': 86.0, 'height': 80.0, 'confidence': 0.31693369150161743, 'class': 'onychomycosis',
        #  'image_path': '/home/deniz/please work/test/6.png', 'prediction_type': 'ObjectDetectionModel'}], 'image': {'width': '480', 'height': '640'}}

    return response_list


def show_performance_metrics():
    df = pd.read_csv(r"Metrics/performance_metrics_default.csv")
    print(df.describe())
    print("\n")


def io_operation(img_path: str):
    with open(img_path, 'rb') as f:
        image_data = f.read()

    return base64.b64encode(image_data).decode('utf-8')
