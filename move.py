# Class for passing players' moves
class Move:
    def __init__(self, _pid: int, _type: str, _value: int | str = ""):
        self.pid = _pid
        self.type = _type
        self.value = _value

    def __str__(self):
        return (
            f"[{self.pid}: {self.type} (dupa{self.value})]"
            if self.value
            else f"[{self.pid}: {self.type}]"
        )
