param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$requiredFiles = @(
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "requirements.txt",
    "LICENSE",
    "docs/case-study.md",
    "docs/workflow.md",
    "docs/research-framework.md",
    "docs/safe-demo.md",
    "skills/ecommerce-market-research-agent/SKILL.md",
    "scripts/generate_market_report.py",
    "scripts/portfolio_audit.ps1",
    "configs/research_rules.yaml",
    "configs/source_policy.yaml",
    "examples/sample_product_brief.md",
    "examples/sample_competitor_table.csv",
    "examples/generated_market_report.md"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $requiredFiles) {
    $path = Join-Path $Root $file
    if (-not (Test-Path -LiteralPath $path)) {
        $failures.Add("Missing required file: $file")
    }
}

$textFiles = Get-ChildItem -LiteralPath $Root -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in @(".md", ".py", ".ps1", ".yaml", ".yml", ".csv", ".txt", "")
    }

$secretPatterns = @(
    "ghp_[A-Za-z0-9_]{20,}",
    "github_pat_[A-Za-z0-9_]{20,}",
    "sk-[A-Za-z0-9]{20,}",
    "xox[baprs]-[A-Za-z0-9-]{10,}",
    "AKIA[0-9A-Z]{16}",
    ("BEGIN " + "RSA PRIVATE KEY"),
    ("BEGIN " + "OPENSSH PRIVATE KEY")
)

foreach ($pattern in $secretPatterns) {
    $matches = $textFiles | Select-String -Pattern $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $failures.Add("Secret-like pattern found: $pattern")
    }
}

$generator = Join-Path $Root "scripts/generate_market_report.py"
if (Test-Path -LiteralPath $generator) {
    $networkImports = Select-String -LiteralPath $generator -Pattern "import requests|import httpx|from urllib|import urllib|scrapy|playwright|selenium|aiohttp" -ErrorAction SilentlyContinue
    if ($networkImports) {
        $failures.Add("Generator appears to include networking or browser automation imports.")
    }
}

$examples = @(
    "examples/sample_product_brief.md",
    "examples/sample_competitor_table.csv"
)

foreach ($example in $examples) {
    $path = Join-Path $Root $example
    if (Test-Path -LiteralPath $path) {
        $content = Get-Content -LiteralPath $path -Raw
        if ($content -notmatch "(?i)fictional|synthetic") {
            $failures.Add("Example file does not clearly label fictional or synthetic data: $example")
        }
    }
}

$rulesPath = Join-Path $Root "configs/research_rules.yaml"
if (Test-Path -LiteralPath $rulesPath) {
    $rulesText = Get-Content -LiteralPath $rulesPath -Raw
    foreach ($requiredTerm in @("source_priority", "evidence_levels", "human_review_prompts", "external_network")) {
        if ($rulesText -notmatch $requiredTerm) {
            $failures.Add("Research rules missing required term: $requiredTerm")
        }
    }
}

$readmePath = Join-Path $Root "README.md"
if (Test-Path -LiteralPath $readmePath) {
    $readme = Get-Content -LiteralPath $readmePath -Raw
    foreach ($requiredTerm in @("Content Growth", "Safe Demo", "does not scrape", "portfolio")) {
        if ($readme -notmatch [regex]::Escape($requiredTerm)) {
            $failures.Add("README missing required positioning term: $requiredTerm")
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Portfolio audit failed:" -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host " - $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Portfolio audit passed." -ForegroundColor Green
Write-Host "Required files, Safe Demo constraints, evidence config, and secret checks look good."
