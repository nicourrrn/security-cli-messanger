import argparse
import asyncio
import base64
import json
import os

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP

from models import generate_rsa_keys, load_keys, save_keys


def encrypt_message(public_key, message):
    encrypted = public_key.encrypt(
        message.encode(),
        OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_message(private_key, encrypted_message):
    encrypted_message = base64.b64decode(encrypted_message)
    decrypted = private_key.decrypt(
        encrypted_message,
        OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return decrypted.decode("utf-8")


# Client class
class Client:
    def __init__(self, base_url, name, private_key, public_key):
        self.base_url = base_url
        self.name = name
        self.private_key = private_key
        self.public_key = public_key
        self.session = aiohttp.ClientSession()

    async def register(self):
        payload = {
            "name": self.name,
            "publicKey": self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode(),
        }
        async with self.session.post(
            f"{self.base_url}/registration", json=payload
        ) as response:
            print(await response.text())

    async def send_data(self, target, message):
        async with self.session.get(f"{self.base_url}/clients") as response:
            clients = await response.text()
            clients = json.loads(clients)

        target_client = next((c for c in clients if c["name"] == target), None)
        if not target_client:
            print(f"Client '{target}' not found!")
            return

        target_public_key = serialization.load_pem_public_key(
            target_client["publicKey"].encode()
        )
        encrypted_data = encrypt_message(target_public_key, message)

        payload = {"target": target, "encryptedData": encrypted_data.hex()}
        async with self.session.post(
            f"{self.base_url}/send_data", json=payload
        ) as response:
            print(await response.text())

    async def get_clients(self):
        async with self.session.get(f"{self.base_url}/clients") as response:
            clients = await response.text()
            clients = json.loads(clients)
            print(json.dumps(clients, indent=4))

    async def get_updates(self):
        headers = {"User": self.name}  # Add the user's name to the headers
        while True:
            async with self.session.get(
                f"{self.base_url}/updates", headers=headers
            ) as response:
                updates = await response.text()
                updates = json.loads(updates)
                for update in updates:
                    try:
                        encrypted_data = bytes.fromhex(update["encryptedData"])
                        message = decrypt_message(self.private_key, encrypted_data)
                        print(f"Update from {update['source']}: {message}")
                    except Exception as e:
                        print(f"Failed to decrypt update: {e}")
            await asyncio.sleep(0.5)

    async def close(self):
        await self.session.close()


# Main function
async def main():
    parser = argparse.ArgumentParser(description="Messenger CLI")
    parser.add_argument(
        "command",
        choices=["register", "send", "clients", "updates"],
        help="Command to execute",
    )
    parser.add_argument(
        "--target", help="Target client name (required for send command)"
    )
    parser.add_argument("--message", help="Message to send (required for send command)")
    parser.add_argument("--name", required=True, help="Your client name")
    parser.add_argument(
        "--server", default="http://localhost:8000", help="Server base URL"
    )
    args = parser.parse_args()

    # Generate RSA keys for the client

    if not os.path.exists("keys.json"):
        private_key, public_key = generate_rsa_keys()
        save_keys(private_key, public_key)
    else:
        private_key, public_key = load_keys()
    client = Client(args.server, args.name, private_key, public_key)

    try:
        if args.command == "register":
            await client.register()
        elif args.command == "send":
            if not args.target or not args.message:
                print("Error: --target and --message are required for send command")
                return
            await client.send_data(args.target, args.message)
        elif args.command == "clients":
            await client.get_clients()
        elif args.command == "updates":
            await client.get_updates()
    except KeyboardInterrupt:
        print("Stopping client...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
