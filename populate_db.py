import sqlite3
import random
from faker import Faker
from datetime import date

# Initialize Faker
fake = Faker()

DB_NAME = "bank.db"

def clear_data(conn):
    """Deletes all data from tables (but not the tables themselves) for a clean run."""
    print("Clearing old data...")
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM accounts")
    cur.execute("DELETE FROM customers")
    cur.execute("DELETE FROM users WHERE role != 'admin'") # Keep admin user
    conn.commit()
    print("Old data cleared.")

def create_customers(cur, n=50):
    """Generates N random customers."""
    print(f"Creating {n} customers...")
    customers = []
    for _ in range(n):
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        customers.append((name, email, phone))
    
    cur.executemany("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", customers)
    
    # Get all customer IDs that were just inserted
    cur.execute("SELECT id FROM customers")
    return [row[0] for row in cur.fetchall()]

def create_users_for_customers(cur, customer_ids):
    """Creates a 'user' login for each customer."""
    print("Creating user logins for customers...")
    users = []
    for cust_id in customer_ids:
        # Create username from customer name (more realistic)
        cur.execute("SELECT name FROM customers WHERE id = ?", (cust_id,))
        customer_name = cur.fetchone()[0]
        # Create username from name: "John Doe" -> "johndoe"
        username = customer_name.lower().replace(" ", "") + str(cust_id)
        password = "password123" # Simple password for all
        role = "customer"
        users.append((username, password, role, cust_id))
        
    cur.executemany("INSERT INTO users (username, password, role, customer_id) VALUES (?, ?, ?, ?)", users)

def create_accounts(cur, customer_ids, min_acc=1, max_acc=3):
    """Generates 1-3 accounts for each customer."""
    print("Creating accounts...")
    accounts = []
    for cust_id in customer_ids:
        for _ in range(random.randint(min_acc, max_acc)):
            acc_type = random.choice(['Savings', 'Checking', 'Business'])
            balance = round(random.uniform(500, 75000), 2)
            accounts.append((cust_id, acc_type, balance))
            
    cur.executemany("INSERT INTO accounts (customer_id, account_type, balance) VALUES (?, ?, ?)", accounts)
    
    # Get all account IDs
    cur.execute("SELECT id FROM accounts")
    return [row[0] for row in cur.fetchall()]

def create_transactions(cur, account_ids, min_trans=5, max_trans=30):
    """Generates 5-30 transactions for each account."""
    print("Creating transactions...")
    transactions = []
    for acc_id in account_ids:
        for _ in range(random.randint(min_trans, max_trans)):
            trans_type = random.choice(['deposit', 'withdraw'])
            amount = round(random.uniform(20, 1500), 2)
            trans_date = fake.date_between(start_date='-2y', end_date='today').isoformat()
            transactions.append((acc_id, trans_type, amount, trans_date))
            
    cur.executemany("INSERT INTO transactions (account_id, type, amount, date) VALUES (?, ?, ?, ?)", transactions)
    print(f"Created {len(transactions)} total transactions.")

def main():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        # Clear existing data
        clear_data(conn)
        
        # Create Customers
        customer_ids = create_customers(cur, n=50)
        
        # Create Users for ALL Customers
        create_users_for_customers(cur, customer_ids)
        
        # Create Accounts
        account_ids = create_accounts(cur, customer_ids)
        
        # Create Transactions
        create_transactions(cur, account_ids)
        
        # Commit all changes
        conn.commit()
        
        # Print login information
        print("\nDatabase populated successfully!")
        print(f"Default Admin Login: admin / admin")
        
        # Print some example customer logins
        cur.execute("""
            SELECT u.username, u.password, c.name, u.customer_id 
            FROM users u 
            JOIN customers c ON u.customer_id = c.id 
            WHERE u.role='customer' 
            LIMIT 10
        """)
        sample_logins = cur.fetchall()
        print("\nSample customer logins (username / password):")
        for username, password, name, cust_id in sample_logins:
            print(f"  {username} / {password} -> {name} (Customer ID: {cust_id})")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()