from os import name

from extract import extract_data

from transform import(
    transform_customers,
    transform_products,
    transform_orders,
    transform_order_items,
    transform_payments,
    transform_sellers,
    save_processed_data,
)

from load import load_data

def main():
    print("\n" + "=" * 70)
    print("🚀 E-COMMERCE DATA PLATFORM")
    print("🚀 PIPELINE ETL")
    print("=" * 70)

    try:
        print("\n📥 INICIANDO ETAPA EXTRACT...")

        data = extract_data()


        print("\n🔄 INICIANDO ETAPA TRANSFORM...")

        customers_clean = transform_customers(data["customers"])
        save_processed_data(customers_clean,"customers_clean.csv")

        products_clean = transform_products(data["products"])
        save_processed_data(products_clean,"products_clean.csv")

        orders_clean = transform_orders(data["orders"])
        save_processed_data(orders_clean,"orders_clean.csv")

        order_items_clean = transform_order_items(data["order_items"])
        save_processed_data(order_items_clean, "order_items_clean.csv")

        payments_clean = transform_payments(data["payments"])
        save_processed_data(payments_clean, "payments_clean.csv")

        sellers_clean = transform_sellers(data["sellers"])
        save_processed_data(sellers_clean, "sellers_clean.csv")

        print("\n🎉 TRANSFORM CONCLUÍDO!") 





        print("\n💾 INICIANDO ETAPA LOAD...") 
        load_data()



        print("\n" + "=" * 70) 
        print("🎉 PIPELINE ETL CONCLUÍDO COM SUCESSO!") 
        print("=" * 70)

    except Exception as error:
        print("\n" + "=" * 70)
        print("❌ PIPELINE FALHOU")
        print("=" * 70)
        print(f"Erro: {error}")
        raise


if __name__ == "__main__":
    main()