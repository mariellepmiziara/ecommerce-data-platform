import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"

def validate_database():
    print("🔎 VALIDAÇÃO DO BANCO DE DADOS")
    print("=" * 60)

    connection = sqlite3.connect(DATABASE_PATH)

    try: 
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
        """)

        tables = cursor.fetchall()
        print("\n📋 Tabelas encontradas:")

        for table in tables:
            print(f"   ✅ {table[0]}")


        print("\n📊 CONTAGEM DE REGISTROS")
        print("-" * 60)

        table_names = [
            "customers",
            "products",
            "sellers",
            "orders",
            "payments",
            "order_items"
        ]

        for table in table_names:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            print(f"{table:<15} {count:>10,}")



        print("\n🔍 DUPLICIDADES")
        print("-" * 60)

        validations = [

            (
                "customers.customer_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT customer_id)
                FROM customers
                """
            ),

            (
                "products.product_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT product_id)
                FROM products
                """
            ),

            (
                "sellers.seller_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT seller_id)
                FROM sellers
                """
            ),

            (
                "orders.order_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT order_id)
                FROM orders
                """
            ),

            (
                "orders_items.order_item_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT order_item_id)
                FROM order_items
                """
            ),

            (
                "payments.payment_id",
                """
                SELECT COUNT(*) - COUNT(DISTINCT payment_id)
                FROM payments
                """
            )
        ]


        for name, query in validations:
            cursor.execute(query)
            duplicates = cursor.fetchone()[0]

            if duplicates == 0:
                print(f"✅ {name}: sem duplicidades")
            else: print(f"❌ {name}: {duplicates} duplicidades")


        print("\n🔗 INTEGRIDADE REFERENCIAL")
        print("-" * 60)


        cursor.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
        """)

        invalid_customers = cursor.fetchone()[0]

        if invalid_customers == 0:
            print("✅ orders → customers")
        else:
            print(
                f"❌ orders → customers: "
                f"{invalid_customers} registros inválidos"   
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN sellers s
                ON o.seller_id = s.seller_id
            WHERE s.seller_id IS NULL;
        """)

        invalid_sellers = cursor.fetchone()[0]

        if invalid_sellers == 0: 
            print("✅ orders → sellers")
        else: 
            print(
                f"❌ orders → sellers: "
                f"{invalid_sellers} registros inválidos"
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """)

        invalid_orders = cursor.fetchone()[0]

        if invalid_orders == 0:
            print("✅ order_items → orders")
        else:
            print(
                f"❌ order_items → orders: "
                f"{invalid_orders} registros inválidos"
            )


        cursor.execute("""
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN products p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
        """)

        invalid_products = cursor.fetchone()[0]

        if invalid_products == 0:
            print("✅ order_items → products")
        else:
            print(
                f"❌ order_items → products: "
                f"{invalid_products} registros inválidos"
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM payments p
            LEFT JOIN orders o
                ON p.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """
        )

        invalid_payment_orders = cursor.fetchone()[0]
        if invalid_payment_orders == 0: 
            print("✅ payments → orders")
        else:
            print(
                f"❌ payments → orders: "
                f"{invalid_payment_orders} registros inválidos"
            )

        print("\n🕳️ VALORES NULOS")
        print("-" * 60)

        null_checks = {


            "customers.email": """
                SELECT COUNT(*)
                FROM customers
                WHERE email IS NULL
             """,

            "orders.customer_id": """
                SELECT COUNT(*)
                FROM orders
                WHERE customer_id IS NULL
            """,

            "order.total_amount": """
                SELECT COUNT(*)
                FROM orders
                WHERE total_amount IS NULL
            """,

            "order_items.quantity": """
                SELECT COUNT(*)
                FROM order_items
                WHERE quantity IS NULL
            """
        }

        for name, query in null_checks.items():
            cursor.execute(query)
            nulls = cursor.fetchone()[0]

            if nulls == 0:
                print(f"✅ {name}: sem nulos")
            else: 
                print(f"⚠️ {name}: {nulls} nulos")

        print("\n" + "=" * 60)
        print("🎉 VALIDAÇÃO CONCLUÍDA!")
        print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    validate_database()


    # 3 registros de customers sem e-mail — mantidos intencionalmente
    # o email foi normalizado, porém não descartou clientes sem email cadastrado