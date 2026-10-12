param(
    [string]$Architecture = "services",
    [string]$HostUrl = "http://localhost:8000",
    [int]$DurationSeconds = 420
)

$ErrorActionPreference = "Stop"

$users = @(1, 5, 10, 25, 50)

$resultsDir = "tests/performance/results"

if (-not (Test-Path $resultsDir)) {
    New-Item `
        -ItemType Directory `
        -Path $resultsDir `
        | Out-Null
}

Write-Host ""
Write-Host "=========================================="
Write-Host "PULSO - Architecture Benchmark"
Write-Host "Architecture: $Architecture"
Write-Host "Host: $HostUrl"
Write-Host "Duration per scenario: $DurationSeconds s"
Write-Host "Users: $($users -join ', ')"
Write-Host "=========================================="
Write-Host ""

foreach ($u in $users) {

    $spawnRate = [Math]::Max(
        1,
        [Math]::Ceiling($u / 5)
    )

    $outputPrefix = (
        "$resultsDir/" +
        "${Architecture}_u${u}"
    )

    Write-Host ""
    Write-Host "------------------------------------------"
    Write-Host "Architecture: $Architecture"
    Write-Host "Concurrent users: $u"
    Write-Host "Spawn rate: $spawnRate users/s"
    Write-Host "Duration: $DurationSeconds s"
    Write-Host "Output: $outputPrefix"
    Write-Host "------------------------------------------"
    Write-Host ""

    python -m locust `
        -f tests/performance/locustfile.py `
        --headless `
        -u $u `
        -r $spawnRate `
        -t "${DurationSeconds}s" `
        --host $HostUrl `
        --csv $outputPrefix `
        --csv-full-history

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Benchmark failed for $u users."
        exit $LASTEXITCODE
    }

    Write-Host ""
    Write-Host "Completed scenario with $u users."
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Benchmark completed successfully."
Write-Host "Results saved in:"
Write-Host $resultsDir
Write-Host "=========================================="