class TimeStructure:
    def __init__(self, hours=0, minutes=0, days=(0,)):
        self.days = days
        self.hours = hours
        self.minutes = minutes

    def __str__(self):
        return f"{self.hours:02d}:{self.minutes:02d}"


