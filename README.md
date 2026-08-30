# Manufacturer Agent

A persona-aware AI assistant for manufacturing operations that answers natural-language questions over live **inventory** and **procurement** data.

The system is designed around three different business personas:

- Warehouse
- Procurement
- Business Owner

Each persona has different access boundaries and asks fundamentally different types of questions.

The application uses:

- Next.js
- FastAPI
- LangGraph
- OpenAI
- PostgreSQL
- LangSmith
- SQLGlot
- Recharts

---

# 1. Problem Statement

A manufacturing company typically has two closely related but operationally separate systems:

1. Procurement
2. Inventory

Procurement is responsible for ordering material from vendors.

Inventory is responsible for physically receiving, storing, transferring, and issuing that material.

These two teams may deal with the same item, but they care about completely different business questions.

For example:

```text
Item: Screws

A warehouse user may ask:

How many screws are physically available right now?

A procurement user may ask:

Has the purchase order for screws been fully received?

The business owner may ask:

How many screws did we order, how many arrived,
and how many are currently left in stock?

The goal of this project is to provide a natural-language AI assistant that understands:

what the user is asking,
which business domain the question belongs to,
who the user is,
which data that persona is allowed to access,
and how to answer accurately using the actual database.

The system must never invent operational numbers.

PostgreSQL remains the source of truth.

2. Core Requirements

The application supports:

Natural-language business questions
Inventory analytics
Procurement analytics
Persona-based access control
Cross-domain analysis for business owners
Dynamic SQL generation
Deterministic SQL validation
Safe database execution
Human-readable answers
Charts when visualization is useful
LangSmith observability
Automated evaluation
3. Personas
Warehouse

Warehouse users are concerned with physical stock and inventory movement.

Typical questions:

Which items currently have zero stock?
Show current stock by warehouse location.
Show recent inventory transactions.

Warehouse users can access inventory data such as:

Items
Categories
Locations
Current stock
Inventory transactions
Warehouse issue targets

Warehouse users are not allowed to access procurement data.

For example:

Show me all purchase orders.

is rejected before SQL generation.

Procurement

Procurement users are concerned with:

Purchase orders
Vendors
Ordered quantities
Received quantities
Purchase prices
PO status
Receipts
Payment information

Example:

Which purchase orders are partially received?
Show details of PO-2026-0029 including vendor and items.

Procurement users may use:

inv_items
inv_locations

as lookup/reference tables so that results contain human-readable item and location names.

However, procurement users are not allowed to perform general inventory analysis.

For example:

What is the current stock of all items?

is rejected.

Business Owner

The business owner can access both inventory and procurement domains.

The owner can also ask genuine cross-domain questions such as:

For PO-2026-0029, compare what was ordered and received
with the current stock of those items.

This requires combining procurement and inventory information.

4. Architecture
                       User + Persona
                             |
                             v
                       Next.js UI
                             |
                             v
                       FastAPI API
                             |
                             v
                        LangGraph
                             |
                             v
                  Intent / Domain Classifier
                             |
                             v
                      Access Guard
                             |
                +------------+------------+
                |                         |
              DENIED                   ALLOWED
                |                         |
                v                         v
          Safe Response             SQL Generator
                                          |
                                          v
                               Persona-Scoped Schema
                                          |
                                          v
                                   SQL Generation
                                          |
                                          v
                                SQLGlot Validation
                                          |
                               +----------+----------+
                               |                     |
                            INVALID                VALID
                               |                     |
                          Retry if possible           v
                                               PostgreSQL
                                                    |
                                      +-------------+-------------+
                                      |                           |
                                    ERROR                       SUCCESS
                                      |                           |
                                 Retry if possible                 v
                                      |                      Visualization
                                      |                           |
                                      +------> Safe Failure       v
                                                             Response
                                                                 |
                                                                 v
                                                            Next.js UI
5. Technology Stack
Frontend
Next.js
TypeScript
Tailwind CSS
Recharts

The frontend provides:

Persona selection
Natural-language question input
Suggested demo questions
Agent responses
Access-denied feedback
Generated SQL inspection
Result tables
Line and bar charts
Backend
Python
FastAPI
LangGraph
OpenAI API
SQLGlot

FastAPI exposes:

POST /api/chat

Example:

{
  "question": "Which purchase orders are partially received?",
  "persona": "procurement"
}
Database
PostgreSQL

The application queries a live manufacturing dataset containing procurement and inventory tables.

Observability

LangSmith is used for:

LangGraph tracing
Node-level execution analysis
Prompt inspection
SQL-generation debugging
Retry inspection
Latency analysis
Access-control verification
Error analysis
6. LangGraph Workflow

The current graph contains these major nodes:

classify
    |
access_guard
    |
access_router
    |
generate_sql
    |
validate_sql
    |
validation_router
    |
execute_sql
    |
execution_router
    |
visualize
    |
respond

Additional nodes:

increment_retry
query_failure

These are used to handle validation/runtime failures safely.

7. Security Model

The project uses multiple independent layers of protection.

Layer 1 — Domain Authorization

The classifier determines:

inventory
procurement
cross_domain

The access guard then checks whether the persona is allowed to access that domain.

Rules:

Warehouse
    inventory       allowed
    procurement     denied
    cross_domain    denied

Procurement
    procurement     allowed
    inventory       denied
    cross_domain    denied

Owner
    inventory       allowed
    procurement     allowed
    cross_domain    allowed
Layer 2 — Persona-Scoped Schema

Restricted personas are not given the entire database schema.

For example:

Warehouse SQL generation receives only inventory-related schema.

Procurement receives procurement tables plus allowed lookup tables.

Owner receives the full relevant schema.

This reduces the chance of the LLM referencing unauthorized data.

Layer 3 — SQLGlot AST Validation

Generated SQL is parsed using SQLGlot.

This allows the validator to inspect every physical table referenced in the SQL AST.

It catches:

Standard joins
Comma-style joins
Nested subqueries
CTEs
Unauthorized tables

Example attack:

SELECT *
FROM inv_items i, proc_purchase_orders p
WHERE i.id = p.vendor_id;

For a warehouse user this is rejected because both physical tables are detected.

Layer 4 — Read-Only Query Enforcement

Only read-only SELECT queries are accepted.

Operations such as:

INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE

are rejected.

Layer 5 — Database Execution Protection

Database execution uses additional safeguards:

Read-only session
Statement timeout
Bounded result rows
Rollback after reads

For production, the database account should additionally have actual SELECT-only PostgreSQL permissions.

8. Reliability / Retry Handling

The agent can recover from two types of SQL failure.

Validation Failure

Example:

LLM generates SQL
        |
        v
SQL validator rejects it
        |
        v
Retry count checked
        |
        +---- retry available ---> regenerate SQL
        |
        +---- exhausted ----------> safe failure response
Runtime Database Failure

Sometimes SQL can pass validation but still fail during execution.

Examples:

Invalid column
Type mismatch
Incorrect database expression

Runtime errors are captured internally.

The raw PostgreSQL error is not returned to the frontend.

Instead:

Execution error
      |
      v
Retry available?
   /       \
 yes       no
  |         |
  v         v
Repair SQL  Safe failure

The previous SQL and internal error can be provided back to the SQL generator during repair.

9. Safe Failure Behavior

When the system cannot safely answer after retries, it returns a generic message such as:

I couldn't safely answer this question from the available
database schema after multiple attempts.
Please try rephrasing the question.

Internal database details such as:

Table names
Internal columns
Driver errors
Stack traces

are not exposed to the frontend.

10. Database Domains

The database contains 17 tables.

Inventory
inv_items
inv_categories
inv_sub_categories
inv_sub_categories_2
inv_locations
inv_current_stock
inv_issued_to_targets
inv_transactions
inv_field_definitions

inv_field_definitions is not actively used by the MVP.

Procurement
proc_vendors
proc_purchase_orders
proc_po_lines
proc_po_payment_tranches
proc_po_receipts
proc_po_line_regularisations
Unexpected Receipts
proc_unexpected_receipt_headers
proc_unexpected_receipts
11. Important Relationships
Purchase Order → Vendor
proc_purchase_orders.vendor_id
    ->
proc_vendors.id
Purchase Order → Lines
proc_purchase_orders.id
    ->
proc_po_lines.po_id
PO Line → Item
proc_po_lines.inv_item_id
    ->
inv_items.id
PO Line → Receipt
proc_po_lines.id
    ->
proc_po_receipts.po_line_id

This means the correct receipt chain is:

Purchase Order
      |
      v
PO Lines
      |
      v
PO Receipts
Receipt → Location
proc_po_receipts.location_id
    ->
inv_locations.id
Current Stock
inv_current_stock.item_id
    ->
inv_items.id

inv_current_stock.location_id
    ->
inv_locations.id
Inventory Transactions
inv_transactions.item_id
    ->
inv_items.id

inv_transactions.location_id
    ->
inv_locations.id

Transaction types include:

inbound
outbound
transfer_in
transfer_out
12. Visualization Support

The visualization layer is based on both:

intent
returned data shape

This makes chart generation more general than one hardcoded query.

Supported examples include:

Price History
date + unit_price

renders:

Line chart
Stock by Location
location_name + total_quantity

renders:

Bar chart
Inventory Movement
transaction_date + movement_quantity

renders:

Line chart
Vendor Comparison
vendor_name + purchase_order_count

renders:

Bar chart
Vendor Spend
vendor_name + total_spend

renders:

Bar chart
Generic Time Series

When the result contains a date-like field and a numeric metric, the system can fall back to a trend line chart.

13. Example Questions
Warehouse
Which items currently have zero stock?
Show me the current stock by warehouse location.
Show me recent inventory transactions.
Procurement
Which purchase orders are partially received?
Show details of PO-2026-0029 including vendor and items.
Show receipts for PO-2026-0029.
Which vendors have the most purchase orders?
Show the purchase price history of
MS C Channel – 125×65×5mm.
Owner
What is the current stock of all items?
Which vendors have the most purchase orders?
For PO-2026-0029, compare what was ordered and received
with the current stock of those items.
14. Automated Evaluation

The primary evaluation suite is:

python test_evaluation.py

Current result:

Passed: 9
Failed: 0
Total:  9
Score:  100.0%

This means all 9 current MVP scenarios pass.

It does not mean that all possible natural-language questions have 100% accuracy.

15. Nine Critical Evaluation Scenarios
#	Scenario	Expected behavior
1	Warehouse inventory access	Allowed
2	Warehouse procurement access	Denied
3	Procurement PO access	Allowed
4	Procurement inventory analysis	Denied
5	Owner inventory access	Allowed
6	Multi-table PO details	Correct joins
7	PO receipts	Correct PO → line → receipt relationship
8	Price history	SQL + line-chart visualization
9	Owner cross-domain PO vs stock	Procurement + inventory combined
16. Security Hardening Tests

Run:

python test_security_hardening.py

Covered scenarios include:

Comma-style join bypass attempt
Explicit unauthorized JOIN
Nested unauthorized subquery
Legitimate warehouse inventory query
Procurement inventory denial
No SQL generation after denied access
Warehouse cross-domain denial
Owner cross-domain allowance

Current status:

ALL SECURITY TESTS PASSED
17. Reliability Tests

Run:

python test_reliability.py

Covered scenarios:

Runtime database exception captured
Raw DB exception not exposed as user-facing error
Failed queries return empty results
Retry exhaustion returns a real message
Internal column names are not leaked
Failed requests return no visualization

Current status:

ALL RELIABILITY TESTS PASSED
18. Visualization Tests

Run:

python test_visualization_general.py

Covered:

Price-history line chart
Stock-by-location bar chart
Inventory-movement line chart
Vendor-comparison bar chart
Vendor-spend bar chart
Non-chart-friendly results return no chart

Current status:

ALL VISUALIZATION TESTS PASSED
19. Project Structure
manufacturer-agent/
|
├── start_app.py
|
├── backend/
│   |
│   ├── app/
│   │   |
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── prompts.py
│   │   │   |
│   │   │   └── nodes/
│   │   │       ├── classify.py
│   │   │       ├── access_guard.py
│   │   │       ├── generate_sql.py
│   │   │       ├── validate_sql.py
│   │   │       ├── execute_sql.py
│   │   │       ├── increment_retry.py
│   │   │       ├── query_failure.py
│   │   │       ├── visualize.py
│   │   │       └── respond.py
│   │   |
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── chat.py
│   │   |
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── schema.py
│   │   |
│   │   ├── security/
│   │   │   ├── personas.py
│   │   │   └── access_control.py
│   │   |
│   │   ├── sql/
│   │   │   ├── generator.py
│   │   │   ├── validator.py
│   │   │   └── executor.py
│   │   |
│   │   ├── response/
│   │   │   └── visualization.py
│   │   |
│   │   ├── config.py
│   │   └── main.py
│   |
│   ├── requirements.txt
│   ├── test_evaluation.py
│   ├── test_security_hardening.py
│   ├── test_reliability.py
│   ├── test_visualization_general.py
│   └── ...
│
├── frontend/
│   |
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       ├── layout.tsx
│   │       └── globals.css
│   |
│   ├── package.json
│   └── ...
│
├── .gitignore
├── .env.example
└── README.md
20. Environment Variables

Create:

backend/.env

Example:

DATABASE_URL=postgresql://username:password@host:port/database

OPENAI_API_KEY=your_openai_api_key

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=manufacturer-agent

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=manufacturer-agent

Never commit the actual .env.

21. Setup
Backend
cd backend

Create environment:

python -m venv venv

Windows:

venv\Scripts\activate

Install:

pip install -r requirements.txt

Start backend:

python -m uvicorn app.main:app --reload

Backend:

http://localhost:8000

Swagger:

http://localhost:8000/docs
Frontend
cd frontend

Install:

npm install

Start:

npm run dev

Frontend:

http://localhost:3000
22. Start Frontend and Backend Together

A root launcher is included:

start_app.py

From the project root:

python start_app.py

This starts:

Frontend: http://localhost:3000
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs

Press:

Ctrl+C

to stop both servers.

23. API Usage

Endpoint:

POST /api/chat

Example request:

{
  "question": "Show receipts for PO-2026-0029.",
  "persona": "procurement"
}

Example response structure:

{
  "answer": "Receipts for PO-2026-0029...",
  "persona": "procurement",
  "domain": "procurement",
  "intent": "receipt_analysis",
  "sql": "SELECT ...",
  "data": {
    "columns": [],
    "rows": []
  },
  "visualization": null
}
24. LangSmith

LangSmith tracing allows inspection of the full workflow.

Typical successful trace:

classify
    |
access_guard
    |
generate_sql
    |
validate_sql
    |
execute_sql
    |
visualize
    |
respond

Runtime repair can look like:

generate_sql
    |
validate_sql
    |
execute_sql
    |
execution_error
    |
increment_retry
    |
generate_sql
    |
validate_sql
    |
execute_sql

Access-denied trace:

classify
    |
access_guard
    |
respond

SQL generation and DB execution are never reached.

25. Design Decisions
Why LangGraph?

The project is deliberately not implemented as:

Question → LLM → SQL

LangGraph provides explicit workflow control.

This allows:

Deterministic access checks
Conditional branches
Retries
SQL validation
Runtime repair
Observability
Clear separation of responsibilities
Why SQLGlot?

A simple regex-based table parser can miss SQL structures such as:

SELECT *
FROM table_a a, table_b b

or nested subqueries.

SQLGlot provides AST-based parsing so the application can inspect all referenced physical tables more reliably.

Why Persona-Scoped Schema?

Prompt instructions are not a security boundary.

Instead of showing every persona every table and saying:

Please don't use the forbidden ones

the schema itself is filtered before being sent to the SQL generator.

This reduces exposure and improves SQL generation quality.

Why Read-Only First?

The interviewer-defined minimum requirement was database reads.

Write actions have deliberately not been implemented because safe writes require:

Strong authentication
Fine-grained authorization
Confirmation
Approval workflows
Audit logging
Database transactions
Idempotency
Rollback behavior

The MVP therefore prioritizes trustworthy read operations.

26. Known Limitations
No Conversation Memory

Each /api/chat request is currently independent.

For example:

User:
How much did we spend with Vendor A this month?

User:
What about last month?

The second request does not currently inherit context from the first.

A production version could use:

LangGraph checkpointers
session IDs
message history
conversation persistence

This was intentionally left outside the core MVP scope.
