# Manufacturer Agent

An AI-powered, persona-aware manufacturing operations assistant for querying **inventory** and **procurement** data using natural language.

The system converts natural-language business questions into safe PostgreSQL queries, enforces persona-specific access rules, executes validated queries against a live database, generates business-friendly responses, and returns structured visualization data for the frontend.

The project is built using:

- Next.js
- FastAPI
- LangGraph
- OpenAI
- PostgreSQL
- LangSmith
- Recharts

---

# 1. Problem Statement

Manufacturing organizations typically store operational data across systems such as:

- Inventory Management
- Procurement
- Purchase Orders
- Vendors
- Warehouses
- Stock Transactions
- Goods Receipts

Business users often need answers to questions such as:

- Which items are currently out of stock?
- Which purchase orders are partially received?
- What items were received against a particular purchase order?
- Which vendor has the highest number of purchase orders?
- What is the purchase price history of an item?
- What is the current stock across warehouse locations?

Traditional dashboards require users to understand predefined reports and filters.

This project provides a conversational interface where users can ask these questions directly in natural language.

The system then:

1. Understands the user's intent.
2. Identifies the relevant business domain.
3. Verifies whether the selected persona has permission to access that domain.
4. Generates SQL dynamically.
5. Validates the generated SQL.
6. Executes the query against PostgreSQL.
7. Converts database results into a business-friendly answer.
8. Generates structured chart metadata when visualization is useful.

---

# 2. Key Features

## Natural Language to SQL

Users can ask business questions such as:

```text
Which purchase orders are partially received?
