from ultralytics import YOLO
from depth import estimate_depth
import numpy as np

model = YOLO("yolov8n.pt")

K = 1.5  # calibration constant

def detect_objects(frame):
    results = model(frame, conf=0.25, verbose=False)

    depth_map = estimate_depth(frame)

    objects = []
    boxes = []
    distances = []
    meters_list = []

    r = results[0]

    if r.boxes is None:
        return objects, boxes, distances, meters_list

    for box in r.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        depth_region = depth_map[y1:y2, x1:x2]

        if depth_region.size == 0:
            continue

        avg_depth = np.mean(depth_region)

        meters = K / (avg_depth + 0.01)
        meters = round(meters, 2)

        if meters < 1:
            distance = "very close"
        elif meters < 2:
            distance = "near"
        else:
            distance = "far"

        objects.append(label)
        boxes.append([x1, y1, x2, y2])
        distances.append(distance)
        meters_list.append(meters)

    return objects, boxes, distances, meters_list