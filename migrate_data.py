import os
import sqlite3

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise ValueError("DATABASE_URL must point to PostgreSQL")

# Read existing orders from SQLite
sqlite_conn = sqlite3.connect("restaurant.db")
sqlite_conn.row_factory = sqlite3.Row

try:
    orders = sqlite_conn.execute(
        "SELECT id, customer_name, food_name, quantity, price FROM orders ORDER BY id"
    ).fetchall()
finally:
    sqlite_conn.close()

# Connect to PostgreSQL
engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as conn:
        existing_count = conn.execute(
            text("SELECT COUNT(*) FROM orders")
        ).scalar_one()

        if existing_count != 0:
            raise RuntimeError(
                "PostgreSQL orders table is not empty; migration cancelled."
            )

        for order in orders:
            conn.execute(
                text("""
                    INSERT INTO orders
                    (id, customer_name, food_name, quantity, price)
                    VALUES
                    (:id, :customer_name, :food_name, :quantity, :price)
                """),
                dict(order),
            )

        if orders:
            conn.execute(text("""
                SELECT setval(
                    pg_get_serial_sequence('orders', 'id'),
                    (SELECT MAX(id) FROM orders)
                )
            """))

    print(f"Successfully transferred {len(orders)} orders.")

finally:
    engine.dispose()