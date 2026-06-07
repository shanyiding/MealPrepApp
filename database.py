import sqlite3

DB_NAME = "mealprep.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        unit TEXT NOT NULL,
        calories_per_unit REAL NOT NULL,
        protein_per_unit REAL NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER NOT NULL,
        quantity_left REAL NOT NULL,
        date_bought TEXT NOT NULL,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS meal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER NOT NULL,
        quantity_eaten REAL NOT NULL,
        calories REAL NOT NULL,
        protein REAL NOT NULL,
        eaten_date TEXT NOT NULL,
        meal_name TEXT DEFAULT 'Meal',
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
    )
    """)

    # Migration for old existing meal_logs table
    cur.execute("PRAGMA table_info(meal_logs)")
    columns = [col[1] for col in cur.fetchall()]

    if "meal_name" not in columns:
        try:
            cur.execute("ALTER TABLE meal_logs ADD COLUMN meal_name TEXT DEFAULT 'Meal'")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def seed_sample_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM ingredients")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    sample_items = [
        ("Eggs", "piece", 70, 6, 10, "2026-06-01"),
        ("Lean ground beef", "g", 1.7, 0.23, 900, "2026-06-04"),
        ("Greek yogurt", "g", 0.59, 0.10, 500, "2026-06-05"),
        ("Broccoli", "g", 0.35, 0.03, 300, "2026-06-06"),
    ]

    for name, unit, cal, protein, qty, bought_date in sample_items:
        cur.execute("""
        INSERT INTO ingredients (name, unit, calories_per_unit, protein_per_unit)
        VALUES (?, ?, ?, ?)
        """, (name, unit, cal, protein))

        ingredient_id = cur.lastrowid

        cur.execute("""
        INSERT INTO inventory_batches (ingredient_id, quantity_left, date_bought)
        VALUES (?, ?, ?)
        """, (ingredient_id, qty, bought_date))

    conn.commit()
    conn.close()


def add_grocery(name, unit, calories_per_unit, protein_per_unit, quantity, date_bought):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM ingredients WHERE LOWER(name) = LOWER(?)", (name,))
    row = cur.fetchone()

    if row:
        ingredient_id = row[0]
        cur.execute("""
        UPDATE ingredients
        SET unit = ?, calories_per_unit = ?, protein_per_unit = ?
        WHERE id = ?
        """, (unit, calories_per_unit, protein_per_unit, ingredient_id))
    else:
        cur.execute("""
        INSERT INTO ingredients (name, unit, calories_per_unit, protein_per_unit)
        VALUES (?, ?, ?, ?)
        """, (name, unit, calories_per_unit, protein_per_unit))
        ingredient_id = cur.lastrowid

    cur.execute("""
    INSERT INTO inventory_batches (ingredient_id, quantity_left, date_bought)
    VALUES (?, ?, ?)
    """, (ingredient_id, quantity, date_bought))

    conn.commit()
    conn.close()


def get_fridge_items():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        i.id,
        i.name,
        i.unit,
        i.calories_per_unit,
        i.protein_per_unit,
        SUM(b.quantity_left),
        GROUP_CONCAT(b.date_bought || ': ' || b.quantity_left || i.unit, ', ')
    FROM ingredients i
    JOIN inventory_batches b ON i.id = b.ingredient_id
    WHERE b.quantity_left > 0
    GROUP BY i.id
    ORDER BY i.name
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_fridge_totals():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        SUM(b.quantity_left * i.calories_per_unit),
        SUM(b.quantity_left * i.protein_per_unit),
        COUNT(DISTINCT i.id)
    FROM inventory_batches b
    JOIN ingredients i ON b.ingredient_id = i.id
    WHERE b.quantity_left > 0
    """)

    result = cur.fetchone()
    conn.close()

    return result[0] or 0, result[1] or 0, result[2] or 0


def deduct_inventory(ingredient_id, amount):
    conn = get_connection()
    cur = conn.cursor()

    remaining = amount

    cur.execute("""
    SELECT id, quantity_left
    FROM inventory_batches
    WHERE ingredient_id = ? AND quantity_left > 0
    ORDER BY date_bought ASC
    """, (ingredient_id,))

    batches = cur.fetchall()

    for batch_id, quantity_left in batches:
        if remaining <= 0:
            break

        if quantity_left <= remaining:
            cur.execute("""
            UPDATE inventory_batches
            SET quantity_left = 0
            WHERE id = ?
            """, (batch_id,))
            remaining -= quantity_left
        else:
            cur.execute("""
            UPDATE inventory_batches
            SET quantity_left = quantity_left - ?
            WHERE id = ?
            """, (remaining, batch_id))
            remaining = 0

    conn.commit()
    conn.close()

    return remaining == 0


def get_ingredient_by_name(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, unit, calories_per_unit, protein_per_unit
    FROM ingredients
    WHERE LOWER(name) = LOWER(?)
    """, (name.strip(),))

    row = cur.fetchone()
    conn.close()
    return row


def save_meal_log(meal_name, eaten_date, ingredients):
    conn = get_connection()
    cur = conn.cursor()

    saved = []

    for item in ingredients:
        name = item["name"].strip()
        amount_text = item["amount"].strip()

        if not name or not amount_text:
            continue

        try:
            amount = float(amount_text)
        except ValueError:
            continue

        ingredient = get_ingredient_by_name(name)

        if not ingredient:
            continue

        ingredient_id, food_name, unit, cal_per_unit, protein_per_unit = ingredient

        calories = amount * cal_per_unit
        protein = amount * protein_per_unit

        cur.execute("""
        INSERT INTO meal_logs (
            ingredient_id,
            quantity_eaten,
            calories,
            protein,
            eaten_date,
            meal_name
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ingredient_id,
            amount,
            calories,
            protein,
            eaten_date,
            meal_name,
        ))

        saved.append((ingredient_id, amount))

    conn.commit()
    conn.close()

    for ingredient_id, amount in saved:
        deduct_inventory(ingredient_id, amount)

    return len(saved)


def get_daily_totals(eaten_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        SUM(calories),
        SUM(protein)
    FROM meal_logs
    WHERE eaten_date = ?
    """, (eaten_date,))

    result = cur.fetchone()
    conn.close()

    return result[0] or 0, result[1] or 0