import torch
print(torch.__version__)
import utils

#loaded_model = utils.load_model(r"Models/MobileNetV3Large.pth",
#                                n_classes = 3,
#                                optimized=0)

#optimized_model = utils.load_model(r"Models/Jitted_MobileNetV2.pth",
#                                   n_classes = 3,
#                                   optimized=1)


#for _ in range(100):
#    img,performance_list = utils.img_forward(model = optimized_model,
#                                             model_optimized = 0,
#                                             img_path=r"Images/Fractured/example3.jpg",
#                                             verbose=1,
#                                             track_performance=1) 

current_path = utils.os.getcwd()
print(current_path)
scan_path = current_path+"/images/scanned_images"
predicted_folder = current_path+"/images/predicted"
utils.object_detection(folder_path=scan_path,
                       save_folder=predicted_folder)