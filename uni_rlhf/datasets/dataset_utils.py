import cv2
from pathlib import Path
import os


def video_to_frames(video_path, output_path):
    """_summary_: Converting video path to image_path

    Args:
        video_path (_type_): _description_
        output_path (_type_): _description_
    """
    cap = cv2.VideoCapture(video_path)
    os.makedirs(output_path, exist_ok=True)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        filename = os.path.join(output_path, f"{count}.jpg")
        cv2.imwrite(filename, frame)
        count += 1
    cap.release()

def reformat_video_info(video_info):
    combined_video_info = []
    n = len(list(video_info.values())[0])
    for i in range(n):
        new_dict = {}
        for key, value in video_info.items():
            if not isinstance(value[i], str):
                temp_value = int(value[i])
                new_dict[key] = temp_value
            else:
                new_dict[key] = value[i]
        combined_video_info.append(new_dict)
    return combined_video_info