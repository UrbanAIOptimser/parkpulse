import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO  # Ensure this import is correct for your setup
import sys

# Load the YOLO model
model = YOLO("models/yolov8s.pt")  # Ensure the model file exists at this path

# Open the video file
cap = cv2.VideoCapture("park.mp4")

# Get video properties
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = cap.get(cv2.CAP_PROP_FPS)

# Define the codec and create VideoWriter object to save the video
output_file_name = "output.mp4"
fourcc = cv2.VideoWriter_fourcc(*"H264")  # Changed the codec to H.264
out = cv2.VideoWriter(output_file_name, fourcc, fps, (frame_width, frame_height))

# Load class labels from file
with open("coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

# Define parking area coordinates
area = [(386, 101), (361, 142), (602, 195), (601, 147)]

frame_count = 0  # Counter for frames
skip_frames = 5  # Number of frames to skip before processing the next one

# Process video
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Skip frames for efficiency
    if frame_count % skip_frames != 0:
        frame_count += 1
        continue

    frame_count += 1

    # Resize frame for processing
    frame = cv2.resize(frame, (1020, 500))

    # Run YOLO model on the frame
    results = model.predict(frame)

    # Extract bounding boxes from the model's results
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    # Initialize counter for cars within the area
    cars_in_area_count = 0

    for index, row in px.iterrows():
        x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
        d = int(row[5])
        c = class_list[d]
        if c == "car":
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # Check if the center of the car is inside the polygon
            if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:
                cars_in_area_count += 1  # Increment count for cars within the area
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)
                cv2.putText(
                    frame,
                    str(c),
                    (x1, y1),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                )

    # Draw the parking area
    cv2.polylines(frame, [np.array(area, np.int32)], True, (0, 255, 255), 2)
    # Display count of cars in the area
    cv2.putText(
        frame,
        f"Cars in area: {cars_in_area_count}",
        (50, 60),
        cv2.FONT_HERSHEY_PLAIN,
        5,
        (255, 0, 0),
        3,
    )

    # Show and save the frame
    cv2.imshow("Processed Video", frame)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
