import torch
import cv2

midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
midas.eval()

device = torch.device("cpu")
midas.to(device)

transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = transforms.small_transform

def estimate_depth(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth_map = prediction.cpu().numpy()
    depth_map = cv2.normalize(depth_map, None, 0, 1, cv2.NORM_MINMAX)

    return depth_map