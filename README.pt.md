# 🛒 Ecommerce Data Platform

![CI](https://github.com/mariellepmiziara/ecommerce-data-platform/actions/workflows/ci.yml/badge.svg?branch=main)

**Pipeline completo de Engenharia de Dados para uma plataforma de e-commerce fictícia, com foco em ETL, qualidade de dados, modelagem relacional, orquestração, testes automatizados e CI.**

Desenvolvido com **Python, Pandas, SQLite, SQL, Apache Airflow, Docker, Pytest e GitHub Actions**.

---

## 📌 Sobre o Projeto

Este projeto simula um cenário real de Engenharia de Dados, no qual dados brutos e inconsistentes de um e-commerce passam por um pipeline ETL completo e reproduzível.

O pipeline transforma dados em formato CSV por meio das seguintes etapas:

**Extração → Transformação → Carga → Validação → Testes Automatizados**

O projeto não se limita à movimentação dos dados. Ele também contempla:

* Avaliação da qualidade dos dados
* Limpeza e padronização
* Validação de regras de negócio
* Integridade referencial
* Transações no banco de dados
* Validação após a carga
* Testes automatizados
* Orquestração do pipeline
* Integração Contínua
* Documentação de problemas de qualidade
* Registro das decisões de negócio e engenharia

> **Observação:** os dados utilizados são sintéticos e foram criados especificamente para este projeto de portfólio. Eles contêm propositalmente problemas de qualidade para demonstrar como um pipeline de Engenharia de Dados pode identificá-los e tratá-los.

---

## 🏗️ Arquitetura

```mermaid
flowchart LR
    A[Arquivos CSV Brutos] --> B[Extração]
    B --> C[Transformação]
    C --> D[Carga]
    D --> E[(Banco SQLite)]
    E --> F[Validação]
    F --> G[Pytest]

    H[Apache Airflow] --> B
    H --> C
    H --> D
    H --> F

    I[GitHub Actions] --> B
    I --> G
```

### Fluxo do Pipeline

```text
Dados Brutos
     │
     ▼
  Extração
     │
     ├── Validação dos arquivos
     ├── Verificação do esquema
     ├── Análise de valores nulos
     └── Detecção de duplicidades
     │
     ▼
Transformação
     │
     ├── Limpeza
     ├── Padronização
     ├── Regras de negócio
     └── Integridade referencial
     │
     ▼
    Carga
     │
     ├── SQLite
     ├── Transações
     └── Rollback em caso de falha
     │
     ▼
  Validação
     │
     ├── Contagem de registros
     ├── Chaves primárias
     ├── Chaves estrangeiras
     └── Colunas críticas
     │
     ▼
Testes Automatizados
     │
     ▼
GitHub Actions — CI
```

---

## 🛠️ Tecnologias

| Tecnologia                  | Utilização                         |
| --------------------------- | ---------------------------------- |
| **Python**                  | Desenvolvimento do pipeline ETL    |
| **Pandas**                  | Extração e transformação dos dados |
| **SQL**                     | Modelagem, validação e análise     |
| **SQLite**                  | Banco de dados relacional          |
| **Apache Airflow**          | Orquestração do pipeline           |
| **Docker / Docker Compose** | Ambiente local do Airflow          |
| **Pytest**                  | Testes automatizados               |
| **Git / GitHub**            | Controle de versão                 |
| **GitHub Actions**          | Integração Contínua (CI)           |

---

## 📂 Estrutura do Projeto

```text
ecommerce-data-platform/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   ├── order_items.csv
│   │   ├── sellers.csv
│   │   └── payments.csv
│   │
│   ├── processed/
│   └── database/
│       └── ecommerce.db
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── validate.py
│   ├── check_db.py
│   └── main.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_validate.py
│   ├── test_transform.py
│   └── test_database.py
│
├── dags/
│   └── ecommerce_pipeline.py
│
├── requirements.txt
├── schema.sql
├── docker-compose.yml
├── .gitignore
└── README.md
```

### Principais Componentes

| Arquivo                      | Responsabilidade                          |
| ---------------------------- | ----------------------------------------- |
| `src/extract.py`             | Leitura e perfil inicial dos dados        |
| `src/transform.py`           | Limpeza, padronização e regras de negócio |
| `src/load.py`                | Carga dos dados no SQLite                 |
| `src/validate.py`            | Validação da qualidade após a carga       |
| `src/main.py`                | Orquestração do pipeline completo         |
| `dags/ecommerce_pipeline.py` | Orquestração com Airflow                  |
| `schema.sql`                 | Definição do esquema do banco             |
| `tests/`                     | Suíte de testes automatizados             |
| `.github/workflows/ci.yml`   | Pipeline de Integração Contínua           |

---

## 🗄️ Modelo de Dados

O projeto possui seis tabelas relacionais:

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : realiza
    SELLERS ||--o{ ORDERS : gerencia
    ORDERS ||--o{ ORDER_ITEMS : possui
    PRODUCTS ||--o{ ORDER_ITEMS : contem
    ORDERS ||--o{ PAYMENTS : possui

    CUSTOMERS {
        int customer_id PK
        string name
        string email
    }

    PRODUCTS {
        int product_id PK
        string category
        float price
        int stock
    }

    SELLERS {
        int seller_id PK
        string name
        string state
    }

    ORDERS {
        int order_id PK
        int customer_id FK
        int seller_id FK
        date order_date
        string status
        float total_amount
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price
        float discount
        float net_amount
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK
        string payment_method
    }
```

| Tabela        | Chave Primária  | Relacionamentos                                  |
| ------------- | --------------- | ------------------------------------------------ |
| `customers`   | `customer_id`   | —                                                |
| `products`    | `product_id`    | —                                                |
| `sellers`     | `seller_id`     | —                                                |
| `orders`      | `order_id`      | `customer_id → customers`, `seller_id → sellers` |
| `order_items` | `order_item_id` | `order_id → orders`, `product_id → products`     |
| `payments`    | `payment_id`    | `order_id → orders`                              |

---

# 🚀 Como Executar

## 1. Clone o repositório

```bash
git clone https://github.com/mariellepmiziara/ecommerce-data-platform.git
cd ecommerce-data-platform
```

## 2. Crie um ambiente virtual

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 4. Execute o pipeline completo

A partir da raiz do projeto:

```bash
python -m src.main
```

O pipeline executa:

```text
Extração
    ↓
Transformação
    ↓
Carga
    ↓
Validação
```

Uma execução bem-sucedida termina com:

```text
🎉 PIPELINE EXECUTADO COM SUCESSO
```

---

# 🧪 Testes Automatizados

Para executar toda a suíte de testes:

```bash
pytest tests/ -v --tb=short
```

Os testes abrangem:

* Extração
* Transformação
* Carga
* Validação
* Integridade do banco de dados

---

# 🔄 Etapas do Pipeline

## 1. Extração

O `extract.py` realiza a leitura dos arquivos CSV e uma avaliação inicial da qualidade dos dados.

### Validações realizadas

* Existência dos arquivos
* Leitura dos CSVs
* Encoding
* Arquivos vazios
* Erros de parsing
* Quantidade de linhas
* Quantidade de colunas
* Valores nulos
* Registros duplicados
* Tipos de dados

São tratados erros como:

```text
FileNotFoundError
EmptyDataError
ParserError
```

Cada conjunto de dados recebe uma avaliação inicial antes da transformação.

---

## 2. Transformação

O `transform.py` executa a limpeza, padronização e aplicação das regras de negócio.

### Limpeza

* Normalização de textos
* Remoção de espaços desnecessários
* Padronização de categorias
* Conversão de datas
* Remoção de duplicidades

### Regras de negócio

Exemplos:

```text
price > 0
quantity > 0
0 <= discount <= 1
```

Registros que violam essas regras são removidos antes da carga.

### Integridade Referencial

As tabelas principais são tratadas antes das tabelas dependentes.

Por exemplo:

```text
orders
  ├── order_items
  └── payments

products
  └── order_items
```

Se um pedido ou produto for removido durante a limpeza, os registros dependentes que apontam para ele também são removidos.

Isso evita registros órfãos no banco de dados.

---

## 3. Carga

O `load.py` carrega os dados tratados no SQLite.

A estratégia atual é de **carga completa (full refresh)**.

A cada execução:

1. O banco é recriado.
2. O esquema é recriado.
3. Os dados tratados são carregados.
4. A transação é confirmada.

O processo utiliza transações:

```text
BEGIN
   ↓
Carga das tabelas
   ↓
COMMIT
```

Em caso de erro:

```text
ROLLBACK
```

Isso evita que o banco permaneça parcialmente carregado.

---

## 4. Validação

O `validate.py` realiza validações diretamente no banco após a carga.

São verificadas:

* Quantidade de registros
* Tabelas vazias
* Duplicidade de chaves primárias
* Integridade de chaves estrangeiras
* Valores nulos em colunas críticas
* Consistência dos relacionamentos

Quando uma regra de validação falha, o pipeline gera:

```python
DataValidationError
```

Dessa forma, tanto a execução local quanto o CI identificam a falha em vez de simplesmente continuar com dados inválidos.

---

# 🔍 Qualidade dos Dados

A qualidade dos dados é tratada como parte central do pipeline.

O projeto segue o fluxo:

```text
Perfil dos dados
      ↓
Limpeza
      ↓
Validação
      ↓
Carga
      ↓
Nova validação
```

O objetivo é impedir que problemas de qualidade sejam silenciosamente propagados para o banco de dados.

---

# ⚠️ Problemas de Qualidade Identificados

Durante o desenvolvimento, dois problemas relevantes foram identificados.

## 1. Registros órfãos — Corrigido

Antes da correção, `order_items` e `payments` possuíam registros que referenciavam pedidos ou produtos removidos durante o processo de limpeza.

Foi implementada a função:

```python
enforce_referential_integrity()
```

Resultado:

```text
order_items: 24.997 → 24.734
payments:    10.000 → 9.997
```

Os registros órfãos identificados foram removidos antes da carga.

---

## 2. Divergência entre `orders.total_amount` e `order_items.net_amount`

Uma análise de reconciliação mostrou que:

```text
orders.total_amount
```

não corresponde à soma de:

```text
SUM(order_items.net_amount)
```

A divergência ocorre em 100% dos pedidos.

A análise agregada apresentou aproximadamente:

```text
orders.total_amount     → $16,0M
order_items.net_amount  → $78,9M
```

A investigação indicou que os campos foram gerados de forma independente no conjunto de dados sintético.

Como a diferença é sistemática, e não um problema isolado de alguns registros, ela foi **documentada em vez de corrigida artificialmente**.

> **Princípio aplicado:** problemas na fonte devem ser identificados, investigados e documentados, e não simplesmente ocultados durante o ETL.

---

# 📊 Análise Exploratória

Foi realizada uma análise exploratória utilizando as fontes de receita consideradas confiáveis.

Como os dados são sintéticos, os resultados não devem ser interpretados como comportamento real de um e-commerce.

### Receita ao longo do tempo

A receita mensal apresenta comportamento relativamente estável:

```text
≈ $1,3M – $1,6M
```

Não foi identificada sazonalidade relevante.

### Receita por categoria

Aproximadamente:

```text
Livros       → $16,2M
Beleza       → $15,7M
Esportes     → $9,5M
```

A variação relativamente pequena entre as categorias é atípica para um catálogo real.

### Métodos de pagamento

Os quatro métodos apresentam volumes de pedidos e valores médios bastante semelhantes.

Nenhum método apresenta comportamento significativamente diferente.

### Status dos pedidos

```text
Concluído   → 73,3%
Cancelado   →  9,62%
Pendente    →  9,57%
Devolvido   →  7,5%
```

O valor médio dos pedidos apresenta pouca variação entre os diferentes status.

### Vendedores

O vendedor com maior faturamento gerou aproximadamente:

```text
$2,03M
```

em 236 pedidos.

Os principais vendedores apresentam desempenho relativamente semelhante.

### Distribuição geográfica

Os clientes apresentam uma distribuição relativamente equilibrada entre os estados brasileiros, sem uma concentração geográfica muito forte.

---

# 💼 Decisões de Negócio Documentadas

## `customers.email` pode ser nulo

A ausência de e-mail não invalida o cadastro de um cliente.

Portanto:

```text
customers.email → pode ser NULL
```

Essa regra é explicitamente considerada pelo `validate.py`.

---

## `orders.total_amount` não é utilizado como fonte confiável de receita

Devido ao problema de reconciliação identificado, as análises financeiras utilizam:

```text
order_items.net_amount
```

por meio da visão analítica:

```text
vw_orders_trusted
```

O campo original `orders.total_amount` é preservado como referência histórica da fonte, mas não é utilizado como métrica de receita confiável.

---

# 🔁 Estratégia de Carga: Full Refresh vs. Incremental

A implementação atual utiliza **full refresh**.

A cada execução, o banco SQLite é recriado e todo o conjunto de dados tratado é carregado novamente.

### Por que utilizar full refresh?

Essa escolha é intencional porque:

* Os dados são sintéticos.
* A fonte é estática.
* O volume é relativamente pequeno.
* Não existe uma fonte de produção enviando pedidos continuamente.
* A implementação é simples.
* O processo é naturalmente idempotente.

O dataset possui aproximadamente:

```text
25 mil order_items
```

no máximo, tornando o full refresh adequado para o projeto.

### Como seria em produção?

Para um ambiente processando milhões ou bilhões de registros, uma estratégia incremental seria mais adequada.

Uma possível implementação utilizaria:

1. Uma coluna de controle, como `order_date` ou `updated_at`.
2. Uma tabela de controle de processamento.
3. Extração incremental.
4. Estratégia de upsert.
5. Atualização transacional do watermark.

Por exemplo:

```sql
INSERT ... ON CONFLICT DO UPDATE
```

poderia ser utilizado para atualizar registros existentes sem gerar duplicidades.

A carga incremental não foi implementada porque a fonte sintética atual não justifica essa complexidade.

---

# ☁️ Orquestração com Airflow

O projeto possui um DAG do Apache Airflow:

```text
dags/ecommerce_pipeline.py
```

O DAG organiza as etapas:

```text
Extração
    ↓
Transformação
    ↓
Carga
    ↓
Validação
```

A etapa de validação foi projetada para fazer o DAG falhar quando os requisitos de qualidade dos dados não forem atendidos.

O ambiente local do Airflow pode ser iniciado com:

```bash
docker compose up
```

---

# 🔄 Integração Contínua — GitHub Actions

O projeto utiliza GitHub Actions para validar automaticamente alterações no código.

O workflow executa:

```text
Checkout
   ↓
Python 3.12
   ↓
Instalação das dependências
   ↓
Execução do pipeline ETL
   ↓
Execução dos testes
```

O workflow é executado em:

* Push para `main`
* Push para `master`
* Pull Requests direcionados para `main`
* Pull Requests direcionados para `master`

### Status atual

**CI: passando ✅**

![CI](https://github.com/mariellepmiziara/ecommerce-data-platform/actions/workflows/ci.yml/badge.svg?branch=main)

Em caso de falha, o workflow também tenta disponibilizar o banco SQLite gerado como artefato para facilitar a investigação.

---

# 📈 Resultado Atual do Pipeline

A execução atual do pipeline produz aproximadamente:

| Dataset         | Registros |
| --------------- | --------: |
| Clientes        |     1.000 |
| Produtos        |       198 |
| Vendedores      |        50 |
| Pedidos         |     9.997 |
| Itens de pedido |    24.734 |
| Pagamentos      |     9.996 |

Esses valores representam o resultado tratado e validado do conjunto de dados sintético atual.

---

# 🎯 Práticas de Engenharia Demonstradas

Este projeto demonstra a aplicação prática de:

* Arquitetura de pipelines ETL
* Python
* Pandas
* SQL
* Modelagem de dados relacionais
* Limpeza de dados
* Perfilamento de dados
* Qualidade de dados
* Integridade referencial
* Validação de regras de negócio
* Tratamento de erros
* Gerenciamento de transações
* Carga full refresh
* Conceitos de carga incremental
* Testes automatizados
* Pytest
* Apache Airflow
* Docker
* Git
* GitHub
* GitHub Actions
* Integração Contínua
* Reprodutibilidade
* Documentação técnica
* Tomada de decisão baseada em dados

---

# 🚧 Próximas Evoluções

O pipeline ETL, as validações, os testes automatizados, a orquestração com Airflow e o CI já estão implementados.

Possíveis evoluções futuras:

* [ ] Mover credenciais do Docker/banco para `.env`
* [ ] Expandir os testes de qualidade de dados
* [ ] Adicionar notificações de falha no Airflow
* [ ] Implementar uma versão com carga incremental
* [ ] Criar novas views SQL analíticas
* [ ] Adicionar uma camada de consumo com BI ou Streamlit
* [ ] Explorar uma arquitetura baseada em cloud
* [ ] Documentar linhagem dos dados
* [ ] Executar o CI também em ambiente containerizado

---

# 👩‍💻 Autora

**Marielle Miziara**

**Engenharia de Dados | Análise de Dados | BI**

Profissional focada na construção de pipelines de dados confiáveis, transformação de dados brutos em informações de qualidade e aplicação de boas práticas de Engenharia de Dados em projetos reais e de portfólio.

---

## ⭐ Objetivo do Projeto

Este projeto foi desenvolvido como demonstração prática de fundamentos de **Engenharia de Dados aplicados de ponta a ponta**.

O objetivo não é apenas fazer um ETL funcionar, mas demonstrar como construir um pipeline que:

```text
Dados Brutos
     ↓
Qualidade dos Dados
     ↓
Transformação
     ↓
Integridade
     ↓
Armazenamento Confiável
     ↓
Validação
     ↓
Testes Automatizados
     ↓
Orquestração
     ↓
Integração Contínua
```

**Dados confiáveis começam com uma engenharia confiável.**
