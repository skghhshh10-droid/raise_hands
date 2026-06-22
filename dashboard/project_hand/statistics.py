class Statistics:

    @staticmethod
    def get_level(total_score):

        if total_score < 20:
            return "LOW"

        elif total_score < 50:
            return "MEDIUM"

        return "HIGH"