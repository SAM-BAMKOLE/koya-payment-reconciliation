// Payment reconciliation.
//
// Reads payments.jsonl and works out how much money we actually collected.
// Run:  node reconcile.js

const fs = require("fs");

function parseAmount(amount) {
  // Convert an amount (number or comma-string) to a number.
  if (typeof amount === "number") return amount;
  if (typeof amount === "string") return Number(amount.replace(/,/g, ""));
  return Number(amount);
}

const latestAttempt = {}; // txn_id -> event with the greatest ts

const lines = fs
  .readFileSync("payments.jsonl", "utf8")
  .split("\n")
  .filter((l) => l.trim().length > 0);

for (const line of lines) {
  // Ignore lines that can't be read.
  let event;
  try {
    event = JSON.parse(line);
  } catch (e) {
    continue;
  }
  // Ignore events without a txn_id.
  const txnId = event && event.txn_id;
  if (!txnId) continue;

  const ts = event.ts || "";
  const current = latestAttempt[txnId];
  if (!current || ts > (current.ts || "")) {
    latestAttempt[txnId] = event;
  }
}

let total = 0;
let count = 0;

for (const txnId of Object.keys(latestAttempt)) {
  const event = latestAttempt[txnId];
  if (event.status === "success") {
    count += 1;
    total += parseAmount(event.amount);
  }
}

const expected = parseInt(fs.readFileSync("expected.txt", "utf8").trim(), 10);

if (count !== expected) {
  console.log(`Check failed: counted ${count} successful payments, expected ${expected}.`);
  console.log("Something in the data isn't being handled the way the README describes.");
} else {
  console.log(`Check passed: ${count} successful payments.`);
  console.log(`Your code: KOYA-${Math.round(total)}`);
}
