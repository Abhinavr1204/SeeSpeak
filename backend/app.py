from flask import Flask, request, jsonify
import cv2
import numpy as np

from vision import detect_objects
from navigation import get_navigation

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["image"]
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    objects, boxes, distances, meters = detect_objects(frame)
    navigation = get_navigation(boxes, distances, frame.shape[1])

    return jsonify({
        "objects": objects,
        "boxes": boxes,
        "distances": distances,
        "meters": meters,
        "navigation": navigation
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    objects = data.get("objects", [])

    if objects:
        return jsonify({"answer": "I see " + ", ".join(objects[:3])})
    else:
        return jsonify({"answer": "Path is clear"})

if __name__ == "__main__":
    app.run(debug=True)