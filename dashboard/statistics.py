from database.attendance import get_attendance


def attendance_count():

    students = get_attendance()

    return len(students)


def attendance_rate(total_students):

    students = get_attendance()

    if total_students == 0:
        return 0

    return round(
        (len(students) / total_students) * 100,
        1
    )
