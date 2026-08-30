from app.database.connection import get_connection


def inspect_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # ---------------------------------------------------------
        # 1. TABLES
        # ---------------------------------------------------------
        print("\n" + "=" * 80)
        print("TABLES")
        print("=" * 80)

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        for (table_name,) in tables:
            print(table_name)

        print(f"\nTotal tables: {len(tables)}")

        # ---------------------------------------------------------
        # 2. COLUMNS
        # ---------------------------------------------------------
        print("\n" + "=" * 80)
        print("COLUMNS")
        print("=" * 80)

        cursor.execute("""
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)

        columns = cursor.fetchall()

        current_table = None

        for table_name, column_name, data_type, nullable in columns:

            if table_name != current_table:
                print(f"\n[{table_name}]")
                current_table = table_name

            print(
                f"  {column_name:<35} "
                f"{data_type:<20} "
                f"nullable={nullable}"
            )

        # ---------------------------------------------------------
        # 3. FOREIGN KEYS
        # ---------------------------------------------------------
        print("\n" + "=" * 80)
        print("FOREIGN KEYS")
        print("=" * 80)

        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """)

        foreign_keys = cursor.fetchall()

        for (
            table_name,
            column_name,
            foreign_table,
            foreign_column,
        ) in foreign_keys:

            print(
                f"{table_name}.{column_name}"
                f" -> "
                f"{foreign_table}.{foreign_column}"
            )

        print(f"\nTotal foreign keys: {len(foreign_keys)}")

        # ---------------------------------------------------------
        # 4. ROW COUNTS
        # ---------------------------------------------------------
        print("\n" + "=" * 80)
        print("ROW COUNTS")
        print("=" * 80)

        for (table_name,) in tables:

            # Table names come directly from information_schema,
            # but identifiers cannot be passed as SQL parameters.
            query = f'SELECT COUNT(*) FROM "{table_name}"'

            cursor.execute(query)

            count = cursor.fetchone()[0]

            print(f"{table_name:<45} {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    inspect_database()