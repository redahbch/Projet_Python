import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import re  

BG_COLOR = "#F0F4F8"       
FRAME_COLOR = "#FFFFFF"    
PRIMARY_COLOR = "#4A90E2"   
SECONDARY_COLOR = "#50E3C2" 
ALERT_COLOR = "#D0021B"   
TEXT_COLOR = "#333333"     
ENTRY_BG = "#FFFFFF"
FONT_NAME = "Helvetica"
FONT_SIZE = 12
FONT_LARGE = 18

def setup_styles():
    """Configures all ttk styles for a professional look."""
    style = ttk.Style()
    style.theme_use('clam')

    style.configure(".", 
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        font=(FONT_NAME, FONT_SIZE))
    style.configure("TFrame", 
        background=FRAME_COLOR,
        relief="solid",
        borderwidth=1)
    style.configure("TLabel", 
        background=FRAME_COLOR, 
        foreground=TEXT_COLOR)
    
    style.configure("Login.TFrame", background=BG_COLOR, relief="none", borderwidth=0)
    style.configure("Login.TLabel", 
        background=BG_COLOR, 
        font=(FONT_NAME, FONT_SIZE))
    style.configure("Title.TLabel", 
        background=BG_COLOR, 
        foreground=PRIMARY_COLOR, 
        font=(FONT_NAME, FONT_LARGE, "bold"))
    
    style.configure("TButton", 
        background=PRIMARY_COLOR,
        foreground="white",
        font=(FONT_NAME, FONT_SIZE, "bold"),
        padding=6,
        relief="flat")
    style.map("TButton",
        background=[('active', SECONDARY_COLOR), ('!disabled', PRIMARY_COLOR)],
        foreground=[('active', 'white')])

    style.configure("Danger.TButton", 
        background=ALERT_COLOR, 
        foreground="white")
    style.map("Danger.TButton",
        background=[('active', "#FF4136"), ('!disabled', ALERT_COLOR)])

    style.configure("TEntry", 
        fieldbackground=ENTRY_BG, 
        foreground=TEXT_COLOR,
        insertwidth=2,
        padding=5)
    
    style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
    style.configure("TNotebook.Tab", 
        background=BG_COLOR, 
        foreground=TEXT_COLOR, 
        font=(FONT_NAME, FONT_SIZE, "bold"),
        padding=[10, 5],
        relief="flat")
    style.map("TNotebook.Tab",
        background=[("selected", FRAME_COLOR)],
        expand=[("selected", [1, 1, 1, 0])])
    
    style.configure("Treeview",
        background=FRAME_COLOR,
        fieldbackground=FRAME_COLOR,
        foreground=TEXT_COLOR,
        rowheight=30, 
        font=(FONT_NAME, FONT_SIZE - 1))
    style.configure("Treeview.Heading", 
        background=PRIMARY_COLOR,
        foreground="white",
        font=(FONT_NAME, FONT_SIZE, "bold"),
        relief="flat")
    style.map("Treeview.Heading",
        background=[('active', SECONDARY_COLOR)])

    style.configure("Treeview", 
        anchor="center") 
    
    style.layout("Treeview.Item", [
        ('Treeitem.padding', {'sticky': 'nswe', 'children': [
            ('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
            ('Treeitem.image', {'side': 'left', 'sticky': ''}),
            ('Treeitem.text', {'side': 'left', 'sticky': 'we'})
        ]})
    ])

class Validator:
    @staticmethod
    def is_valid_email(email):
        """Simple regex for email validation."""
        if not email: return True 
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.match(pattern, email)

    @staticmethod
    def is_valid_phone(phone):
        """Simple regex for phone validation (10-15 digits, optional +)."""
        if not phone: return True 
        pattern = r"^\+?[0-9\s.-]{10,15}$"
        return re.match(pattern, phone)

    @staticmethod
    def is_valid_amount(amount_str):
        """Checks if a string is a valid positive float."""
        try:
            amount = float(amount_str)
            return amount >= 0
        except ValueError:
            return False

class DatabaseManager:
    """Handles all database operations for customers, accounts, and transactions."""

    def __init__(self, db_name="bank.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                account_type TEXT,
                balance REAL DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                type TEXT,
                amount REAL,
                date TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer',
                customer_id INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin', 'admin')")
        cur.execute("INSERT OR IGNORE INTO users (username, password, role, customer_id) VALUES ('user', 'user', 'customer', 1)")

        conn.commit()
        conn.close()

class BaseApp(ttk.Frame):
    """Reusable GUI structure for all sections."""
    def __init__(self, master, db):
        super().__init__(master, style="TFrame")
        self.db = db
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def clear_entries(self, entries):
        """Clear all entry widgets."""
        for entry in entries:
            entry.delete(0, tk.END)
            
    def bind_enter_to_submit(self, entry, submit_func):
        """Binds the <Return> key on an entry to a submit function."""
        entry.bind("<Return>", lambda event: submit_func())

class CustomersApp(BaseApp):
    def __init__(self, master, db):
        super().__init__(master, db)
        self.create_form()
        self.create_buttons()
        self.create_table()
        self.load_customers()

    def create_form(self):
        form = ttk.Frame(self)
        form.pack(pady=10)
        ttk.Label(form, text="Name").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text="Email").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text="Phone").grid(row=2, column=0, padx=5, pady=5)

        self.name_entry = ttk.Entry(form, width=40)
        self.email_entry = ttk.Entry(form, width=40)
        self.phone_entry = ttk.Entry(form, width=40)

        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.bind_enter_to_submit(self.phone_entry, self.add_customer)
        self.entries = [self.name_entry, self.email_entry, self.phone_entry]

    def create_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Customer", command=self.add_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_customer, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=lambda: self.clear_entries(self.entries)).pack(side=tk.LEFT, padx=5)

    def create_table(self):
        cols = ("id", "name", "email", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        s = ttk.Style()
        s.configure("Treeview.Heading", anchor="center")

        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=tk.CENTER) 
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select_row)

    def load_customers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM customers")
            for customer in cur.fetchall():
                self.tree.insert("", tk.END, values=customer)

    def add_customer(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return
        if not Validator.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if not Validator.is_valid_phone(phone):
            messagebox.showerror("Error", "Invalid phone format. Must be 10-15 digits.")
            return

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            conn.commit()
            
        self.load_customers()
        self.clear_entries(self.entries) 
        messagebox.showinfo("Success", "Customer added successfully.")

    def update_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to update.")
            return
        
        cust_id = self.tree.item(selected[0])["values"][0]
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        if not Validator.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        if not Validator.is_valid_phone(phone):
            messagebox.showerror("Error", "Invalid phone format.")
            return

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE customers SET name=?, email=?, phone=? WHERE id=?", (name, email, phone, cust_id))
            conn.commit()
            
        self.load_customers()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", "Customer updated successfully.")

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete.")
            return
            
        cust_id = self.tree.item(selected[0])["values"][0]
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer? This will also delete all their accounts and transactions."):
            return

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM customers WHERE id=?", (cust_id,))
            conn.commit()
            
        self.load_customers()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", "Customer deleted successfully.")

    def select_row(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.clear_entries(self.entries)
            self.name_entry.insert(0, values[1])
            self.email_entry.insert(0, values[2])
            self.phone_entry.insert(0, values[3])

class AccountsApp(BaseApp):
    def __init__(self, master, db):
        super().__init__(master, db)
        self.create_form()
        self.create_buttons()
        self.create_table()
        self.load_accounts()

    def create_form(self):
        form = ttk.Frame(self)
        form.pack(pady=10)
        ttk.Label(form, text="Customer ID").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text="Account Type").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text="Initial Balance").grid(row=2, column=0, padx=5, pady=5)

        self.cust_entry = ttk.Entry(form, width=40)
        self.type_entry = ttk.Entry(form, width=40)
        self.balance_entry = ttk.Entry(form, width=40)

        self.cust_entry.grid(row=0, column=1, padx=5, pady=5)
        self.type_entry.grid(row=1, column=1, padx=5, pady=5)
        self.balance_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.type_entry.insert(0, "Savings") 
        
        self.bind_enter_to_submit(self.balance_entry, self.add_account)
        self.entries = [self.cust_entry, self.type_entry, self.balance_entry]

    def create_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_account, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=lambda: self.clear_entries(self.entries)).pack(side=tk.LEFT, padx=5)

    def create_table(self):
        cols = ("id", "customer_id", "account_type", "balance")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        s = ttk.Style()
        s.configure("Treeview.Heading", anchor="center")

        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=tk.CENTER)
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select_row)

    def load_accounts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM accounts")
            for acc in cur.fetchall():
                self.tree.insert("", tk.END, values=acc)

    def add_account(self):
        cust_id = self.cust_entry.get()
        acc_type = self.type_entry.get()
        balance_str = self.balance_entry.get() or "0"

        if not cust_id:
            messagebox.showerror("Error", "Customer ID is required.")
            return
        if not acc_type:
            messagebox.showerror("Error", "Account Type is required.")
            return
        if not Validator.is_valid_amount(balance_str):
            messagebox.showerror("Error", "Invalid balance amount. Must be a number.")
            return
            
        balance = float(balance_str)

        with self.db.connect() as conn:
            cur = conn.cursor()
            
            cur.execute("SELECT 1 FROM customers WHERE id=?", (cust_id,))
            if not cur.fetchone():
                messagebox.showerror("Error", f"No customer found with ID: {cust_id}")
                return
                
            cur.execute("INSERT INTO accounts (customer_id, account_type, balance) VALUES (?, ?, ?)", (cust_id, acc_type, balance))
            conn.commit()
            
        self.load_accounts()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", "Account added successfully.")

    def update_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account to update.")
            return
            
        acc_id = self.tree.item(selected[0])["values"][0]
        cust_id = self.cust_entry.get() 
        acc_type = self.type_entry.get()
        balance_str = self.balance_entry.get()

        if not acc_type:
            messagebox.showerror("Error", "Account Type is required.")
            return
        if not Validator.is_valid_amount(balance_str):
            messagebox.showerror("Error", "Invalid balance amount. Must be a number.")
            return

        balance = float(balance_str)

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE accounts SET account_type=?, balance=? WHERE id=?", (acc_type, balance, acc_id))
            conn.commit()
            
        self.load_accounts()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", "Account updated successfully.")

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an account to delete.")
            return
            
        acc_id = self.tree.item(selected[0])["values"][0]
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this account? This will also delete all its transactions."):
            return

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM accounts WHERE id=?", (acc_id,))
            conn.commit()
            
        self.load_accounts()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", "Account deleted successfully.")

    def select_row(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.clear_entries(self.entries)
            self.cust_entry.insert(0, values[1])
            self.type_entry.insert(0, values[2])
            self.balance_entry.insert(0, values[3])

class TransactionsApp(BaseApp):
    def __init__(self, master, db):
        super().__init__(master, db)
        self.create_form()
        self.create_buttons()
        self.create_table()
        self.load_transactions()
        master.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def create_form(self):
        form = ttk.Frame(self)
        form.pack(pady=10)
        ttk.Label(form, text="Account ID").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(form, text="Type (deposit/withdraw)").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text="Amount").grid(row=2, column=0, padx=5, pady=5)

        self.acc_entry = ttk.Entry(form, width=40)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, width=38)
        self.type_combo['values'] = ('deposit', 'withdraw')
        self.type_combo.current(0)
        self.amount_entry = ttk.Entry(form, width=40)

        self.acc_entry.grid(row=0, column=1, padx=5, pady=5)
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.bind_enter_to_submit(self.amount_entry, self.add_transaction)
        self.entries = [self.acc_entry, self.amount_entry]

    def create_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=lambda: self.clear_entries(self.entries)).pack(side=tk.LEFT, padx=5)

    def create_table(self):
        cols = ("id", "account_id", "type", "amount", "date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        s = ttk.Style()
        s.configure("Treeview.Heading", anchor="center")
        
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor=tk.CENTER)
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC")
            for t in cur.fetchall():
                self.tree.insert("", tk.END, values=t)
                
    def on_tab_changed(self, event):
        """Reloads data when this tab is selected."""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Transactions":
            self.load_transactions()

    def add_transaction(self):
        acc_id = self.acc_entry.get()
        t_type = self.type_var.get().lower()
        amount_str = self.amount_entry.get()
        today = date.today().isoformat()

        if not acc_id:
            messagebox.showerror("Error", "Account ID is required.")
            return
        if not Validator.is_valid_amount(amount_str) or float(amount_str) <= 0:
            messagebox.showerror("Error", "Invalid amount. Must be a positive number.")
            return
            
        amount = float(amount_str)

        with self.db.connect() as conn:
            cur = conn.cursor()
            
            cur.execute("SELECT balance FROM accounts WHERE id=?", (acc_id,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Error", f"No account found with ID: {acc_id}")
                return
            
            current_balance = row[0]
            
            if t_type == "withdraw":
                if current_balance < amount:
                    messagebox.showerror("Error", "Insufficient funds for this withdrawal.")
                    return
                new_balance = current_balance - amount
            else: 
                new_balance = current_balance + amount

            cur.execute("UPDATE accounts SET balance = ? WHERE id=?", (new_balance, acc_id))
            
            cur.execute("INSERT INTO transactions (account_id, type, amount, date) VALUES (?, ?, ?, ?)",
                        (acc_id, t_type, amount, today))
            
            conn.commit()

        self.load_transactions()
        self.clear_entries(self.entries)
        messagebox.showinfo("Success", f"{t_type.capitalize()} recorded successfully! New balance: ${new_balance:,.2f}")

class AdminInterface(ttk.Frame):
    def __init__(self, master, db, logout_callback):
        super().__init__(master, style="Login.TFrame") 
        self.pack(fill=tk.BOTH, expand=True)
        self.db = db

        header_frame = ttk.Frame(self, style="Login.TFrame")
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text="🏦 Admin Dashboard", style="Title.TLabel").pack(side=tk.LEFT, padx=20)
        
        ttk.Button(header_frame, text="Logout", command=logout_callback).pack(side=tk.RIGHT, padx=20)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        customers_tab = CustomersApp(notebook, self.db)
        accounts_tab = AccountsApp(notebook, self.db)
        transactions_tab = TransactionsApp(notebook, self.db)

        notebook.add(customers_tab, text="Customers")
        notebook.add(accounts_tab, text="Accounts")
        notebook.add(transactions_tab, text="Transactions")

class CustomerInterface(ttk.Frame):
    def __init__(self, master, db, customer_id, logout_callback):
        super().__init__(master, style="TFrame")
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.db = db
        self.customer_id = customer_id
        self.logout_callback = logout_callback
        
        self.customer_name = self.get_customer_name()
        
        self.create_widgets()
        self.load_details()
        
    def get_customer_name(self):
        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM customers WHERE id=?", (self.customer_id,))
            row = cur.fetchone()
            return row[0] if row else "Valued Customer"

    def create_widgets(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text=f"Welcome, {self.customer_name}!", style="Title.TLabel").pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Logout", command=self.logout_callback).pack(side=tk.RIGHT)

        content_frame = ttk.Frame(self, style="Login.TFrame") 
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(content_frame, text="Your Accounts", style="Title.TLabel").pack(pady=10)
        
        cols_acc = ("id", "account_type", "balance")
        self.accounts_tree = ttk.Treeview(content_frame, columns=cols_acc, show="headings")
        s = ttk.Style()
        s.configure("Treeview.Heading", anchor="center")
        for col in cols_acc:
            self.accounts_tree.heading(col, text=col.capitalize())
            self.accounts_tree.column(col, anchor=tk.CENTER)
        self.accounts_tree.pack(fill=tk.X, padx=10)
        
        ttk.Label(content_frame, text="Your Transactions", style="Title.TLabel").pack(pady=20)
        
        cols_trans = ("id", "account_id", "type", "amount", "date")
        self.trans_tree = ttk.Treeview(content_frame, columns=cols_trans, show="headings")
        for col in cols_trans:
            self.trans_tree.heading(col, text=col.capitalize())
            self.trans_tree.column(col, anchor=tk.CENTER)
        self.trans_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_details(self):
        for tree in [self.accounts_tree, self.trans_tree]:
            for row in tree.get_children():
                tree.delete(row)
        
        with self.db.connect() as conn:
            cur = conn.cursor()
            
            cur.execute("SELECT id, account_type, balance FROM accounts WHERE customer_id=?", (self.customer_id,))
            account_ids = []
            for acc in cur.fetchall():
                account_ids.append(acc[0])
                self.accounts_tree.insert("", tk.END, values=acc)
            
            if account_ids:
                placeholders = ",".join("?" * len(account_ids))
                query = f"SELECT * FROM transactions WHERE account_id IN ({placeholders}) ORDER BY date DESC"
                cur.execute(query, account_ids)
                for t in cur.fetchall():
                    self.trans_tree.insert("", tk.END, values=t)

class LoginFrame(ttk.Frame):
    def __init__(self, master, db, login_success_callback):
        super().__init__(master, style="Login.TFrame")
        self.pack(fill=tk.BOTH, expand=True)
        self.db = db
        self.login_success_callback = login_success_callback

        form_frame = ttk.Frame(self, style="TFrame", padding=40)
        form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(form_frame, text="🏦 Bank Login", style="Title.TLabel", background=FRAME_COLOR).pack(pady=(0, 20))
        
        ttk.Label(form_frame, text="Username").pack(pady=5)
        self.user_entry = ttk.Entry(form_frame, width=30)
        self.user_entry.pack(pady=5)
        
        ttk.Label(form_frame, text="Password").pack(pady=5)
        self.pass_entry = ttk.Entry(form_frame, width=30, show="*")
        self.pass_entry.pack(pady=5)
        
        self.login_button = ttk.Button(form_frame, text="Login", command=self.attempt_login, width=28)
        self.login_button.pack(pady=20)
        
        self.user_entry.insert(0, "admin") 
        self.pass_entry.insert(0, "admin") 
        
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())
        self.pass_entry.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        with self.db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT password, role, customer_id FROM users WHERE username=?", (username,))
            row = cur.fetchone()

            if row and row[0] == password:
                role = row[1]
                customer_id = row[2]
                print(f"DEBUG: Login successful - Username: {username}, Role: {role}, Customer ID: {customer_id}")  # Debug line
                self.login_success_callback(role, customer_id)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏦 Professional Bank Management System")
        self.geometry("1000x700") 
        self.db = DatabaseManager()
        
        setup_styles()
        self.configure(bg=BG_COLOR)

        self.current_frame = None
        self.show_login_screen()

    def show_login_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self.db, self.on_login_success)
        self.title("Bank System - Login")

    def on_login_success(self, role, customer_id):
        if self.current_frame:
            self.current_frame.destroy()
            
        if role == 'admin':
            self.current_frame = AdminInterface(self, self.db, self.show_login_screen)
            self.title("Bank System - Admin Dashboard")
        else: # customer
            self.current_frame = CustomerInterface(self, self.db, customer_id, self.show_login_screen)
            self.title("Bank System - Customer Portal")

if __name__ == "__main__":
    app = BankApp()

    app.mainloop()
