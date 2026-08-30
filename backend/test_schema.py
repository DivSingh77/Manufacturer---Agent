from app.database.schema import build_schema_context
from app.security.access_control import (get_allowed_tables,
                                         validate_tables_for_persona)


def main():

    print("\n" + "=" * 80)
    print("PERSONA ACCESS TEST")
    print("=" * 80)

    for persona in ["warehouse", "procurement", "owner"]:

        print(f"\n{persona.upper()}")

        tables = get_allowed_tables(persona)

        for table in sorted(tables):
            print(f"  ✓ {table}")

    print("\n" + "=" * 80)
    print("ACCESS VALIDATION")
    print("=" * 80)

    allowed, unauthorized = validate_tables_for_persona(
        "warehouse",
        [
            "inv_items",
            "inv_current_stock",
        ],
    )

    print(
        "Warehouse inventory query:",
        allowed,
        unauthorized
    )

    allowed, unauthorized = validate_tables_for_persona(
        "warehouse",
        [
            "proc_purchase_orders",
        ],
    )

    print(
        "Warehouse procurement query:",
        allowed,
        unauthorized
    )

    print("\n" + "=" * 80)
    print("SCHEMA CONTEXT")
    print("=" * 80)

    context = build_schema_context()

    print(context)


if __name__ == "__main__":
    main()