import sqlite3
from random import choice, randint, uniform
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    # ----------------- CREATE TABLES -----------------
    cursor.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        salary INTEGER,
        city TEXT
    );

    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        country TEXT,
        segment TEXT
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        user_id INTEGER,
        amount REAL,
        date TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        qty INTEGER,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    # ----------------- FILL USERS -----------------
    users = [
        ("Alice Brown", "manager", 1200, "London"),
        ("Bob Stone", "manager", 1100, "Paris"),
        ("Charlie Ray", "analyst", 1500, "Berlin"),
        ("Diana Key", "admin", 1800, "New York"),
        ("Edward Black", "manager", 1300, "Tokyo"),
    ]
    cursor.executemany("INSERT INTO users (name, role, salary, city) VALUES (?,?,?,?)", users)

    # ----------------- FILL CUSTOMERS -----------------
    customers = [
        ("ACME Corp", "USA", "business"),
        ("Zenit LLC", "Germany", "business"),
        ("Kohan Ltd", "Japan", "business"),
        ("Maria Gomez", "Spain", "private"),
        ("Ivan Petrov", "Russia", "private"),
        ("Liu Wei", "China", "private")
    ]
    cursor.executemany("INSERT INTO customers (name, country, segment) VALUES (?,?,?)", customers)

    # ----------------- FILL PRODUCTS -----------------
    products = [
        ("Laptop Pro 15", "electronics", 1200.0),
        ("Laptop Air 13", "electronics", 800.0),
        ("Office Chair", "furniture", 150.0),
        ("Desk Wood", "furniture", 300.0),
        ("Monitor 27", "electronics", 350.0),
        ("Keyboard", "electronics", 40.0)
    ]
    cursor.executemany("INSERT INTO products (name, category, price) VALUES (?,?,?)", products)

    # ----------------- GENERATE ORDERS -----------------
    user_ids = [1, 2, 3, 4, 5]
    customer_ids = [1, 2, 3, 4, 5, 6]
    product_ids = [1, 2, 3, 4, 5, 6]

    for _ in range(50):  # 50 заказов
        cust = choice(customer_ids)
        user = choice(user_ids)

        # случайная дата в пределах последних 120 дней
        date = datetime.now() - timedelta(days=randint(1, 120))
        date_str = date.strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO orders (customer_id, user_id, amount, date) VALUES (?,?,?,?)",
            (cust, user, 0, date_str)
        )
        order_id = cursor.lastrowid

        # создаём 1–5 позиций на каждый заказ
        total_amount = 0
        for _ in range(randint(1, 5)):
            prod = choice(product_ids)
            qty = randint(1, 5)
            cursor.execute("SELECT price FROM products WHERE id=?", (prod,))
            price = cursor.fetchone()[0]
            total_amount += price * qty

            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, qty) VALUES (?,?,?)",
                (order_id, prod, qty)
            )

        # обновляем сумму заказа
        cursor.execute("UPDATE orders SET amount=? WHERE id=?", (round(total_amount, 2), order_id))

    conn.commit()
    conn.close()
    print("База данных crm.db успешно создана.")


if __name__ == "__main__":
    init_db()
