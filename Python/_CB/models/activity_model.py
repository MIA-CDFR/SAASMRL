class ActivityModel:
    @staticmethod
    def classify(acc, hr):
        intensidade = 0.7 * acc + 0.3 * hr

        if intensidade < 0.3:
            return "parado"
        elif intensidade < 0.7:
            return "leve"
        else:
            return "intensa"