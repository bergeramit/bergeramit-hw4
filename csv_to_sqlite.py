#!/usr/bin/env python3
# csv_to_sqlite.py
#
# Usage:
#   python3 csv_to_sqlite.py <database.db> <file.csv>
#
# Example:
#   python3 csv_to_sqlite.py data.db zip_county.csv
#   python3 csv_to_sqlite.py data.db county_health_rankings.csv
#
# Notes:
# - Assumes the CSV has a header row and that the header names are valid SQL identifiers
#   (letters, digits, underscore; not starting with a digit; no spaces/quotes).
# - Table name is the CSV filename (without extension), lightly sanitized.
# - All columns are created as TEXT.
# - If the table already exists, it will be dropped and recreated.

import csv
import os
import re
import sqlite3
import sys


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def table_name_from_path(csv_path: str) -> str:
    base = os.path.splitext(os.path.basename(csv_path))[0]
    # Sanitize conservatively: letters/digits/underscore; cannot start with a digit.
    name = re.sub(r"\W+", "_", base).strip("_")
    if not name:
        die(f"Could not derive a valid table name from: {csv_path}")
    if re.match(r"^\d", name):
        name = f"_{name}"
    return name


def is_valid_identifier(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s))


def main() -> None:
    if len(sys.argv) != 3:
        die("Usage: python3 csv_to_sqlite.py <database.db> <file.csv>")

    db_path, csv_path = sys.argv[1], sys.argv[2]
    if not os.path.exists(csv_path):
        die(f"CSV not found: {csv_path}")

    table = table_name_from_path(csv_path)

    # Open CSV. utf-8-sig trims BOM if present; newline='' is recommended for csv module.
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            die("CSV appears to have no header row.")

        columns = [c.strip() for c in reader.fieldnames]
        if any(not c for c in columns):
            die("CSV header contains an empty column name.")
        if not all(is_valid_identifier(c) for c in columns):
            die("CSV header contains invalid SQL identifiers (letters/digits/_; cannot start with a digit).")

        # Connect and import.
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()

            # Start a single transaction for speed and atomicity.
            cur.execute("BEGIN")

            # Drop existing table (if any) and recreate.
            cur.execute(f"DROP TABLE IF EXISTS {table}")
            cols_ddl = ", ".join(f"{c} TEXT" for c in columns)
            cur.execute(f"CREATE TABLE {table} ({cols_ddl})")

            # Prepare insert statement.
            placeholders = ", ".join("?" for _ in columns)
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

            # Stream rows in reasonable batches.
            batch = []
            BATCH_SIZE = 1000
            for row in reader:
                # Convert empty strings to NULL for cleanliness; keep others as-is.
                values = [ (row.get(col) if row.get(col) != "" else None) for col in columns ]
                batch.append(values)
                if len(batch) >= BATCH_SIZE:
                    cur.executemany(insert_sql, batch)
                    batch.clear()
            if batch:
                cur.executemany(insert_sql, batch)

            conn.commit()
        finally:
            conn.close()

    print(f"Imported '{csv_path}' into '{db_path}' as table '{table}'.")


if __name__ == "__main__":
    main()
