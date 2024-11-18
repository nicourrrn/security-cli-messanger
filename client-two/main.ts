import {
  generateKeyPairSync,
  publicEncrypt,
  privateDecrypt,
  constants,
} from "crypto";

const urlBase = "http://localhost:8000";

class Client {
  name: string;
  publicKey: string;
  privateKey: string | null;

  constructor(name: string, publicKey: string, privateKey: string) {
    this.name = name;
    this.publicKey = publicKey;
    this.privateKey = privateKey;
  }
}

class Data {
  source: string;
  target: string;
  encryptedData: string;

  constructor(source: string, target: string, encryptedData: string) {
    this.source = source;
    this.target = target;
    this.encryptedData = encryptedData;
  }

  encrypt(publicKey: string) {
    this.encryptedData = publicEncrypt(
      {
        key: publicKey,
        padding: constants.RSA_PKCS1_OAEP_PADDING,
        oaepHash: "sha256",
      },
      Buffer.from(this.encryptedData),
    ).toString("base64");
  }

  decrypt(privateKey: string) {
    try {
      this.encryptedData = privateDecrypt(
        {
          key: privateKey,
          padding: constants.RSA_PKCS1_OAEP_PADDING,
          oaepHash: "sha256",
        },
        Buffer.from(this.encryptedData, "base64"),
      ).toString();
    } catch (error) {
      console.log("Error decrypting data");
    }
  }
}

class MessangesClient {
  me: Client;
  clients: Client[];
  updates: Data[];
  constructor(client: Client) {
    this.me = client;
    this.clients = [];
    this.updates = [];
  }

  async registrations(): Promise<string> {
    const response = await fetch(`${urlBase}/registration`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(this.me),
    });
    return response.text();
  }

  async getClients(): Promise<Client[]> {
    const response = await fetch(`${urlBase}/clients`, {
      method: "GET",
    });
    this.clients = await response.json();

    return this.clients;
  }

  async sendData(rawData: string, target: Client): Promise<string> {
    let data = new Data(this.me.name, target.name, rawData);
    data.encrypt(target.publicKey);

    const response = await fetch(`${urlBase}/send_data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return response.text();
  }

  async getUpdates(): Promise<Data[]> {
    const response = await fetch(`${urlBase}/updates`, {
      method: "GET",
      headers: { User: this.me.name },
    });
    let data = (await response.json()) as Data[];

    data = data.map((d) => new Data(d.source, d.target, d.encryptedData));
    data.forEach((d: Data) => d.decrypt(this.me.privateKey || ""));

    this.updates.concat(data);

    return data;
  }
}

const { publicKey, privateKey } = generateKeyPairSync("rsa", {
  modulusLength: 2048,
  publicKeyEncoding: {
    type: "spki",
    format: "pem",
  },
  privateKeyEncoding: {
    type: "pkcs8",
    format: "pem",
  },
});

const client = new Client(prompt("Input your username"), publicKey, privateKey);
const messangesClient = new MessangesClient(client);

console.log(await messangesClient.registrations());
setInterval(async () => {
  let newMessages = await messangesClient.getUpdates();
  console.write("----------NEW MESSAGES----------\n");
  for (let m of newMessages) {
    console.log(`New message from ${m.source}: ${m.encryptedData}`);
  }
  console.write("--------------------------------\n");
}, 100);

while (true) {
  for (let c in await messangesClient.getClients()) {
    console.write(`${c}) ${messangesClient.clients[c].name}\n`);
  }

  let target = parseInt(prompt("Select a target: "));
  if (isNaN(target) || target > messangesClient.clients.length) {
    console.log("Invalid target");
    continue;
  }
  let lastMessage = false;
  while (!lastMessage) {
    let message = prompt("Type a message: ");
    if (message === "exit") {
      lastMessage = true;
      continue;
    }
    console.log(
      `Sending ${message} to ${messangesClient.clients[target].name}`,
    );
    console.log(
      await messangesClient.sendData(message, messangesClient.clients[target]),
    );
  }
}
