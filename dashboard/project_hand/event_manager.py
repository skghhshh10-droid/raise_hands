class EventManager:

    def __init__(self):
        self.events = []
        self.event_id = 1

    def create_event(self, event_type):

        event = {
            "id": self.event_id,
            "type": event_type,
            "status": "pending"
        }

        self.events.append(event)
        self.event_id += 1

        return event

    def approve_event(self, event_id):

        for event in self.events:

            if event["id"] == event_id:
                event["status"] = "approved"
                return event
    def reject_event(self, event_id) :

        for event in self.events:
            if event["id"] == event_id :
                event["status"] = "rejected"
                return event
                
