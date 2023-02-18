
# Class for passing players' moves
class Move:
    def __init__(self, _pid, _type, _value = None):
        self.pid = _pid
        self.type = _type
        self.value = _value

    def __str__(self):
        return f"[{self.pid}: {self.type} ({self.value})]" if self.value else f"[{self.pid}: {self.type}]"
