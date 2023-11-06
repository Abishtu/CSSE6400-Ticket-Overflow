import uuid

class Ticket():
    def __init__(self, userID: str, concertID: str,
                 host: str, printStatus: str) -> None:    
        self._id = str(uuid.uuid4())
        self._concert = {
            'id': concertID,
            'url': f"{host}api/v1/concerts/{concertID}"
        }
        self._user = {
            'id': userID,
            'url': f"{host}api/v1/users/{userID}"
        }
        self._print_status = printStatus
    
    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'concert': self._concert,
            'user': self._user,
            'print_status': self._print_status,
        }
    
    def __repr__(self) -> str:
        return f"<Ticket {self._user['id']} {self._concert['id']}>"