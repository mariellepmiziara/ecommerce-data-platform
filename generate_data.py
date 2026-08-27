"""
generate_data.py

Gera dados fictícios de e-commerce para o projeto
E-commerce Data Platform.

Os dados são criados para simular uma fonte real de dados,
incluindo alguns problemas de qualidade que serão tratados
posteriormente pelo pipeline de ETL.

Arquivos gerados:
    - customers.csv
    - products.csv
    - orders.csv
    - order_items.csv
    - sellers.csv
    - payments.csv

Origem:
    Dados sintéticos gerados localmente para fins educacionais
    e de portfólio em Engenharia de Dados.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

SEED = 42

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

N_CUSTOMERS = 1_000
N_PRODUCTS = 200
N_ORDERS = 10_000
N_ORDER_ITEMS = 25_000
N_SELLERS = 50


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def create_directories() -> None:
    """Cria os diretórios necessários para armazenar os dados."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"📁 Diretório de dados: {RAW_DIR}")


def generate_customers() -> pd.DataFrame:
    """Gera dados fictícios de clientes."""

    states = [
        "MG",
        "SP",
        "RJ",
        "PR",
        "RS",
        "BA",
        "SC",
        "GO",
        "PE",
        "ES",
    ]

    cities = [
        "Uberaba",
        "São Paulo",
        "Rio de Janeiro",
        "Curitiba",
        "Porto Alegre",
        "Salvador",
        "Florianópolis",
        "Goiânia",
        "Recife",
        "Belo Horizonte",
    ]

    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, N_CUSTOMERS + 1),
            "name": [
                f"Cliente {i:04d}"
                for i in range(1, N_CUSTOMERS + 1)
            ],
            "email": [
                f"cliente{i:04d}@email.com"
                for i in range(1, N_CUSTOMERS + 1)
            ],
            "city": np.random.choice(
                cities,
                size=N_CUSTOMERS,
            ),
            "state": np.random.choice(
                states,
                size=N_CUSTOMERS,
            ),
            "created_at": pd.date_range(
                start="2024-01-01",
                periods=N_CUSTOMERS,
                freq="12h",
            ),
        }
    )

    # --------------------------------------------------------
    # Problemas de qualidade propositalmente inseridos
    # --------------------------------------------------------

    # Valores nulos
    customers.loc[[17, 234, 700], "email"] = None

    # Duplicação de registros
    duplicates = customers.iloc[[49, 399]].copy()

    customers = pd.concat(
        [customers, duplicates],
        ignore_index=True,
    )

    return customers


def generate_products() -> pd.DataFrame:
    """Gera dados fictícios de produtos."""

    categories = [
        "Eletrônicos",
        "Casa",
        "Esportes",
        "Livros",
        "Moda",
        "Beleza",
    ]

    products = pd.DataFrame(
        {
            "product_id": np.arange(1, N_PRODUCTS + 1),
            "product_name": [
                f"Produto {i:03d}"
                for i in range(1, N_PRODUCTS + 1)
            ],
            "category": np.random.choice(
                categories,
                size=N_PRODUCTS,
            ),
            "price": np.round(
                np.random.uniform(
                    15,
                    2500,
                    N_PRODUCTS,
                ),
                2,
            ),
            "cost": np.round(
                np.random.uniform(
                    8,
                    1700,
                    N_PRODUCTS,
                ),
                2,
            ),
            "stock": np.random.randint(
                0,
                500,
                N_PRODUCTS,
            ),
        }
    )

    # --------------------------------------------------------
    # Problemas de qualidade
    # --------------------------------------------------------

    # Preço negativo
    products.loc[8, "price"] = -50

    # Categoria inconsistente
    products.loc[35, "category"] = "eletronicos"

    # Estoque negativo
    products.loc[120, "stock"] = -10

    return products


def generate_sellers() -> pd.DataFrame:
    """Gera dados fictícios de vendedores."""

    states = [
        "MG",
        "SP",
        "RJ",
        "PR",
        "RS",
        "BA",
        "SC",
        "GO",
        "PE",
        "ES",
    ]

    cities = [
        "Uberaba",
        "São Paulo",
        "Rio de Janeiro",
        "Curitiba",
        "Porto Alegre",
        "Salvador",
        "Florianópolis",
        "Goiânia",
        "Recife",
        "Belo Horizonte",
    ]

    sellers = pd.DataFrame(
        {
            "seller_id": np.arange(1, N_SELLERS + 1),
            "seller_name": [
                f"Vendedor {i:02d}"
                for i in range(1, N_SELLERS + 1)
            ],
            "city": np.random.choice(
                cities,
                size=N_SELLERS,
            ),
            "state": np.random.choice(
                states,
                size=N_SELLERS,
            ),
        }
    )

    return sellers


def generate_orders() -> pd.DataFrame:
    """Gera dados fictícios de pedidos."""

    statuses = [
        "completed",
        "pending",
        "cancelled",
        "returned",
    ]

    payment_methods = [
        "credit_card",
        "debit_card",
        "pix",
        "boleto",
    ]

    order_dates = (
      pd.Timestamp("2025-01-01")
      + pd.to_timedelta(
            np.random.randint(
                0,
                365 * 24 * 60,
                N_ORDERS,
        ),
        unit="m",
    )
).strftime("%Y-%m-%d %H:%M:%S")

    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, N_ORDERS + 1),
            "customer_id": np.random.randint(
                1,
                N_CUSTOMERS + 1,
                N_ORDERS,
            ),
            "seller_id": np.random.randint(
                1,
                N_SELLERS + 1,
                N_ORDERS,
            ),
            "order_date": order_dates,
            "status": np.random.choice(
                statuses,
                size=N_ORDERS,
                p=[
                    0.72,
                    0.10,
                    0.10,
                    0.08,
                ],
            ),
            "payment_method": np.random.choice(
                payment_methods,
                size=N_ORDERS,
            ),
            "total_amount": np.round(
                np.random.uniform(
                    20,
                    3500,
                    N_ORDERS,
                ),
                2,
            ),
        }
    )

    # --------------------------------------------------------
    # Problemas de qualidade
    # --------------------------------------------------------

    # Valores negativos
    orders.loc[[123, 456], "total_amount"] = -100

    # Data inválida
    orders.loc[789, "order_date"] = "INVALID_DATE"

    # Duplicação de registro
    duplicate = orders.iloc[[100]].copy()

    orders = pd.concat(
        [orders, duplicate],
        ignore_index=True,
    )

    return orders


def generate_order_items() -> pd.DataFrame:
    """Gera os itens associados aos pedidos."""

    order_items = pd.DataFrame(
        {
            "order_item_id": np.arange(
                1,
                N_ORDER_ITEMS + 1,
            ),
            "order_id": np.random.randint(
                1,
                N_ORDERS + 1,
                N_ORDER_ITEMS,
            ),
            "product_id": np.random.randint(
                1,
                N_PRODUCTS + 1,
                N_ORDER_ITEMS,
            ),
            "quantity": np.random.randint(
                1,
                6,
                N_ORDER_ITEMS,
            ),
            "unit_price": np.round(
                np.random.uniform(
                    15,
                    2500,
                    N_ORDER_ITEMS,
                ),
                2,
            ),
            "discount": np.round(
                np.random.uniform(
                    0,
                    0.30,
                    N_ORDER_ITEMS,
                ),
                4,
            ),
        }
    )

    # --------------------------------------------------------
    # Problemas de qualidade
    # --------------------------------------------------------

    # Quantidade inválida
    order_items.loc[25, "quantity"] = 0

    # Desconto acima de 100%
    order_items.loc[125, "discount"] = 1.5

    # Preço negativo
    order_items.loc[500, "unit_price"] = -20

    return order_items


def generate_payments(
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Gera dados de pagamentos associados aos pedidos."""

    payment_dates = (
        pd.Timestamp("2025-01-01")
        + pd.to_timedelta(
            np.random.randint(
                0,
                365 * 24,
                N_ORDERS,
            ),
            unit="h",
        )
    )

    payments = pd.DataFrame(
        {
            "payment_id": np.arange(
                1,
                N_ORDERS + 1,
            ),
            "order_id": np.arange(
                1,
                N_ORDERS + 1,
            ),
            "payment_date": payment_dates,
            "amount": orders.iloc[
                :N_ORDERS
            ]["total_amount"].abs().values,
            "status": np.random.choice(
                [
                    "approved",
                    "pending",
                    "failed",
                ],
                size=N_ORDERS,
                p=[
                    0.88,
                    0.07,
                    0.05,
                ],
            ),
        }
    )

    # --------------------------------------------------------
    # Problemas de qualidade
    # --------------------------------------------------------

    # Valor nulo
    payments.loc[77, "amount"] = None

    # Registro duplicado
    duplicate = payments.iloc[[200]].copy()

    payments = pd.concat(
        [payments, duplicate],
        ignore_index=True,
    )

    return payments


# ============================================================
# SALVAMENTO
# ============================================================

def save_dataframe(
    df: pd.DataFrame,
    filename: str,
) -> None:
    """
    Salva um DataFrame como CSV utilizando UTF-8.

    Parâmetros
    ----------
    df : pd.DataFrame
        Dados que serão salvos.

    filename : str
        Nome do arquivo CSV.
    """

    output_path = RAW_DIR / filename

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"✅ {filename:<20} "
        f"{len(df):>7,} registros | "
        f"{len(df.columns):>2} colunas"
    )


# ============================================================
# RELATÓRIO
# ============================================================

def print_quality_summary(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Exibe um resumo dos datasets gerados."""

    print("\n" + "=" * 70)
    print("📊 RESUMO DOS DADOS GERADOS")
    print("=" * 70)

    total_records = 0

    for name, df in datasets.items():

        nulls = int(df.isnull().sum().sum())
        duplicates = int(df.duplicated().sum())

        total_records += len(df)

        print(
            f"\n{name}"
            f"\n  Registros: {len(df):,}"
            f"\n  Colunas: {len(df.columns)}"
            f"\n  Nulos: {nulls}"
            f"\n  Duplicados: {duplicates}"
        )

    print("\n" + "-" * 70)
    print(
        f"Total de registros gerados: "
        f"{total_records:,}"
    )
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Executa a geração completa dos dados."""

    print("=" * 70)
    print("🛒 E-COMMERCE DATA PLATFORM")
    print("   Geração de dados sintéticos")
    print("=" * 70)

    # Reprodutibilidade
    np.random.seed(SEED)

    # Criar diretórios
    create_directories()

    print("\n📦 Gerando datasets...\n")

    # --------------------------------------------------------
    # Geração
    # --------------------------------------------------------

    customers = generate_customers()

    products = generate_products()

    sellers = generate_sellers()

    orders = generate_orders()

    order_items = generate_order_items()

    payments = generate_payments(orders)

    datasets = {
        "customers.csv": customers,
        "products.csv": products,
        "orders.csv": orders,
        "order_items.csv": order_items,
        "sellers.csv": sellers,
        "payments.csv": payments,
    }

    # --------------------------------------------------------
    # Salvamento
    # --------------------------------------------------------

    for filename, df in datasets.items():
        save_dataframe(
            df,
            filename,
        )

    # --------------------------------------------------------
    # Relatório
    # --------------------------------------------------------

    print_quality_summary(datasets)

    print("\n🎉 Dados gerados com sucesso!")
    print(f"📁 Local: {RAW_DIR}")


if __name__ == "__main__":
    main()