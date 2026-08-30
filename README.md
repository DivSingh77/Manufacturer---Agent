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

The system dynamically generates PostgreSQL such as:

SELECT
    po.id,
    po.po_number,
    po.status,
    po.placed_on,
    po.total_amount
FROM proc_purchase_orders po
WHERE po.status = 'partial';

The generated SQL is validated before execution.

Persona-Based Access Control

The system supports three personas:

Warehouse

Warehouse users can access inventory-related data only.

Allowed areas include:

Items
Categories
Warehouse locations
Current stock
Inventory transactions
Warehouse issues

Example:

Which items currently have zero stock?

Allowed.

But:

Show me all purchase orders.

is denied before SQL generation.

Procurement

Procurement users can access:

Purchase orders
Purchase-order lines
Vendors
Receipts
Payment tranches
Unexpected receipts
Regularisations

They also have lookup access to:

inv_items
inv_locations

This allows procurement queries to show human-readable item and warehouse information without granting full inventory-analysis access.

For example:

Show details of PO-2026-0029 including vendor and items.

is allowed.

But:

What is the current stock of all items?

is denied.

Owner

Owner users have cross-domain access to both:

Inventory
Procurement

This allows higher-level operational analysis across the organization.

3. Security Architecture

The application does not rely only on the LLM for authorization.

It uses multiple layers of protection.

User Question
      |
      v
Intent / Domain Classification
      |
      v
Persona Access Guard
      |
      +----------------------+
      |                      |
   Denied                  Allowed
      |                      |
      v                      v
Safe Response          SQL Generation
                             |
                             v
                      SQL Validation
                             |
                      +------+------+
                      |             |
                   Invalid        Valid
                      |             |
                    Retry           v
                               PostgreSQL

This provides defense in depth.

Even if the LLM generates an unauthorized query, the SQL validator performs a second deterministic authorization check before execution.

4. Technology Stack
Frontend
Next.js
TypeScript
Tailwind CSS
Recharts

The frontend provides:

Persona selector
Natural-language query interface
AI-generated answers
SQL inspection
Query result tables
Dynamic charts
Access-control feedback
Backend
Python
FastAPI
LangGraph
OpenAI API

FastAPI exposes the main endpoint:

POST /api/chat

Example request:

{
  "question": "Which purchase orders are partially received?",
  "persona": "procurement"
}
Database
PostgreSQL
Railway-hosted database

The agent works against a live relational manufacturing dataset.

Agent Orchestration

LangGraph is used to define the execution workflow.

Main nodes:

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

Conditional routing is used for:

Access-denied requests
SQL-validation failures
SQL retry behavior
Observability

LangSmith is used for:

Tracing LangGraph executions
Inspecting node execution
Debugging prompts
SQL-generation analysis
Latency analysis
Error inspection
Guardrail verification
5. LangGraph Workflow

The complete workflow is:

                         User
                           |
                           v
                    Next.js Frontend
                           |
                           v
                     FastAPI /api/chat
                           |
                           v
                    +---------------+
                    |   Classifier  |
                    +-------+-------+
                            |
                 intent + domain
                            |
                            v
                    +---------------+
                    | Access Guard  |
                    +-------+-------+
                            |
                    +-------+-------+
                    |               |
                  Denied          Allowed
                    |               |
                    v               v
                 Respond      SQL Generator
                                    |
                                    v
                              SQL Validator
                                    |
                             +------+------+
                             |             |
                           Invalid       Valid
                             |             |
                           Retry           v
                                      PostgreSQL
                                           |
                                           v
                                   Visualization
                                           |
                                           v
                                      Response
                                           |
                                           v
                                      Next.js UI
6. Database Domains

The database contains 17 core tables.

Inventory Domain
inv_items

Stores item master data.

inv_categories

Stores item categories.

inv_sub_categories

Stores first-level subcategories.

inv_sub_categories_2

Stores deeper item classification.

inv_locations

Stores warehouse/storage locations.

inv_current_stock

Stores current stock quantity per item/location.

inv_issued_to_targets

Stores warehouse issue targets.

inv_transactions

Stores inventory movement history.

Transaction types include:

inbound
outbound
transfer_in
transfer_out

Reference types include:

purchase_order
unexpected_receipt
transfer
warehouse_issue
inv_field_definitions

Additional inventory metadata.

Procurement Domain
proc_vendors

Vendor master.

proc_purchase_orders

Purchase-order header.

Observed statuses:

placed
partial
received
proc_po_lines

Purchase-order item lines.

proc_po_payment_tranches

PO payment information.

proc_po_receipts

Goods received against PO lines.

proc_po_line_regularisations

PO line regularisation records.

Unexpected Receipt Domain
proc_unexpected_receipt_headers

Unexpected receipt header records.

proc_unexpected_receipts

Unexpected receipt line-level records.

7. Important Data Relationships
Purchase Order to Vendor
proc_purchase_orders.vendor_id
    ->
proc_vendors.id
Purchase Order to Lines
proc_purchase_orders.id
    ->
proc_po_lines.po_id
PO Lines to Items
proc_po_lines.inv_item_id
    ->
inv_items.id
Purchase Order Receipts

Correct receipt relationship:

proc_purchase_orders.id
        |
        v
proc_po_lines.po_id

proc_po_lines.id
        |
        v
proc_po_receipts.po_line_id

Human-readable receipt queries may additionally join:

proc_po_lines.inv_item_id
    ->
inv_items.id

proc_po_receipts.location_id
    ->
inv_locations.id
Inventory Transactions
inv_transactions.item_id
    ->
inv_items.id

inv_transactions.location_id
    ->
inv_locations.id
8. Example Queries
Warehouse
Which items currently have zero stock?
Show me the current stock by warehouse location.
Show me recent inventory transactions.
Procurement
Which purchase orders are partially received?
Show details of PO-2026-0029 including vendor and items.
Show receipts for PO-2026-0029.
Which vendors have the most purchase orders?
Which items have been purchased most frequently?
Show the purchase price history of MS C Channel – 125×65×5mm.
Owner
What is the current stock of all items?
Which vendors have the most purchase orders?
Show details of PO-2026-0029 including vendor and items.
9. Visualization Support

The backend can return chart-ready metadata for relevant questions.

Example query:

Show the purchase price history of MS C Channel – 125×65×5mm.

Example backend visualization response:

{
  "type": "line",
  "title": "Purchase Price History",
  "x_key": "placed_on",
  "y_key": "unit_price",
  "data": [
    {
      "po_number": "PO-2026-0019",
      "placed_on": "2026-08-07",
      "unit_price": 18.2,
      "quantity_ordered": 805,
      "line_total": 14651,
      "currency": "INR"
    },
    {
      "po_number": "PO-2026-0029",
      "placed_on": "2026-08-12",
      "unit_price": 18.13,
      "quantity_ordered": 2884,
      "line_total": 52286.92,
      "currency": "INR"
    }
  ]
}

The frontend renders this using Recharts.

10. Project Structure
manufacturer-agent/
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
│   ├── test_graph.py
│   ├── test_personas.py
│   ├── test_access.py
│   ├── test_procurement.py
│   ├── test_receipts.py
│   ├── test_visualization.py
│   └── test_evaluation.py
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
11. Environment Variables

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

Do not commit the real .env file.

The repository .gitignore excludes environment files.

Example safe file:

.env.example

may be committed with placeholder credentials.

12. Backend Setup

Navigate to the backend:

cd backend

Create a virtual environment if required:

python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Start FastAPI:

python -m uvicorn app.main:app --reload

Backend:

http://localhost:8000

Swagger:

http://localhost:8000/docs
13. Frontend Setup

Navigate to:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Frontend:

http://localhost:3000
14. API Usage

Endpoint:

POST /api/chat

Example:

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
15. SQL Safety

Generated SQL is checked before execution.

The validator:

Allows read-only queries.
Rejects unauthorized tables.
Rejects modification statements.
Rejects multiple statements.
Verifies persona-level table access.

Forbidden SQL operations include:

INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
16. Access-Control Examples
Warehouse attempting Procurement

Request:

{
  "question": "Show me all purchase orders.",
  "persona": "warehouse"
}

Response:

{
  "answer": "Access denied: warehouse users cannot access procurement data.",
  "persona": "warehouse",
  "domain": "procurement",
  "sql": null
}

Notice:

sql = null

The request is blocked before SQL generation.

Procurement attempting Inventory Analysis

Request:

{
  "question": "What is the current stock of all items?",
  "persona": "procurement"
}

Response:

{
  "answer": "Access denied: procurement users cannot perform inventory analysis.",
  "persona": "procurement",
  "domain": "inventory",
  "sql": null
}
17. Automated Evaluation

The project includes an automated evaluation suite:

python test_evaluation.py

Current MVP evaluation result:

Passed: 8
Failed: 0
Total:  8
Score:  100.0%

Covered scenarios:

Test	Result
Warehouse inventory access	PASS
Warehouse procurement denial	PASS
Procurement purchase-order access	PASS
Procurement inventory denial	PASS
Owner inventory access	PASS
Multi-table PO details	PASS
PO receipt joins	PASS
Price-history visualization	PASS

Important:

This does not claim that the agent has 100% general natural-language accuracy.

It means that the current deterministic MVP evaluation suite has all critical scenarios passing.

18. LangSmith Observability

LangSmith tracing is enabled for the project.

Example successful workflow:

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
visualize
    |
respond

For access-denied requests:

classify
    |
access_guard
    |
DENIED
    |
respond

SQL generation and database execution are not reached.

LangSmith helps inspect:

Node-level execution
LLM prompts
LLM responses
Generated SQL
Latency
Errors
Guardrail decisions
19. Design Decisions
Why LangGraph?

The application is not implemented as a single LLM prompt.

LangGraph provides explicit stateful orchestration and conditional routing.

This makes it easier to:

Separate responsibilities
Add access-control nodes
Add retries
Add validation
Debug execution
Trace individual workflow stages
Extend the application later
Why Separate SQL Generation and Validation?

An LLM should not directly execute arbitrary database queries.

The system therefore separates:

LLM SQL Generation
        |
        v
Deterministic SQL Validation
        |
        v
Database Execution

This reduces the risk of unauthorized or destructive operations.

Why Persona-Level Guardrails Before SQL Generation?

Unauthorized requests should ideally never reach the SQL generator.

Example:

Warehouse
    +
Purchase-order question
        |
        v
Classifier
        |
        v
Access Guard
        |
        v
DENIED

This reduces unnecessary LLM/database work and provides a clearer security boundary.

20. Current Limitations

This project is intentionally scoped as an MVP.

Read-Only Operations

The current system focuses on read-only analytics and question answering.

Write operations such as:

Create purchase order
Update purchase order
Modify stock
Receive inventory
Delete records

are intentionally not exposed.

Production-grade write support would require:

Explicit confirmation
Approval workflows
Transaction management
Audit logging
Rollback capability
Fine-grained authorization
SQL Validator

The current validator is lightweight.

For production, an AST-based parser such as SQLGlot could be used for deeper query analysis.

Database Security

A production deployment should additionally use:

Dedicated read-only database credentials
Query timeouts
Maximum result limits
Connection pooling
Row/column-level authorization
Database audit logging
Schema Scaling

The current system can provide schema context directly to the SQL generator.

For significantly larger schemas, a production architecture should use schema retrieval based on:

user question
    |
domain
    |
intent
    |
relevant tables only

This would reduce token usage and improve SQL accuracy.
