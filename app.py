from yolo.detector import detect_hand_raise
from database.attendance import save_attendance
from dashboard.statistics import attendance_count
from ui.main_page import show_dashboard

import cv2


def main():

    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    if ret:

        detected, result_frame = detect_hand_raise(frame)

        if detected:
            save_attendance("학생1")

    count = attendance_count()

    show_dashboard(count)

    cap.release()


if __name__ == "__main__":
    main()
