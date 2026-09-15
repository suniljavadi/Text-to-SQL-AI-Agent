"""Seed deterministic synthetic business data for local demos."""
from datetime import date, timedelta
from pathlib import Path
import random
from sqlalchemy import create_engine, text
from app.config import get_settings

random.seed(42)
NAMES = ["Aarav Mehta", "Maya Chen", "Noah Williams", "Sofia Garcia", "Liam Brown", "Emma Wilson", "Oliver Smith", "Aisha Khan", "Ethan Davis", "Priya Shah"]
CITIES = ["Mumbai", "Bengaluru", "Delhi", "Pune", "Chennai", "Hyderabad", "Kolkata", "Jaipur"]

def seed() -> None:
    engine = create_engine(get_settings().database_url, connect_args={"check_same_thread": False} if get_settings().database_url.startswith("sqlite") else {})
    schema = Path(__file__).with_name("schema.sql").read_text()
    if get_settings().database_url.startswith("sqlite"):
        schema = schema.replace("INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    with engine.begin() as conn:
        for statement in schema.split(";"):
            if statement.strip():
                conn.execute(text(statement))
        if conn.execute(text("SELECT COUNT(*) FROM departments")).scalar_one() > 0:
            return
        for name, location in [("Sales", "West"), ("Operations", "South"), ("Finance", "North"), ("Support", "Central")]:
            conn.execute(text("INSERT INTO departments(name, location) VALUES (:name,:location)"), {"name": name, "location": location})
        for i, name in enumerate(NAMES, 1):
            first, last = name.split()
            conn.execute(text("INSERT INTO employees(department_id,first_name,last_name,email,hire_date,salary) VALUES (:d,:f,:l,:e,:h,:s)"), {"d": (i % 4) + 1, "f": first, "l": last, "e": f"employee{i}@example.test", "h": date(2020,1,1) + timedelta(days=i*70), "s": 50000 + i*4200})
        for i in range(1, 31):
            conn.execute(text("INSERT INTO customers(customer_name,email,city,segment,signup_date) VALUES (:n,:e,:c,:s,:d)"), {"n": f"Customer {i:02d}", "e": f"customer{i}@example.test", "c": CITIES[i % len(CITIES)], "s": ["Consumer","SMB","Enterprise"][i % 3], "d": date(2023,1,1) + timedelta(days=i*11)})
        products = [("Analytics Platform", "Software", 1200, 500), ("Data Gateway", "Infrastructure", 850, 300), ("Insight License", "Software", 450, 150), ("Support Package", "Services", 700, 250), ("Training Workshop", "Services", 1500, 600), ("Security Add-on", "Software", 990, 350), ("Cloud Connector", "Infrastructure", 650, 220), ("BI Starter", "Software", 300, 90)]
        for name, category, price, cost in products:
            conn.execute(text("INSERT INTO products(product_name,category,unit_price,cost,active) VALUES (:n,:c,:p,:co,true)"), {"n": name, "c": category, "p": price, "co": cost})
        for i in range(1, 121):
            order_date = date(2024,1,1) + timedelta(days=(i*7) % 730)
            status = "Completed" if i % 11 else ("Pending" if i % 5 else "Returned")
            conn.execute(text("INSERT INTO orders(customer_id,employee_id,order_date,status,shipping_city) VALUES (:c,:e,:d,:s,:city)"), {"c": (i % 30)+1, "e": (i % 10)+1, "d": order_date, "s": status, "city": CITIES[i % len(CITIES)]})
            for j in range(1, (i % 3)+2):
                product_id = ((i+j) % 8)+1
                conn.execute(text("INSERT INTO order_items(order_id,product_id,quantity,unit_price) VALUES (:o,:p,:q,(SELECT unit_price FROM products WHERE product_id=:p))"), {"o": i, "p": product_id, "q": (i+j) % 5 + 1})
    print("Synthetic database seeded.")

if __name__ == "__main__":
    seed()
