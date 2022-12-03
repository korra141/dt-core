import numpy as np
import cv2
import os
import ctypes

class Model():
    def __init__(self):
        pass
    def infer(self, image):
        raise NotImplementedError()

class ModelWrapper():
    def __init__(self, model_name, dt_token, debug=False):

        # For simpler model
        if model_name == "baseline":
            from object_detection import BaseModel
            self.model = BaseModel()
            return
        
        cache_path = "/code/solution/nn_models"
        from dt_device_utils import DeviceHardwareBrand, get_device_hardware_brand
        from dt_mooc.cloud import Storage

        if get_device_hardware_brand() == DeviceHardwareBrand.JETSON_NANO:
            cache_path = "/data/config/nn_models"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        storage = Storage(dt_token)
        storage.cache_directory = cache_path # todo this is dirty fix upstram in lib
        file_already_existed = storage.is_hash_found_locally(model_name, cache_path)
        storage.download_files(model_name, cache_path)
        weight_file_path = f"{storage.cache_directory}/{model_name}"


        if get_device_hardware_brand() == DeviceHardwareBrand.JETSON_NANO and not file_already_existed:
            print("\n\n\n\nCONVERTING TO ONNX. THIS WILL TAKE A LONG TIME...\n\n\n")
            # https://github.com/duckietown/tensorrtx/tree/dt-yolov5/yolov5
            run("git clone https://github.com/duckietown/tensorrtx.git -b dt-obj-det")
            run(f"cp {weight_file_path}.wts ./tensorrtx/yolov5.wts")
            run(f"cd tensorrtx && ls && chmod 777 ./do_convert.sh && ./do_convert.sh", exception_on_failure=True)
            run(f"mv tensorrtx/build/yolov5.engine {weight_file_path}.engine")
            run(f"mv tensorrtx/build/libmyplugins.so {weight_file_path}.so")
            run("rm -rf tensorrtx")
            print("\n\n\n\n...DONE CONVERTING! NEXT TIME YOU RUN USING THE SAME MODEL, WE WON'T NEED TO DO THIS!\n\n\n")

        if get_device_hardware_brand() == DeviceHardwareBrand.JETSON_NANO:
            self.model = TRTModel(weight_file_path)
        
        else:
            self.model = AMD64Model(weight_file_path)


    def infer(self, image):
        return self.model.infer(image)


class AMD64Model():
    def __init__(self, weight_file_path):
        super().__init__()

        import torch
        torch.hub.set_dir('/code/solution/nn_models')
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=f'{weight_file_path}.pt')
        try:
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            else:
                self.model = self.model.cpu()
        except Exception:
            self.model = self.model.cpu()

    def infer(self, image):
        # TODO size should be read from one place
        det = self.model(image, size=416)

        xyxy = det.xyxy[0]  # grabs det of first image (aka the only image we sent to the net)

        if xyxy.shape[0] > 0:
            conf = xyxy[:,-2]
            clas = xyxy[:,-1]
            xyxy = xyxy[:,:-2]

            return xyxy, clas, conf
        return [], [], []

class TRTModel(Model):
    def __init__(self, weight_file_path):
        super().__init__()
        ctypes.CDLL(weight_file_path+".so")
        from object_detection.tensorrt_model import YoLov5TRT
        self.model = YoLov5TRT(weight_file_path+".engine")
    def infer(self, image):
        # todo ensure this is in boxes, classes, scores format
        results = self.model.infer_for_robot([image])
        boxes = results[0][0]
        confs = results[0][1]
        classes = results[0][2]

        if classes.shape[0] > 0:
            return boxes, classes, confs
        return [], [], []




