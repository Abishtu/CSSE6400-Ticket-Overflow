import uuid
class Concert():
    def __init__(self, name: str, 
                 venue: str, date: str,
                 capacity: int, status: str) -> None:    
        self._id = str(uuid.uuid4())
        self._name = name
        self._venue = venue
        self._date = date
        self._capacity = capacity
        self._status = status
    
    def generate_uuid(self) -> None:
        return 

    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'name': self._name,
            'venue': self._venue,
            'date': self._date,
            'capacity': self._capacity,
            'status': self._status,
        }
    
    def __repr__(self) -> str:
        return f"<Concert {self._id} {self._name}>"