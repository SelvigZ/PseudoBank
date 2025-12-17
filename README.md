# PseudoBank

A data sanitization tool that replaces sensitive information with fake placeholders before sharing reports with AI tools.

**No pip install needed** - all dependencies are bundled. Just copy the folder and run.

---

## Executive Summary

**Problem:** We want to use AI tools (like Claude) to help analyze reports and write code, but our reports contain sensitive information (vendor names, program names) that shouldn't be shared externally.

**Solution:** PseudoBank replaces sensitive values with fake placeholders *before* sharing. The AI never sees real names. Code developed using fake data works identically on real data because it references column headers, not specific values.

**Key Security Points:**
- Sensitive data never leaves the secure environment
- AI tools only see sanitized/fake data
- No decryption keys or stored mappings to protect
- Runs completely offline
- Random assignment prevents pattern analysis
- **100% auditable** - all code is plain text Python, no compiled binaries
- **No internet/pip required** - dependencies are bundled

---

## Quick Start

**Requirements:** Python 3.x (no pip needed)

**Run it:**
```
pseudobank.bat "path\to\your\report.xlsx"
```

That's it. No installation, no pip, no setup.

---

## What This Tool Does (In Plain English)

### The Problem

You have a report like this:

| Vendor Name | Program | Amount |
|-------------|---------|--------|
| Acme Corp | Project Alpha | $5,000 |
| Boeing Defense | Blue Horizon | $3,000 |

You want AI help analyzing it, but you can't share "Acme Corp" or "Project Alpha" externally.

### The Solution

PseudoBank creates a sanitized copy:

| Vendor Name | Program | Amount |
|-------------|---------|--------|
| Vendor_047 | Program_093 | $5,000 |
| Vendor_128 | Program_017 | $3,000 |

**What changed:**
- Vendor names → Random fake names (Vendor_047, Vendor_128)
- Program names → Random fake names (Program_093, Program_017)
- Dollar amounts → **Unchanged** (not sensitive)
- Column headers → **Unchanged** (needed for code to work)

**What you share with AI:** The sanitized version only.

**What stays on your secure machine:** The original report with real names.

---

## The Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  SECURE ENVIRONMENT (Your Machine)                                  │
│                                                                     │
│    Original Report          PseudoBank           Sanitized Report   │
│    ┌──────────────┐         ┌───────┐           ┌──────────────┐   │
│    │ Acme Corp    │  ────►  │ WASH  │  ────►    │ Vendor_047   │   │
│    │ Boeing       │         └───────┘           │ Vendor_128   │   │
│    └──────────────┘                             └──────────────┘   │
│          │                                             │            │
│          │                                             │            │
│          ▼                                             ▼            │
│    STAYS HERE                                    SAFE TO SHARE      │
│    (never shared)                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  EXTERNAL AI TOOL (Claude, etc.)                                    │
│                                                                     │
│    Receives: Sanitized data only                                    │
│    Sees: "Vendor_047 has 50% of spend"                              │
│    Returns: Code that references "Vendor Name" column               │
│                                                                     │
│    NEVER SEES: Real vendor names, real program names                │
└─────────────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACK IN SECURE ENVIRONMENT                                         │
│                                                                     │
│    Code from AI    +    Original Report    =    Real Insights       │
│                                                                     │
│    The code works because it uses COLUMN NAMES (like "Vendor Name") │
│    not the fake values (like "Vendor_047").                         │
│                                                                     │
│    Result: Charts and analysis show real names like "Acme Corp"     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Security Measures

### 1. Data Never Leaves Secure Environment

The original report with real names stays on your machine. Only the sanitized copy (with fake names) is shared externally.

### 2. Random Number Assignment

Fake values use **random** numbers, not sequential:
- `Acme Corp` → `Vendor_047` (not `Vendor_001`)
- `Boeing` → `Vendor_128` (not `Vendor_002`)

**Why this matters:** Sequential numbering (001, 002, 003) could reveal patterns like "001 is probably the first alphabetically" or "001 is the most common." Random numbers eliminate these patterns.

### 3. Fresh Assignment Every Time

Each time you run the tool, values get **new random numbers**:
- Monday: `Acme Corp` → `Vendor_047`
- Tuesday: `Acme Corp` → `Vendor_283`

**Why this matters:** Even if someone saw two sanitized reports, they couldn't correlate which fake vendor is which across reports.

### 4. No Stored Mappings

The tool does **not** store a lookup table of real-to-fake mappings. There is:
- No encryption key to protect
- No mapping file to secure
- No way to "decode" the fake names back to real names

Each session is independent and disposable.

### 5. Completely Offline

The tool runs entirely on your local machine:
- No internet connection required
- No data sent to external servers
- No cloud storage
- No pip install needed (dependencies bundled)

### 6. Selective Column Protection

You choose which columns to sanitize:
- **Sanitize:** Vendor names, program names, organization names
- **Keep unchanged:** Dollar amounts, dates, document numbers, generic codes

Dollar amounts and dates are typically not sensitive and are needed for meaningful analysis.

### 7. Fully Auditable Code

**No compiled executables.** Every file in this project is plain text:
- `pseudobank.bat` - Simple batch launcher (open in Notepad to inspect)
- `src/pseudonymize.py` - Main Python script (fully readable)
- `src/config.py` - Configuration settings
- `lib/` - Bundled Python libraries (pandas, openpyxl, etc.)

Anyone can review exactly what this tool does before running it.

---

## What Data Is Protected vs. Shared

| Data Type | Protected? | What AI Sees |
|-----------|------------|--------------|
| Vendor/Company names | YES | Vendor_047, Vendor_128, etc. |
| Program/Project names | YES | Program_093, Program_017, etc. |
| Organization names | YES | Org_056, Org_234, etc. |
| Dollar amounts | NO | Actual numbers (needed for analysis) |
| Dates | NO | Actual dates (needed for analysis) |
| Document numbers | NO | Actual values (generic identifiers) |
| Column headers | NO | Actual names (needed for code to work) |

**Note:** You control which columns are sanitized each time you run the tool.

---

## Installation & Usage

### Requirements

- Python 3.x (that's it - no pip needed!)

### Running PseudoBank

**Option 1: Use the batch launcher**
```
pseudobank.bat "C:\path\to\your\report.xlsx"
```

**Option 2: Let it prompt you** (recommended for paths with spaces)
```
pseudobank.bat
```
Then enter your file path when prompted. **Do NOT type quotes** around the path - just paste it directly.

**Option 3: Run Python directly**
```
python src/pseudonymize.py --input "C:\path\to\your\report.xlsx"
```

### Output Location

Sanitized files are created in the `output/` folder with the prefix `CLEAN_`:
- Original: `quarterly_report.xlsx`
- Sanitized: `output/CLEAN_quarterly_report.xlsx`

---

## Project Structure

```
PseudoBank/
├── pseudobank.bat         # Easy launcher (double-click or run from cmd)
├── README.md              # This documentation
├── SETUP_INSTRUCTIONS.txt # Step-by-step setup guide
├── lib/                   # Bundled dependencies (no pip needed!)
│   ├── pandas/
│   ├── openpyxl/
│   └── ...
├── src/
│   ├── pseudonymize.py    # Main Python script
│   └── config.py          # Folder settings
├── sample_data/           # Example input files
└── output/                # Sanitized files appear here
```

---

## Frequently Asked Questions

### Can someone reverse-engineer the fake names back to real names?

**No.** There is no stored mapping between real and fake names. The assignment is random and not recorded. Even the person who ran the tool cannot decode `Vendor_047` back to `Acme Corp` after the session ends.

### What if I need to sanitize 100+ unique vendors?

The tool handles this automatically. It assigns random numbers from 001-999, ensuring no duplicates within a single report. If you somehow exceed 999 unique values in one column, it continues with higher numbers.

### Does the AI need to know the real names to write useful code?

**No.** The AI writes code that references column names (like `df['Vendor Name']`), not specific values. The code works identically whether the column contains `Acme Corp` or `Vendor_047`.

### What file formats are supported?

- Excel (.xlsx, .xls)
- CSV (.csv)

### Is this tool approved for use with CUI/sensitive data?

This tool is designed to help sanitize data *before* sharing. However, approval for use with specific data classifications should be verified with your Information Security Officer. The tool itself does not transmit any data - it only creates a local sanitized copy.

### Why are the dependencies bundled?

Many secure/restricted machines don't allow pip install or internet access. By bundling pandas and openpyxl in the `lib/` folder, you can just copy the entire PseudoBank folder to your machine and run it - no installation needed.

### What about numpy? Why isn't it bundled?

Numpy is **not** bundled because it conflicts with conda/Anaconda environments commonly found on government machines. The bundled pandas will use the system's numpy (from conda), which works correctly. If you bundle numpy separately, you'll get import errors.

### Why no .exe file?

Compiled executables are harder to audit and can raise security concerns. By keeping everything as plain text (Python scripts and batch files), anyone can open the files in Notepad and verify exactly what the tool does. This transparency is important for use in secure environments.

---

## Summary for Security Review

| Concern | How PseudoBank Addresses It |
|---------|----------------------------|
| Sensitive names exposed to AI | Names replaced with random fake placeholders before sharing |
| Pattern analysis from sequential IDs | Random number assignment (not 001, 002, 003) |
| Cross-report correlation | Fresh random numbers each session |
| Stored mapping files as vulnerability | No mappings stored - each session is independent |
| Data transmission to external servers | Tool runs 100% offline on local machine |
| Accidental sharing of original file | Original stays in place; sanitized copy created in separate output folder |
| Hidden/malicious code in executables | **No executables** - all code is plain text Python, fully auditable |
| Need for pip/internet on secure machines | **Dependencies bundled** - no pip install required |

---

*Last Updated: 2025-12-17*
