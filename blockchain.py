from flask import Flask, jsonify, request, render_template
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import json
import hashlib

app = Flask(__name__, static_url_path='', static_folder='static')

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = f"{self.index}{json.dumps(self.transactions)}{self.previous_hash}"
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def add_block(self):
        if not self.pending_transactions:
            return "No transactions to add"
        new_block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        self.chain.append(new_block)
        self.pending_transactions = []
        return f"Block {new_block.index} added with hash: {new_block.hash}"

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.verifying_key

    def create_transaction(self, recipient, amount):
        transaction = {
            "sender": self.public_key.to_string().hex(),
            "recipient": recipient,
            "amount": amount
        }
        transaction["signature"] = self.private_key.sign(json.dumps(transaction, sort_keys=True).encode()).hex()
        return transaction

blockchain = Blockchain()
wallets = []

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/wallet/new', methods=['GET'])
def create_wallet():
    wallet = Wallet()
    wallets.append(wallet)
    return jsonify({
        "private_key": wallet.private_key.to_string().hex(),
        "public_key": wallet.public_key.to_string().hex()
    })

@app.route('/wallets', methods=['GET'])
def get_wallets():
    wallets_data = [{"public_key": wallet.public_key.to_string().hex()} for wallet in wallets]
    return jsonify(wallets_data)

@app.route('/transaction/new', methods=['POST'])
def create_transaction():
    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')
    signature = data.get('signature')
    transaction = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "signature": signature
    }
    blockchain.add_transaction(transaction)
    return jsonify({"message": "Transaction added to pending transactions"})

@app.route('/block/new', methods=['POST'])
def add_block():
    result = blockchain.add_block()
    return jsonify({"message": result})

@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    chain_data = [{
        "index": block.index,
        "transactions": block.transactions,
        "previous_hash": block.previous_hash,
        "hash": block.hash
    } for block in blockchain.chain]
    return jsonify(chain_data)

if __name__ == '__main__':
    app.run(debug=True)
