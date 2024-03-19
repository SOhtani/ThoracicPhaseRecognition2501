from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
import argparse
import os

import tensorflow as tf
from tensorflow.keras.layers import Dropout
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.keras.applications.efficientnet import EfficientNetB7

import case_names


class FixedDropout(Dropout):
    def _get_noise_shape(self, inputs):
        if self.noise_shape is None:
            # return self.noise_shape
            return None

        concrete_inputs_shape = array_ops.shape(inputs)
        noise_shape = []
        for i, value in enumerate(self.noise_shape):
            noise_shape.append(concrete_inputs_shape[i] if value is None else value)
        return ops.convert_to_tensor(noise_shape)


def save_memory():
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        for k in range(len(physical_devices)):
            tf.config.experimental.set_memory_growth(physical_devices[k], True)
            print('memory growth: ', tf.config.experimental.get_memory_growth(physical_devices[k]))


class Predictor:
    def __init__(self, model_p, width, height):
        self.width, self.height = width, height
        save_memory()
        self.model = self._load_model(model_p)

    def _load_model(self, model_p):
        custom_objects = {
            'tf': tf,
            'relu6': tf.nn.relu6,
            'swish': tf.nn.swish,
            'FixedDropout': FixedDropout,
            'DepthwiseConv2D': tf.keras.layers.DepthwiseConv2D,
        }
        return tf.keras.models.load_model(
            model_p, custom_objects=custom_objects, compile=False)

    def _pre_process(self, image):
        # use another variable not to rewrite image
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR -> RGB
        rgb_image = Image.fromarray(rgb_image)
        rgb_image = rgb_image.resize((self.width, self.height), Image.LANCZOS)
        rgb_image = np.array(rgb_image, dtype=np.float32) / 255.
        batch = np.expand_dims(rgb_image, axis=0)
        return batch
    
    def predict(self, image):
        batch = self._pre_process(image)
        pred = self.model.predict_on_batch(batch)[0]
        return pred


def main(model_p, case_dir, save_root_dir):
    width, height =  224, 224
    predictor = Predictor(model_p, width, height)

    save_taigai_dir = save_root_dir / "taigai"
    save_not_taigai_dir = save_root_dir / "not_taigai"

    taigai_index = 0
    for img_p in tqdm(list(case_dir.glob("**/*.png"))):
        case_id = img_p.parts[-3]
        phase_id = img_p.parts[-2]
        filename = img_p.parts[-1]

        img = cv2.imread(str(img_p))
        pred = predictor.predict(img)

        if np.argmax(pred) == taigai_index:
            save_p = save_taigai_dir / case_id / phase_id / filename
        else:
            save_p = save_not_taigai_dir / case_id / phase_id / filename

        save_p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_p), img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('gpu_id', type=str)
    parser.add_argument('case_index', type=int)
    parser.add_argument('case_list_name', type=str)
    args = parser.parse_args()

    model_p = "/mnt/cloudy_z/result/MTS_Gate_classification/train_182db_test_28db/test/model/last_model.h5"
    case_root_dir = Path("/mnt/data1/input/Thoracic/images/upsampling_considering_taigai")
    save_root_dir = Path("/mnt/data1/input/Thoracic/images/upsampling_considering_taigai_exclude_taigai")

    case_names_list = getattr(case_names, args.case_list_name)

    case_dir = case_root_dir / case_names_list[args.case_index]
    print(case_names_list[args.case_index])
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_id
    main(model_p, case_dir, save_root_dir)
