const API_URL = window.location.origin;
let miningInterval;
let attemptCount = 0;

window.onload = function() {
    document.getElementById("welcome-modal").style.display = "block";
};

document.querySelector(".close-button").onclick = function() {
    document.getElementById("welcome-modal").style.display = "none";
};

async function generateWallet() {
    const response = await fetch(`${API_URL}/wallet/new`);
    const data = await response.json();
    document.getElementById("wallet-output").value = `Private Key: ${data.private_key}\nPublic Key: ${data.public_key}`;
    adjustKeyLength();
}

async function viewWallets() {
    const response = await fetch(`${API_URL}/wallets`);
    const wallets = await response.json();
    const walletsList = document.getElementById("wallets-output");
    walletsList.innerHTML = "";
    wallets.forEach(wallet => {
        const li = document.createElement("li");
        li.classList.add("wallet-item");
        li.innerHTML = `
            <p><strong>Public Key:</strong></p>
            <p><span class="short-key">${wallet.public_key}</span></p>
        `;
        walletsList.appendChild(li);
        adjustKeyLength();
    });
}

function adjustKeyLength() {
    const keys = document.querySelectorAll('.short-key');
    keys.forEach(key => {
        const maxLength = 80;
        const fullKey = key.textContent;
        if (fullKey.length > maxLength) {
            key.textContent = fullKey.substring(0, maxLength) + '...';
        }
    });
}

async function createTransaction() {
    const sender = document.getElementById("sender-key").value.trim();
    const recipient = document.getElementById("recipient-key").value.trim();
    const amount = document.getElementById("amount").value;

    if (!sender || !recipient || !amount) {
        alert("Please fill out all fields.");
        return;
    }

    const transaction = {
        sender: sender,
        recipient: recipient,
        amount: parseFloat(amount),
        signature: "dummy_signature"
    };

    const response = await fetch(`${API_URL}/transaction/new`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transaction)
    });

    const result = await response.json();
    document.getElementById("transaction-output").innerText = result.message;
}

async function startMining() {
    document.getElementById("mining-output").innerText = "Starting mining...";
    attemptCount = 0;

    const response = await fetch(`${API_URL}/transactions`);
    const transactions = await response.json();

    if (transactions.length === 0) {
        const newTransaction = {
            sender: "15example_sender888745465
