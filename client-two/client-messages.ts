import { Client, Data } from "./models.ts";

const urlBase = "http://localhost:8000";

export class MessangesClient {
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
