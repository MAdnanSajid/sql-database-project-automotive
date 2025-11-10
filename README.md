## Automotive Workshop Database Project (SQLite + Python)

This project demonstrates the creation and population of a relational SQL database using **SQLite3** and **Python's Faker library**. The chosen topic is an **Automotive Workshop Management System**, designed to fulfill the requirements of a database generation assignment.

---

### Key Focus Areas and Schema

The database schema is structured to track core workshop operations:

| Table | Primary Key | Foreign Keys | Row Count (Approx.) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`Customers`** | `customer_id` | - | 260 | Stores basic customer information. |
| **`Vehicles`** | `vehicle_id` | `customer_id` | 620 | Stores vehicle details, linked to the owner. |
| **`Mechanics`** | `mechanic_id` | - | 20 | Workshop staff information and hourly rates. |
| **`PartsInventory`** | `part_id` | - | 9 | Stock, pricing, and supplier information for parts. |
| **`Services`** | `service_id` | `vehicle_id`, `mechanic_id` | **1000** | Record of work performed, including date, type, and labor cost. |
| **`ServiceParts`** | **Compound** (`service_id`, `part_id`) | `service_id`, `part_id` | 1900+ | Junction table detailing parts used for each service. |
| **`Invoices`** | `invoice_id` | `service_id` | 1000 | Financial record, totaling service cost + parts cost. |

---

### Data Types

| Data Type | Example Column | Table | Example Values |
| :--- | :--- | :--- | :--- |
| **Nominal** (Categorical) | `status` | `Services` | 'Pending', 'In Progress', 'Completed' |
| **Ordinal** (Ordered) | `experience_level` | `Mechanics` | 'Junior', 'Mid', 'Senior' |
| **Interval** (Arbitrary Zero) | `year` | `Vehicles` | 1990 to 2024 (e.g., 2015) |
| **Ratio** (Meaningful Zero) | `hourly_rate` | `Mechanics` | 12.00 to 100.00 |

---

### Running the Project

To generate the `automotive_workshop.db` file, you need Python and the required libraries.
