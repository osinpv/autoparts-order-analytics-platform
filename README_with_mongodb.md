# Autoparts Order Analytics Platform

A backend project for managing the lifecycle of automotive parts orders, inventory, shipments, and payments.

This project is built as a realistic transactional system rather than a simple CRUD demo. It models how an order moves through inventory reservation, payment processing, shipment, delivery, cancellation, and return flows, while preserving auditability through an inventory movement ledger.

---

## Project goals

The main goals of this project are:

- model realistic order and inventory workflows
- separate operational concerns such as inventory, shipment, and payment
- enforce business rules in the API and database
- keep schema evolution reproducible through Alembic migrations
- support automated integration tests against PostgreSQL
- document architectural trade-offs explicitly

---

## Tech stack

- **Python**
- **FastAPI**
- **SQLAlchemy ORM**
- **Alembic**
- **PostgreSQL**
- **MongoDB**
- **Motor**
- **pytest**

---

## Domain coverage

The project currently includes the following main domains.

### Catalog / master data
- product category
- product brand
- product
- warehouse

### Inventory
- `inventory_balance` — current stock state per `(warehouse_id, product_id)`
- `inventory_movement` — immutable ledger of inventory changes

### Orders
- `sales_order`
- `sales_order_item`

### Shipments
- `shipment`

### Payments
- `payment`

---

## MongoDB document store

In addition to the relational PostgreSQL model, the project includes a MongoDB document store for flexible product catalog data.

PostgreSQL remains the system of record for transactional and strongly relational domains such as:

- products
- inventory balances
- inventory movements
- orders
- shipments
- payments

MongoDB is used as a sidecar document store for product catalog extensions where the structure can vary by product category.

Current MongoDB collection:

- `product_documents`

This collection stores flexible product metadata such as:

- category-specific attributes
- vehicle fitment data
- OEM part numbers

Example document shape:

```json
{
  "product_id": 3,
  "sku": "BMW-BRAKE-PADS-001",
  "category": "Brake Rotor",
  "attributes": {
    "position": "front",
    "diameter_mm": 340,
    "ventilated": true
  },
  "fitment": [
    {
      "make": "BMW",
      "model": "430i",
      "year_from": 2017,
      "year_to": 2020,
      "engine": "B48"
    }
  ],
  "oem_numbers": [
    "34116860911"
  ],
  "created_at": "2026-05-17T00:00:00Z"
}
```

The intent is to keep transactional correctness in PostgreSQL while using MongoDB for document-oriented catalog data that would otherwise require a highly generic and over-normalized relational attribute model.

---

## Core entities

### Product
Represents a sellable catalog item.

### Warehouse
Represents a storage location.

### Inventory balance
Represents the current stock snapshot for a specific product in a specific warehouse.

Tracks:
- `on_hand_qty`
- `reserved_qty`

`available_qty` is derived as:

```text
available_qty = on_hand_qty - reserved_qty
```

### Inventory movement
Represents an immutable ledger record for stock state transitions.

The ledger stores:
- `movement_type`
- `qty`
- `reference_type`
- `reference_id`
- `resulting_on_hand_qty`
- `resulting_reserved_qty`

This allows the system to answer both:
- what changed
- what the stock state became after the change

### Sales order
Represents a customer order with one or more order items.

### Shipment
Represents the shipment record created when an order is shipped.

Tracks:
- shipment number
- order reference
- shipment status
- carrier name
- tracking number
- shipped timestamp

### Payment
Represents a payment attempt for an order.

Tracks:
- payment number
- order reference
- payment status
- payment method
- amount
- paid timestamp

The design now supports **multiple payment attempts** for the same order.

---

## Current business workflows

### 1. Inventory reserve
A reserved order reduces available stock by increasing `reserved_qty`.

Flow:
1. order exists
2. inventory is reserved
3. ledger gets `RESERVE`

### 2. Inventory release
Reserved stock can be released back into availability.

Flow:
1. order or manual process triggers release
2. `reserved_qty` decreases
3. ledger gets `RELEASE`

### 3. Shipping
Shipping is allowed only if:
- the order is in `RESERVED`
- the order has at least one payment in `PAID` status

Flow:
1. validate order status
2. validate payment state
3. decrease stock from reserved inventory
4. create shipment record
5. set order status to `SHIPPED`
6. ledger gets `SHIP`

### 4. Delivery
Delivery is modeled on the shipment entity.

Flow:
1. shipment is in `SHIPPED`
2. shipment becomes `DELIVERED`
3. related order becomes `DELIVERED`

### 5. Cancellation
Cancellation is modeled at the order level.

Rules:
- `NEW` order can be cancelled directly
- `RESERVED` order can be cancelled, which first releases reserved inventory
- `RELEASED` order can be cancelled
- `SHIPPED` order cannot be cancelled

### 6. Return
Return is currently modeled as a **full-order return**.

Rules:
- return is allowed for `SHIPPED` or `DELIVERED` orders
- return restores inventory
- ledger gets `RETURN`
- order becomes `RETURNED`

Current simplification:
- returns are full-order only
- partial return lines are not modeled yet

### 7. Payment creation
Payments are created as nested resources under orders:

- `POST /orders/{order_id}/payments`

Rules:
- payment can only be created for orders in:
  - `NEW`
  - `RESERVED`
  - `RELEASED`
- payment is blocked if there is already at least one:
  - `PENDING`
  - `PAID`
  payment for that order
- payment can be retried if previous payments are only:
  - `FAILED`
  - `REFUNDED`

### 8. Payment completion / failure
Payment lifecycle is independent from order fulfillment status.

Flows:
- `POST /payments/{payment_id}/complete`
- `POST /payments/{payment_id}/fail`

Rules:
- only `PENDING` payments can be completed
- only `PENDING` payments can be failed

---

## Status models

### Order status
Current order statuses:

- `NEW`
- `RESERVED`
- `RELEASED`
- `SHIPPED`
- `DELIVERED`
- `CANCELLED`
- `RETURNED`

### Shipment status
Current shipment statuses:

- `CREATED`
- `SHIPPED`
- `DELIVERED`
- `RETURNED`

Note:
`DELIVERED` is currently treated as the terminal shipment state in the practical business interpretation of this project.

### Payment status
Current payment statuses:

- `PENDING`
- `PAID`
- `FAILED`
- `REFUNDED`

---

## Important business rules

### Shipping requires payment
An order cannot be shipped unless at least one payment for that order is in `PAID` status.

### Payment attempts
The system supports multiple payment attempts per order.

Rules:
- cannot create a new payment if at least one existing payment is `PENDING`
- cannot create a new payment if at least one existing payment is `PAID`
- can create a new payment if all previous payments are only `FAILED` or `REFUNDED`

### Delivered shipment updates order
Delivering a shipment also updates the related order to `DELIVERED`.

### Shipment is separate from return
Shipment and return are intentionally treated as different concepts:
- shipment describes delivery execution
- return describes product coming back into inventory
- shipment is not reused as the return entity

### Inventory ledger stores resulting snapshots
Ledger rows store resulting stock snapshots so historical state reconstruction is simpler and query-friendly.

---

## Architectural decisions

### 1. Inventory ledger uses resulting snapshots
Instead of storing only deltas, each movement stores:
- resulting on-hand
- resulting reserved

This makes audit and historical reasoning much easier.

### 2. `available_qty` is derived, not stored
`available_qty` is intentionally not persisted in the database.
It is derived from:

```text
on_hand_qty - reserved_qty
```

This avoids redundant state.

### 3. Payment is modeled as a separate domain
Payment status is not currently merged into `order_status`.
This keeps money lifecycle separate from fulfillment lifecycle.

### 4. Shipment is created through order shipping flow
A shipment is currently created as a side effect of `ship_order(...)`.
Shipment has its own read/update lifecycle after creation.

### 5. PostgreSQL is the source of truth for concurrency behavior
The project intentionally uses PostgreSQL-specific transaction and locking features, including pessimistic locking with timeout behavior.

### 6. MongoDB is used for flexible catalog documents
MongoDB is used only for product catalog extensions, not for transactional workflows.

The main reason is that different automotive part categories can have very different attributes:

- brake rotors may have diameter, position, ventilation, and bolt pattern
- cabin filters may have filter type, material, and dimensions
- tires may have width, aspect ratio, rim size, and season

Instead of forcing all of these into a generic relational attribute/value model, the project stores category-specific metadata in MongoDB as flexible document attributes.

PostgreSQL remains the source of truth for the base `product` entity. MongoDB `product_documents.product_id` is treated as an extension of an existing PostgreSQL product.

### 7. Product document creation validates against PostgreSQL
A MongoDB product document cannot be created for an arbitrary product id.

During `POST /product-documents`, the API validates that:

- the referenced `product_id` exists in PostgreSQL
- the submitted `sku` matches the PostgreSQL product SKU

This prevents MongoDB catalog documents from drifting away from the relational product master data.

### 8. Vehicle fitment is modeled as an array of objects
Vehicle compatibility is modeled as embedded `fitment` records:

```json
"fitment": [
  {
    "make": "BMW",
    "model": "430i",
    "year_from": 2017,
    "year_to": 2020,
    "engine": "B48"
  }
]
```

This structure preserves the relationship between make, model, engine, and year range.

An earlier alternative of storing separate arrays such as `models` and `years` was avoided because it loses correlation between model and year and creates problems for compound multikey indexing.

Queries use MongoDB `$elemMatch` semantics so all fitment conditions are matched against the same embedded compatibility record.

### 9. MongoDB schema validation defines the minimum document contract
MongoDB is intentionally not used as a schemaless dumping ground.

The `product_documents` collection has schema validation rules for the minimum required contract:

- `product_id`
- `sku`
- `category`
- `attributes`
- `created_at`

The `fitment` array also validates required fields inside each embedded fitment object:

- `make`
- `model`
- `year_from`
- `year_to`

At the same time, the `attributes` object remains flexible by design because product-specific attributes differ significantly across automotive part categories.

---

## Concurrency strategy

### Pessimistic locking
Inventory rows are locked during stock-sensitive operations using row-level locking.

This protects against lost updates and overselling scenarios in concurrent workflows.

### Lock timeout
The project includes support for lock timeout handling so blocked operations can fail gracefully with a user-facing message such as:

- `Resource busy, try again later.`

### Optimistic versioning
A version column is also present in inventory balance design discussions and implementation flow, but the main stock-sensitive workflow currently relies on pessimistic locking for stronger safety under hot-row contention.

---

## API overview

### Orders
Examples of order-related endpoints:

- `POST /orders`
- `POST /orders/{order_id}/reserve`
- `POST /orders/{order_id}/release`
- `POST /orders/{order_id}/ship`
- `POST /orders/{order_id}/cancel`
- `POST /orders/{order_id}/return`

### Shipments
- `GET /shipments`
- `GET /shipments/{shipment_id}`
- `PATCH /shipments/{shipment_id}`
- `POST /shipments/{shipment_id}/deliver`

### Payments
- `GET /payments`
- `GET /payments/{payment_id}`
- `POST /orders/{order_id}/payments`
- `POST /payments/{payment_id}/complete`
- `POST /payments/{payment_id}/fail`

### Product documents
MongoDB-backed product document endpoints:

- `POST /product-documents`
- `GET /product-documents/{product_id}`
- `GET /product-documents/search/by-fitment`
- `GET /product-documents/search/by-oem/{oem_number}`

These endpoints expose flexible catalog document data stored in MongoDB.

The `POST /product-documents` endpoint validates the referenced product against PostgreSQL before creating the MongoDB document.

---

## Running the project

### Start local infrastructure
The project uses PostgreSQL for transactional data and MongoDB for flexible product catalog documents.

Start the local containers:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

Expected local services:

- PostgreSQL on `localhost:5432`
- MongoDB on `localhost:27017`

MongoDB connection settings are read from `.env`:

```env
MONGO_URL=mongodb://autoparts_mongo_user:autoparts_mongo_password@localhost:27017/autoparts_docs?authSource=admin
MONGO_DB_NAME=autoparts_docs
```

### Start the API locally

From the project root:

```powershell
.\scripts\run_app.ps1
```

Direct alternative:

```powershell
fastapi dev app/main.py
```

---

## Database migrations

### Apply migrations to the main development database

```powershell
alembic upgrade head
```

### Apply migrations to the test database

```powershell
.\scripts\migrate_test_db.ps1
```

This uses the dedicated PostgreSQL test database:

- `autoparts_test`

---

## MongoDB initialization

PostgreSQL schema changes are managed through Alembic migrations.

MongoDB collection initialization is handled through Docker MongoDB init scripts.

Current MongoDB initialization includes:

- creating the `product_documents` collection
- applying collection-level schema validation
- creating indexes for common access patterns

Current indexes:

- unique index on `product_id`
- fitment search index on:
  - `fitment.make`
  - `fitment.model`
  - `fitment.engine`
- OEM lookup index on:
  - `oem_numbers`

The MongoDB init script is stored in:

```text
mongo/init/001_create_product_documents.js
```

Note:

MongoDB Docker init scripts are executed only when the MongoDB data volume is first created. They are suitable for initial local bootstrap. Future schema changes to an existing MongoDB database should be handled with explicit migration scripts, for example using `collMod` for validation changes.

---

## Test setup

This project uses:

- `pytest`
- a dedicated PostgreSQL test database
- Alembic migrations applied from zero to bootstrap the schema
- automated API integration tests
- separate manual tests for lock/concurrency scenarios

### Why PostgreSQL is used for tests

SQLite is intentionally not used for the main integration test suite because the project relies on PostgreSQL-specific behavior such as:

- `SELECT ... FOR UPDATE`
- lock timeout handling
- schema-aware migrations
- check constraints
- transaction and concurrency behavior

---

## Running tests

### Run the full automated test suite

```powershell
.\scripts\run_tests.ps1
```

Equivalent direct command:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test"
pytest -q -m "not manual"
```

### Run only inventory tests

```powershell
.\scripts\run_inventory_tests.ps1
```

### Run only order tests

```powershell
.\scripts\run_order_tests.ps1
```

### Run only manual tests

```powershell
.\scripts\run_manual_tests.ps1
```

Manual tests are excluded from the default automated run because they are slower and intentionally wait on lock scenarios.

---

## Test structure

```text
tests/
├─ conftest.py
├─ helpers.py
├─ inventory/
├─ orders/
├─ payments/
├─ shipments/
└─ manual/
```

### Shared files

- `conftest.py` — dependency overrides, DB session, DB cleanup
- `helpers.py` — API helper functions and composite setup helpers

---

## Current automated coverage

The automated test suite currently covers:

### Inventory
- reserve success
- reserve failure when available quantity is insufficient
- release failure when trying to release more than reserved
- ship failure when trying to ship more than reserved
- ledger snapshot consistency across reserve / release / ship

### Orders
- order creation uses server-side product pricing
- order creation failure for missing product
- order creation validation for empty item list
- order reserve success
- order reserve failure when inventory is insufficient
- order release success
- order release wrong status
- double release protection
- order ship success
- shipping blocked without paid payment
- shipping blocked with pending payment
- shipping blocked with failed payment
- cancel shipped order forbidden
- return shipped order success
- return delivered order success
- return twice protection

### Shipments
- shipment creation during shipping
- get shipment by id
- filter shipments by order id
- update carrier / tracking
- deliver shipment success
- deliver shipment twice failure

### Payments
- create payment for order
- payment complete success
- payment fail success
- complete payment twice failure
- payment creation blocked for shipped order
- read payments by order id
- read payment by id
- create second payment after failed payment
- block second payment while first is pending
- block second payment while paid payment exists

### Manual / concurrency
- lock timeout behavior for pessimistic row locking

---

## Fresh test database bootstrap

If the test database already exists and needs to be recreated:

1. Recreate `autoparts_test`
2. Apply migrations
3. Run tests

Typical flow:

```powershell
.\scripts\migrate_test_db.ps1
.\scripts\run_tests.ps1
```

---

## Migration history

The migration history is designed to support fresh bootstrap of new databases, including the dedicated test database.

This is important because the schema evolved through several stages, including:

- migration from `public` to `autoparts_owner`
- Alembic version table relocation
- inventory ledger redesign
- order lifecycle expansion
- shipment and payment domains
- multiple payment attempt support

---

## Known simplifications

This project intentionally keeps some parts simplified for the current stage.

### Full-order return only
Returns currently operate at the whole-order level.
Partial returns are not modeled yet.

### Order status is still evolving
The current `order_status` mixes some fulfillment and aggregate-level concepts.
This is acceptable for the current stage, but a future redesign may separate:
- fulfillment state
- payment state
- aggregate order completion state

### No customer entity yet
Orders currently store `customer_email` directly.
A future iteration may introduce:
- `customer`
- addresses
- billing/shipping separation

### No refund flow yet
Payment supports `REFUNDED` status in the model, but the refund action flow is not implemented yet.

### No split shipments yet
The current design assumes a simple shipment flow and does not yet model partial or split shipments across multiple shipment records.

### MongoDB migration flow is initial-bootstrap only
MongoDB collection creation, validation rules, and indexes are currently initialized through Docker init scripts.

This is sufficient for local bootstrap and portfolio demonstration, but it is not yet a full MongoDB migration framework.

A future iteration may add explicit MongoDB migration scripts for evolving validation rules and indexes on existing databases.

---

## Future work

Possible next steps:

- payment refund flow
- customer entity
- shipping and billing addresses
- partial returns
- split shipments
- warehouse transfer flow
- richer order details endpoint combining:
  - order
  - items
  - shipment
  - payment
- MongoDB migration runner for document collection changes
- richer product document search by category-specific attributes
- data quality checks comparing PostgreSQL products with MongoDB product documents
- export / flatten MongoDB product fitment documents into analytics-friendly tabular format
- CI integration
- coverage reporting
- OpenAPI / contract polishing

---

## Summary

This project is designed as a realistic transactional backend focused on order fulfillment, inventory correctness, shipment tracking, and payment lifecycle management.

The project also demonstrates a hybrid persistence approach:

- PostgreSQL is used for transactional consistency, relational integrity, inventory correctness, and order/payment workflows.
- MongoDB is used for flexible product catalog documents where embedded attributes, OEM numbers, and vehicle fitment records are more natural than a rigid relational attribute model.

This separation keeps the core order lifecycle strongly consistent while allowing the catalog layer to support heterogeneous automotive part metadata.

It intentionally favors:
- explicit domain workflows
- database-backed business rules
- audit-friendly ledger design
- reproducible migrations
- PostgreSQL-based integration testing
- clear architectural trade-off documentation
