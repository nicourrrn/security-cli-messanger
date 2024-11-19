import base64
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP


def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key, filename="keys.json"):
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    keys = {
        "private_key": base64.b64encode(private_key_bytes).decode(),
        "public_key": base64.b64encode(public_key_bytes).decode(),
    }
    with open(filename, "w") as f:
        f.write(json.dumps(keys))


def load_keys(filename="keys.json"):
    with open(filename, "r") as f:
        keys = json.load(f)
    private_key_bytes = base64.b64decode(keys["private_key"].encode())
    public_key_bytes = base64.b64decode(keys["public_key"].encode())
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    public_key = serialization.load_pem_public_key(public_key_bytes)
    return private_key, public_key
