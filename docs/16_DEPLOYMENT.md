# Deployment Guide & Environment Setup
## Growpido Track B — Prospect to Diagnostic Intelligence Engine

---

### 1. System Prerequisites
Before deploying and launching the Growpido Prospect Intelligence Engine, verify that your environment satisfies the following baseline requirements:
- **Operating System:** Windows 10/11, macOS (Sonoma+), or Linux (Ubuntu 22.04 LTS / Debian 12).
- **Python Runtime:** Python `3.11.x` or `3.12.x` (64-bit).
- **Package Manager:** `pip` (v23.0+) or `uv` (recommended for ultra-fast installs).
- **Git:** Git 2.40+ installed and configured.
- **Docker (Optional):** Docker Engine 24.0+ & Docker Compose v2 for containerized deployment.

---

### 2. Local Installation & Setup Walkthrough

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/growpido-prospect-intelligence.git
cd growpido-prospect-intelligence
```

#### Step 2: Create & Activate Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### Step 3: Install Core Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables
Copy the template configuration and supply your API keys:
```bash
cp .env.example .env
```
Edit `.env` using your preferred editor:
```ini
# --- LLM API Credentials ---
# Option A: Google Gemini (Recommended default)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Option B: OpenAI (Optional fallback)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# --- OSINT Search Providers ---
# Primary Search API (Tavily)
TAVILY_API_KEY=your_tavily_api_key_here

# Enable automatic fallback to DuckDuckGo if primary key is absent
ALLOW_DUCKDUCKGO_FALLBACK=true

# --- Application & Storage ---
SQLITE_DB_PATH=data/growpido.db
ENABLE_HUMAN_GATE=true
DEBUG_MODE=false
```

#### Step 5: Initialize Database Schema
```bash
python -m src.storage.db --init
```

#### Step 6: Run Application (Streamlit UI)
```bash
streamlit run src/app.py --server.port 8501
```
Open your browser and navigate to: `http://localhost:8501`.

---

### 3. Containerized Deployment (Docker)

For reproducible, zero-configuration evaluation, a production Dockerfile and Docker Compose configuration are provided.

#### Build & Run via Docker Compose:
```bash
# Build the container image
docker compose build

# Launch the container in detached mode
docker compose up -d

# View live application logs
docker compose logs -f
```
Access the application at `http://localhost:8501`.

#### Standalone Docker Run:
```bash
docker build -t growpido-engine:v1 .
docker run -p 8501:8501 --env-file .env growpido-engine:v1
```

---

### 4. Verification & Health Check Procedure
Verify that all subsystems are functional by executing the automated test suite:
```bash
pytest tests/ -v
```
Expected output:
```text
tests/test_ingest.py::test_valid_linkedin_url PASSED               [ 12%]
tests/test_discovery.py::test_tier_classification PASSED          [ 25%]
tests/test_verification.py::test_double_check_protocol PASSED    [ 50%]
tests/test_verification.py::test_contradiction_detection PASSED   [ 62%]
tests/test_refusal.py::test_unverified_claim_refusal PASSED        [ 75%]
tests/test_gap_synthesizer.py::test_three_gap_generation PASSED    [ 87%]
tests/test_e2e.py::test_full_prospect_run PASSED                   [100%]
============================== 7 passed in 4.15s ==============================
```
