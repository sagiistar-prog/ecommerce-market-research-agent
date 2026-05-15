param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Add-Failure {
    param(
        [System.Collections.Generic.List[string]]$Failures,
        [string]$Message
    )
    $Failures.Add($Message)
}

function Join-Term {
    param([string[]]$Parts)
    return ($Parts -join "")
}

function From-Codepoints {
    param([int[]]$Codes)
    return (-join ($Codes | ForEach-Object { [char]$_ }))
}

function Get-RepoRelativePath {
    param([string]$Path)
    $rootPrefix = $Root.TrimEnd("\", "/") + [System.IO.Path]::DirectorySeparatorChar
    if ($Path.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring($rootPrefix.Length)
    }
    return (Split-Path -Leaf $Path)
}

Push-Location -LiteralPath $Root
try {
    $trackedFiles = git ls-files
}
finally {
    Pop-Location
}

if (-not $trackedFiles) {
    Write-Host "Portfolio audit failed:" -ForegroundColor Red
    Write-Host " - No tracked files found. Run this audit inside the project repository." -ForegroundColor Red
    exit 1
}

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
    if (-not ($trackedFiles -contains $file)) {
        Add-Failure $failures "Missing tracked required file: $file"
    }
    elseif (-not (Test-Path -LiteralPath $path)) {
        Add-Failure $failures "Tracked required file is not present on disk: $file"
    }
}

$textExtensions = @(".md", ".py", ".ps1", ".yaml", ".yml", ".csv", ".txt", "")
$textFiles = foreach ($file in $trackedFiles) {
    $path = Join-Path $Root $file
    if (Test-Path -LiteralPath $path) {
        $extension = [System.IO.Path]::GetExtension($file)
        if ($textExtensions -contains $extension) {
            $path
        }
    }
}

$secretPatterns = @(
    "ghp_[A-Za-z0-9_]{20,}",
    "github_pat_[A-Za-z0-9_]{20,}",
    "sk-[A-Za-z0-9]{20,}",
    "xox[baprs]-[A-Za-z0-9-]{10,}",
    "AKIA[0-9A-Z]{16}",
    ("api[_-]?key" + "\s*[:=]"),
    ((Join-Term @("to", "ken")) + "\s*[:=]"),
    ("secret" + "\s*[:=]"),
    ("password" + "\s*[:=]"),
    ("BEGIN " + "RSA PRIVATE KEY"),
    ("BEGIN " + "OPENSSH PRIVATE KEY")
)

foreach ($pattern in $secretPatterns) {
    $matches = Select-String -Path $textFiles -Pattern $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        foreach ($match in $matches) {
            $relative = Get-RepoRelativePath $match.Path
            Add-Failure $failures "Secret-like pattern found in ${relative}:$($match.LineNumber)"
        }
    }
}

$absolutePathMatches = Select-String -Path $textFiles -Pattern "[A-Za-z]:\\[^\s)`'`"]+" -ErrorAction SilentlyContinue
foreach ($match in $absolutePathMatches) {
    $relative = Get-RepoRelativePath $match.Path
    Add-Failure $failures "Local absolute path found in ${relative}:$($match.LineNumber)"
}

$emailMatches = Select-String -Path $textFiles -Pattern "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" -ErrorAction SilentlyContinue
foreach ($match in $emailMatches) {
    $relative = Get-RepoRelativePath $match.Path
    Add-Failure $failures "Email-like address found in ${relative}:$($match.LineNumber)"
}

$generator = Join-Path $Root "scripts/generate_market_report.py"
if (Test-Path -LiteralPath $generator) {
    $networkImports = Select-String -LiteralPath $generator -Pattern "import requests|import httpx|from urllib|import urllib|scrapy|playwright|selenium|aiohttp" -ErrorAction SilentlyContinue
    if ($networkImports) {
        Add-Failure $failures "Generator appears to include networking or browser automation imports."
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
            Add-Failure $failures "Example file does not clearly label fictional or synthetic data: $example"
        }
    }
}

$rulesPath = Join-Path $Root "configs/research_rules.yaml"
if (Test-Path -LiteralPath $rulesPath) {
    $rulesText = Get-Content -LiteralPath $rulesPath -Raw
    foreach ($requiredTerm in @("source_priority", "evidence_levels", "human_review_prompts", "external_network")) {
        if ($rulesText -notmatch $requiredTerm) {
            Add-Failure $failures "Research rules missing required term: $requiredTerm"
        }
    }
}

$readmePath = Join-Path $Root "README.md"
if (Test-Path -LiteralPath $readmePath) {
    $readme = Get-Content -LiteralPath $readmePath -Raw
    foreach ($requiredTerm in @("Content Growth", "Safe Demo", "does not scrape", "portfolio")) {
        if ($readme -notmatch [regex]::Escape($requiredTerm)) {
            Add-Failure $failures "README missing required positioning term: $requiredTerm"
        }
    }
}

Write-Host "Running Business Confidentiality Audit..."

$businessRiskTerms = @(
    (Join-Term @("Euro", "link")),
    (Join-Term @("euro", "link")),
    (Join-Term @("New", " ", "Fada")),
    (Join-Term @("RX", " ", "Consult")),
    (Join-Term @("euro", "link", "-v", "48", "-ui")),
    (Join-Term @("v", "48")),
    (From-Codepoints @(24847,22823,21033,32442,32455,20132,27969,24179,21488)),
    (From-Codepoints @(20013,22269,21697,29260,36827,20837,27431,27954)),
    (From-Codepoints @(20013,22269,21697,29260,36827,20837,24847,22823,21033)),
    (From-Codepoints @(23458,25143,20013,24515)),
    (From-Codepoints @(31169,22495,21830,26426)),
    (From-Codepoints @(20844,22495,20114,21160,27744)),
    (From-Codepoints @(65,73,32,21019,20316,21488)),
    (From-Codepoints @(21457,24067,19982,35302,36798)),
    (From-Codepoints @(20114,21160,19982,23458,25143)),
    (From-Codepoints @(24066,22330,20998,26512)),
    (From-Codepoints @(66,31471,31169,22495)),
    (From-Codepoints @(20844,22495,39640,24847,21521)),
    (From-Codepoints @(73,110,115,116,97,103,114,97,109,32,22238,27969)),
    (From-Codepoints @(83,104,111,112,105,102,121,32,19978,26550)),
    (Join-Term @("Meta", " ", "Graph", " ", "API")),
    (Join-Term @("Str", "ipe")),
    (Join-Term @("TA", "RIC")),
    (Join-Term @("Euro", "stat")),
    (Join-Term @("EUR", "-Lex")),
    (From-Codepoints @(82,65,71,32,30693,35782,24211)),
    (From-Codepoints @(21830,19994,38381,29615)),
    (From-Codepoints @(30408,21033,27169,24335)),
    (From-Codepoints @(35746,38405)),
    (From-Codepoints @(28857,25968)),
    (Join-Term @("bill", "ing")),
    (Join-Term @("C", "RM")),
    (Join-Term @("lead", "_contact")),
    (From-Codepoints @(30495,23454,23458,25143)),
    (From-Codepoints @(30495,23454,21512,20316,26041)),
    (From-Codepoints @(25216,26415,24635,30417))
)

foreach ($term in $businessRiskTerms) {
    $matches = Select-String -Path $textFiles -Pattern $term -SimpleMatch -CaseSensitive -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        $relative = Get-RepoRelativePath $match.Path
        Add-Failure $failures "Business confidentiality risk term found in ${relative}:$($match.LineNumber)"
    }
}

$chargeTerm = Join-Term @("bill", "ing")
$customerSystemTerm = Join-Term @("c", "rm")
$privateContactTerm = Join-Term @("lead", "_contact")
$retrievalTerm = Join-Term @("r", "ag")

$contextRiskPatterns = @(
    @{
        Label = "commercial ops context";
        Pattern = "(?i)\b(" + [regex]::Escape($chargeTerm) + "|" + [regex]::Escape($customerSystemTerm) + ")\b"
    },
    @{
        Label = "private contact table context";
        Pattern = "(?i)\b" + [regex]::Escape($privateContactTerm) + "\b"
    },
    @{
        Label = "retrieval knowledge-base context";
        Pattern = "(?i)\b" + [regex]::Escape($retrievalTerm) + "\b.{0,24}\b(knowledge|database|base|kb)\b|\b(knowledge|database|base|kb)\b.{0,24}\b" + [regex]::Escape($retrievalTerm) + "\b"
    }
)

foreach ($risk in $contextRiskPatterns) {
    $matches = Select-String -Path $textFiles -Pattern $risk.Pattern -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        $relative = Get-RepoRelativePath $match.Path
        Add-Failure $failures "Business confidentiality contextual risk ($($risk.Label)) found in ${relative}:$($match.LineNumber)"
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
Write-Host "Required files, Safe Demo constraints, confidentiality gate, and secret checks look good."
