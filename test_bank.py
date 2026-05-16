import unittest
import sqlite3
import os

DB = 'bank.db'

class TestBankSystem(unittest.TestCase):
    def setUp(self):
        # Remove the existing DB safely
        try:
            if os.path.exists(DB):
                os.remove(DB)
        except PermissionError:
            raise RuntimeError(f"Make sure no other script is using '{DB}' while testing.")

        # Create new DB connection
        self.conn = sqlite3.connect(DB)
        self.cursor = self.conn.cursor()

        # Create tables
        self.cursor.execute('''CREATE TABLE users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE,
                                password TEXT)''')
        self.cursor.execute('''CREATE TABLE accounts (
                                acc_no INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                name TEXT,
                                phone TEXT,
                                email TEXT,
                                account_type TEXT,
                                balance REAL,
                                FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.cursor.execute('''CREATE TABLE transactions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                acc_no INTEGER,
                                type TEXT,
                                amount REAL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(acc_no) REFERENCES accounts(acc_no))''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    # Your test methods like test_register_and_login, etc. go here

    def test_register_and_login(self):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "testpass"))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM users WHERE username=? AND password=?", ("testuser", "testpass"))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)

    def test_create_account(self):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("john", "1234"))
        user_id = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO accounts (user_id, name, phone, email, account_type, balance) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, "John Doe", "1234567890", "john@example.com", "Saving", 1000))
        self.conn.commit()
        self.cursor.execute("SELECT * FROM accounts WHERE user_id=?", (user_id,))
        account = self.cursor.fetchone()
        self.assertIsNotNone(account)

    def test_deposit(self):
        self.test_create_account()
        self.cursor.execute("SELECT acc_no FROM accounts")
        acc_no = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
        balance_before = self.cursor.fetchone()[0]
        deposit_amount = 500
        new_balance = balance_before + deposit_amount
        self.cursor.execute("UPDATE accounts SET balance=? WHERE acc_no=?", (new_balance, acc_no))
        self.cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)", (acc_no, "Deposit", deposit_amount))
        self.conn.commit()
        self.cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
        balance_after = self.cursor.fetchone()[0]
        self.assertEqual(balance_after, new_balance)

    def test_withdraw(self):
        self.test_deposit()
        self.cursor.execute("SELECT acc_no FROM accounts")
        acc_no = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
        balance_before = self.cursor.fetchone()[0]
        withdraw_amount = 300
        new_balance = balance_before - withdraw_amount
        self.cursor.execute("UPDATE accounts SET balance=? WHERE acc_no=?", (new_balance, acc_no))
        self.cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)", (acc_no, "Withdraw", withdraw_amount))
        self.conn.commit()
        self.cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
        balance_after = self.cursor.fetchone()[0]
        self.assertEqual(balance_after, new_balance)

    def test_check_balance(self):
        self.test_create_account()
        self.cursor.execute("SELECT acc_no FROM accounts")
        acc_no = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc_no,))
        balance = self.cursor.fetchone()[0]
        self.assertIsInstance(balance, float)

    def test_transactions(self):
        self.test_deposit()
        self.cursor.execute("SELECT acc_no FROM accounts")
        acc_no = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT * FROM transactions WHERE acc_no=?", (acc_no,))
        txns = self.cursor.fetchall()
        self.assertGreater(len(txns), 0)

    def test_close_account(self):
        self.test_create_account()
        self.cursor.execute("SELECT acc_no FROM accounts")
        acc_no = self.cursor.fetchone()[0]
        self.cursor.execute("UPDATE accounts SET balance=? WHERE acc_no=?", (0, acc_no))
        self.cursor.execute("DELETE FROM accounts WHERE acc_no=?", (acc_no,))
        self.cursor.execute("DELETE FROM transactions WHERE acc_no=?", (acc_no,))
        self.conn.commit()
        self.cursor.execute("SELECT * FROM accounts WHERE acc_no=?", (acc_no,))
        result = self.cursor.fetchone()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
