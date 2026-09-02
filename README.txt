# Ecommerce Data Platform

Pipeline de engenharia de dados (ETL) para dados de um e-commerce fictício, construído com **Python (pandas)** e **SQLite**. O projeto simula um cenário real: dados brutos "sujos" chegam em CSV, passam por extração, transformação/limpeza, carga em banco relacional e validação de integridade — incluindo a descoberta e documentação de um problema de qualidade de dados no dataset original.

## Índice

- [Arquitetura do pipeline](#arquitetura-do-pipeline)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Modelo de dados](#modelo-de-dados)
- [Como rodar](#como-rodar)
- [Etapas do pipeline](#etapas-do-pipeline)
- [Data Quality Findings](#data-quality-findings)
- [Decisões de negócio documentadas](#decisões-de-negócio-documentadas)
- [Próximos passos](#próximos-passos)

## Arquitetura do pipeline

```
CSV (raw) --> extract.py --> transform.py --> load.py --> SQLite (ecommerce.db) --> validate.py
```

- **extract.py**: lê os CSVs brutos, valida shape/tipos/nulos/duplicatas e reporta um relatório de qualidade inicial por dataset.
- **transform.py**: limpa e padroniza cada tabela (datas, textos, categorias, valores inválidos), remove duplicidades e, ao final, **aplica uma etapa de integridade referencial** entre tabelas pai (orders, products) e tabelas filhas (order_items, payments) — evitando registros órfãos no banco.
- **load.py**: carrega os CSVs já tratados no banco SQLite (`ecommerce.db`), uma tabela por vez.
- **validate.py**: roda checagens pós-carga no banco — contagem de registros, duplicidades, integridade referencial (chaves estrangeiras) e valores nulos em colunas críticas.

## Estrutura de pastas

```
ecommerce-data-platform/
├── data/
│   ├── raw/            # CSVs originais (não tratados)
│   ├── processed/      # CSVs limpos, gerados pelo transform.py
│   └── database/       # ecommerce.db (SQLite)
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── validate.py
│   └── check_db.py
└── README.md
```

## Modelo de dados

| Tabela         | Chave primária    | Relacionamentos                          |
|----------------|-------------------|-------------------------------------------|
| `customers`    | `customer_id`      | —                                          |
| `products`     | `product_id`       | —                                          |
| `sellers`      | `seller_id`        | —                                          |
| `orders`       | `order_id`         | `customer_id` → customers, `seller_id` → sellers |
| `order_items`  | `order_item_id`    | `order_id` → orders, `product_id` → products |
| `payments`     | `payment_id`       | `order_id` → orders                       |

## Como rodar

```bash
# 1. Extração (lê CSVs brutos e reporta qualidade inicial)
python src/extract.py

# 2. Transformação (limpeza + integridade referencial)
python src/transform.py

# 3. Carga no banco SQLite
python src/load.py

# 4. Validação pós-carga
python src/validate.py
```

## Etapas do pipeline

### Extract
- Leitura de CSV com `encoding="utf-8"` e tratamento de erros (`FileNotFoundError`, `EmptyDataError`, `ParserError`).
- Relatório de qualidade por dataset: total de registros, colunas, nulos, duplicados e tipos de dados.

### Transform
- Normalização de texto (`strip`, `lower` quando aplicável).
- Conversão e validação de datas (`pd.to_datetime` com `errors="coerce"`).
- Remoção de duplicidades completas e, quando aplicável, por chave primária.
- Validação de regras de negócio (ex: `price > 0`, `quantity > 0`, `discount` entre 0 e 1) com remoção de registros inválidos.
- Padronização de categorias inconsistentes (ex: variações de grafia em `category`).
- **Integridade referencial pós-transformação**: como `orders` e `products` podem descartar registros inválidos, `order_items` e `payments` são filtrados para remover qualquer linha que referencie um `order_id`/`product_id` que não sobreviveu à limpeza das tabelas pai.

### Load
- Carga de cada tabela processada no SQLite via `to_sql(..., if_exists="replace")`.
- Uso de transação (`commit`/`rollback`) para garantir atomicidade da carga.

### Validate
- Contagem de registros por tabela.
- Checagem de duplicidades por chave primária.
- Checagem de integridade referencial entre todas as tabelas relacionadas.
- Checagem de nulos em colunas críticas (ex: `customers.email`, `orders.total_amount`).

## Data Quality Findings

Durante a validação, dois problemas foram identificados, investigados e corrigidos/documentados:

### 1. Órfãos de integridade referencial (corrigido)
Antes da correção, `order_items` e `payments` continham registros apontando para `order_id`/`product_id` que haviam sido removidos durante a limpeza de `orders` e `products` (datas inválidas, valores negativos, etc.). Isso gerava falhas de integridade referencial no banco.

**Correção**: adicionada a função `enforce_referential_integrity()` em `transform.py`, que remove das tabelas filhas qualquer registro órfão antes da carga. Resultado: `order_items` passou de 24.997 para 24.734 registros, `payments` de 10.000 para 9.997 — todos os 100% órfãos identificados.

### 2. Inconsistência entre `orders.total_amount` e a soma de `order_items` (documentado, não "corrigido")
Uma análise via SQL (`vw_order_reconciliation`) mostrou que **100% dos pedidos** têm `orders.total_amount` divergente da soma de `order_items.net_amount` — nenhum caso isolado, mas um padrão sistemático em todo o dataset.

**Conclusão**: os dois campos foram gerados de forma independente neste dataset sintético (não há relação causal real entre eles). Isso não é algo para "consertar" silenciosamente — é uma decisão de negócio sobre qual fonte é confiável (ver seção abaixo).

## Decisões de negócio documentadas

- **`customers.email` com nulos**: mantidos intencionalmente. Nem todo cliente possui e-mail cadastrado; a ausência não invalida o registro.
- **`orders.total_amount` não é confiável**: para qualquer análise financeira, usar `order_total_amount_trusted`, calculado a partir da soma de `order_items.net_amount` (view `vw_orders_trusted`). O valor bruto `total_amount` é mantido no banco apenas como referência histórica do dado original, nunca usado em relatórios.

## Próximos passos

- [ ] Análise exploratória (receita mensal, categorias mais vendidas, ticket médio por forma de pagamento)
- [ ] Views/queries SQL adicionais para métricas de negócio
- [ ] Orquestração do pipeline com Airflow (DAG)
- [ ] Testes automatizados (pytest) para as funções de transformação
