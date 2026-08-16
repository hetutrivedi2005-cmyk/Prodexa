# Prodexa — Product Catalog Data Engineering, Matching & Evaluation Platform

Prodexa is an enterprise-grade product catalog data engineering, matching, enrichment, human-in-the-loop validation, grounded content generation, and independent evaluation pipeline. It transforms raw, dirty catalog feeds into highly structured, evidence-proven, validated, and benchmarked product catalog data.

---

## Technical Architecture & Pipeline Phases

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

## Tech Stack

- **Python 3.10 - 3.14**
- **Pandas / NumPy**: Tabular data processing and statistical analysis.
- **Pydantic v2**: Strict schema-level validation of output files.
- **Official Google GenAI SDK**: Structured JSON structured data generation.
- **pytest**: Framework for dedicated unit tests and regression suites.

---

## Project Structure

```
Prodexa/
│
├── data/
│   ├── raw/                           # Raw feeds
│   ├── processed/                     # Intermediate pipeline stages
│   ├── master/                        # Master taxonomies & Ground Truth
│   ├── final/                         # Final output delivery artifacts
│   └── evaluation/                    # Phase 15 comparison summary logs
│
├── src/                               # Source modules for Phases 1-15
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
├── tests/                             # Unit tests for Phases 2-15
├── reports/                           # Output reports and audits
├── requirements.txt                   # Dependencies
└── README.md                          # Documentation
```

---

## Quick Start

### 1. Installation

Install required dependencies:

```bash
python -m pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Output & Evaluation Engines

#### Run Phase 14 Final Output Pipeline:
This filters, schema-validates, and exports the final catalog delivery datasets:
```bash
python -m src.output.phase14_pipeline
```
*Outputs generated:*
- `data/final/product.json`
- `data/final/enriched.csv`
- `data/final/validation_report.csv`
- `data/final/evidence.json`
- `reports/phase14_final_acceptance.txt`

#### Run Phase 15 Evaluation Pipeline:
This runs comparison benchmarks against Ground Truth:
```bash
python -m src.evaluation.phase15_pipeline
```
*Outputs generated:*
- `data/evaluation/field_comparison.jsonl`
- `data/evaluation/evaluation_summary.json`
- `data/evaluation/error_analysis.csv`
- `reports/phase15_final_acceptance.txt` (Complete dashboard metrics)

---

## Running Verification Suites & Tests

### Run Full Regression Test Suite
Executes all **520 core regression unit tests** covering validation rules, LLM extraction caches, normalizations, and pipelines:
```bash
python -m pytest -v
```

### Run Phase 14 Unit Tests & Adversarial Audits
```bash
python -m pytest tests/test_phase14_output.py -v
python -m src.output.phase14_adversarial_audit
```

### Run Phase 15 Unit Tests & Adversarial Audits
```bash
python -m pytest tests/test_phase15_evaluation.py -v
python -m src.evaluation.phase15_adversarial_audit
```
