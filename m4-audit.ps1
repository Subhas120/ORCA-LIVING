$ErrorActionPreference = "Continue"

$Root = (Get-Location).Path

$Pass = 0
$Warn = 0
$Fail = 0

function PASS {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
    $script:Pass++
}

function WARN {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
    $script:Warn++
}

function FAIL {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    $script:Fail++
}

function SECTION {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Get-FileText {
    param([string]$RelativePath)

    $Path = Join-Path $Root $RelativePath

    if (Test-Path $Path) {
        return Get-Content $Path -Raw
    }

    return ""
}

# ============================================================
# 1. REPOSITORY
# ============================================================

SECTION "1. REPOSITORY"

if (Test-Path (Join-Path $Root ".git")) {
    PASS "Git repository detected"
}
else {
    FAIL "Git repository missing"
}

$RequiredFiles = @(
    "backend\main.py",
    "backend\api\router.py",
    "backend\api\voice_router.py",
    "backend\models\request.py",
    "backend\models\response.py",
    "backend\services\decision_service.py",
    "backend\services\m1_service.py",
    "backend\services\m2_adapter.py",
    "backend\services\response_adapter.py",
    "backend\services\voice\voice_pipeline.py",
    "backend\services\voice\translation_provider.py",
    "agents\common\agent_contract.py",
    "agents\ocean\ocean_agent.py",
    "agents\ocean\safety.py",
    "orca_living\engines\decision_pipeline.py",
    "src\App.jsx",
    "src\services\m4Adapter.js"
)

foreach ($File in $RequiredFiles) {
    $Path = Join-Path $Root $File

    if (Test-Path $Path) {
        PASS "Exists: $File"
    }
    else {
        FAIL "Missing: $File"
    }
}

# ============================================================
# 2. GIT
# ============================================================

SECTION "2. GIT STATUS"

git status --short

$Branch = git branch --show-current 2>$null

if ($Branch) {
    PASS "Branch: $Branch"
}
else {
    WARN "Could not determine current branch"
}

# ============================================================
# 3. PYTHON IMPORTS
# ============================================================

SECTION "3. PYTHON IMPORTS"

$ImportTests = @(
    "from backend.main import app",
    "from backend.api.router import router",
    "from backend.api.voice_router import router",
    "from backend.services.decision_service import decision_service",
    "from backend.services.m1_service import M1Service",
    "from backend.services.m2_adapter import M2Adapter",
    "from backend.services.response_adapter import ResponseAdapter",
    "from agents.ocean.ocean_agent import handle_ocean",
    "from agents.ocean.safety import assess_marine_safety"
)

foreach ($ImportTest in $ImportTests) {

    $Code = $ImportTest + "`nprint('IMPORT_OK')"

    $Output = $Code | python 2>&1

    if ($Output -match "IMPORT_OK") {
        PASS "Import OK: $ImportTest"
    }
    else {
        FAIL "Import failed: $ImportTest"
        Write-Host ($Output | Select-Object -Last 5)
    }
}

# ============================================================
# 4. M2
# ============================================================

SECTION "4. M2 CONTRACT"

$M2Contract = Get-FileText "agents\common\agent_contract.py"
$M2Ocean = Get-FileText "agents\ocean\ocean_agent.py"
$M2Safety = Get-FileText "agents\ocean\safety.py"

if ($M2Contract -match "scenario_id") {
    PASS "AgentRequest has scenario_id"
}
else {
    FAIL "AgentRequest missing scenario_id"
}

if ($M2Ocean -match "apply_demo_scenario") {
    PASS "M2 has demo scenario application"
}
else {
    FAIL "M2 demo scenario application missing"
}

if ($M2Ocean -match "UNSAFE_WEATHER") {
    PASS "UNSAFE_WEATHER scenario exists"
}
else {
    FAIL "UNSAFE_WEATHER scenario missing"
}

if ($M2Ocean -match "INSUFFICIENT_EVIDENCE") {
    PASS "INSUFFICIENT_EVIDENCE scenario exists"
}
else {
    FAIL "INSUFFICIENT_EVIDENCE scenario missing"
}

if ($M2Ocean -match "assess_marine_safety") {
    PASS "M2 calls its safety authority"
}
else {
    FAIL "M2 safety authority call missing"
}

if ($M2Safety -match "WAVE_HEIGHT_LIMIT") {
    PASS "Wave safety threshold exists"
}
else {
    WARN "Wave safety threshold not detected"
}

if ($M2Safety -match "CURRENT_SPEED_LIMIT") {
    PASS "Current safety threshold exists"
}
else {
    WARN "Current safety threshold not detected"
}

# ============================================================
# 5. M1 + SHARED M4 ORCHESTRATION
# ============================================================

SECTION "5. M1 + M4 ORCHESTRATION"

$M1 = Get-FileText "backend\services\m1_service.py"
$DecisionService = Get-FileText "backend\services\decision_service.py"
$Router = Get-FileText "backend\api\router.py"
$VoiceRouter = Get-FileText "backend\api\voice_router.py"

if ($M1 -match "DecisionIntelligencePipeline") {
    PASS "M4 uses DecisionIntelligencePipeline"
}
else {
    FAIL "DecisionIntelligencePipeline not found in M1Service"
}

if ($M1 -match "\.run") {
    PASS "M1Service calls pipeline.run()"
}
else {
    FAIL "M1Service does not call pipeline.run()"
}

if ($DecisionService -match "M1Service" -and $DecisionService -match "M2Adapter" -and $DecisionService -match "ResponseAdapter") {
    PASS "Shared DecisionService owns M2 -> M1 -> M4 orchestration"
}
else {
    FAIL "Shared DecisionService orchestration contract incomplete"
}

if ($Router -match "decision_service\.run") {
    PASS "REST router delegates to shared DecisionService"
}
else {
    FAIL "REST router does not use shared DecisionService"
}

if ($VoiceRouter -match "decision_service\.run") {
    PASS "Voice router delegates to shared DecisionService"
}
else {
    FAIL "Voice router does not use shared DecisionService"
}

if ($VoiceRouter -notmatch "def _run_decision[\s\S]{0,300}M1Service") {
    PASS "Voice router does not contain a second M1 orchestration engine"
}
else {
    FAIL "Voice router contains duplicate M1 orchestration"
}

# ============================================================
# 6. RESPONSE MODEL
# ============================================================

SECTION "6. RESPONSE MODEL"

$Response = Get-FileText "backend\models\response.py"

$ResponseFields = @(
    "recommendedCandidate",
    "alternativeCandidates",
    "rejectedCandidates",
    "decisionSummary",
    "tradeoffs",
    "uncertainty",
    "evidence",
    "sensitivity",
    "paretoCandidateIds",
    "robustness",
    "valueOfInformation",
    "counterfactuals",
    "explanation",
    "decisionTrace",
    "confidence",
    "marineSafetyStatus",
    "marineSafetyReasons",
    "dataMode"
)

foreach ($Field in $ResponseFields) {

    if ($Response -match $Field) {
        PASS "Response contains $Field"
    }
    else {
        FAIL "Response missing $Field"
    }
}

# ============================================================
# 7. RESPONSE ADAPTER
# ============================================================

SECTION "7. RESPONSE ADAPTER"

$Adapter = Get-FileText "backend\services\response_adapter.py"

foreach ($Field in $ResponseFields) {

    if ($Adapter -match $Field) {
        PASS "Adapter handles $Field"
    }
    else {
        WARN "Adapter does not explicitly contain $Field"
    }
}

# ============================================================
# 8. SAFETY
# ============================================================

SECTION "8. SAFETY PROPAGATION"

if ($DecisionService -match "marine_safety_status") {
    PASS "Shared DecisionService reads marine safety status"
}
else {
    FAIL "Shared DecisionService does not read marine safety status"
}

if ($DecisionService -match "INSUFFICIENT_EVIDENCE") {
    PASS "Shared DecisionService handles insufficient evidence"
}
else {
    FAIL "Shared DecisionService missing insufficient evidence handling"
}

if ($DecisionService -match "NO_SAFE_CANDIDATES") {
    PASS "Shared DecisionService handles no-safe-candidates"
}
else {
    FAIL "Shared DecisionService missing no-safe-candidates handling"
}

if ($DecisionService -match "marineSafetyStatus") {
    PASS "DecisionService forwards marine safety status"
}
else {
    FAIL "DecisionService does not forward marine safety status"
}

if ($DecisionService -match "M1 returned a recommendation despite") {
    PASS "Unsafe M1 contract violation fails closed"
}
else {
    FAIL "Unsafe M1 contract guard missing"
}

if ($Adapter -match "marineSafetyStatus") {
    PASS "Adapter preserves marine safety status"
}
else {
    FAIL "Adapter loses marine safety status"
}

if ($Adapter -match "marineSafetyReasons") {
    PASS "Adapter preserves marine safety reasons"
}
else {
    FAIL "Adapter loses marine safety reasons"
}

# ============================================================
# 9. FRONTEND
# ============================================================

SECTION "9. FRONTEND CONTRACT"

$FrontendAdapter = Get-FileText "src\services\m4Adapter.js"
$App = Get-FileText "src\App.jsx"

$FrontendFields = @(
    "marineSafetyStatus",
    "marineSafetyReasons",
    "recommendedCandidate",
    "rejectedCandidates",
    "decisionTrace",
    "paretoCandidateIds",
    "tradeoffs",
    "uncertainty",
    "evidence"
)

foreach ($Field in $FrontendFields) {

    if ($FrontendAdapter -match $Field) {
        PASS "Frontend adapter handles $Field"
    }
    else {
        FAIL "Frontend adapter missing $Field"
    }
}

if ($FrontendAdapter -match "recommended\?\.safety\s*===\s*1") {
    FAIL "Frontend reconstructs safety from candidate.safety"
}
else {
    PASS "Old candidate.safety safety reconstruction not detected"
}

if ($FrontendAdapter -match "response\.marineSafetyStatus") {
    PASS "Frontend uses M4 marineSafetyStatus"
}
else {
    FAIL "Frontend does not use M4 marineSafetyStatus"
}

if ($FrontendAdapter -match "response\.marineSafetyReasons") {
    PASS "Frontend uses M4 marineSafetyReasons"
}
else {
    FAIL "Frontend does not use M4 marineSafetyReasons"
}

# ============================================================
# 10. REQUEST
# ============================================================

SECTION "10. REQUEST MODEL"

$Request = Get-FileText "backend\models\request.py"

$RequestFields = @(
    "query",
    "location",
    "date",
    "time",
    "activity",
    "vessel_type",
    "scenario_id"
)

foreach ($Field in $RequestFields) {

    if ($Request -match $Field) {
        PASS "Request supports $Field"
    }
    else {
        FAIL "Request missing $Field"
    }
}

# ============================================================
# 11. VOICE
# ============================================================

SECTION "11. VOICE"

$Voice = Get-FileText "backend\services\voice\voice_pipeline.py"
$Translation = Get-FileText "backend\services\voice\translation_provider.py"
$VoiceRouter = Get-FileText "backend\api\voice_router.py"

if ($Voice.Length -gt 0) {
    PASS "Voice pipeline exists"
}
else {
    FAIL "Voice pipeline is empty or missing"
}

if ($Translation.Length -gt 0) {
    PASS "Translation provider exists"
}
else {
    FAIL "Translation provider is empty or missing"
}

if ($VoiceRouter.Length -gt 0) {
    PASS "Voice router exists"
}
else {
    FAIL "Voice router is empty or missing"
}

if ($Voice -match "language") {
    PASS "Voice pipeline has language handling"
}
else {
    WARN "Language handling not detected in voice pipeline"
}

if ($Translation -match "translate") {
    PASS "Translation operation detected"
}
else {
    WARN "Translation operation not clearly detected"
}

# ============================================================
# 12. TEST SUITE
# ============================================================

SECTION "12. PYTEST"

python -m pytest agents backend/tests -q

if ($LASTEXITCODE -eq 0) {
    PASS "Pytest passed"
}
else {
    FAIL "Pytest failed"
}

# ============================================================
# 13. HEALTH
# ============================================================

SECTION "13. BACKEND HEALTH"

try {

    $Health = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8000/health" `
        -Method Get `
        -TimeoutSec 5 `
        -ErrorAction Stop

    PASS "Backend health endpoint reachable"

    $Health | ConvertTo-Json -Depth 10

}
catch {

    WARN "Backend not reachable on port 8000"
    Write-Host "Start backend with:"
    Write-Host "python -m uvicorn backend.main:app --reload --port 8000"
}

# ============================================================
# 14. API TEST FUNCTION
# ============================================================

function Test-DecisionScenario {

    param(
        [string]$Name,
        [string]$Scenario,
        [string]$ExpectedStatus,
        [string]$ExpectedSafety
    )

    Write-Host ""
    Write-Host "---- $Name ----" -ForegroundColor Magenta

    $BodyObject = @{
        query = "Find the best fishing zone"
        location = "Kochi"
        date = "tomorrow"
        time = "morning"
        activity = "fishing"
        vessel_type = "small_vessel"
        scenario_id = $Scenario
    }

    $Body = $BodyObject | ConvertTo-Json

    try {

        $Response = Invoke-RestMethod `
            -Uri "http://127.0.0.1:8000/api/v1/decision" `
            -Method Post `
            -ContentType "application/json" `
            -Body $Body `
            -TimeoutSec 15

        Write-Host ($Response | ConvertTo-Json -Depth 20)

        if ($Response.status -eq $ExpectedStatus) {
            PASS "$Name status = $ExpectedStatus"
        }
        else {
            FAIL "$Name expected status $ExpectedStatus but got $($Response.status)"
        }

        if ($Response.marineSafetyStatus -eq $ExpectedSafety) {
            PASS "$Name marineSafetyStatus = $ExpectedSafety"
        }
        elseif ($ExpectedSafety -eq "") {
            PASS "$Name safety expectation skipped"
        }
        else {
            FAIL "$Name expected safety $ExpectedSafety but got $($Response.marineSafetyStatus)"
        }

        if ($ExpectedStatus -eq "DECISION_AVAILABLE") {
            if ($null -ne $Response.recommendedCandidate) {
                PASS "$Name has recommended candidate"
            }
            else {
                FAIL "$Name missing recommended candidate"
            }
        }
        else {
            if ($null -eq $Response.recommendedCandidate) {
                PASS "$Name has no recommendation"
            }
            else {
                FAIL "$Name exposed recommendation in non-decision state"
            }
        }

        if ($ExpectedSafety -eq "UNSAFE") {
            if ($Response.status -ne "DECISION_AVAILABLE") {
                PASS "$Name unsafe state is not decision-available"
            }
            else {
                FAIL "$Name unsafe state reached DECISION_AVAILABLE"
            }
        }

    }
    catch {
        FAIL "$Name API request failed: $($_.Exception.Message)"
    }
}

# ============================================================
# 15. E2E DEMO SCENARIOS
# ============================================================

SECTION "15. E2E DEMO SCENARIOS"

Test-DecisionScenario `
    -Name "Normal safe" `
    -Scenario "PFZ_KOCHI_DEMO" `
    -ExpectedStatus "DECISION_AVAILABLE" `
    -ExpectedSafety "SAFE"

Test-DecisionScenario `
    -Name "Unsafe weather" `
    -Scenario "UNSAFE_WEATHER" `
    -ExpectedStatus "NO_SAFE_CANDIDATES" `
    -ExpectedSafety "UNSAFE"

Test-DecisionScenario `
    -Name "Insufficient evidence" `
    -Scenario "INSUFFICIENT_EVIDENCE" `
    -ExpectedStatus "INSUFFICIENT_EVIDENCE" `
    -ExpectedSafety "INSUFFICIENT_EVIDENCE"

# ============================================================
# 16. FINAL SUMMARY
# ============================================================

SECTION "16. AUDIT SUMMARY"

Write-Host "PASS: $Pass" -ForegroundColor Green
Write-Host "WARN: $Warn" -ForegroundColor Yellow
Write-Host "FAIL: $Fail" -ForegroundColor Red

if ($Fail -eq 0) {
    Write-Host "M4 AUDIT RESULT: PASS" -ForegroundColor Green
}
else {
    Write-Host "M4 AUDIT RESULT: FAIL" -ForegroundColor Red
}
