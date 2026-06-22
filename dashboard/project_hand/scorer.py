from config import SCORES


class Scorer:

    @staticmethod
    def apply_event(student, event):

        if event["status"] != "approved":
            return

        point = SCORES[event["type"]]

        if event["type"] == "ATTENDANCE":
            student.add_attendance(point)

        else:
            student.add_participation(point)

            if event["type"] == "QUESTION":
                student.add_presentation()

            if student.participation_score < 0:
                student.participation_score = 0