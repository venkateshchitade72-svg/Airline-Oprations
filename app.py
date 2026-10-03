import os
from base64 import b64encode
from datetime import date, datetime
from pathlib import Path

import mysql.connector
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Venkatesh Airline",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

asset_folder = Path(__file__).parent / "assets"
airplane_image = b64encode((asset_folder / "airplane.jpg").read_bytes()).decode("ascii")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    :root { --ink: #182a35; --muted: #687a80; --teal: #147d78; --mint: #e4f1eb; --coral: #dc7058; --line: #dce5e1; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp, [data-testid="stAppViewContainer"] { background-color: #f5f8f5; background-image: linear-gradient(135deg, rgba(245,248,245,.62) 0%, rgba(251,250,245,.66) 54%, rgba(238,245,243,.62) 100%), url("data:image/jpeg;base64,__AIRPLANE_IMAGE__"); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; }
    [data-testid="stMain"] { background: transparent !important; }
    [data-testid="stSidebar"] { background: #18343c; }
    [data-testid="stSidebar"] * { color: #eff7f1 !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .42rem .2rem; }
    h1, h2, h3 { color: var(--ink); }
    h1, h2 { font-family: 'Playfair Display', Georgia, serif; letter-spacing: 0; }
    .eyebrow { color: var(--teal); font-size: .74rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .masthead { position: relative; isolation: isolate; overflow: hidden; min-height: 190px; display: flex; flex-direction: column; justify-content: center; padding: 1.8rem 2rem; border: 0; border-radius: 6px; background-color: #17343d; background-image: linear-gradient(90deg, rgba(12,35,44,.82) 0%, rgba(12,35,44,.56) 58%, rgba(12,35,44,.3) 100%), url("data:image/jpeg;base64,__AIRPLANE_IMAGE__"); background-size: cover; background-position: center 54%; margin: .25rem 0 1.45rem; }
    .masthead > * { position: relative; z-index: 1; }
    .masthead .eyebrow { color: #b5e3d7; }
    .masthead h1 { color: #fff; font-size: 2.1rem; margin: .18rem 0 .1rem; }
    .masthead p { color: rgba(255,255,255,.86); margin: 0; }
    @media (max-width: 640px) { .masthead { min-height: 170px; padding: 1.3rem; } .masthead::after { width: 34%; opacity: .8; } .masthead h1 { font-size: 1.8rem; } }
    div[data-testid="stMetric"] { background: rgba(255,255,255,.82); border: 1px solid var(--line); border-radius: 5px; padding: .9rem 1rem; }
    div[data-testid="stMetricLabel"] p { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--teal); }
    div[data-testid="stForm"] { background: rgba(255,255,255,.78); border: 1px solid var(--line); border-radius: 5px; padding: 1.1rem; }
    .stButton button[kind="primaryFormSubmit"], .stFormSubmitButton button { background: var(--teal); border-color: var(--teal); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 5px; }
    hr { border-color: var(--line); }
    </style>
    """.replace("__AIRPLANE_IMAGE__", airplane_image),
    unsafe_allow_html=True,
)


def setting(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def connect_database():
    return mysql.connector.connect(
        host=setting("AIR_DB_HOST", "localhost"),
        port=int(setting("AIR_DB_PORT", "3306")),
        user=setting("AIR_DB_USER", "root"),
        password=setting("AIR_DB_PASSWORD"),
        database=setting("AIR_DB_NAME", "air"),
        connection_timeout=int(setting("AIR_DB_CONNECT_TIMEOUT", "5")),
    )


def ensure_ticket_food_columns(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM ticket")
        existing_columns = {row[0] for row in cursor.fetchall()}
        if "food_charge" not in existing_columns:
            cursor.execute("ALTER TABLE ticket ADD COLUMN food_charge INT NOT NULL DEFAULT 0")
        if "food_items" not in existing_columns:
            cursor.execute("ALTER TABLE ticket ADD COLUMN food_items VARCHAR(500) NOT NULL DEFAULT ''")
    finally:
        cursor.close()


def fetch_rows(connection, query, values=()):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, values)
        return cursor.fetchall()
    finally:
        cursor.close()


def execute(connection, query, values=()):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def show_header(section, title, subtitle):
    st.markdown(f'<div class="eyebrow">{section}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(value.strip(), date_format).date()
            except ValueError:
                continue
    return date.today()


def dashboard(connection):
    show_header("Airline operations", "Good day. Here's your desk.", "A live view of passengers, bookings, and ticket revenue.")
    stats = fetch_rows(
        connection,
        """SELECT COUNT(*) AS bookings, COUNT(DISTINCT custno) AS passengers,
                  COALESCE(SUM(total), 0) AS revenue FROM ticket""",
    )[0]
    passenger_count = fetch_rows(connection, "SELECT COUNT(*) AS count FROM pdata")[0]["count"]
    first, second, third, fourth = st.columns(4)
    first.metric("Passengers registered", f"{passenger_count:,}")
    second.metric("Tickets issued", f"{stats['bookings']:,}")
    third.metric("Ticket revenue", f"₹{stats['revenue']:,.0f}")
    fourth.metric("Baggage collected", f"₹{sum(row['luggage'] or 0 for row in fetch_rows(connection, 'SELECT luggage FROM ticket')):,.0f}")

    chart_col, recent_col = st.columns([1, 1.25], gap="large")
    with chart_col:
        st.subheader("Bookings by fare")
        fare_rows = fetch_rows(
            connection,
            "SELECT tkt AS fare, COUNT(*) AS bookings FROM ticket GROUP BY tkt ORDER BY tkt DESC",
        )
        if fare_rows:
            chart = pd.DataFrame(fare_rows).set_index("fare")
            st.bar_chart(chart, color="#147d78")
        else:
            st.info("No ticket bookings yet. New bookings will appear here.")
    with recent_col:
        st.subheader("Recent bookings")
        recent = fetch_rows(
            connection,
            """SELECT p.custno AS `Customer #`, p.name AS Passenger, p.source AS `From`,
                      p.destination AS `To`, p.journey_date AS `Journey date`,
                      t.tkt AS Fare, t.luggage AS Baggage,
                      t.food_items AS `Food items`, t.food_charge AS `Food charge`,
                      t.total AS Total
               FROM pdata p INNER JOIN ticket t ON p.custno = t.custno
               ORDER BY p.journey_date DESC LIMIT 8""",
        )
        if recent:
            st.dataframe(pd.DataFrame(recent), hide_index=True, use_container_width=True)
        else:
            st.info("No bookings to show yet.")


def customers_page(connection):
    show_header("Passenger records", "Customers", "Register passengers and keep journey details in one place.")
    with st.expander("＋  Register a passenger", expanded=False):
        with st.form("register_customer", clear_on_submit=True):
            left, right = st.columns(2)
            customer_id = left.number_input("Customer number", min_value=1, max_value=2147483647, step=1)
            name = right.text_input("Full name", max_chars=20)
            address = left.text_input("Address", max_chars=100)
            journey_date = right.date_input("Journey date", value=date.today())
            source = left.text_input("From", max_chars=20)
            destination = right.text_input("To", max_chars=20)
            submitted = st.form_submit_button("Add passenger", type="primary")
        if submitted:
            if not all((name.strip(), address.strip(), source.strip(), destination.strip())):
                st.warning("Please complete all passenger and journey fields.")
            else:
                execute(
                    connection,
                    "INSERT INTO pdata (custno, name, address, journey_date, source, destination) VALUES (%s, %s, %s, %s, %s, %s)",
                    (customer_id, name.strip(), address.strip(), journey_date, source.strip(), destination.strip()),
                )
                st.success(f"Passenger {name.strip()} was registered.")
                st.rerun()

    records = fetch_rows(
        connection,
        "SELECT custno AS `Customer #`, name AS Passenger, address AS Address, journey_date AS `Journey date`, source AS `From`, destination AS `To` FROM pdata ORDER BY custno DESC",
    )
    search = st.text_input("Search passengers", placeholder="Name, destination, or customer number")
    if search:
        filtered = [row for row in records if search.casefold() in " ".join(str(value or "") for value in row.values()).casefold()]
    else:
        filtered = records
    st.caption(f"Showing {len(filtered)} of {len(records)} passengers")
    st.dataframe(pd.DataFrame(filtered), hide_index=True, use_container_width=True)

    if records:
        st.divider()
        st.subheader("Update passenger details")
        id_to_record = {row["Customer #"]: row for row in records}
        selected_id = st.selectbox("Select customer", list(id_to_record), format_func=lambda value: f"{value} · {id_to_record[value]['Passenger']}")
        selected = id_to_record[selected_id]
        with st.form("update_customer"):
            left, right = st.columns(2)
            updated_name = left.text_input("Full name", value=selected["Passenger"] or "", max_chars=20)
            updated_address = right.text_input("Address", value=selected["Address"] or "", max_chars=100)
            updated_date = left.date_input("Journey date", value=as_date(selected["Journey date"]), key="update_journey_date")
            updated_source = right.text_input("From", value=selected["From"] or "", max_chars=20)
            updated_destination = left.text_input("To", value=selected["To"] or "", max_chars=20)
            save = st.form_submit_button("Save passenger changes", type="primary")
        if save:
            if not all((updated_name.strip(), updated_address.strip(), updated_source.strip(), updated_destination.strip())):
                st.warning("Please complete all passenger and journey fields.")
            else:
                execute(
                    connection,
                    "UPDATE pdata SET name=%s, address=%s, journey_date=%s, source=%s, destination=%s WHERE custno=%s",
                    (updated_name.strip(), updated_address.strip(), updated_date, updated_source.strip(), updated_destination.strip(), selected_id),
                )
                st.success("Passenger details updated.")
                st.rerun()
        if st.checkbox("Confirm passenger and booking deletion", key="confirm_customer_delete"):
            if st.button("Delete passenger and their bookings", key="delete_customer"):
                cursor = connection.cursor()
                try:
                    cursor.execute("DELETE FROM ticket WHERE custno=%s", (selected_id,))
                    cursor.execute("DELETE FROM pdata WHERE custno=%s", (selected_id,))
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
                finally:
                    cursor.close()
                st.success("Passenger and associated bookings deleted.")
                st.rerun()


def booking_page(connection):
    show_header("Ticketing", "Create a booking", "Choose a passenger, select a cabin, and calculate baggage charges.")
    passengers = fetch_rows(connection, "SELECT custno, name FROM pdata ORDER BY name")
    if not passengers:
        st.info("Register a passenger before creating a booking.")
        return
    try:
        classes = fetch_rows(connection, "SELECT itemname, rate FROM classtype ORDER BY rate DESC")
    except mysql.connector.Error:
        classes = []
    if not classes:
        classes = [
            {"itemname": "First class", "rate": 6000},
            {"itemname": "Business class", "rate": 4000},
            {"itemname": "Economy class", "rate": 2000},
        ]

    passenger_ids = [row["custno"] for row in passengers]
    food_rows = fetch_rows(connection, "SELECT sno, itemname, price FROM foodinfo ORDER BY itemname, sno")
    passenger_by_id = {row["custno"]: row["name"] for row in passengers}
    fares = {row["itemname"]: int(row["rate"]) for row in classes}
    customer_id = st.selectbox("Passenger", passenger_ids, format_func=lambda value: f"{passenger_by_id[value]} · #{value}")
    cabin = st.selectbox("Cabin class", list(fares), format_func=lambda value: f"{value} · ₹{fares[value]:,}")
    luggage_kg = st.number_input("Extra baggage (kg)", min_value=0, max_value=200, value=0, step=1)
    fare = fares[cabin]
    baggage_charge = int(luggage_kg) * 100

    food_options = {
        f"{row['itemname']} · ₹{int(row['price']):,} · #{row['sno']} · item {index + 1}": row
        for index, row in enumerate(food_rows)
    }
    selected_food_labels = st.multiselect(
        "Food menu",
        list(food_options),
        help="Select food items to add to this booking.",
    )
    food_charge = 0
    food_order = []
    if selected_food_labels:
        st.caption("Set the quantity for each selected item.")
        for label in selected_food_labels:
            item = food_options[label]
            quantity = st.number_input(
                f"{item['itemname']} · ₹{int(item['price']):,} each",
                min_value=1,
                max_value=50,
                value=1,
                step=1,
                key=f"booking_food_quantity_{label}",
            )
            food_charge += int(item["price"]) * quantity
            food_order.append(f"{quantity} x {item['itemname']}")
    elif not food_rows:
        st.info("No food items are listed in the catalog yet.")

    total = fare + baggage_charge + food_charge
    st.markdown(
        f"**Fare** ₹{fare:,}　 ·　 **Baggage** ₹{baggage_charge:,}　 ·　 "
        f"**Food** ₹{food_charge:,}　 ·　 **Total** ₹{total:,}"
    )
    submitted = st.button("Confirm booking", type="primary")
    if submitted:
        execute(
            connection,
            "INSERT INTO ticket (custno, tkt, luggage, food_charge, food_items, total) VALUES (%s, %s, %s, %s, %s, %s)",
            (customer_id, fare, baggage_charge, food_charge, ", ".join(food_order), total),
        )
        st.success(f"Booking confirmed for {passenger_by_id[customer_id]} · total ₹{total:,}.")
        st.rerun()

    st.divider()
    st.subheader("Booking ledger")
    bookings = fetch_rows(
        connection,
        """SELECT p.custno AS `Customer #`, p.name AS Passenger, p.source AS `From`,
                  p.destination AS `To`, p.journey_date AS `Journey date`,
                  t.tkt AS Fare, t.luggage AS Baggage,
                  t.food_items AS `Food items`, t.food_charge AS `Food charge`,
                  t.total AS Total
           FROM pdata p INNER JOIN ticket t ON p.custno = t.custno
           ORDER BY p.journey_date DESC""",
    )
    st.dataframe(pd.DataFrame(bookings), hide_index=True, use_container_width=True)
    if bookings:
        st.subheader("Edit booking details")
        booking_index = st.selectbox(
            "Select booking",
            range(len(bookings)),
            format_func=lambda index: (
                f"{bookings[index]['Passenger']} · #{bookings[index]['Customer #']} · "
                f"₹{bookings[index]['Total']}"
            ),
        )
        selected_booking = bookings[booking_index]
        with st.form("edit_booking"):
            updated_fare = st.number_input("Ticket fare (₹)", min_value=0, step=100, value=int(selected_booking["Fare"]))
            updated_baggage = st.number_input("Baggage charge (₹)", min_value=0, step=100, value=int(selected_booking["Baggage"] or 0))
            updated_food_charge = int(selected_booking["Food charge"] or 0)
            st.caption(
                f"Food: {selected_booking['Food items'] or 'None'} · "
                f"₹{updated_food_charge:,} (kept with this booking)"
            )
            st.markdown(f"**Updated total** ₹{updated_fare + updated_baggage + updated_food_charge:,}")
            save_booking = st.form_submit_button("Save booking changes", type="primary")
        if save_booking:
            execute(
                connection,
                     """UPDATE ticket SET tkt=%s, luggage=%s, food_charge=%s, total=%s
                         WHERE custno=%s AND tkt=%s AND luggage=%s AND food_charge=%s AND total=%s LIMIT 1""",
                (
                    updated_fare,
                    updated_baggage,
                          updated_food_charge,
                          updated_fare + updated_baggage + updated_food_charge,
                    selected_booking["Customer #"],
                    selected_booking["Fare"],
                    selected_booking["Baggage"],
                          selected_booking["Food charge"],
                    selected_booking["Total"],
                ),
            )
            st.success("Booking details updated.")
            st.rerun()


def catalog_page(connection):
    show_header("Services and fares", "Catalog", "Maintain the fare classes and onboard food list.")
    classes_tab, food_tab = st.tabs(["Fare classes", "Food menu"])
    with classes_tab:
        class_rows = fetch_rows(connection, "SELECT sno AS `Serial #`, itemname AS Class, rate AS `Fare (₹)` FROM classtype ORDER BY rate DESC")
        st.dataframe(pd.DataFrame(class_rows), hide_index=True, use_container_width=True)
        with st.expander("Add fare class"):
            with st.form("add_class", clear_on_submit=True):
                serial = st.number_input("Serial number", min_value=1, step=1, key="class_serial")
                class_name = st.text_input("Class name", key="class_name", max_chars=50)
                rate = st.number_input("Ticket fare (₹)", min_value=0, step=100, key="class_rate")
                add_class = st.form_submit_button("Add fare class", type="primary")
            if add_class:
                execute(connection, "INSERT INTO classtype (sno, itemname, rate) VALUES (%s, %s, %s)", (serial, class_name.strip(), rate))
                st.success("Fare class added.")
                st.rerun()
        if class_rows:
            choices = {row["Serial #"]: row for row in class_rows}
            selected = st.selectbox("Edit fare class", list(choices), format_func=lambda value: f"{choices[value]['Class']} · #{value}")
            with st.form("edit_class"):
                edit_name = st.text_input("Class name", value=choices[selected]["Class"], max_chars=50)
                edit_rate = st.number_input("Ticket fare (₹)", min_value=0, step=100, value=int(choices[selected]["Fare (₹)"]))
                save_class = st.form_submit_button("Save class")
            if save_class:
                execute(connection, "UPDATE classtype SET itemname=%s, rate=%s WHERE sno=%s", (edit_name.strip(), edit_rate, selected))
                st.success("Fare class updated.")
                st.rerun()
            if st.checkbox("Confirm fare class deletion", key="confirm_class_delete"):
                if st.button("Delete selected fare class", key="delete_class"):
                    execute(connection, "DELETE FROM classtype WHERE sno=%s", (selected,))
                    st.success("Fare class deleted.")
                    st.rerun()

    with food_tab:
        food_rows = fetch_rows(connection, "SELECT sno AS `Serial #`, itemname AS Item, price AS `Price (₹)` FROM foodinfo ORDER BY itemname")
        st.dataframe(pd.DataFrame(food_rows), hide_index=True, use_container_width=True)
        with st.expander("Add food item"):
            with st.form("add_food", clear_on_submit=True):
                food_serial = st.number_input("Serial number", min_value=1, step=1, key="food_serial")
                food_name = st.text_input("Food item", key="food_name", max_chars=50)
                food_price = st.number_input("Price per pack (₹)", min_value=0, step=10, key="food_price")
                add_food = st.form_submit_button("Add food item", type="primary")
            if add_food:
                execute(connection, "INSERT INTO foodinfo (sno, itemname, price) VALUES (%s, %s, %s)", (food_serial, food_name.strip(), food_price))
                st.success("Food item added.")
                st.rerun()
        if food_rows:
            food_choices = {row["Serial #"]: row for row in food_rows}
            selected_food = st.selectbox("Edit food item", list(food_choices), format_func=lambda value: f"{food_choices[value]['Item']} · #{value}")
            with st.form("edit_food"):
                edit_food_name = st.text_input("Food item", value=food_choices[selected_food]["Item"], max_chars=50)
                edit_food_price = st.number_input("Price per pack (₹)", min_value=0, step=10, value=int(food_choices[selected_food]["Price (₹)"]))
                save_food = st.form_submit_button("Save food item")
            if save_food:
                execute(connection, "UPDATE foodinfo SET itemname=%s, price=%s WHERE sno=%s", (edit_food_name.strip(), edit_food_price, selected_food))
                st.success("Food item updated.")
                st.rerun()
            if st.checkbox("Confirm food item deletion", key="confirm_food_delete"):
                if st.button("Delete selected food item", key="delete_food"):
                    execute(connection, "DELETE FROM foodinfo WHERE sno=%s", (selected_food,))
                    st.success("Food item deleted.")
                    st.rerun()


st.sidebar.markdown("### ✈  VENKATESH AIRLINE")
st.sidebar.caption("Passenger and ticket operations")
page = st.sidebar.radio("Workspace", ["Overview", "Customers", "Bookings", "Catalog"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("VENKATESH AIRLINE")
st.markdown(
    '<div class="masthead"><div class="eyebrow">AIRLINE OPERATIONS</div><h1>VENKATESH AIRLINE</h1><p>Passenger records · ticketing · onboard services</p></div>',
    unsafe_allow_html=True,
)

try:
    database = connect_database()
    ensure_ticket_food_columns(database)
except mysql.connector.Error as error:
    st.error(f"Could not connect to the MySQL database: {error}")
    st.info("Confirm MySQL is running, the `air` database and expected tables exist, then configure the database connection using the README.")
    st.stop()

try:
    if page == "Overview":
        dashboard(database)
    elif page == "Customers":
        customers_page(database)
    elif page == "Bookings":
        booking_page(database)
    else:
        catalog_page(database)
except mysql.connector.Error as error:
    database.rollback()
    st.error(f"Database operation failed: {error}")
    st.caption("Check that the `air` database has the `pdata`, `ticket`, `classtype`, and `foodinfo` tables with the columns used by the original program.")
finally:
    database.close()