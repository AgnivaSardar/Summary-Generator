class TimelineAnalyzer:

    @staticmethod
    def sort_events(events):

        return sorted(

            events,

            key=lambda event:
            event["date"]
        )