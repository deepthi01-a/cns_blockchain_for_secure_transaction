import requests
from tkinter import Tk, Label, Entry, Button, Text, messagebox

SERVER_URL = "http://127.0.0.1:5000"  # Flask server URL
access_token = None

# GUI Functions
def login():
    global access_token
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and password are required!")
        return

    data = {"username": username, "password": password}
    response = requests.post(f"{SERVER_URL}/login", json=data)
    if response.status_code == 200:
        access_token = response.json()['token']
        messagebox.showinfo("Success", "Login successful!")
    else:
        messagebox.showerror("Error", response.json()['message'])

def check_balance():
    if not access_token:
        messagebox.showerror("Error", "Please login first!")
        return

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{SERVER_URL}/balance", headers=headers)
    if response.status_code == 200:
        balance = response.json().get('balance')
        username = response.json().get('username')
        messagebox.showinfo("Balance", f"Username: {username}\nBalance: {balance}")
    else:
        messagebox.showerror("Error", response.json()['message'])

def transfer():
    if not access_token:
        messagebox.showerror("Error", "Please login first!")
        return

    receiver = entry_receiver.get()
    amount = entry_amount.get()

    if not receiver or not amount:
        messagebox.showerror("Error", "Receiver and amount are required!")
        return

    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'receiver': receiver, 'amount': int(amount)}
    response = requests.post(f"{SERVER_URL}/transfer", json=data, headers=headers)
    if response.status_code == 200:
        messagebox.showinfo("Success", response.json()['message'])
    else:
        messagebox.showerror("Error", response.json()['message'])

def view_blockchain():
    response = requests.get(f"{SERVER_URL}/get_blockchain")
    if response.status_code == 200:
        blockchain = response.json().get('blockchain')
        blockchain_text.delete(1.0, "end")
        for block in blockchain:
            blockchain_text.insert("end", f"Block {block['index']}:\n")
            blockchain_text.insert("end", f"Transactions: {block['transactions']}\n")
            blockchain_text.insert("end", f"Previous Hash: {block['previous_hash']}\n")
            blockchain_text.insert("end", f"Hash: {block['hash']}\n\n")
    else:
        messagebox.showerror("Error", "Failed to fetch blockchain.")

# GUI Setup
root = Tk()
root.title("Bank System with Blockchain")

Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
entry_username = Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=5)

Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)
entry_password = Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5)

Button(root, text="Login", command=login).grid(row=2, column=0, columnspan=2, pady=10)
Button(root, text="Check Balance", command=check_balance).grid(row=3, column=0, columnspan=2, pady=10)

Label(root, text="Transfer To:").grid(row=4, column=0, padx=10, pady=5)
entry_receiver = Entry(root)
entry_receiver.grid(row=4, column=1, padx=10, pady=5)

Label(root, text="Amount:").grid(row=5, column=0, padx=10, pady=5)
entry_amount = Entry(root)
entry_amount.grid(row=5, column=1, padx=10, pady=5)

Button(root, text="Transfer", command=transfer).grid(row=6, column=0, columnspan=2, pady=10)
Button(root, text="View Blockchain", command=view_blockchain).grid(row=7, column=0, columnspan=2, pady=10)

Label(root, text="Blockchain:").grid(row=8, column=0, columnspan=2, pady=5)
blockchain_text = Text(root, height=10, width=50)
blockchain_text.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
