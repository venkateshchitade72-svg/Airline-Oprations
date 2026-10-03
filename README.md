# Airline Desk

Streamlit frontend for the MySQL airline workflow in `airline_2.py`. It provides an operations overview, passenger registration and editing, ticket booking, and fare/food catalog management.

The workspace and masthead use a locally bundled airplane photo.

## Run

Install the dependencies and start the app from this folder:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app expects a running MySQL server, a database named `air`, and the existing `pdata`, `ticket`, `classtype`, and `foodinfo` tables. The original script connects to the same database but does not include the table-creation SQL.

On startup, the app adds `food_charge` and `food_items` columns to `ticket` if they are missing. Booking totals include selected food items at their catalog prices multiplied by quantity.

Configure the connection with environment variables before starting Streamlit. The defaults are host `localhost`, port `3306`, user `root`, and database `air`; set the password rather than storing it in source code.

```powershell
$env:AIR_DB_HOST = "localhost"
$env:AIR_DB_PORT = "3306"
$env:AIR_DB_USER = "root"
$env:AIR_DB_PASSWORD = "your-mysql-password"
$env:AIR_DB_NAME = "air"
python -m streamlit run app.py
```

Streamlit secrets can also be used in `.streamlit/secrets.toml`:

```toml
AIR_DB_HOST = "localhost"
AIR_DB_PORT = "3306"
AIR_DB_USER = "root"
AIR_DB_PASSWORD = "your-mysql-password"
AIR_DB_NAME = "air"
```

Ticket fares default to the original First (₹6,000), Business (₹4,000), and Economy (₹2,000) prices when `classtype` is empty or unavailable. Extra baggage is charged at ₹100 per kg, matching the original program.