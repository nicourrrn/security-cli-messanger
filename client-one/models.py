import base64

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


class Client:
    def __init__(
        self,
        name: str,
        public_key: RSA.RsaKey | str,
        private_key: RSA.RsaKey | None = None,
    ):
        self.name = name
        if isinstance(public_key, str):
            public_key = RSA.import_key(public_key)
        self.public_key: RSA.RsaKey = public_key
        self.private_key: RSA.RsaKey | None = private_key

    @staticmethod
    def load(data: dict) -> "Client":
        return Client(
            name=data["name"],
            private_key=RSA.import_key(data["private_key"]),
            public_key=RSA.import_key(data["public_key"]),
        )

    @staticmethod
    def with_name(name: str) -> "Client":
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()
        return Client(name, private_key=private_key, public_key=public_key)

    def dump(self) -> dict:
        private_key = (
            self.private_key.export_key().decode() if self.private_key else None
        )
        return {
            "name": self.name,
            "private_key": private_key,
            "public_key": self.public_key.export_key().decode(),
        }


class Data:
    def __init__(self, source: str, target: str, message: str):
        self.source = source
        self.target = target
        self.message = message

    def encrypt(self, key: RSA.RsaKey) -> str:
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        return base64.b64encode(cipher.encrypt(self.message.encode())).decode("utf-8")

    @staticmethod
    def decrypt(source: str, target: str, message: str, key: RSA.RsaKey) -> "Data":
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)

        message = cipher.decrypt(base64.b64decode(message)).decode("utf-8")
        return Data(source, target, message)
