def get_navigation(boxes, distances, frame_width):
    if not boxes:
        return "Path is clear"

    center_x = frame_width // 2

    priority = 0
    for i, d in enumerate(distances):
        if d == "very close":
            priority = i
            break

    x1, y1, x2, y2 = boxes[priority]
    obj_center = (x1 + x2) // 2
    distance = distances[priority]

    if distance == "very close":
        return "Stop immediately. Obstacle very close"

    if obj_center < center_x - 120:
        return f"Obstacle on left. Move right ({distance})"
    elif obj_center > center_x + 120:
        return f"Obstacle on right. Move left ({distance})"
    else:
        return f"Obstacle ahead. Move carefully ({distance})"