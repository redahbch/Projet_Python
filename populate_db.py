import sqlite3
import random
from faker import Faker
from datetime import date

fake = Faker()
DB_NAME = "bank.db"

def clear_data(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM accounts")
    cur.execute("DELETE FROM customers")
    cur.execute("DELETE FROM users WHERE role != 'admin'")
    conn.commit()

def create_customers(cur, n=50):
    customers = []
    for _ in range(n):
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        customers.append((name, email, phone))
    cur.executemany("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", customers)
    cur.execute("SELECT id FROM customers")
    return [row[0] for row in cur.fetchall()]

def create_users_for_customers(cur, customer_ids):
    users = []
    for cust_id in customer_ids:
        cur.execute("SELECT name FROM customers WHERE id = ?", (cust_id,))
        customer_name = cur.fetchone()[0]
        username = customer_name.lower().replace(" ", "") + str(cust_id)
        password = "password123"
        role = "customer"
        users.append((username, password, role, cust_id))
    cur.executemany("INSERT INTO users (username, password, role, customer_id) VALUES (?, ?, ?, ?)", users)

def create_accounts(cur, customer_ids, min_acc=1, max_acc=3):
    accounts = []
    for cust_id in customer_ids:
        for _ in range(random.randint(min_acc, max_acc)):
            acc_type = random.choice(['Savings', 'Checking', 'Business'])
            balance = round(random.uniform(500, 75000), 2)
            accounts.append((cust_id, acc_type, balance))
    cur.executemany("INSERT INTO accounts (customer_id, account_type, balance) VALUES (?, ?, ?)", accounts)
    cur.execute("SELECT id FROM accounts")
    return [row[0] for row in cur.fetchall()]

def create_transactions(cur, account_ids, min_trans=5, max_trans=30):
    transactions = []
    for acc_id in account_ids:
        for _ in range(random.randint(min_trans, max_trans)):
            trans_type = random.choice(['deposit', 'withdraw'])
            amount = round(random.uniform(20, 1500), 2)
            trans_date = fake.date_between(start_date='-2y', end_date='today').isoformat()
            transactions.append((acc_id, trans_type, amount, trans_date))
    cur.executemany("INSERT INTO transactions (account_id, type, amount, date) VALUES (?, ?, ?, ?)", transactions)

def main():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        clear_data(conn)
        customer_ids = create_customers(cur, n=50)
        create_users_for_customers(cur, customer_ids)
        account_ids = create_accounts(cur, customer_ids)
        create_transactions(cur, account_ids)
        conn.commit()
        print("Database populated successfully.")
        print("Default Admin Login: admin / admin")
        cur.execute("""
            SELECT u.username, u.password, c.name, u.customer_id 
            FROM users u 
            JOIN customers c ON u.customer_id = c.id 
            WHERE u.role='customer' 
            LIMIT 10
        """)
        sample_logins = cur.fetchall()
        for username, password, name, cust_id in sample_logins:
            print(f"{username} / {password} -> {name} (Customer ID: {cust_id})")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
