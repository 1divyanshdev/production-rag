# Production RAG - Comprehensive Testing Protocol

**Repository:** `z:\GENAI PROJECTS\production-rag`  
**Purpose:** Systematic verification of all components before PyPI release  
**Tester:** OpenCode / AI Assistant  

---

## 📋 Testing Instructions

You are tasked with **thoroughly testing** the Production RAG library and application. This is a **critical pre-release verification**. Test everything methodically and report all results.

### Your Mission:
1. Execute each test section below in order
2. Record **exact outputs, errors, and warnings**
3. Note **successes** with ✅ and **failures** with ❌
4. Compile a **final report** at the end with all issues found
5. Do NOT fix issues - only report them

### Environment Setup:
- **Working directory:** `z:\GENAI PROJECTS\production-rag`
- **Python environment:** `.venv` (already created)
- **Configuration:** `.env` file exists with API keys
- **Operating System:** Windows 11
- **Shell:** PowerShell

---

## 🧪 TEST SUITE

---

### **TEST SECTION 1: Environment Verification**

#### Test 1.1: Python Environment
```powershell
cd "z:\GENAI PROJECTS\production-rag"
.venv\Scripts\python.exe --version
```
**Expected:** Python 3.11.x or 3.12.x  
**Record:** Exact version number

#### Test 1.2: Dependencies Installed
```powershell
.venv\Scripts\python.exe -m pip list | Select-String -Pattern "pymupdf|pydantic|qdrant|fastapi"
```
**Expected:** All packages installed  
**Record:** Version numbers

#### Test 1.3: Package Installed in Editable Mode
```powershell
.venv\Scripts\python.exe -m pip show production-rag
```
**Expected:** Shows package info with Location pointing to current directory  
**Record:** Installation status

#### Test 1.4: Environment Variables
```powershell
Test-Path .env
```
**Expected:** True  
**Record:** Whether .env file exists (DO NOT display contents - contains secrets)

---

### **TEST SECTION 2: Package Imports and Structure**

#### Test 2.1: Basic Library Import
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGPipeline, RAGConfig; print('✅ Import successful')"
```
**Expected:** `✅ Import successful`  
**Record:** Any import errors

#### Test 2.2: All Public Exports
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGPipeline, RAGConfig, QueryResult, IndexingResult, EmbeddingSettings, LLMSettings, VectorStoreSettings, RetrievalSettings, GeneratedAnswer, Chunk, Document, ScoredChunk, PDFParseError, EmbeddingError, LLMError, VectorStoreError; print('✅ All exports available')"
```
**Expected:** `✅ All exports available`  
**Record:** Any missing exports

#### Test 2.3: Package Metadata
```powershell
.venv\Scripts\python.exe -c "import rag_core; print(f'Version: {rag_core.__version__}'); print(f'Exports: {len(rag_core.__all__)}')"
```
**Expected:** Version: 0.1.0, Exports: 19  
**Record:** Actual values

#### Test 2.4: No FastAPI Dependency in Core
```powershell
.venv\Scripts\python.exe -c "import sys; from rag_core import RAGPipeline; fastapi_imported = 'fastapi' in sys.modules; print(f'FastAPI imported: {fastapi_imported}')"
```
**Expected:** `FastAPI imported: False`  
**Record:** Actual result (CRITICAL: should be False)

---

### **TEST SECTION 3: Configuration System**

#### Test 3.1: RAGConfig Initialization (Default)
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGConfig; config = RAGConfig(); print(f'✅ Config created'); print(f'Embedding provider: {config.embedding_settings.provider}')"
```
**Expected:** Config created successfully  
**Record:** Any errors

#### Test 3.2: RAGConfig with Explicit Settings
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGConfig, EmbeddingSettings; es = EmbeddingSettings(api_key='test', provider='jina'); config = RAGConfig(embedding_settings=es); print(f'✅ Explicit config works')"
```
**Expected:** Success  
**Record:** Any errors

#### Test 3.3: Settings Validation
```powershell
.venv\Scripts\python.exe -c "from rag_core import EmbeddingSettings; try: es = EmbeddingSettings(provider='invalid'); except Exception as e: print(f'✅ Validation works: {type(e).__name__}')"
```
**Expected:** Validation error caught  
**Record:** Error type

---

### **TEST SECTION 4: Core Library Functionality**

#### Test 4.1: RAGPipeline Initialization
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGPipeline, RAGConfig; config = RAGConfig(); rag = RAGPipeline(config); print(f'✅ Pipeline initialized'); print(f'Embedder model: {rag.embedder.model}'); print(f'Embedder dimension: {rag.embedder.dimension}')"
```
**Expected:** Pipeline initialized, embedder details shown  
**Record:** All output, any errors

#### Test 4.2: Vector Store Initialization
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGPipeline; rag = RAGPipeline(); print(f'✅ Vector store ready'); print(f'Collection: {rag.vector_store.settings.collection}'); print(f'Mode: {\"server\" if rag.vector_store.settings.url else \"embedded\"}')"
```
**Expected:** Vector store initialized in embedded mode  
**Record:** Collection name and mode

#### Test 4.3: LLM Provider Lazy Loading
```powershell
.venv\Scripts\python.exe -c "from rag_core import RAGPipeline; rag = RAGPipeline(); print(f'LLM loaded initially: {rag._llm_provider is not None}'); _ = rag.llm_provider; print(f'LLM loaded after access: {rag._llm_provider is not None}')"
```
**Expected:** False initially, True after access  
**Record:** Lazy loading behavior

---

### **TEST SECTION 5: Offline Test Suite**

#### Test 5.1: Run All Tests
```powershell
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```
**Expected:** All tests pass (177 tests)  
**Record:** 
- Total tests run
- Passed count
- Failed count (should be 0)
- Skipped count
- Any warnings
- Total time taken
- **If any failures, copy FULL error messages**

#### Test 5.2: Library-Specific Tests Only
```powershell
.venv\Scripts\python.exe -m pytest tests/library/ -v --tb=short
```
**Expected:** 35 library tests pass  
**Record:** Pass/fail count

#### Test 5.3: Component Unit Tests Only
```powershell
.venv\Scripts\python.exe -m pytest tests/unit/ -v --tb=short
```
**Expected:** 142 unit tests pass  
**Record:** Pass/fail count

---

### **TEST SECTION 6: Examples Execution**

#### Test 6.1: Check Examples Exist
```powershell
Get-ChildItem examples\*.py | Select-Object Name
```
**Expected:** 5 Python files listed  
**Record:** File names

#### Test 6.2: Import Test for Each Example
Test that each example file has valid syntax (don't run, just import):

```powershell
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'examples'); import importlib.util; spec = importlib.util.spec_from_file_location('example', 'examples/01_basic_usage.py'); print('✅ Example 1 syntax valid' if spec else '❌ Example 1 invalid')"
```

Repeat for examples 02-05, recording results for each.

#### Test 6.3: Example README Exists
```powershell
Test-Path examples\README.md
```
**Expected:** True  
**Record:** Exists or not

---

### **TEST SECTION 7: Backend Integration**

#### Test 7.1: Backend Can Import Library
```powershell
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from backend.app.api.deps import get_services; print('✅ Backend imports library successfully')"
```
**Expected:** Success  
**Record:** Any import errors

#### Test 7.2: Backend Startup Test (Dry Run)
```powershell
.venv\Scripts\python.exe -c "from backend.app.main import app; print(f'✅ FastAPI app created'); print(f'Routes: {len(app.routes)}')"
```
**Expected:** App created, routes listed  
**Record:** Number of routes

#### Test 7.3: Start Backend Server (Actual)
```powershell
Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--port", "8000" -PassThru
```

Wait 5 seconds, then test:

```powershell
Start-Sleep -Seconds 5
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -Method GET
```

**Expected:** 200 OK response with JSON  
**Record:** 
- HTTP status code
- Response body
- Any connection errors

**IMPORTANT:** After testing, stop the backend process

---

### **TEST SECTION 8: Frontend Integration**

#### Test 8.1: Frontend Environment Configuration
```powershell
Test-Path frontend\.env.local
```
**Expected:** True  
**Record:** File exists

#### Test 8.2: Check Frontend Environment Variable
```powershell
Get-Content frontend\.env.local | Select-String "NEXT_PUBLIC_API_URL"
```
**Expected:** Contains `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`  
**Record:** Actual value (without sensitive data)

#### Test 8.3: Frontend Dependencies
```powershell
cd frontend
Test-Path node_modules
```
**Expected:** True (dependencies installed)  
**Record:** Result

#### Test 8.4: Frontend API Client Types
```powershell
Get-Content frontend\lib\api.ts | Select-String "export interface" | Measure-Object -Line
```
**Expected:** Multiple interfaces exported  
**Record:** Count

---

### **TEST SECTION 9: Documentation Verification**

#### Test 9.1: Main README Exists and Has Content
```powershell
$readme = Get-Content README.md -Raw
$readme.Length -gt 5000
```
**Expected:** True (substantial content)  
**Record:** Character count

#### Test 9.2: README Has Badges
```powershell
Get-Content README.md | Select-String -Pattern "badge" | Measure-Object -Line
```
**Expected:** At least 3 badges  
**Record:** Count

#### Test 9.3: Study Guide Exists
```powershell
$guide = Get-Content docs\PYTHON_LIBRARY_GUIDE.md -Raw
$guide.Length -gt 10000
```
**Expected:** True (comprehensive guide)  
**Record:** Character count

#### Test 9.4: Study Guide Has All Sections
```powershell
$sections = @(
    "Project Overview",
    "What Existed Before and What Changed",
    "Repository Map",
    "Architecture Diagrams",
    "Installation and First Use",
    "Public API Explained",
    "Complete Ingestion Execution Flow",
    "Complete Question-Answering Execution Flow",
    "Configuration and Provider Architecture",
    "Data Structures and Error Handling",
    "Library-to-FastAPI Integration",
    "Testing and Verification",
    "Debugging Guide",
    "Design Decisions",
    "How to Extend the Library",
    "Current Limitations",
    "Complete Build Walkthrough"
)

foreach ($section in $sections) {
    $found = Select-String -Path docs\PYTHON_LIBRARY_GUIDE.md -Pattern $section -Quiet
    Write-Output "${section}: $found"
}
```
**Expected:** All sections present (True)  
**Record:** Any missing sections

#### Test 9.5: LICENSE File Exists
```powershell
Test-Path LICENSE
Get-Content LICENSE | Select-String "MIT License"
```
**Expected:** File exists, contains MIT License  
**Record:** Result

#### Test 9.6: CONTRIBUTING Guide Exists
```powershell
Test-Path CONTRIBUTING.md
```
**Expected:** True  
**Record:** Result

---

### **TEST SECTION 10: CI/CD Verification**

#### Test 10.1: GitHub Actions Workflow Exists
```powershell
Test-Path .github\workflows\test.yml
```
**Expected:** True  
**Record:** Result

#### Test 10.2: Workflow Configuration Valid
```powershell
Get-Content .github\workflows\test.yml | Select-String -Pattern "pytest|python-version"
```
**Expected:** Contains pytest and python-version  
**Record:** Lines found

#### Test 10.3: Workflow Tests Both Python Versions
```powershell
(Get-Content .github\workflows\test.yml -Raw) -match "3.11.*3.12"
```
**Expected:** True (tests 3.11 and 3.12)  
**Record:** Result

---

### **TEST SECTION 11: Package Metadata**

#### Test 11.1: pyproject.toml Exists and Valid
```powershell
Test-Path pyproject.toml
Get-Content pyproject.toml | Select-String -Pattern "name.*=.*production-rag"
```
**Expected:** File exists, name is "production-rag"  
**Record:** Result

#### Test 11.2: Version Number Consistent
```powershell
$pyproject_version = (Get-Content pyproject.toml | Select-String 'version = "(.+)"').Matches.Groups[1].Value
$init_version = (Get-Content rag_core\__init__.py | Select-String '__version__ = "(.+)"').Matches.Groups[1].Value
Write-Output "pyproject.toml: $pyproject_version"
Write-Output "__init__.py: $init_version"
Write-Output "Match: $($pyproject_version -eq $init_version)"
```
**Expected:** Both versions are "0.1.0" and match  
**Record:** Versions and whether they match

#### Test 11.3: Dependencies Separated
```powershell
Get-Content pyproject.toml | Select-String -Pattern "\[project.optional-dependencies\]" -Context 0,10
```
**Expected:** Shows optional dependencies (api, dev)  
**Record:** Optional dependency groups found

---

### **TEST SECTION 12: Git Repository Status**

#### Test 12.1: Check Git Status
```powershell
cd "z:\GENAI PROJECTS\production-rag"
git status --short
```
**Expected:** Clean or showing new files from testing  
**Record:** Output (untracked files, modifications)

#### Test 12.2: Recent Commits
```powershell
git log --oneline -5
```
**Expected:** Recent commits visible  
**Record:** Last 5 commit messages

#### Test 12.3: Remote Repository
```powershell
git remote -v
```
**Expected:** Origin points to GitHub  
**Record:** Remote URL

---

### **TEST SECTION 13: File Structure Validation**

#### Test 13.1: Core Package Structure
```powershell
Get-ChildItem rag_core -Directory | Select-Object Name
```
**Expected:** Subdirectories: chunking, embeddings, generation, ingestion, llm, models, retrieval, vector_stores  
**Record:** Actual directories found

#### Test 13.2: All __init__.py Files Present
```powershell
Get-ChildItem rag_core -Recurse -Filter "__init__.py" | Measure-Object
```
**Expected:** Multiple __init__.py files  
**Record:** Count

#### Test 13.3: No __pycache__ in Git
```powershell
git ls-files | Select-String "__pycache__"
```
**Expected:** No results (pycache should be gitignored)  
**Record:** Any pycache files in git

---

### **TEST SECTION 14: Critical Functionality Smoke Test**

⚠️ **IMPORTANT:** These tests require valid API keys in .env

#### Test 14.1: Create Minimal Test PDF
```powershell
.venv\Scripts\python.exe -c "
import pymupdf
doc = pymupdf.open()
page = doc.new_page()
page.insert_text((50, 50), 'Test document content for Production RAG.', fontsize=12)
doc.save('test_doc.pdf')
doc.close()
print('✅ Test PDF created: test_doc.pdf')
"
```
**Expected:** test_doc.pdf created  
**Record:** Success or error

#### Test 14.2: Index Test Document
```powershell
.venv\Scripts\python.exe -c "
from rag_core import RAGPipeline
rag = RAGPipeline()
try:
    result = rag.index_document('test_doc.pdf')
    print(f'✅ Indexed: {result.indexed_chunks} chunks')
    print(f'Document ID: {result.document_id}')
    print(f'Duplicate: {result.skipped_duplicate}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```
**Expected:** Document indexed successfully  
**Record:** Chunks indexed, document ID, or error

#### Test 14.3: Query Test Document
```powershell
.venv\Scripts\python.exe -c "
from rag_core import RAGPipeline
rag = RAGPipeline()
try:
    answer = rag.query('What is in the document?')
    print(f'✅ Query executed')
    print(f'Answer: {answer.answer[:100]}...')
    print(f'Sources: {len(answer.sources)}')
    print(f'Refused: {answer.refused}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```
**Expected:** Answer generated with sources  
**Record:** Answer snippet, source count, refused status, or error

#### Test 14.4: Cleanup Test Files
```powershell
Remove-Item test_doc.pdf -ErrorAction SilentlyContinue
Remove-Item -Recurse qdrant_storage -ErrorAction SilentlyContinue
```
**Expected:** Test files removed  
**Record:** Cleanup status

---

## 📊 FINAL REPORT FORMAT

After completing all tests, compile a report with this structure:

```markdown
# Production RAG Testing Report

**Date:** [Current Date]
**Tester:** [Your Name/ID]
**Repository:** z:\GENAI PROJECTS\production-rag
**Commit:** [Git commit hash]

## Executive Summary
- Total Tests: [X]
- Passed: [X] ✅
- Failed: [X] ❌
- Warnings: [X] ⚠️
- Overall Status: [PASS/FAIL with issues/FAIL]

## Test Results by Section

### Section 1: Environment Verification
- Test 1.1: [PASS/FAIL] - [Details]
- Test 1.2: [PASS/FAIL] - [Details]
[... continue for all tests ...]

## Critical Issues Found
1. [Issue description]
   - Test: [Test number]
   - Severity: [Critical/High/Medium/Low]
   - Error: [Exact error message]
   - Impact: [What breaks]

2. [Next issue...]

## Warnings and Minor Issues
1. [Warning description]
   - Test: [Test number]
   - Recommendation: [What should be fixed]

## Verification Status

### ✅ Working Correctly:
- [List of confirmed working features]

### ❌ Needs Fixing:
- [List of broken features]

### ⚠️ Needs Attention:
- [List of issues that need review]

## Recommendations
1. [Priority 1 fixes]
2. [Priority 2 improvements]
3. [Optional enhancements]

## Raw Test Outputs
[Attach or link to complete test logs]
```

---

## 🎯 SUCCESS CRITERIA

For Production RAG to be considered **ready for PyPI release**, the following must ALL pass:

### Critical (Must Pass):
- ✅ All 177 tests pass (TEST SECTION 5)
- ✅ Library imports without FastAPI (TEST SECTION 2.4)
- ✅ RAGPipeline initializes (TEST SECTION 4.1)
- ✅ Package metadata correct (TEST SECTION 11)
- ✅ CI/CD workflow exists (TEST SECTION 10)
- ✅ LICENSE file present (TEST SECTION 9.5)

### Important (Should Pass):
- ✅ All documentation complete (TEST SECTION 9)
- ✅ Backend can use library (TEST SECTION 7)
- ✅ Examples have valid syntax (TEST SECTION 6)
- ✅ Frontend configuration correct (TEST SECTION 8)

### Nice to Have (Can fix later):
- ⚠️ Smoke tests with real API (TEST SECTION 14)
- ⚠️ Frontend fully functional (requires backend running)

---

## 🚨 IMPORTANT NOTES

1. **Do NOT commit .env file** - it contains secrets
2. **Do NOT display API keys** in the report
3. **Record EXACT error messages** - don't paraphrase
4. **If a test hangs**, wait 30 seconds then stop and report
5. **If backend/frontend start**, stop them after testing
6. **Clean up test files** after smoke tests
7. **If ANY critical test fails**, mark overall status as FAIL

---

## 📝 DELIVERABLES

1. **Complete test execution** (run all sections)
2. **Detailed report** (using format above)
3. **List of all issues** (prioritized by severity)
4. **Recommendation** (Ready for PyPI: Yes/No/With fixes)

---

**BEGIN TESTING NOW**

Execute each test section in order. Record everything. Report back with the complete findings.

Good luck! 🚀
