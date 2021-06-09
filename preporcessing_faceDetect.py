import cv2
import numpy as np
import Facedetect
from skimage.util import img_as_float
import h5py


class DatasetDeepPhysUBFC:
    def __init__(self):
        self.path = "/home/js/Desktop/UBFC"
        self.subject_cnt = [1, 3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33,
                            34, 35, 36, 37, 38, 39, 40, 42, 43, 44, 45, 46, 47]
        self.subject_cnt = [49]

    def __call__(self):
        output_video = np.zeros((1, 36, 36, 6))
        output_label = np.zeros((1,))
        for sub_cnt in self.subject_cnt:
            raw_video = self.preprocess_raw_video(self.path + "/subject" + str(sub_cnt) + "/vid.avi")
            output_video = np.concatenate((output_video, raw_video), axis=0)
            label = self.preprocess_label(self.path + "/subject" + str(sub_cnt) + "/ground_truth.txt")
            output_label = np.concatenate((output_label, label), axis=0)
            print(sub_cnt)
        output_video = np.delete(output_video, 0, 0)
        output_label = np.delete(output_label, 0)
        # Save Data
        data_file = h5py.File('/home/js/Desktop/Data/Pytorch_rppgs_save/preprocessing/test/UBFC_test_49.hdf5', 'w')
        data_file.create_dataset('output_video', data=output_video)
        data_file.create_dataset('output_label', data=output_label)
        data_file.close()

        return output_video, output_label

    def preprocess_raw_video(self, path):
        cap = cv2.VideoCapture(path)
        frame_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        raw_video = np.empty((frame_total - 1, 36, 36, 6))
        prev_frame = None
        j = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break
            crop_frame = self.face_detect(frame)
            if prev_frame is None:
                prev_frame = crop_frame
                continue
            raw_video[j, :, :, :3], raw_video[j, :, :, -3:] = self.normalize_difference(prev_frame, crop_frame)
            prev_frame = crop_frame
            j += 1
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
        cap.release()
        return raw_video

    def face_detect(self, frame):
        face_detector = Facedetect.Facedetect()
        src_cols = frame.shape[0]
        src_rows = frame.shape[1]
        ratio_cols = src_cols / 800
        ratio_rows = src_rows / 1200
        out_result = face_detector.detect(cv2.resize(frame, dsize=(128, 128), interpolation=cv2.INTER_CUBIC))
        parameter_width = 30
        parameter_height = 100
        for i in range(len(out_result)):
            if len(out_result[i]) < 15:
                break
            for j in range(len(out_result[i])):
                if j % 2 is 1:
                    out_result[i][j] = int(out_result[i][j] * ratio_cols)
                else:
                    out_result[i][j] = int(out_result[i][j] * ratio_rows)
        dst = cv2.resize(
            img_as_float(frame[out_result[0][1] - parameter_height:out_result[0][3] + int(parameter_height / 2),
                         out_result[0][12] - parameter_width:out_result[0][14] + parameter_width]), dsize=(36, 36),
            interpolation=cv2.INTER_AREA)
        dst = cv2.cvtColor(dst.astype('float32'), cv2.COLOR_BGR2RGB)
        dst[dst > 1] = 1
        dst[dst < (1 / 255)] = 1 / 255
        return dst

    def normalize_difference(self, prev_frame, crop_frame):
        # motion input
        M = (crop_frame - prev_frame) / (crop_frame + prev_frame)
        M = M / np.std(M)
        # appearance input
        A = crop_frame / np.std(crop_frame)

        return M, A

    def preprocess_label(self, path):
        # Load input
        f = open(path, 'r')
        f_read = f.read().split('\n')
        label = ' '.join(f_read[0].split()).split()
        label = list(map(float, label))
        delta_label = []
        for i in range(len(label) - 1):
            delta_label.append(label[i + 1] - label[i])
        delta_label = np.array(delta_label).astype('float32')
        delta_pulse = delta_label.copy()
        f.close()
        # Normalize
        part = 0
        window = 32
        while part < (len(delta_pulse) // window) - 1:
            delta_pulse[part * window:(part + 1) * window] /= np.std(delta_pulse[part * window:(part + 1) * window])
            part += 1
        if len(delta_pulse) % window != 0:
            delta_pulse[part * window:] /= np.std(delta_pulse[part * window:])

        return delta_pulse
