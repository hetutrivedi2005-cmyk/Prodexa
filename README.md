# Prodexa — Product Catalog Data Engineering, Matching & Evaluation Platform

Prodexa is an enterprise-grade product catalog data engineering, matching, enrichment, human-in-the-loop validation, grounded content generation, 252-column expected-output delivery format mapping, and web intelligence platform. It transforms raw, incomplete catalog feeds into highly structured, evidence-proven, validated, benchmarked, and commerce-ready product records.

---

## 🚀 Web Application & Architecture Stack

Prodexa includes a full-stack web application designed with an industrial blueprint aesthetic:

- **Backend API Server (`server.py`)**: Built with **FastAPI** running on `http://127.0.0.1:8000`, exposing JWT authentication, product catalog explorer endpoints, review queue actions (Accept, Edit, Reject, Escalate), evidence provenance APIs, dynamic report streaming, final output file downloads, and upload ingestion.
- **Frontend SPA (`frontend/`)**: Built with **React** + **Vite** running on `http://localhost:3000`, featuring:
  - **Dark Industrial Blueprint Design System**: `--bg: #0A0E13`, blueprint grid pattern backdrop, ambient radial glows, and Space Grotesk / Inter / IBM Plex Mono typography.
  - **Interactive 3D Stage**: 5 stacked process slabs (`01 Raw feed` → `05 Delivery`) with interactive mouse/touch parallax drag rotation and particle animations.
  - **Live Transformation & Evidence Inspector**: Side-by-side comparison of unstructured raw feeds vs. structured JSON records with evidence grounding quotes.
  - **Workspace Console**: User Dashboard, Catalog Explorer, Product Detail Inspector, HITL Review Queue, Evidence Provenance, Final Output Downloads, and Admin Control Center.

---

## 📊 Official Delivery Format Schema Audit & Delivery Layer

Prodexa provides a deterministic mapping layer that transforms internal product intelligence models to the official 252-column delivery format (`Unihack_ Expected Output - Delivery Format.csv`):

- **Final Delivery CSV**: `data/final/unihack_expected_output.csv` (1,000 rows × 252 columns, matching exact template column names and header ordering).
- **Schema Audit Report**: `reports/expected_output_schema_audit.txt` containing complete field-by-field mapping, population counts, percentages, and support category breakdown:
  - **Expected Schema Fields**: `252`
  - **Fields Originally Present in `enriched.csv`**: `22`
  - **Directly Matched Fields**: `17`
  - **Internal/Extra Metadata Fields**: `5` (`validation_status`, `confidence_score`, `confidence_decision`, `human_review_status`, `evidence_status`)
  - **Fields Not Directly Available in `enriched.csv`**: `235` (mapped deterministically from other pipeline outputs or left clean empty when genuinely unavailable)
  - **Populated Fields**: `63` (25.0%)
  - **Clean Empty Fields**: `189` (75.0%)
- **Support Category Breakdown**:
  - `FULLY_SUPPORTED` (>= 80% populated): **20 fields**
  - `PARTIALLY_SUPPORTED` (1% - 79% populated): **43 fields**
  - `NOT_SUPPORTED` (0% populated; clean empty strings): **189 fields**
  - **Category Verification Check**: $20 + 43 + 189 = 252$
- **Schema Validation Status**: `PASS` (Expected: 252, Generated: 252, Mismatch: 0, Duplicate: 0, Unexpected: 0, Rows: 1000).

---

## 🛠️ The 15 Intelligence Pipeline Phases

Prodexa consists of 15 modular processing, content generation, delivery, and evaluation phases:

### Phase 1 — Data Cleaning Engine (`src/cleaning/`)
- Sanitizes raw datasets by stripping vendor placeholders (`-- Unbranded --`, `n/a`, etc.).
- Normalizes Unicode text and formats manufacturer names consistently.
- Drops empty or duplicated entries, outputting `data/processed/cleaned_dataset.csv`.

### Phase 2 — Product Understanding Engine (`src/understanding/`)
- Structured attribute extraction (MPN, brand, product type, size, quantity) from descriptions using Google Gemini LLM via the official GenAI SDK.
- Implements description deduplication caching to minimize API traffic.
- Saves structured outputs to `data/processed/understood_products.csv`.

### Phase 3 — Manufacturer/Brand Resolution (`src/resolution/`)
- Standardizes manufacturer and brand names against taxonomy masters using canonical ID mapping.

### Phase 4 — Product Classification (`src/classification/`)
- Categorizes products into hierarchical taxonomies based on product type keywords and similarity models.

### Phase 5 — Attribute Extraction (`src/attributes/`)
- Extracts category-specific technical attributes (voltage, grit, wattage, dimensions, material).

### Phase 6 — LOV Resolution (`src/lov/`)
- Maps extracted attribute values to strict Lists-of-Values (LOV) enum vocabularies.

### Phase 7 — UOM Normalization (`src/uom/`)
- Standardizes Units of Measure (UOM) to canonical units (e.g. `inch` / `inches` -> `in`, `volts` -> `v`).

### Phase 8 — Web Evidence Enrichment (`src/enrichment/`)
- Crawls and retrieves external web evidence to enrich missing attributes with strict source authority ranking.

### Phase 9 — Quality & De-duplication (`src/quality/`)
- Runs span-validators to ensure all extracted facts exist in source texts without LLM hallucination.

### Phase 10 — Validation Engine (`src/validation/`)
- Enforces multi-attribute integrity rules (e.g. dimensional limits, voltage-category constraints, required fields).

### Phase 11 — Confidence Engine (`src/confidence/`)
- Computes multi-band confidence scores (`AUTO_APPROVE`, `REVIEW_RECOMMENDED`, `HUMAN_REVIEW`) using validation, evidence presence, and source authority.

### Phase 12 — Human-in-the-Loop Review Dashboard (`src/review/`)
- Provides interactive review queue management where human decisions approve, edit, reject, or escalate flagged attributes without mutating raw source data.

### Phase 13 — Grounded Product Description Engine (`src/content/`)
- Generates titles, short descriptions, and long descriptions grounded strictly in validated payload facts.
- Runs claim grounding audits on **12,267 factual claims** ensuring 100% grounding rate and zero marketing hype.

### Phase 14 — Final Output & Delivery Engine (`src/output/`)
- Assembles final catalog data, preserving native/baseline attributes without false exclusions.
- Exports validated products to `product.json`, `enriched.csv`, `validation_report.csv`, and `evidence.json`.
- Runs SHA256 integrity checks validating protected files.

### Phase 15 — Independent Ground-Truth Evaluation Engine (`src/evaluation/`)
- Benchmarks final outputs against `data/master/ground_truth.csv`.
- Normalizes whitespace, case, and unit variations to prevent superficial mismatches.
- Computes Field Accuracy, LOV Compliance, UOM Compliance, Completeness, Recovery Rate, and Confidence Quality.
- Implements deterministic repeatability checks (running twice produces identical outputs).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10–3.14, FastAPI, Uvicorn, Pandas, NumPy, Pydantic v2, PyJWT, Google GenAI SDK.
- **Frontend**: React, Vite, Tailwind CSS, Lucide React Icons.
- **Design System**: Space Grotesk, Inter, IBM Plex Mono, Custom Blueprint Backdrop Grid.
- **Testing**: pytest unit testing and regression suites.

---

## 📁 Project Structure

```
Prodexa/
│
├── data/
│   ├── raw/                           # Raw input feeds (input.csv)
│   ├── processed/                     # Intermediate pipeline outputs (described_products.csv, etc.)
│   ├── master/                        # Taxonomy, LOVs, UOMs, Ground Truth, Expected Template
│   ├── final/                         # Production delivery outputs (unihack_expected_output.csv)
│   ├── evidence/                      # Attribute evidence records
│   └── evaluation/                    # Phase 15 evaluation summary logs
│
├── frontend/                          # React + Vite Web Application
│   ├── src/
│   │   ├── components/                # Navbar, Sidebar, ParticleCanvas, ReviewModal, etc.
│   │   ├── context/                   # AuthContext (JWT Authentication & Role state)
│   │   ├── pages/                     # LandingPage, UserDashboard, AdminDashboard, ProductExplorer...
│   │   └── api.js                     # Centralized API fetch layer
│   ├── vite.config.js                 # Proxy config (/api -> http://127.0.0.1:8000)
│   └── package.json
│
├── src/                               # Source modules for 15 Intelligence Pipeline Phases
│   ├── cleaning/
│   ├── understanding/
│   ├── resolution/
│   ├── classification/
│   ├── attributes/
│   ├── lov/
│   ├── uom/
│   ├── enrichment/
│   ├── quality/
│   ├── validation/
│   ├── confidence/
│   ├── review/
│   ├── content/
│   ├── output/                        # Phase 14 Output components
│   └── evaluation/                    # Phase 15 Evaluation components
│
├── scripts/                           # Audit & Schema mapping scripts
│   └── audit_and_generate_expected_output.py
│
├── reports/                           # Output audit & validation reports
│   └── expected_output_schema_audit.txt
│
├── server.py                          # FastAPI Backend API Server
├── requirements.txt                   # Dependencies
└── README.md                          # Platform Documentation
```

---

## ⚡ Quick Start

### 1. Installation

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install Frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### 2. Run Delivery Schema Audit & Delivery CSV Generation

Generate the official 252-column delivery CSV and schema audit report:

```bash
python scripts/audit_and_generate_expected_output.py
```
*Outputs generated:*
- `data/final/unihack_expected_output.csv` (1000 rows × 252 columns)
- `reports/expected_output_schema_audit.txt`

### 3. Run FastAPI Backend Server

Launch the FastAPI backend server on `http://127.0.0.1:8000`:

```bash
python server.py
```

### 4. Run Frontend Web Application

In a separate terminal, launch the React Vite dev server:

```bash
cd frontend
npm run dev
```

Open your browser to:
- **Web Interface**: `http://localhost:3000/`
- **FastAPI API & Production SPA**: `http://127.0.0.1:8000/`

---

## 🧪 Verification & Testing

### Run Full Regression Suite:
```bash
python -m pytest -v
```

### Run Phase 14 & 15 Verification Scripts:
```bash
python -m src.output.phase14_pipeline
python -m src.evaluation.phase15_pipeline
```
