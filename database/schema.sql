CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    first_name VARCHAR(60) NOT NULL, last_name VARCHAR(60) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE, hire_date DATE NOT NULL,
    salary NUMERIC(12,2) NOT NULL CHECK (salary > 0)
);
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name VARCHAR(120) NOT NULL, email VARCHAR(150) NOT NULL UNIQUE,
    city VARCHAR(80) NOT NULL, segment VARCHAR(30) NOT NULL CHECK (segment IN ('Consumer','SMB','Enterprise')),
    signup_date DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL, category VARCHAR(80) NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0), cost NUMERIC(12,2) NOT NULL CHECK (cost > 0),
    active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    employee_id INTEGER REFERENCES employees(employee_id), order_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL CHECK (status IN ('Completed','Pending','Cancelled','Returned')),
    shipping_city VARCHAR(80) NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id), quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0)
);
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status_date ON orders(status, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
