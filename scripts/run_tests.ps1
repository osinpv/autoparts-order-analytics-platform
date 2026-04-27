$previousTestDatabaseUrl = $env:TEST_DATABASE_URL

try {
    $env:TEST_DATABASE_URL = "postgresql+psycopg://autoparts_user:autoparts_pass@localhost:5432/autoparts_test"
    pytest -q -m "not manual"
}
finally {
    if ($null -ne $previousTestDatabaseUrl -and $previousTestDatabaseUrl -ne "") {
        $env:TEST_DATABASE_URL = $previousTestDatabaseUrl
    }
    else {
        Remove-Item Env:TEST_DATABASE_URL -ErrorAction SilentlyContinue
    }
}
