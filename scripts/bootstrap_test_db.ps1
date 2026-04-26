$adminUrl = "postgresql://autoparts_user:autoparts_pass@localhost:5432/postgres"

psql $adminUrl -c "DROP DATABASE IF EXISTS autoparts_test;"
psql $adminUrl -c "CREATE DATABASE autoparts_test;"

$env:DATABASE_URL="postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test"
alembic upgrade head

$env:TEST_DATABASE_URL="postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test"
pytest -q -m "not manual"