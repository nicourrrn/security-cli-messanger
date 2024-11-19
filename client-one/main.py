import asyncio
import json

import aiohttp

from models import Client, Data

client = Client.with_name("pustostas")
base_url = "http://localhost:8000"


async def clientToJson(client: Client) -> dict:
    return {"name": client.name, "publicKey": client.public_key.export_key().decode()}


async def clientFromJson(client: dict) -> Client:
    return Client(client["name"], public_key=client["publicKey"])


async def dataFromJson(data: dict, me: Client) -> Data:
    if me.private_key is None:
        raise ValueError("Private key is required to decrypt message")
    return Data.decrypt(
        data["source"], data["target"], data["encryptedData"], me.private_key
    )


async def dataToJson(data: Data, me: Client) -> dict:
    return {
        "source": data.source,
        "target": data.target,
        "encryptedData": data.encrypt(me.public_key),
    }


async def register(session: aiohttp.ClientSession, me: Client):
    async with session.post(
        f"{base_url}/registration", json=await clientToJson(me)
    ) as response:
        response.raise_for_status()


async def get_clients(session: aiohttp.ClientSession) -> list[Client]:
    async with session.get(f"{base_url}/clients") as response:
        response.raise_for_status()
        return [
            await clientFromJson(client)
            for client in await response.json(content_type=None)
        ]


async def send_data(session: aiohttp.ClientSession, me: Client, data: Data):
    async with session.post(
        f"{base_url}/send_data",
        json=await dataToJson(data, me),
    ) as response:
        response.raise_for_status()


async def get_updates(session: aiohttp.ClientSession, me: Client) -> list[Data]:
    async with session.get(
        f"{base_url}/updates", headers={"User": me.name}
    ) as response:
        response.raise_for_status()
        return [
            await dataFromJson(data, me)
            for data in await response.json(content_type=None)
        ]


async def print_clients(clients: list[Client]) -> int:
    for i, client in enumerate(clients):
        print(f"{i}) {client.name}")
    return int(input("Choose client: "))


async def print_send_data(me: Client, target: str) -> Data:
    message = input("Message: ")
    return Data(me.name, target, message)


async def print_updates(updates: list[Data]):
    for update in updates:
        print(f"{update.source}: {update.message}")


async def main():
    http_client = aiohttp.ClientSession()
    me: Client
    try:
        with open("me.json", "r") as f:
            me = Client.load(json.load(f))
    except FileNotFoundError:
        me = Client.with_name(input("Your name: "))
        with open("me.json", "w") as f:
            json.dump(me.dump(), f)

    await register(http_client, me)
    clients = await get_clients(http_client)
    target = 0
    while (command := input("Command: ")) != "exit":
        if command == "clients":
            clients = await get_clients(http_client)
            target = await print_clients(clients)
        elif "send" in command:
            data = await print_send_data(me, clients[target].name)
            await send_data(http_client, me, data)
        elif command == "updates":
            updates = await get_updates(http_client, me)
            await print_updates(updates)
            input("Press Enter to continue...")

        print("\x1b[2J\x1b[H")

    await http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
