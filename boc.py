import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# ============================================================
# BOC RESTAURANT POS
# ============================================================

APP_NAME = "BOC RESTAURANT"
CURRENCY = "₹"
TAX_RATE = 0.05

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "boc.db")

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# COLOURS
# ============================================================

RED = "#9F1239"
RED_LIGHT = "#E11D48"
RED_DARK = "#881337"

CREAM = "#FFF7ED"
CREAM_DARK = "#FFEDD5"

DARK = "#1F2937"
DARKER = "#111827"

WHITE = "#FFFFFF"
GRAY = "#6B7280"
LIGHT_GRAY = "#F3F4F6"

GREEN = "#16A34A"
BLUE = "#2563EB"
ORANGE = "#EA580C"
YELLOW = "#CA8A04"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    return sqlite3.connect(DB_FILE)


def setup_database():

    conn = get_db()
    cur = conn.cursor()

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number INTEGER,
            order_time TEXT,
            customer TEXT,
            table_number TEXT,
            order_type TEXT,
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            total REAL DEFAULT 0,
            payment_method TEXT,
            amount_received REAL DEFAULT 0,
            change_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'PENDING'
        )
    """)

    # --------------------------------------------------------
    # AUTOMATIC DATABASE MIGRATION
    # --------------------------------------------------------

    cur.execute("PRAGMA table_info(orders)")

    columns = [
        row[1]
        for row in cur.fetchall()
    ]

    required_columns = {

        "order_number":
            "ALTER TABLE orders ADD COLUMN order_number INTEGER",

        "order_time":
            "ALTER TABLE orders ADD COLUMN order_time TEXT",

        "customer":
            "ALTER TABLE orders ADD COLUMN customer TEXT",

        "table_number":
            "ALTER TABLE orders ADD COLUMN table_number TEXT",

        "order_type":
            "ALTER TABLE orders ADD COLUMN order_type TEXT",

        "subtotal":
            "ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0",

        "tax":
            "ALTER TABLE orders ADD COLUMN tax REAL DEFAULT 0",

        "discount":
            "ALTER TABLE orders ADD COLUMN discount REAL DEFAULT 0",

        "total":
            "ALTER TABLE orders ADD COLUMN total REAL DEFAULT 0",

        "payment_method":
            "ALTER TABLE orders ADD COLUMN payment_method TEXT",

        "amount_received":
            "ALTER TABLE orders ADD COLUMN amount_received REAL DEFAULT 0",

        "change_amount":
            "ALTER TABLE orders ADD COLUMN change_amount REAL DEFAULT 0",

        "status":
            "ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'PENDING'"
    }

    for column, sql in required_columns.items():

        if column not in columns:

            cur.execute(sql)

    # --------------------------------------------------------
    # ORDER ITEMS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price REAL
        )
    """)

    # --------------------------------------------------------
    # SAMPLE MENU
    # --------------------------------------------------------

    cur.execute("SELECT COUNT(*) FROM menu")

    if cur.fetchone()[0] == 0:

        items = [

            ("Classic Veg Burger", "Burgers", 120),
            ("Chicken Burger", "Burgers", 180),
            ("French Fries", "Sides", 80),
            ("Cheese Pizza", "Pizza", 250),
            ("Paneer Pizza", "Pizza", 280),
            ("White Sauce Pasta", "Pasta", 220),
            ("Paneer Tikka", "Starters", 180),
            ("Chicken Tikka", "Starters", 220),
            ("Cold Coffee", "Drinks", 100),
            ("Fresh Lime", "Drinks", 70),
            ("Masala Tea", "Drinks", 50),
            ("Chocolate Ice Cream", "Desserts", 90)

        ]

        cur.executemany("""
            INSERT INTO menu
            (name, category, price)
            VALUES (?, ?, ?)
        """, items)

    # --------------------------------------------------------
    # FIX OLD ORDER NUMBERS
    # --------------------------------------------------------

    cur.execute("""
        SELECT id
        FROM orders
        WHERE order_number IS NULL
        ORDER BY id
    """)

    old_orders = cur.fetchall()

    for number, row in enumerate(old_orders, start=1):

        cur.execute("""
            UPDATE orders
            SET order_number = ?
            WHERE id = ?
        """, (
            number,
            row[0]
        ))

    conn.commit()
    conn.close()


# ============================================================
# MAIN APPLICATION
# ============================================================

class BOCApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "BOC Restaurant POS"
        )

        self.root.geometry(
            "1350x800"
        )

        self.root.minsize(
            1100,
            700
        )

        self.cart = []

        self.current_order_id = None

        self.current_discount = 0

        self.setup_styles()

        self.create_sidebar()

        self.create_main_area()

        self.show_dashboard()

    # ========================================================
    # STYLES
    # ========================================================

    def setup_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=DARK,
            rowheight=34,
            fieldbackground=WHITE,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=RED,
            foreground=WHITE,
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#FCE7F3")
            ],
            foreground=[
                ("selected", DARK)
            ]
        )

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        self.sidebar = tk.Frame(
            self.root,
            bg=DARKER,
            width=230
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # LOGO

        logo = tk.Frame(
            self.sidebar,
            bg=RED,
            height=110
        )

        logo.pack(
            fill="x"
        )

        tk.Label(
            logo,
            text="BOC",
            bg=RED,
            fg=WHITE,
            font=("Arial", 32, "bold")
        ).pack(
            pady=(15, 0)
        )

        tk.Label(
            logo,
            text="RESTAURANT POS",
            bg=RED,
            fg=CREAM,
            font=("Arial", 9, "bold")
        ).pack()

        # NAVIGATION

        self.nav_button(
            "⌂   Dashboard",
            self.show_dashboard
        )

        self.nav_button(
            "🍽   New Order",
            self.show_new_order
        )

        self.nav_button(
            "▣   Orders",
            self.show_orders
        )

        self.nav_button(
            "₹   Billing",
            self.show_billing
        )

        self.nav_button(
            "▤   Menu",
            self.show_menu
        )

        self.nav_button(
            "◈   Sales",
            self.show_sales
        )

        tk.Frame(
            self.sidebar,
            bg=DARKER
        ).pack(
            fill="both",
            expand=True
        )

        tk.Label(
            self.sidebar,
            text="BOC v1.0",
            bg=DARKER,
            fg="#9CA3AF",
            font=("Arial", 9)
        ).pack(
            pady=15
        )

    def nav_button(
        self,
        text,
        command
    ):

        tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=DARKER,
            fg=WHITE,
            activebackground=RED,
            activeforeground=WHITE,
            font=("Arial", 12, "bold"),
            anchor="w",
            relief="flat",
            bd=0,
            padx=22,
            pady=15
        ).pack(
            fill="x"
        )

    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        self.main = tk.Frame(
            self.root,
            bg=CREAM
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

    def clear_main(self):

        for widget in self.main.winfo_children():

            widget.destroy()

    # ========================================================
    # PAGE HEADER
    # ========================================================

    def page_header(
        self,
        title,
        subtitle=""
    ):

        frame = tk.Frame(
            self.main,
            bg=CREAM
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        tk.Label(
            frame,
            text=title,
            bg=CREAM,
            fg=DARKER,
            font=("Arial", 25, "bold")
        ).pack(
            anchor="w"
        )

        if subtitle:

            tk.Label(
                frame,
                text=subtitle,
                bg=CREAM,
                fg=GRAY,
                font=("Arial", 10)
            ).pack(
                anchor="w",
                pady=(3, 0)
            )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.clear_main()

        self.page_header(
            "Good Day 👋",
            "Welcome to BOC Restaurant Management"
        )

        # CARDS

        cards = tk.Frame(
            self.main,
            bg=CREAM
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=15
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'PENDING'
        """)

        pending = cur.fetchone()[0]

        cur.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(total), 0)
            FROM orders
            WHERE status = 'COMPLETED'
        """)

        completed, sales = cur.fetchone()

        cur.execute("""
            SELECT COUNT(*)
            FROM menu
        """)

        menu_count = cur.fetchone()[0]

        conn.close()

        self.dashboard_card(
            cards,
            "PENDING ORDERS",
            str(pending),
            RED
        )

        self.dashboard_card(
            cards,
            "COMPLETED",
            str(completed),
            BLUE
        )

        self.dashboard_card(
            cards,
            "TOTAL SALES",
            f"₹{sales:,.2f}",
            GREEN
        )

        self.dashboard_card(
            cards,
            "MENU ITEMS",
            str(menu_count),
            ORANGE
        )

        # WELCOME BOX

        welcome = tk.Frame(
            self.main,
            bg=WHITE,
            highlightbackground=CREAM_DARK,
            highlightthickness=1
        )

        welcome.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        tk.Label(
            welcome,
            text="BOC RESTAURANT",
            bg=WHITE,
            fg=RED,
            font=("Arial", 28, "bold")
        ).pack(pady=(60, 5))

        tk.Label(
            welcome,
            text="Fast • Simple • Reliable",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 13)
        ).pack()

        tk.Button(
            welcome,
            text="+  CREATE NEW ORDER",
            command=self.show_new_order,
            bg=RED,
            fg=WHITE,
            activebackground=RED_LIGHT,
            font=("Arial", 14, "bold"),
            relief="flat",
            padx=30,
            pady=15
        ).pack(pady=35)

    def dashboard_card(
        self,
        parent,
        title,
        value,
        color
    ):

        card = tk.Frame(
            parent,
            bg=WHITE,
            width=220,
            height=115
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=7
        )

        tk.Frame(
            card,
            bg=color,
            width=6
        ).pack(
            side="left",
            fill="y"
        )

        tk.Label(
            card,
            text=title,
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 3)
        )

        tk.Label(
            card,
            text=value,
            bg=WHITE,
            fg=DARKER,
            font=("Arial", 23, "bold")
        ).pack(
            anchor="w",
            padx=18
        )

    # ========================================================
    # MENU
    # ========================================================

    def show_menu(self):

        self.clear_main()

        self.page_header(
            "Menu",
            "Available food and prices"
        )

        table = ttk.Treeview(
            self.main,
            columns=(
                "id",
                "name",
                "category",
                "price"
            ),
            show="headings"
        )

        table.heading(
            "id",
            text="ID"
        )

        table.heading(
            "name",
            text="ITEM"
        )

        table.heading(
            "category",
            text="CATEGORY"
        )

        table.heading(
            "price",
            text="PRICE"
        )

        table.column(
            "id",
            width=70
        )

        table.column(
            "name",
            width=400
        )

        table.column(
            "category",
            width=250
        )

        table.column(
            "price",
            width=180
        )

        table.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, category, price
            FROM menu
            ORDER BY category, name
        """)

        rows = cur.fetchall()

        conn.close()

        for row in rows:

            table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"₹{row[3]:.2f}"
                )
            )

    # ========================================================
    # NEW ORDER
    # ========================================================

    def show_new_order(self):

        self.clear_main()

        self.cart = []
        self.current_discount = 0

        self.page_header(
            "New Order",
            "Create an order and send it to the order queue"
        )

        # CUSTOMER BAR

        customer_bar = tk.Frame(
            self.main,
            bg=WHITE
        )

        customer_bar.pack(
            fill="x",
            padx=30,
            pady=5
        )

        tk.Label(
            customer_bar,
            text="Customer",
            bg=WHITE,
            fg=DARK,
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            padx=(15, 5),
            pady=15
        )

        self.customer_entry = tk.Entry(
            customer_bar,
            width=20,
            font=("Arial", 11)
        )

        self.customer_entry.pack(
            side="left"
        )

        tk.Label(
            customer_bar,
            text="Table",
            bg=WHITE,
            fg=DARK,
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            padx=(20, 5)
        )

        self.table_entry = tk.Entry(
            customer_bar,
            width=8,
            font=("Arial", 11)
        )

        self.table_entry.pack(
            side="left"
        )

        tk.Label(
            customer_bar,
            text="Type",
            bg=WHITE,
            fg=DARK,
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            padx=(20, 5)
        )

        self.order_type = ttk.Combobox(
            customer_bar,
            values=[
                "Dine In",
                "Takeaway",
                "Delivery"
            ],
            state="readonly",
            width=12
        )

        self.order_type.current(0)

        self.order_type.pack(
            side="left"
        )

        # ORDER AREA

        area = tk.Frame(
            self.main,
            bg=CREAM
        )

        area.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        # MENU LEFT

        left = tk.Frame(
            area,
            bg=WHITE
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        tk.Label(
            left,
            text="SELECT ITEMS",
            bg=WHITE,
            fg=DARKER,
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        self.food_table = ttk.Treeview(
            left,
            columns=(
                "id",
                "name",
                "category",
                "price"
            ),
            show="headings"
        )

        for col, title in [
            ("id", "ID"),
            ("name", "ITEM"),
            ("category", "CATEGORY"),
            ("price", "PRICE")
        ]:

            self.food_table.heading(
                col,
                text=title
            )

        self.food_table.pack(
            fill="both",
            expand=True,
            padx=10
        )

        tk.Button(
            left,
            text="+ ADD TO ORDER",
            command=self.add_to_cart,
            bg=GREEN,
            fg=WHITE,
            activebackground="#15803D",
            font=("Arial", 12, "bold"),
            relief="flat",
            pady=10
        ).pack(
            fill="x",
            padx=15,
            pady=12
        )

        # CART RIGHT

        right = tk.Frame(
            area,
            bg=WHITE,
            width=400
        )

        right.pack(
            side="right",
            fill="both",
            padx=(8, 0)
        )

        tk.Label(
            right,
            text="CURRENT ORDER",
            bg=WHITE,
            fg=DARKER,
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        self.cart_table = ttk.Treeview(
            right,
            columns=(
                "item",
                "qty",
                "total"
            ),
            show="headings",
            height=10
        )

        self.cart_table.heading(
            "item",
            text="ITEM"
        )

        self.cart_table.heading(
            "qty",
            text="QTY"
        )

        self.cart_table.heading(
            "total",
            text="TOTAL"
        )

        self.cart_table.pack(
            fill="x",
            padx=10
        )

        self.subtotal_label = tk.Label(
            right,
            text="Subtotal   ₹0.00",
            bg=WHITE,
            fg=DARK,
            font=("Arial", 11)
        )

        self.subtotal_label.pack(
            anchor="e",
            padx=20,
            pady=(15, 3)
        )

        self.tax_label = tk.Label(
            right,
            text="Tax 5%     ₹0.00",
            bg=WHITE,
            fg=DARK,
            font=("Arial", 11)
        )

        self.tax_label.pack(
            anchor="e",
            padx=20,
            pady=3
        )

        self.total_label = tk.Label(
            right,
            text="TOTAL      ₹0.00",
            bg=WHITE,
            fg=RED,
            font=("Arial", 20, "bold")
        )

        self.total_label.pack(
            anchor="e",
            padx=20,
            pady=12
        )

        tk.Button(
            right,
            text="REMOVE SELECTED",
            command=self.remove_cart_item,
            bg="#FEE2E2",
            fg=RED,
            font=("Arial", 10, "bold"),
            relief="flat",
            pady=8
        ).pack(
            fill="x",
            padx=15,
            pady=5
        )

        tk.Button(
            right,
            text="SEND ORDER  →",
            command=self.send_order,
            bg=RED,
            fg=WHITE,
            activebackground=RED_DARK,
            font=("Arial", 14, "bold"),
            relief="flat",
            pady=13
        ).pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.load_food_for_order()

    # ========================================================
    # LOAD FOOD
    # ========================================================

    def load_food_for_order(self):

        for item in self.food_table.get_children():

            self.food_table.delete(item)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, category, price
            FROM menu
            ORDER BY category, name
        """)

        rows = cur.fetchall()

        conn.close()

        for row in rows:

            self.food_table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"₹{row[3]:.2f}"
                )
            )

    # ========================================================
    # ADD TO CART
    # ========================================================

    def add_to_cart(self):

        selected = self.food_table.selection()

        if not selected:

            messagebox.showwarning(
                "BOC",
                "Please select an item first."
            )

            return

        values = self.food_table.item(
            selected[0]
        )["values"]

        item_id = int(values[0])
        name = values[1]

        price = float(
            str(values[3]).replace("₹", "")
        )

        for item in self.cart:

            if item["id"] == item_id:

                item["quantity"] += 1

                self.refresh_cart()

                return

        self.cart.append({
            "id": item_id,
            "name": name,
            "price": price,
            "quantity": 1
        })

        self.refresh_cart()

    # ========================================================
    # REFRESH CART
    # ========================================================

    def refresh_cart(self):

        for item in self.cart_table.get_children():

            self.cart_table.delete(item)

        subtotal = 0

        for item in self.cart:

            line_total = (
                item["price"] *
                item["quantity"]
            )

            subtotal += line_total

            self.cart_table.insert(
                "",
                "end",
                values=(
                    item["name"],
                    item["quantity"],
                    f"₹{line_total:.2f}"
                )
            )

        tax = subtotal * TAX_RATE

        total = (
            subtotal +
            tax -
            self.current_discount
        )

        self.subtotal_label.config(
            text=f"Subtotal   ₹{subtotal:.2f}"
        )

        self.tax_label.config(
            text=f"Tax 5%     ₹{tax:.2f}"
        )

        self.total_label.config(
            text=f"TOTAL      ₹{total:.2f}"
        )

    # ========================================================
    # REMOVE CART ITEM
    # ========================================================

    def remove_cart_item(self):

        selected = self.cart_table.selection()

        if not selected:
            return

        index = self.cart_table.index(
            selected[0]
        )

        if index < len(self.cart):

            self.cart.pop(index)

        self.refresh_cart()

    # ========================================================
    # SEND ORDER
    # ========================================================

    def send_order(self):

        if not self.cart:

            messagebox.showwarning(
                "BOC",
                "Your order is empty.\n\nPlease add food items first."
            )

            return

        customer = self.customer_entry.get().strip()

        table_number = self.table_entry.get().strip()

        order_type = self.order_type.get()

        if customer == "":
            customer = "Walk-in Customer"

        if table_number == "":
            table_number = "-"

        subtotal = sum(
            item["price"] * item["quantity"]
            for item in self.cart
        )

        tax = subtotal * TAX_RATE

        discount = self.current_discount

        total = (
            subtotal +
            tax -
            discount
        )

        try:

            conn = get_db()
            cur = conn.cursor()

            # Generate order number

            cur.execute("""
                SELECT
                    COALESCE(MAX(order_number), 0) + 1
                FROM orders
            """)

            order_number = cur.fetchone()[0]

            # Date/time

            order_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Insert order

            cur.execute("""
                INSERT INTO orders (
                    order_number,
                    order_time,
                    customer,
                    table_number,
                    order_type,
                    subtotal,
                    tax,
                    discount,
                    total,
                    payment_method,
                    amount_received,
                    change_amount,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_number,
                order_time,
                customer,
                table_number,
                order_type,
                subtotal,
                tax,
                discount,
                total,
                "",
                0,
                0,
                "PENDING"
            ))

            order_id = cur.lastrowid

            # Insert order items

            for item in self.cart:

                cur.execute("""
                    INSERT INTO order_items (
                        order_id,
                        item_name,
                        quantity,
                        price
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    order_id,
                    item["name"],
                    item["quantity"],
                    item["price"]
                ))

            conn.commit()

            conn.close()

        except Exception as error:

            messagebox.showerror(
                "BOC DATABASE ERROR",
                f"Could not save order.\n\n{error}"
            )

            return

        messagebox.showinfo(
            "ORDER SENT",
            f"Order #{order_number} created successfully!\n\n"
            f"Customer: {customer}\n"
            f"Table: {table_number}\n"
            f"Total: ₹{total:.2f}"
        )

        self.cart = []

        self.show_orders()

    # ========================================================
    # ORDERS
    # ========================================================

    def show_orders(self):

        self.clear_main()

        self.page_header(
            "Orders",
            "Manage pending restaurant orders"
        )

        table = ttk.Treeview(
            self.main,
            columns=(
                "id",
                "order",
                "customer",
                "table",
                "type",
                "total",
                "status"
            ),
            show="headings"
        )

        headings = [
            ("id", "ID"),
            ("order", "ORDER #"),
            ("customer", "CUSTOMER"),
            ("table", "TABLE"),
            ("type", "TYPE"),
            ("total", "TOTAL"),
            ("status", "STATUS")
        ]

        for column, heading in headings:

            table.heading(
                column,
                text=heading
            )

        table.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                order_number,
                customer,
                table_number,
                order_type,
                total,
                status
            FROM orders
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        conn.close()

        for row in rows:

            table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    f"₹{row[5]:.2f}",
                    row[6]
                )
            )

        tk.Button(
            self.main,
            text="OPEN BILLING  →",
            command=self.show_billing,
            bg=RED,
            fg=WHITE,
            font=("Arial", 13, "bold"),
            relief="flat",
            padx=30,
            pady=12
        ).pack(
            pady=15
        )

    # ========================================================
    # BILLING
    # ========================================================

    def show_billing(self):

        self.clear_main()

        self.page_header(
            "Billing",
            "Select a pending order and collect payment"
        )

        area = tk.Frame(
            self.main,
            bg=CREAM
        )

        area.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=5
        )

        # LEFT

        left = tk.Frame(
            area,
            bg=WHITE
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            left,
            text="PENDING ORDERS",
            bg=WHITE,
            fg=DARKER,
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        self.billing_table = ttk.Treeview(
            left,
            columns=(
                "id",
                "order",
                "customer",
                "total"
            ),
            show="headings"
        )

        for col, title in [
            ("id", "ID"),
            ("order", "ORDER #"),
            ("customer", "CUSTOMER"),
            ("total", "TOTAL")
        ]:

            self.billing_table.heading(
                col,
                text=title
            )

        self.billing_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.billing_table.bind(
            "<<TreeviewSelect>>",
            self.select_billing_order
        )

        # RIGHT BILL

        right = tk.Frame(
            area,
            bg=WHITE,
            width=470
        )

        right.pack(
            side="right",
            fill="both"
        )

        tk.Label(
            right,
            text="BILL PREVIEW",
            bg=WHITE,
            fg=DARKER,
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        self.bill_text = tk.Text(
            right,
            bg="#FFFBF5",
            fg=DARKER,
            font=("Courier New", 10),
            relief="flat"
        )

        self.bill_text.pack(
            fill="both",
            expand=True,
            padx=15
        )

        # PAYMENT

        payment = tk.Frame(
            right,
            bg=WHITE
        )

        payment.pack(
            fill="x",
            padx=15,
            pady=10
        )

        tk.Label(
            payment,
            text="Payment:",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        self.payment_method = ttk.Combobox(
            payment,
            values=[
                "CASH",
                "UPI",
                "CARD"
            ],
            state="readonly",
            width=10
        )

        self.payment_method.current(0)

        self.payment_method.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Label(
            payment,
            text="Received:",
            bg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        self.amount_received = tk.Entry(
            payment,
            width=12
        )

        self.amount_received.grid(
            row=0,
            column=3,
            padx=5
        )

        tk.Button(
            right,
            text="COMPLETE PAYMENT",
            command=self.complete_payment,
            bg=GREEN,
            fg=WHITE,
            activebackground="#15803D",
            font=("Arial", 13, "bold"),
            relief="flat",
            pady=12
        ).pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.load_billing_orders()

    # ========================================================
    # BILLING ORDERS
    # ========================================================

    def load_billing_orders(self):

        for item in self.billing_table.get_children():

            self.billing_table.delete(item)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                order_number,
                customer,
                total
            FROM orders
            WHERE status = 'PENDING'
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        conn.close()

        for row in rows:

            self.billing_table.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"₹{row[3]:.2f}"
                )
            )

    # ========================================================
    # SELECT BILL
    # ========================================================

    def select_billing_order(self, event):

        selected = self.billing_table.selection()

        if not selected:
            return

        values = self.billing_table.item(
            selected[0]
        )["values"]

        self.current_order_id = int(
            values[0]
        )

        self.display_bill()

    # ========================================================
    # DISPLAY BILL
    # ========================================================

    def display_bill(self):

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                order_number,
                order_time,
                customer,
                table_number,
                order_type,
                subtotal,
                tax,
                discount,
                total
            FROM orders
            WHERE id = ?
        """, (
            self.current_order_id,
        ))

        order = cur.fetchone()

        cur.execute("""
            SELECT
                item_name,
                quantity,
                price
            FROM order_items
            WHERE order_id = ?
        """, (
            self.current_order_id,
        ))

        items = cur.fetchall()

        conn.close()

        if not order:
            return

        bill = ""

        bill += "====================================\n"
        bill += "          BOC RESTAURANT\n"
        bill += "       RESTAURANT POS SYSTEM\n"
        bill += "====================================\n\n"

        bill += f"Order No : #{order[0]}\n"
        bill += f"Date     : {order[1]}\n"
        bill += f"Customer : {order[2]}\n"
        bill += f"Table    : {order[3]}\n"
        bill += f"Type     : {order[4]}\n"

        bill += "\n------------------------------------\n"

        for item in items:

            name = item[0]
            quantity = item[1]
            price = item[2]

            line = quantity * price

            bill += (
                f"{name}\n"
                f"  {quantity} x ₹{price:.2f}"
                f"       ₹{line:.2f}\n"
            )

        bill += "------------------------------------\n"

        bill += f"Subtotal       ₹{order[5]:.2f}\n"
        bill += f"Tax 5%         ₹{order[6]:.2f}\n"
        bill += f"Discount       ₹{order[7]:.2f}\n"

        bill += "------------------------------------\n"

        bill += f"TOTAL          ₹{order[8]:.2f}\n"

        bill += "====================================\n"
        bill += "          THANK YOU!\n"
        bill += "       VISIT US AGAIN ❤️\n"
        bill += "====================================\n"

        self.bill_text.delete(
            "1.0",
            tk.END
        )

        self.bill_text.insert(
            "1.0",
            bill
        )

    # ========================================================
    # COMPLETE PAYMENT
    # ========================================================

    def complete_payment(self):

        if not self.current_order_id:

            messagebox.showwarning(
                "BOC",
                "Please select an order first."
            )

            return

        try:

            received = float(
                self.amount_received.get()
                .strip()
                or 0
            )

        except ValueError:

            messagebox.showerror(
                "BOC",
                "Enter a valid amount received."
            )

            return

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT total
            FROM orders
            WHERE id = ?
        """, (
            self.current_order_id,
        ))

        result = cur.fetchone()

        if not result:

            conn.close()

            messagebox.showerror(
                "BOC",
                "Order not found."
            )

            return

        total = float(result[0])

        payment_method = self.payment_method.get()

        # For UPI/CARD, received amount can be equal automatically

        if payment_method in ["UPI", "CARD"]:

            received = total

        if received < total:

            conn.close()

            messagebox.showwarning(
                "BOC",
                f"Amount received is not enough.\n\n"
                f"Bill: ₹{total:.2f}\n"
                f"Received: ₹{received:.2f}"
            )

            return

        change = received - total

        cur.execute("""
            UPDATE orders
            SET
                payment_method = ?,
                amount_received = ?,
                change_amount = ?,
                status = 'COMPLETED'
            WHERE id = ?
        """, (
            payment_method,
            received,
            change,
            self.current_order_id
        ))

        conn.commit()

        conn.close()

        messagebox.showinfo(
            "PAYMENT COMPLETE",
            f"Payment successful!\n\n"
            f"Method: {payment_method}\n"
            f"Bill: ₹{total:.2f}\n"
            f"Received: ₹{received:.2f}\n"
            f"Change: ₹{change:.2f}"
        )

        self.current_order_id = None

        self.show_billing()

    # ========================================================
    # SALES
    # ========================================================

    def show_sales(self):

        self.clear_main()

        self.page_header(
            "Sales",
            "Restaurant sales overview"
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(total), 0)
            FROM orders
            WHERE status = 'COMPLETED'
        """)

        completed, sales = cur.fetchone()

        cur.execute("""
            SELECT
                COUNT(*)
            FROM orders
            WHERE status = 'PENDING'
        """)

        pending = cur.fetchone()[0]

        conn.close()

        cards = tk.Frame(
            self.main,
            bg=CREAM
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.dashboard_card(
            cards,
            "COMPLETED ORDERS",
            str(completed),
            GREEN
        )

        self.dashboard_card(
            cards,
            "PENDING ORDERS",
            str(pending),
            RED
        )

        self.dashboard_card(
            cards,
            "TOTAL SALES",
            f"₹{sales:,.2f}",
            BLUE
        )


# ============================================================
# START BOC
# ============================================================

if __name__ == "__main__":

    setup_database()

    root = tk.Tk()

    app = BOCApp(root)

    root.mainloop()
