from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Generate a key for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Connect to SQLite database
conn = sqlite3.connect('password_manager.db', check_same_thread=False)
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS passwords
             (id INTEGER PRIMARY KEY, website TEXT, username TEXT, password TEXT)''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_password', methods=['POST'])
def add_password():
    website = request.form['website']
    username = request.form['username']
    password = request.form['password']
    encrypted_password = cipher_suite.encrypt(password.encode())
    c.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)", (website, username, encrypted_password))
    conn.commit()
    flash('Password added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/get_password', methods=['POST'])
def get_password():
    website = request.form['website']
    c.execute("SELECT username, password FROM passwords WHERE website = ?", (website,))
    row = c.fetchone()
    password_data = None
    if row:
        decrypted_password = cipher_suite.decrypt(row[1]).decode()
        password_data = {'username': row[0], 'password': decrypted_password}
    else:
        flash('No password found for the specified website.', 'warning')
    return render_template('index.html', password_data=password_data)

@app.route('/delete_password', methods=['POST'])
def delete_password():
    website = request.form['website']
    c.execute("DELETE FROM passwords WHERE website = ?", (website,))
    conn.commit()
    flash('Password deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
