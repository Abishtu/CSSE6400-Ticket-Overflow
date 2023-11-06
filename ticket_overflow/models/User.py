import uuid

class User():
    def __init__(self, name: str, 
                 email: str) -> None:    
        self._id = str(uuid.uuid4())
        self._name = name
        self._email = email
    
    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'name': self._name,
            'email': self._email
        }
    
    def __repr__(self) -> str:
        return f"<User {self._id} {self._name}>"