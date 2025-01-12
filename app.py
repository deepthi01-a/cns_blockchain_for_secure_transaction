from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import json

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key
jwt = JWTManager(app)

# File paths
USERS_DB = 'users.json'
BLOCKCHAIN_DB = 'blockchain.json'

# Initialize blockchain
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Blockchain helper functions
def create_block(transactions):
    blockchain = load_json(BLOCKCHAIN_DB)
    previous_block = blockchain[-1] if blockchain else {'index': 0, 'hash': '0'}
    block = {
        'index': len(blockchain) + 1,
        'transactions': transactions,
        'previous_hash': previous_block['hash'],
        'hash': str(len(blockchain) + 1)  # Simplified hash for demonstration
    }
    blockchain.append(block)
    save_json(BLOCKCHAIN_DB, blockchain)
    return block

# Routes
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_json(USERS_DB)
    if username in users:
        return jsonify({'message': 'Account already exists!'}), 400

    users[username] = {'password': password, 'balance': 1000}
    save_json(USERS_DB, users)
    return jsonify({'message': 'Account created successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_json(USERS_DB)
    if username not in users or users[username]['password'] != password:
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = create_access_token(identity=username)
    return jsonify({'message': 'Login successful!', 'token': token}), 200

@app.route('/balance', methods=['GET'])
@jwt_required()
def balance():
    username = get_jwt_identity()
    users = load_json(USERS_DB)
    return jsonify({'username': username, 'balance': users[username]['balance']}), 200

@app.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    username = get_jwt_identity()
    data = request.get_json()
    receiver = data.get('receiver')
    amount = data.get('amount')

    users = load_json(USERS_DB)
    if receiver not in users:
        return jsonify({'message': 'Receiver not found!'}), 404
    if users[username]['balance'] < amount:
        return jsonify({'message': 'Insufficient balance!'}), 400

    users[username]['balance'] -= amount
    users[receiver]['balance'] += amount
    save_json(USERS_DB, users)

    # Record transaction on the blockchain
    transaction = {'sender': username, 'receiver': receiver, 'amount': amount}
    block = create_block([transaction])

    return jsonify({'message': 'Transfer successful!', 'block': block}), 200

@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    blockchain = load_json(BLOCKCHAIN_DB)
    return jsonify({'blockchain': blockchain}), 200

if __name__ == '__main__':
    app.run(debug=True)
