
import sqlite3
import tkinter as tk
from tkinter import messagebox
import sys
# UI THEME
BG = "#f4f7fb"
PRIMARY = "#1e3a5f"
ACCENT = "#2d89ef"
SUCCESS = "#28a745"
DANGER = "#dc3545"
CARD = "#ffffff"

def style_window(win, title, size):
    win.title(title)
    win.geometry(size)
    win.configure(bg=BG)
    return win

def styled_entry(parent):
    e = tk.Entry(
        parent,
        font=("Arial", 12),
        bd=1,
        relief="solid"
    )
    e.pack(pady=6, ipadx=8, ipady=6)
    return e

def styled_button(parent, text, cmd, color=ACCENT):
    b = tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=color,
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        padx=10,
        pady=8
    )
    b.pack(pady=10)
    return b

root = None
current_user_id = None


# DATABASE
def init_db():
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            acc_no INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT,
            email TEXT,
            account_type TEXT,
            balance REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acc_no INTEGER,
            type TEXT,
            amount REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(acc_no) REFERENCES accounts(acc_no)
        )
    """)

    conn.commit()
    conn.close()


# REGISTER
def register():
    def submit():
        username = entry_username.get()
        password = entry_password.get()

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            messagebox.showinfo("Success", "Registration Successful")
            reg_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

        conn.close()

    reg_window = tk.Toplevel()
    reg_window.title("Register")
    reg_window.geometry("400x300")

    tk.Label(reg_window, text="Register", font=("Arial", 20)).pack(pady=10)

    tk.Label(reg_window, text="Username").pack()
    entry_username = tk.Entry(reg_window)
    entry_username.pack()

    tk.Label(reg_window, text="Password").pack()
    entry_password = tk.Entry(reg_window, show="*")
    entry_password.pack()

    tk.Button(reg_window, text="Register", command=submit).pack(pady=10)


# LOGIN
def login():
    def check_login():
        global current_user_id

        username = entry_username.get()
        password = entry_password.get()

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            current_user_id = user[0]
            login_window.destroy()
            main_page()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    login_window = tk.Tk()
    style_window(login_window, "Bank Login", "450x400")

    tk.Label(
        login_window,
        text="🏦 BANK MANAGEMENT SYSTEM",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=30)

    tk.Label(login_window, text="Username", bg=BG, fg=PRIMARY).pack()
    entry_username = styled_entry(login_window)

    tk.Label(login_window, text="Password", bg=BG, fg=PRIMARY).pack()
    entry_password = tk.Entry(
        login_window,
        show="*",
        font=("Arial", 12),
        bd=1,
        relief="solid"
    )
    entry_password.pack(pady=6, ipadx=8, ipady=6)

    styled_button(login_window, "Login", check_login)
    styled_button(login_window, "Register", register, SUCCESS)

    login_window.mainloop()


# CREATE ACCOUNT
def create_account():
    win = tk.Toplevel(root)
    style_window(win, "Create Account", "450x550")

    tk.Label(
        win,
        text="Create New Account",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Name", bg=BG, fg=PRIMARY).pack()
    entry_name = styled_entry(win)

    tk.Label(win, text="Phone", bg=BG, fg=PRIMARY).pack()
    entry_phone = styled_entry(win)

    tk.Label(win, text="Email", bg=BG, fg=PRIMARY).pack()
    entry_email = styled_entry(win)

    tk.Label(win, text="Account Type", bg=BG, fg=PRIMARY).pack()
    entry_type = styled_entry(win)

    tk.Label(win, text="Initial Deposit", bg=BG, fg=PRIMARY).pack()
    entry_balance = styled_entry(win)

    def save():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO accounts (user_id, name, phone, email, account_type, balance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            current_user_id,
            entry_name.get(),
            entry_phone.get(),
            entry_email.get(),
            entry_type.get(),
            float(entry_balance.get())
        ))

        conn.commit()
        acc_no = cursor.lastrowid
        conn.close()

        messagebox.showinfo("Success", f"Account Created\nAccount No: {acc_no}")
        win.destroy()

    styled_button(win, "Save Account", save, SUCCESS)

# CHECK BALANCE
def check_balance():
    win = tk.Toplevel(root)
    style_window(win, "Check Balance", "400x250")

    tk.Label(
        win,
        text="Check Account Balance",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    def show():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (entry_acc.get(),))
        result = cursor.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Balance", f"Balance: ₹{result[0]}")
        else:
            messagebox.showerror("Error", "Account not found")

    styled_button(win, "Check Balance", show, ACCENT)


# DEPOSIT
def deposit():
    win = tk.Toplevel(root)
    style_window(win, "Deposit Money", "400x320")

    tk.Label(
        win,
        text="Deposit Money",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    tk.Label(win, text="Amount", bg=BG, fg=PRIMARY).pack()
    entry_amt = styled_entry(win)

    def submit():
        acc = entry_acc.get()
        amt = float(entry_amt.get())

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc,))
        result = cursor.fetchone()

        if result:
            new_balance = result[0] + amt
            cursor.execute("UPDATE accounts SET balance=? WHERE acc_no=?", (new_balance, acc))
            cursor.execute(
                "INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)",
                (acc, "Deposit", amt)
            )
            conn.commit()
            messagebox.showinfo("Success", "Deposit successful")
        else:
            messagebox.showerror("Error", "Account not found")

        conn.close()

    styled_button(win, "Deposit", submit, SUCCESS)
# WITHDRAW
def withdraw():
    win = tk.Toplevel(root)
    style_window(win, "Withdraw Money", "400x320")

    tk.Label(
        win,
        text="Withdraw Money",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    tk.Label(win, text="Amount", bg=BG, fg=PRIMARY).pack()
    entry_amt = styled_entry(win)

    def submit():
        acc = entry_acc.get()
        amt = float(entry_amt.get())

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (acc,))
        result = cursor.fetchone()

        if result:
            if result[0] >= amt:
                new_balance = result[0] - amt
                cursor.execute("UPDATE accounts SET balance=? WHERE acc_no=?", (new_balance, acc))
                cursor.execute(
                    "INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)",
                    (acc, "Withdraw", amt)
                )
                conn.commit()
                messagebox.showinfo("Success", "Withdraw successful")
            else:
                messagebox.showerror("Error", "Insufficient balance")
        else:
            messagebox.showerror("Error", "Account not found")

        conn.close()

    styled_button(win, "Withdraw", submit, "#ffc107")

# TRANSACTIONS
def view_transactions():
    win = tk.Toplevel(root)
    style_window(win, "Transactions", "650x450")

    tk.Label(
        win,
        text="Transaction History",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=15)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    text = tk.Text(
        win,
        font=("Consolas", 11),
        width=70,
        height=15,
        bd=1,
        relief="solid"
    )
    text.pack(pady=10)

    def show():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, amount, timestamp FROM transactions WHERE acc_no=?",
            (entry_acc.get(),)
        )
        rows = cursor.fetchall()
        conn.close()

        text.delete("1.0", tk.END)

        for row in rows:
            text.insert(
                tk.END,
                f"{row[0]}   |   ₹{row[1]}   |   {row[2]}\n"
            )

    styled_button(win, "Show Transactions", show, "#6f42c1")


# ACCOUNT DETAILS
def view_account_details():
    win = tk.Toplevel(root)
    style_window(win, "Account Details", "400x250")

    tk.Label(
        win,
        text="Account Details",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    def show():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE acc_no=?", (entry_acc.get(),))
        row = cursor.fetchone()
        conn.close()

        if row:
            messagebox.showinfo(
                "Details",
                f"Account No: {row[0]}\nName: {row[2]}\nPhone: {row[3]}\nEmail: {row[4]}\nType: {row[5]}\nBalance: ₹{row[6]}"
            )

    styled_button(win, "Show Details", show, "#20c997")


# CLOSE ACCOUNT

def close_account():
    win = tk.Toplevel(root)
    style_window(win, "Close Account", "400x250")

    tk.Label(
        win,
        text="Close Account",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="Account Number", bg=BG, fg=PRIMARY).pack()
    entry_acc = styled_entry(win)

    def close():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM accounts WHERE acc_no=?", (entry_acc.get(),))
        cursor.execute("DELETE FROM transactions WHERE acc_no=?", (entry_acc.get(),))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account closed")

    styled_button(win, "Close Account", close, DANGER)

# TRANSFER
def transfer_money():
    win = tk.Toplevel(root)
    style_window(win, "Transfer Money", "450x400")

    tk.Label(
        win,
        text="Transfer Money",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    tk.Label(win, text="From Account", bg=BG).pack()
    entry_from = styled_entry(win)

    tk.Label(win, text="To Account", bg=BG).pack()
    entry_to = styled_entry(win)

    tk.Label(win, text="Amount", bg=BG).pack()
    entry_amt = styled_entry(win)

    def transfer():
        from_acc = entry_from.get()
        to_acc = entry_to.get()
        amt = float(entry_amt.get())

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (from_acc,))
        sender = cursor.fetchone()

        cursor.execute("SELECT balance FROM accounts WHERE acc_no=?", (to_acc,))
        receiver = cursor.fetchone()

        if sender and receiver:
            if sender[0] >= amt:
                cursor.execute("UPDATE accounts SET balance=balance-? WHERE acc_no=?", (amt, from_acc))
                cursor.execute("UPDATE accounts SET balance=balance+? WHERE acc_no=?", (amt, to_acc))
                cursor.execute(
                    "INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)",
                    (from_acc, "Transfer", amt)
                )
                conn.commit()
                messagebox.showinfo("Success", "Transfer successful")
            else:
                messagebox.showerror("Error", "Insufficient balance")
        else:
            messagebox.showerror("Error", "Invalid account")

        conn.close()

    styled_button(win, "Transfer Money", transfer, PRIMARY)

# EXIT
def exit_app():
    if messagebox.askyesno(
        "Exit Application",
        "Are you sure you want to exit?"
    ):
        root.destroy()
        sys.exit()


# MAIN PAGE
def main_page():
    global root
    root = tk.Tk()
    style_window(root, "Bank Dashboard", "900x650")

    tk.Label(
        root,
        text="🏦 BANK MANAGEMENT DASHBOARD",
        font=("Arial", 22, "bold"),
        bg=BG,
        fg=PRIMARY
    ).pack(pady=20)

    dashboard = tk.Frame(root, bg=BG)
    dashboard.pack(pady=20)

    buttons = [
        ("Create Account", create_account, ACCENT),
        ("Check Balance", check_balance, SUCCESS),
        ("Deposit", deposit, "#17a2b8"),
        ("Withdraw", withdraw, "#ffc107"),
        ("Transactions", view_transactions, "#6f42c1"),
        ("Account Details", view_account_details, "#20c997"),
        ("Close Account", close_account, DANGER),
        ("Transfer Money", transfer_money, PRIMARY),
        ("Exit", exit_app, "#343a40")
    ]

    row = 0
    col = 0

    for text, cmd, color in buttons:
        btn = tk.Button(
            dashboard,
            text=text,
            command=cmd,
            bg=color,
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=3,
            relief="flat",
            cursor="hand2"
        )
        btn.grid(row=row, column=col, padx=15, pady=15)

        col += 1
        if col > 2:
            col = 0
            row += 1

    root.mainloop()


if __name__ == "__main__":
    init_db()
    login()