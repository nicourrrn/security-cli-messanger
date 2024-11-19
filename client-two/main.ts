import { generateKeyPairSync } from "crypto";
import readline from "readline";

import { MessangesClient } from "./client-messages.ts";
import { Client } from "./models.ts";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// const client = Client.withoutKeys("Vadym");
// client.saveMe();

const client = Client.fromFile();
const messangesClient = new MessangesClient(client);

let userInput = "";
let lineHandler = async (line: string) => {};

console.write("\x1b[2J\x1b[H");
console.write(await messangesClient.registrations());

const writeNewMessages = () => {
  setInterval(async () => {
    let newMessages = await messangesClient.getUpdates();
    console.log("\x1b[H\x1b[3B");
    console.write("----------NEW MESSAGES----------\n");
    for (let m of newMessages) {
      console.log(`New message from ${m.source}: ${m.encryptedData}`);
    }
    console.write("--------------------------------\n");
    console.write(`\x1b[H\x1b[1B\x1b[2K${userInput}${rl.line}`);
  }, 500);
};

const chooseTarget = async () => {
  console.write("\x1b[H\x1b[2K");
  for (let c in await messangesClient.getClients()) {
    console.write(`${c}) ${messangesClient.clients[c].name} | `);
  }
  userInput = `Select a target: ${rl.line}`;
  lineHandler = async (line) => {
    let target = parseInt(line);
    if (isNaN(target) || target > messangesClient.clients.length) {
      console.write("Invalid target");
      chooseTarget();
      return;
    }
    sendingMessages(target);
  };
};

const sendingMessages = async (target: number) => {
  console.write("\x1b[H\x1b[2K");
  userInput = "Type a message: ";
  lineHandler = async (line) => {
    if (line === "exit") {
      chooseTarget();
      return;
    }
    console.write(
      `\x1b[2KSending ${line} to \x1b[1m${messangesClient.clients[target].name}\x1b[22m`,
    );
    await messangesClient.sendData(line, messangesClient.clients[target]);
  };
};

rl.on("line", async (line) => {
  await lineHandler(line);
});
chooseTarget();
writeNewMessages();
