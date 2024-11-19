import readline from "node:readline";

// Створюємо інтерфейс для вводу
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let outputCounter = 0;
let input = "";

console.log(`Введено: ${input}`);
console.log("\x1b[2J");
console.log("\x1b[H");

// Функція для оновлення консолі
function updateConsole() {
  // Очистимо екран
  console.log("\x1b[s");
  console.log("\x1b[H");
  console.log("\x1b[1B");
  console.log(`Оновлення №${outputCounter}`);
  console.log("\x1b[u");
  console.log("\x1b[2A");
  console.write(`Введено: ${rl.line}`);
}

// Асинхронне оновлення даних у консолі
function simulateDataUpdates() {
  setInterval(() => {
    outputCounter++;
    updateConsole();
  }, 1000);
}

// Обробка вводу
rl.on("line", (input) => {
  console.log(`Введено: ${input}`);
  console.log("Продовжуйте вводити:");
});

rl.on("close", () => {
  console.log("Програма завершила роботу");
});

// Запускаємо процес
simulateDataUpdates();
updateConsole();
