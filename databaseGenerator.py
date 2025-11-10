import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta


fake = Faker()
conn = sqlite3.connect("automotive_workshop.db")
cursor = conn.cursor()


# Using for only making changes and resetting everything
# tables = ["ServiceParts", "Invoices", "Services", "Vehicles", "Customers", "Mechanics", "PartsInventory"]
# for table in tables:
#     cursor.execute(f"DROP TABLE IF EXISTS {table}")


# Create Tables

cursor.execute("""
CREATE TABLE Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    registration_date DATE
);
""")

cursor.execute("""
CREATE TABLE Vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    make TEXT,
    model TEXT,
    year INTEGER CHECK (year >= 1990 AND year <= 2025),
    mileage REAL CHECK (mileage >= 0),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Mechanics (
    mechanic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    experience_level TEXT CHECK (experience_level IN ('Junior', 'Mid', 'Senior')),
    specialization TEXT,
    hourly_rate REAL CHECK (hourly_rate > 0)
);
""")

cursor.execute("""
CREATE TABLE PartsInventory (
    part_id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT NOT NULL,
    quantity INTEGER CHECK (quantity >= 0),
    price_per_unit REAL CHECK (price_per_unit > 0),
    supplier TEXT
);
""")

cursor.execute("""
CREATE TABLE Services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    mechanic_id INTEGER,
    service_type TEXT,
    status TEXT CHECK (status IN ('Pending', 'In Progress', 'Completed')),
    service_date DATE,
    cost REAL CHECK (cost >= 0),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (mechanic_id) REFERENCES Mechanics(mechanic_id)
);
""")

cursor.execute("""
CREATE TABLE ServiceParts (
    service_id INTEGER,
    part_id INTEGER,
    quantity_used INTEGER CHECK (quantity_used > 0),
    PRIMARY KEY (service_id, part_id),
    FOREIGN KEY (service_id) REFERENCES Services(service_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES PartsInventory(part_id)
);
""")

cursor.execute("""
CREATE TABLE Invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER,
    invoice_date DATE,
    total_amount REAL CHECK (total_amount >= 0),
    payment_status TEXT CHECK (payment_status IN ('Paid', 'Unpaid', 'Pending')),
    FOREIGN KEY (service_id) REFERENCES Services(service_id) ON DELETE CASCADE
);
""")

conn.commit()


# Mock Data to use with faker
car_makes_models = {
    "Toyota": ["Corolla", "Camry", "Yaris"],
    "Honda": ["Civic", "Accord", "Fit"],
    "Ford": ["Focus", "Fiesta", "Fusion"],
    "Suzuki": ["Cultus", "Ciaz", "Mira"],
    "Hyundai": ["Elantra", "Sonata", "Tucson"],
    "Nissan": ["Altima", "Sentra", "Micra"],
    "Kia": ["Sportage", "Picanto", "Cerato"]
}

service_types = ["Oil Change", "Engine Repair", "Tire Replacement", "Brake Inspection", "Battery Replacement"]
specializations = ["Engine", "Electrical", "Body", "Brakes", "Transmission"]
status_choices = ["Pending", "In Progress", "Completed"]
experience_levels = ["Junior", "Mid", "Senior"]
payment_statuses = ["Paid", "Unpaid", "Pending"]

#Populate Tables

# Customers
num_customers = 250
for _ in range(num_customers):
    cursor.execute("""
        INSERT INTO Customers (name, email, phone, registration_date)
        VALUES (?, ?, ?, ?)
    """, (
        fake.name(),
        fake.email() if random.random() > 0.15 else None,
        fake.phone_number(),
        fake.date_between(start_date='-3y', end_date='today')
    ))
existing_customers = cursor.execute("SELECT name, email, phone, registration_date FROM Customers").fetchall()
for _ in range(int(num_customers * 0.05)):
    duplicate = random.choice(existing_customers)
    cursor.execute("""
        INSERT INTO Customers (name, email, phone, registration_date)
        VALUES (?, ?, ?, ?)
    """, duplicate)   

# Mechanics
num_mechanics = 20
for _ in range(num_mechanics):
    cursor.execute("""
        INSERT INTO Mechanics (name, experience_level, specialization, hourly_rate)
        VALUES (?, ?, ?, ?)
    """, (
        fake.name(),
        random.choice(experience_levels),
        random.choice(specializations),
        round(random.uniform(12, 100), 2)
    ))

# PartsInventory
parts_list = ["Brake Pad", "Oil Filter", "Air Filter", "Battery", "Spark Plug", "Headlight", "Clutch", "Wires", "Battery Connectors"]
for part_name in parts_list:
    cursor.execute("""
        INSERT INTO PartsInventory (part_name, quantity, price_per_unit, supplier)
        VALUES (?, ?, ?, ?)
    """, (
        part_name,
        random.randint(1, 50),
        round(random.uniform(8, 264), 2),
        fake.company()
    ))

# Vehicles
num_vehicles = 600
for _ in range(num_vehicles):
    make = random.choice(list(car_makes_models.keys()))
    model = random.choice(car_makes_models[make])
    cursor.execute("""
        INSERT INTO Vehicles (customer_id, make, model, year, mileage)
        VALUES (?, ?, ?, ?, ?)
    """, (
        random.randint(1, num_customers),
        make,
        model,
        random.randint(1990, 2024),
        round(random.uniform(500, 250000), 2)
    ))

# Services
num_services = 1000
existing_vehicles = cursor.execute("SELECT customer_id, make, model, year, mileage FROM Vehicles").fetchall()
for _ in range(int(num_vehicles * 0.03)):
    duplicate = random.choice(existing_vehicles)
    cursor.execute("""
        INSERT INTO Vehicles (customer_id, make, model, year, mileage)
        VALUES (?, ?, ?, ?, ?)
    """, duplicate)
for _ in range(num_services):
    vehicle_id = random.randint(1, num_vehicles)
    mechanic_id = random.randint(1, num_mechanics)
    reg_date = cursor.execute("""
        SELECT c.registration_date
        FROM Vehicles v
        JOIN Customers c ON v.customer_id = c.customer_id
        WHERE v.vehicle_id = ?
    """, (vehicle_id,)).fetchone()[0]
    reg_date = datetime.strptime(reg_date, "%Y-%m-%d")
    service_date = fake.date_between_dates(date_start=reg_date, date_end=datetime.today())
    cursor.execute("""
        INSERT INTO Services (vehicle_id, mechanic_id, service_type, status, service_date, cost)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        vehicle_id,
        mechanic_id,
        random.choice(service_types),
        random.choice(status_choices),
        service_date,
        round(random.uniform(50, 1500), 2)
    ))

# ServiceParts
service_ids = [row[0] for row in cursor.execute("SELECT service_id FROM Services")]
part_ids = [row[0] for row in cursor.execute("SELECT part_id FROM PartsInventory")]

for s_id in service_ids:
    used_parts = random.sample(part_ids, random.randint(1, 3))
    for pid in used_parts:
        cursor.execute("""
            INSERT INTO ServiceParts (service_id, part_id, quantity_used)
            VALUES (?, ?, ?)
        """, (s_id, pid, random.randint(1, 3)))

# Invoices
for s_id in service_ids:
    service_row = cursor.execute("SELECT cost, service_date FROM Services WHERE service_id=?", (s_id,)).fetchone()
    service_cost = service_row[0]
    service_date = datetime.strptime(service_row[1], "%Y-%m-%d")
    
    part_costs = cursor.execute("""
        SELECT SUM(sp.quantity_used * p.price_per_unit)
        FROM ServiceParts sp
        JOIN PartsInventory p ON sp.part_id = p.part_id
        WHERE sp.service_id=?
    """, (s_id,)).fetchone()[0] or 0
    
    total_amount = round(service_cost + part_costs, 2)
    invoice_date = fake.date_between_dates(date_start=service_date, date_end=datetime.today())

    cursor.execute("""
        INSERT INTO Invoices (service_id, invoice_date, total_amount, payment_status)
        VALUES (?, ?, ?, ?)
    """, (
        s_id,
        invoice_date,
        total_amount,
        random.choice(payment_statuses)
    ))

conn.commit()
conn.close()

