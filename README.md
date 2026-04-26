# AutoParts Order & Analytics Platform

A project focused on designing a transactional retail backend with strong database-oriented architecture.

Current scope includes:
- product and warehouse master data
- inventory balance management
- inventory movement ledger
- transactional inventory operations
- concurrency control patterns
- API-first implementation with FastAPI + PostgreSQL



## Implemented features

Current implementation covers the core inventory foundation of a transactional retail platform:

- Product domain:
  - product categories
  - product brands
  - products
  - warehouses

- Inventory domain:
  - current inventory balance per `(warehouse, product)`
  - inventory reserve / release operations
  - inventory receive / ship operations
  - inventory movement ledger (history of all inventory changes)

- API capabilities:
  - create and list categories, brands, products, warehouses
  - get entities by id
  - enriched details endpoints for products and inventory balances
  - filtered inventory search by:
    - warehouse
    - product
    - SKU
    - category
    - brand

- Data integrity:
  - unique constraints
  - foreign keys
  - check constraints for inventory quantities
  - typed movement and reference values with database validation

- Concurrency controls:
  - optimistic versioning on `inventory_balance`
  - pessimistic row locking for hot inventory mutation paths
  - lock timeout handling for busy inventory rows



## Inventory architecture

The inventory module is intentionally split into two layers:

### 1. `inventory_balance`
Stores the **current state** of inventory for a single `(warehouse, product)` pair.

Fields include:
- `on_hand_qty`
- `reserved_qty`

`available_qty` is **not stored physically** in this table.
It is derived as:

`available_qty = on_hand_qty - reserved_qty`

This keeps the current-state table cleaner and reduces the risk of storing inconsistent derived data.

### 2. `inventory_movement`
Stores the **history of inventory changes**.

Each movement records:
- movement type
- quantity
- business reference type / reference id
- resulting inventory snapshot after the operation:
  - `resulting_on_hand_qty`
  - `resulting_reserved_qty`
  - `resulting_available_qty` is calculated in the API layer

This design allows the system to answer both questions:

- **What is the current state?** → `inventory_balance`
- **How did the system get there?** → `inventory_movement`

This is a common pattern in transactional systems where current-state reads must be fast, but auditability and historical reconstruction are also required.



## Inventory operations

The following business operations are currently implemented:

- `reserve`
- `release`
- `receive`
- `ship`

### Reserve
Increases `reserved_qty` if enough inventory is available.

### Release
Decreases `reserved_qty` if sufficient quantity is currently reserved.

### Receive
Increases `on_hand_qty` when inventory is received into stock.

### Ship
Decreases both:
- `on_hand_qty`
- `reserved_qty`

This models shipment of already reserved inventory.

Every successful inventory mutation also writes a ledger entry into `inventory_movement` within the same transaction.



## Concurrency strategy

Two concurrency control techniques are intentionally demonstrated in this project:

### Optimistic locking
`inventory_balance` includes a `version_num` column and SQLAlchemy versioning support.

This protects against lost updates and demonstrates an optimistic concurrency pattern.

### Pessimistic locking
For hot inventory mutation paths (`reserve`, `release`, `receive`, `ship`), the implementation uses:

`SELECT ... FOR UPDATE`

This was chosen because inventory rows are contention-prone and business-critical.

With pessimistic locking:
- concurrent updates are serialized
- each transaction checks the most current state
- oversell risk is reduced
- clients get a business result based on actual latest inventory

### Lock timeout
Hot-path locking also uses a lock timeout.
If a row remains locked for too long, the API returns a controlled error such as:

`Resource busy, try again later.`

This avoids indefinite waiting and makes concurrency behavior more predictable for API consumers.



## Data integrity rules

### `inventory_balance`
Database constraints enforce:
- `on_hand_qty >= 0`
- `reserved_qty >= 0`
- `reserved_qty <= on_hand_qty`

### `inventory_movement`
Database constraints enforce:
- `qty > 0`
- `resulting_on_hand_qty >= 0`
- `resulting_reserved_qty >= 0`
- `resulting_reserved_qty <= resulting_on_hand_qty`

Allowed movement types and reference types are also validated at both:
- application level
- database level



## Why this design

This implementation intentionally favors clarity of transactional behavior over excessive abstraction.

Key design choices:
- `available_qty` is derived, not stored in `inventory_balance`
- ledger stores resulting state snapshots to simplify historical investigation
- hot inventory mutations use pessimistic locking
- optimistic versioning remains in place as an additional concurrency example
- reference types are typed and validated to prepare the model for future order / shipment integration


## Order workflow

The project currently implements a minimal transactional order lifecycle:

- `NEW`
- `RESERVED`
- `RELEASED`
- `SHIPPED`

### `POST /orders`
Creates an order header and order items.

Important design choice:
- client does **not** provide item price
- server loads the current product price from `product.price`
- `sales_order_item.unit_price` stores the price snapshot at the time of order creation
- `line_amount` and `order_total_amount` are calculated server-side

This prevents clients from manipulating pricing in the order request.



## Order and inventory integration

Inventory is not reserved automatically during order creation.

Instead, the workflow is intentionally split into explicit business actions:

### `POST /orders/{order_id}/reserve`
- allowed only for orders in `NEW` status
- locks affected inventory rows using pessimistic locking
- validates available quantity for each order item
- increases `reserved_qty`
- writes `RESERVE` entries into `inventory_movement`
- updates order status to `RESERVED`

### `POST /orders/{order_id}/release`
- allowed only for orders in `RESERVED` status
- decreases `reserved_qty`
- writes `RELEASE` entries into `inventory_movement`
- updates order status to `RELEASED`

### `POST /orders/{order_id}/ship`
- allowed only for orders in `RESERVED` status
- decreases both:
  - `on_hand_qty`
  - `reserved_qty`
- writes `SHIP` entries into `inventory_movement`
- updates order status to `SHIPPED`



## Transactional guarantees

Order reservation and shipment flows are implemented as multi-row transactional operations.

For each order item, the application:

- locates the corresponding inventory balance by `(warehouse_id, product_id)`
- locks the row with `SELECT ... FOR UPDATE`
- validates inventory state
- updates current balance
- writes ledger history

If any item fails validation, the entire operation is rolled back.

This ensures consistency across:
- order status
- inventory balance
- inventory movement ledger



## Pricing design

At order creation time, pricing is controlled by the server.

Client request payload contains:
- `product_id`
- `warehouse_id`
- `qty`

The server then:
- loads `product.price`
- stores it as `sales_order_item.unit_price`
- calculates `line_amount`
- calculates `order_total_amount`

This design preserves:
- pricing integrity
- order history stability
- snapshot pricing behavior

Even if `product.price` changes later, existing order items keep the original captured price.



## Why the workflow is split

Order creation and inventory reservation are intentionally separated.

This makes the lifecycle easier to:
- understand
- debug
- test
- explain in interviews

It also mirrors real business workflows more clearly:

- order exists
- order is reserved
- reservation may be released
- reserved inventory may be shipped

This explicit state transition model is easier to evolve than a single oversized "create-and-do-everything" endpoint.




## End-to-end demo scenario

A typical demo flow for the current system:

1. Create warehouse
2. Create category
3. Create brand
4. Create product
5. Create inventory balance
6. Create order
7. Reserve order
8. Inspect inventory balance changes
9. Inspect inventory movement ledger
10. Release order reservation (optional path)
11. Ship order (happy path from `RESERVED`)

This demonstrates:
- master data setup
- transactional order creation
- secure server-side pricing
- inventory reservation
- inventory release
- shipment
- current-state vs history-table architecture
- pessimistic locking on hot inventory rows




## Current order statuses

Current implementation uses the following order statuses:

- `NEW`
- `RESERVED`
- `RELEASED`
- `SHIPPED`

At this stage, status values are stored as strings.
A future improvement would be to apply the same discipline used in inventory:
- typed enum in application code
- database constraint on allowed status values




## Running the project

### Start the API locally

From the project root:

```powershell
.\scripts\run_app.ps1
```

This starts the FastAPI development server.

If needed, you can also run it directly:

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

### Run manual tests

```powershell
.\scripts\run_manual_tests.ps1
```

Manual tests are excluded from the default automated run because they are slower and may intentionally wait on row locks.

---

## Test structure

```text
tests/
├─ conftest.py
├─ helpers.py
├─ inventory/
├─ orders/
└─ manual/
```

### Test folders

- `tests/inventory` — inventory-only scenarios
- `tests/orders` — order workflow scenarios
- `tests/manual` — manual or slow concurrency tests

### Shared files

- `conftest.py` — test DB session, FastAPI dependency override, DB cleanup
- `helpers.py` — reusable API helper functions and composite setup helpers

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
- order ship wrong status
- ship-after-release protection
- double ship protection

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

If you want a completely clean bootstrap, recreate the test database first, then rerun migrations.

---

## Notes on migration history

The migration history was made safe for fresh bootstrap of new databases, including the dedicated test database.

This is important because the project evolved through multiple schema moves and refactors, including:

- creation of `autoparts_owner`
- movement of tables from `public`
- Alembic version table relocation
- subsequent constraint and workflow-related schema changes

As a result, both development and test environments can now be created from zero using migrations.
