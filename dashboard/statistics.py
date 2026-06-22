# 출석 통계 모듈

def attendance_count(students):
    count = 0
    for s in students:
        if s.attented:
            count += 1
    return count

def attendance_rate(students):
    if len(stydents) == 0:
        return 0
    return attendance_count(students) / len(students)

