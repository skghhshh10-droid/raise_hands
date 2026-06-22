from student import Student
from pose_detector import get_status
from event_manager import EventManager
from scorer import Scorer
from statistics import Statistics

# 추후 이름 및 이벤트 연결

student = Student()

event_manager = EventManager()

status = get_status()

event = event_manager.create_event(status)

print("\n===== 이벤트 발생 =====")
print(event)

approve = input(
    "\n이 이벤트를 승인하시겠습니까? (y/n): "
)

if approve.lower() == "y":

    event_manager.approve_event(
        event["id"]
    )

    print("승인 완료")

else:

    event_manager.reject_event(
        event["id"]
    )

    print("거절 완료")

Scorer.apply_event(student, event)


total_score = student.get_total_score()

level = Statistics.get_level(total_score)

print("\n===== 학생 정보 =====")

print("이름 :", student.name)

print(
    "출석 점수 :",
    student.attendance_score
)

print(
    "참여도 점수 :",
    student.participation_score
)

print(
    "발표 횟수 :",
    student.presentation_count
)

print(
    "총점 :",
    total_score
)

print(
    "참여도 레벨 :",
    level
)