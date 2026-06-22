class Student:

    def __init__(self, name):
        self.name = name
        self.attendance_score = 0
        self.participation_score = 0

        self.presentation_count = 0

    def add_attendance(self, score):
        self.attendance_score += score

    def add_participation(self, score):
        self.participation_score += score

    def get_total_score(self):
        return (
            self.attendance_score +
            self.participation_score
        )
    def add_presentation(self):
        self.presentation_count += 1
