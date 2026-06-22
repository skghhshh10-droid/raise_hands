from yolo.detector import detect_hand_raise
from database.attendance import save_attendance
from dashboard.statistics import attendance_count
from ui.main_page import show_dashboard


def main():

    frame = None

    if detect_hand_raise(frame):
        save_attendance("학생1")

    count = attendance_count()

    show_dashboard(count)


if __name__ == "__main__":
    main()
