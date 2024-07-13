import cv2
import numpy as np

video_path3 = r"D:/acsn/a.mp4"
video_path4 = r"D:/acsn/b.mp4"

def check_video_file(path):
    import os
    if not os.path.isfile(path):
        print(f"Ошибка: Файл не существует - {path}")
        return False
    return True

def initialize_tracker(frame, box):
    tracker = cv2.TrackerMIL_create()
    tracker.init(frame, box)
    return tracker

def draw_rectangle(frame, bbox):
    x, y, w, h = [int(i) for i in bbox]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

def calculate_color_vector(frame, bbox):
    x, y, w, h = [int(i) for i in bbox]
    roi = frame[y:y+h, x:x+w]
    avg_color_per_row = np.average(roi, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color

def calculate_frame_difference(prev_frame, curr_frame):
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    frame_diff = cv2.absdiff(gray_prev, gray_curr)
    _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
    return thresh

def get_frame(camera):
    ret, frame = camera.read()
    if not ret:
        return None
    return frame

def frame_diff(prev_frame, cur_frame, next_frame):
    diff_frames1 = cv2.absdiff(next_frame, cur_frame)
    diff_frames2 = cv2.absdiff(cur_frame, prev_frame)
    return cv2.bitwise_and(diff_frames1, diff_frames2)

def check_overlap(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
        return True
    return False

def get_moving_objects(frame, bg_subtractor):
    mask = bg_subtractor.apply(frame)
    _, thresh = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bboxes = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small objects
            x, y, w, h = cv2.boundingRect(contour)
            bboxes.append((x, y, w, h))
    
    return bboxes

def process_videos(video_path3, video_path4):
    if not check_video_file(video_path3) or not check_video_file(video_path4):
        return

    camera3 = cv2.VideoCapture(video_path3)
    camera4 = cv2.VideoCapture(video_path4)

    bg_subtractor3 = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor4 = cv2.createBackgroundSubtractorMOG2()

    bbox3 = None
    bbox4 = None
    tracker3 = None
    tracker4 = None

    prev_frame3 = None
    prev_frame4 = None

    while True:
        frame1 = get_frame(camera3)
        frame2 = get_frame(camera4)
        if frame1 is None or frame2 is None:
            break

        moving_objects3 = get_moving_objects(frame1, bg_subtractor3)
        moving_objects4 = get_moving_objects(frame2, bg_subtractor4)

        if not moving_objects3 and not moving_objects4:
            continue

        if moving_objects3 and bbox3 is None:
            bbox3 = moving_objects3[0]  # Select the first detected object
            tracker3 = initialize_tracker(frame1, bbox3)

        if moving_objects4 and bbox4 is None:
            bbox4 = moving_objects4[0]  # Select the first detected object
            tracker4 = initialize_tracker(frame2, bbox4)

        success3, bbox3 = tracker3.update(frame1) if tracker3 else (False, None)
        success4, bbox4 = tracker4.update(frame2) if tracker4 else (False, None)

        if success3:
            draw_rectangle(frame1, bbox3)
            color_vector3 = calculate_color_vector(frame1, bbox3)
            print(f"Camera 3 color vector: {color_vector3}")

            if prev_frame3 is not None:
                frame_diff3 = calculate_frame_difference(prev_frame3, frame1)
                cv2.imshow("Camera 3 Frame Difference", frame_diff3)

        if success4:
            draw_rectangle(frame2, bbox4)
            color_vector4 = calculate_color_vector(frame2, bbox4)
            print(f"Camera 4 color vector: {color_vector4}")

            if prev_frame4 is not None:
                frame_diff4 = calculate_frame_difference(prev_frame4, frame2)
                cv2.imshow("Camera 4 Frame Difference", frame_diff4)

        # Передача трекеров между камерами
        if success3 and success4:
            if check_overlap(bbox3, bbox4):
                print("Объект пересек слепую зону")
                if tracker3 is not None:
                    tracker4 = tracker3
                    bbox4 = bbox3
                elif tracker4 is not None:
                    tracker3 = tracker4
                    bbox3 = bbox4

        cv2.imshow("Camera 3", frame1)
        cv2.imshow("Camera 4", frame2)

        prev_frame3 = frame1.copy()
        prev_frame4 = frame2.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera3.release()
    camera4.release()
    cv2.destroyAllWindows()

# Запуск обработки видеофайлов
process_videos(video_path3, video_path4)
