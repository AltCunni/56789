class Coder:
    def __init__(self, key):
        self.key = key

    def code(self, msg) -> str:
        return "".join([chr(ord(msg[i]) ^ self.key) for i in range(len(msg))])

    def decode(self, msg) -> str:
        return "".join([chr(ord(msg[i]) ^ self.key) for i in range(len(msg))])

class DiffHel:
    def __init__(self, ab, p, g):
        self._ab = ab
        self._p = p
        self._g = g

    @property
    def calculate_key(self):
        return self._g ** self._ab % self._p

    def calculate_k(self, mixed_key):
        return mixed_key ** self._ab % self._p