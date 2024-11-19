import {
  generateKeyPairSync,
  publicEncrypt,
  privateDecrypt,
  constants,
} from "crypto";

import fs from "fs";

export class Client {
  name: string;
  publicKey: string;
  privateKey: string | null;

  constructor(name: string, publicKey: string, privateKey: string) {
    this.name = name;
    this.publicKey = publicKey;
    this.privateKey = privateKey;
  }

  saveMe() {
    fs.writeFileSync(`./me.json`, JSON.stringify(this));
  }

  static fromFile() {
    let data = fs.readFileSync(`./me.json`, "utf8");
    let client = JSON.parse(data);
    return new Client(client.name, client.publicKey, client.privateKey);
  }

  static withoutKeys(name: string) {
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

    return new Client(name, publicKey, privateKey);
  }
}

export class Data {
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
