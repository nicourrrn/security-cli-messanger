import asyncio
import json

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP


# RSA utilities
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_message(public_key, message):
    encrypted = public_key.encrypt(
        message.encode(),
        OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return encrypted


def decrypt_message(private_key, encrypted_message):
    decrypted = private_key.decrypt(
        encrypted_message,
        OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return decrypted.decode()


# Client class
class P2PClient:
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
        # Fetch the public key of the target from the clients endpoint
        async with self.session.get(f"{self.base_url}/clients") as response:
            clients = await response.json()

        target_client = next(
            (c for c in clients["clients"] if c["name"] == target), None
        )
        if not target_client:
            print(f"Client '{target}' not found!")
            return

        # Encrypt message with the target's public key
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
            clients = await response.json()
            print(json.dumps(clients, indent=4))

    async def get_updates(self):
        while True:
            async with self.session.get(f"{self.base_url}/updates") as response:
                updates = await response.json()
                for update in updates:
                    try:
                        # Decrypt incoming message
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
    # Generate RSA keys for the client
    private_key, public_key = generate_rsa_keys()
    client_name = "pustostas"
    base_url = "http://localhost:8000"

    client = P2PClient(base_url, client_name, private_key, public_key)

    try:
        # Register client
        await client.register()

        # Fetch and print clients
        # await client.get_clients()

        # Send a message to another client
        # target_name = "nicourrrn"
        # message = "Hello, this is a test!"
        # await client.send_data(target_name, message)

        # Start fetching updates
        # await client.get_updates()

    except KeyboardInterrupt:
        print("Stopping client...")
    finally:
        await client.close()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
