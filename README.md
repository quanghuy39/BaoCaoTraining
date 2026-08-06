# ClassicModels Sales Management System

A simple Sales Management System built with **Python** and **MySQL**, using the **ClassicModels** sample database. This project demonstrates CRUD operations, SQL queries, multi-table joins, and statistical reports through a command-line interface (CLI).

---

## Features

### Customer Management
- View customer list
- Search customers by country
- Add a new customer
- Delete a customer (with foreign key constraint checking)

### Product Management
- View products by product line
- Update product MSRP
- Calculate revenue by product line

### Order Management
- View orders by customer
- View order details
- Update order status

### Reports
- Number of orders by status
- Top customers by total payment

---

## Technologies

- Python 3
- MySQL 8.x
- PyMySQL
- Tabulate
- Docker

---

## Database

The project uses the **ClassicModels** sample database.

Main tables:

| Table | Description |
|-------|-------------|
| customers | Customer information |
| products | Product information |
| productlines | Product categories |
| orders | Orders |
| orderdetails | Order details |
| payments | Customer payments |
| employees | Employee information |
| offices | Office information |

---

## SQL Concepts Demonstrated

This project demonstrates the following SQL statements:

- SELECT
- INSERT
- UPDATE
- DELETE
- WHERE
- LIKE
- ORDER BY
- LIMIT
- JOIN
- GROUP BY
- HAVING
- COUNT()
- SUM()
- MAX()

---

## Project Structure

```
.
├── app.py
├── classicmodels.sql
├── Dockerfile
└── README.md
```

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/your-username/classicmodels-management.git
cd classicmodels-management
```

---

### 2. Install Python packages

```bash
pip install pymysql tabulate
```

---

### 3. Create MySQL database

```sql
CREATE DATABASE classicmodels;
```

Import the sample database:

```bash
mysql -u root -p classicmodels < classicmodels.sql
```

---

### 4. Configure database connection

Edit the configuration inside `app.py`.

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "your_password",
    "database": "classicmodels",
}
```

---

### 5. Run the application

```bash
python app.py
```

---

## Main Menu

```
======================================
SALES MANAGEMENT SYSTEM
======================================

1. Customer Management

2. Product Management

3. Order Management

4. Reports

0. Exit
```

---




## Author

Hoàng Quang Huy


## License

This project is developed for educational purposes.
