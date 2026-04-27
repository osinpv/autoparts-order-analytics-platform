$previousDatabaseUrl = $env:DATABASE_URL

try {
    $env:DATABASE_URL = "postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test"
    alembic upgrade head
}
finally {
    if ($null -ne $previousDatabaseUrl -and $previousDatabaseUrl -ne "") {
        $env:DATABASE_URL = $previousDatabaseUrl
    }
    else {
        Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    }
}
