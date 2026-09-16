# 🎓 Academic Proposal MCP Server

[![MCP Version](https://img.shields.io/badge/MCP-1.2.0-blue.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**Academic Proposal MCP Server** is a self-contained, independent server built on the **Model Context Protocol (MCP)**. It is designed for students, researchers, and academic institutions to automate the creation, structuring, iterative versioning, and methodology validation of formal academic thesis and research proposals.

---

## 🌟 Key Features

1. **Dual Document Support (Proposal `.docx` & Pra-Proposal `.odt`)**:
   - **Thesis Proposal (3 Chapters DOCX)**: Full academic proposal adhering to official institutional formatting (`generate_proposal_from_topic`, `generate_academic_proposal`).
   - **Pre-Proposal Form (SA2-01A ODT)**: Standard institutional pre-proposal document (`generate_praproposal_from_topic`, `generate_academic_praproposal`).
2. **Strict Research Design Canvas Alignment**:
   - Strictly enforces **1 Single Measurable Problem Question** (`CLB04-01` & `CLB04-02`), eliminating open-ended or descriptive phrasing.
   - Automatically defines explicit Independent ($X$) and Dependent ($Y$) variables, aligns linear objectives, and verifies actionable stakeholder benefits.
3. **Mandatory Personal Data Re-Confirmation Workflow**:
   - Ensures student and supervisor details (*Nama Mahasiswa, NIM, Departemen/Jurusan, Program Studi, Keminatan, Bidang Skripsi, Dosen Pembimbing, NIP, Lokasi*) are explicitly verified and confirmed before and after document generation.
4. **CSV Literature Matrix Ingestion**:
   - Ingests literature review matrices or benchmark datasets directly from CSV files (`parse_literature_csv_data`).
   - Automatically builds comparison matrices and Harvard/IEEE bibliographies.
5. **Multi-MCP Research Coordination**:
   - Seamlessly interoperates with external research MCPs such as `paper-search` (`search_arxiv`, `search_semantic`, `search_google_scholar`) and `go-docs`.
   - Derives targeted academic queries via `plan_proposal_research` and includes registered prompt workflows (`auto_praproposal_workflow`, `auto_proposal_workflow`).
6. **Iterative Version Tracking & Markdown Exporting**:
   - Facilitates document versioning (`v1.0` $\rightarrow$ `v1.1` $\rightarrow$ `v2.0`) with automated changelog recording in `version_history.json`.
   - Extracts DOCX proposals into clean Markdown for LLM analysis.

---

## 🛠️ Available MCP Tools

| Tool | Description | Key Parameters |
| :--- | :--- | :--- |
| `generate_topic_from_artefact` | Synthesizes a structured academic research proposal topic (Title, 3-dimensional Urgency, Single Measurable Problem, Variables X & Y, Objectives, Benefits, and Canvas Audit) from any real-world artifact (news, case stories, problem documents, OCR/image descriptions). | `artefact_content`, `artefact_type`, `artefact_title`, `bidang_kajian`, `proposed_method_or_x`, `target_metric_or_y`, `institutional_focus` |
| `generate_diagram_image` | Generates high-resolution academic diagrams (Flowchart, Conceptual Framework, Layered Architecture), ensures `/asset` folder exists, and optionally embeds into target DOCX. | `diagram_type`, `title`, `steps_or_nodes`, `variabel_x`, `variabel_y`, `asset_folder`, `target_document_docx` |
| `insert_diagram_to_document` | Inserts an existing diagram image from `/asset` into a proposal DOCX with official caption numbering (`Gambar X.Y <Judul>`). | `document_filename`, `image_filename_or_path`, `caption_title`, `chapter_num`, `figure_num` |
| `generate_praproposal_from_topic` | One-shot generator for academic pre-proposal form (`.odt`, format SA2-01A) directly from topic, student metadata, CSV data, or paper-search results with automatic Canvas validation. | `topic`, `variabel_x`, `variabel_y`, `student_metadata`, `csv_filename`, `retrieved_papers`, `output_filename` |
| `generate_academic_praproposal` | Assembles and generates a complete academic pre-proposal document (`.odt`, format SA2-01A) with automated Canvas compliance auditing. | `metadata`, `sections`, `output_filename` |
| `validate_praproposal_compliance` | Validates pre-proposal form (SA2-01A) rigor against standard research canvas and word count budget limits (Latar Belakang <= 500w, Landasan Kepustakaan <= 250w, Metode <= 250w). | `metadata`, `sections`, `odt_filename`, `variabel_independen`, `variabel_dependen`, `single_problem_only` |
| `generate_praproposal_rubric_report` | Generates a comprehensive pre-proposal audit checklist report in Markdown format based on institutional SA2-01A rules and Canvas rubrics. | `proposal_title`, `student_name`, `student_id`, `metadata`, `sections`, `odt_filename`, `variabel_independen`, `variabel_dependen`, `output_markdown_filename` |
| `validate_canvas_compliance` | Validates research proposal rigor against standard academic research design principles. | `rumusan_masalah`, `variabel_independen`, `variabel_dependen`, `tujuan_penelitian`, `manfaat_penelitian`, `single_problem_only` |
| `generate_rubric_checklist_report` | Generates a comprehensive academic audit checklist report in Markdown format based on standard evaluation rubrics. | `proposal_title`, `student_name`, `student_id`, `rumusan_masalah`, `variabel_independen`, `variabel_dependen`, `tujuan_penelitian`, `manfaat_penelitian`, `output_markdown_filename` |
| `get_canvas_guidelines` | Retrieves the complete rubric and checklist for academic research design criteria (Chapter 1-3 & SA2-01A). | *(none)* |
| `generate_academic_proposal` | Assembles and generates a complete, publication-grade academic proposal DOCX file. | `metadata`, `bab1_data`, `bab2_subbab`, `bab3_subbab`, `daftar_referensi`, `output_filename` |
| `generate_proposal_from_topic` | One-shot proposal generator combining research topic, CSV literature data, and paper-search results with automatic research flowchart rendering. | `topic`, `variabel_x`, `variabel_y`, `csv_filename`, `retrieved_papers`, `output_filename` |
| `plan_proposal_research` | Analyzes a topic to derive variables (X & Y), single research question, and search queries for `paper-search` MCP. | `topic`, `bidang_kajian`, `variabel_x`, `variabel_y` |
| `parse_literature_csv_data` | Parses a literature review or benchmark CSV file from workspace into DOCX comparison table and references. | `csv_filename`, `csv_content` |
| `inspect_proposal_document` | Analyzes the structural health and word count budget of proposal documents (`.docx` or `.odt`). | `filename` (default: `"Proposal Skripsi v1.0.docx"`) |
| `increment_proposal_version` | Duplicates active thesis proposal (.docx) to an updated version and records changelog entries in `version_history.json`. | `current_version`, `new_version`, `changelog` |
| `increment_praproposal_version` | Duplicates active pre-proposal (.odt) to an updated version and records changelog entries in `version_history.json`. | `current_version`, `new_version`, `changelog`, `filename_prefix` |
| `export_proposal_as_markdown` | Converts any DOCX proposal in the workspace into clean, structured Markdown. | `filename` |

---

## 🚀 Installation & Setup

### Option A: Using Docker (Recommended)

#### 1. Clone the Repository & Build the Image

```bash
git clone https://github.com/ranoes/academic-mcp-proposal.git
cd academic-mcp-proposal
docker build -t academic-proposal-mcp:latest .
```

#### 2. Configure Your MCP Client

Add the following entry to your MCP configuration file (e.g., `mcp_config.json` in Antigravity, or `claude_desktop_config.json` in Claude Desktop):

```json
{
  "mcpServers": {
    "academic-proposal-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        ".:/workspace",
        "academic-proposal-mcp:latest"
      ]
    }
  }
}
```

> **Note:** `.:/workspace` otomatis memetakan direktori proyek yang sedang aktif dibuka di IDE ke dalam `/workspace` container Docker tanpa perlu menuliskan path absolut secara manual.

---

### Option B: Running with Python / UV (Without Docker)

If you prefer running directly in a local Python environment:

```bash
# Clone the repository
git clone https://github.com/ranoes/academic-mcp-proposal.git
cd academic-mcp-proposal

# Install dependencies and package
pip install -e .
python server.py
```

Configuration in `mcp_config.json` for Python:

```json
{
  "mcpServers": {
    "academic-proposal-mcp": {
      "command": "python",
      "args": ["${workspaceFolder}/server.py"],
      "env": {
        "WORKSPACE_DIR": "${workspaceFolder}"
      }
    }
  }
}
```

---

## 🛠️ Available MCP Tools Reference

Below is a detailed guide for all **16 MCP Tools** provided by the server, organized by function:

---

### 📑 1. Document Generation Tools

#### A. `generate_proposal_from_topic`
One-shot generator that produces a complete 3-Chapter Thesis Proposal in `.docx` format directly from a topic, variable specifications, CSV literature, and/or retrieved papers.
- **Parameters**: `topic` (str), `variabel_x` (str, opt), `variabel_y` (str, opt), `student_metadata` (dict, opt), `csv_filename` (str, opt), `csv_content` (str, opt), `retrieved_papers` (list, opt), `output_filename` (str, default: `"Proposal Skripsi v1.0.docx"`)
- **Example Payload**:
  ```json
  {
    "topic": "Optimizing Distributed Sensor Network Lifetime using Reinforcement Learning Routing Algorithms",
    "variabel_x": "Adaptive Reinforcement Learning Q-Routing Mechanism",
    "variabel_y": "Network Operational Longevity and Packet Delivery Ratio",
    "csv_filename": "literature.csv",
    "output_filename": "Proposal Skripsi v1.0.docx"
  }
  ```

#### B. `generate_academic_proposal`
Assembles a publication-grade academic proposal `.docx` file from explicit chapter structures (`metadata`, `bab1_data`, `bab2_subbab`, `bab3_subbab`, `daftar_referensi`).
- **Parameters**: `metadata` (dict), `bab1_data` (dict), `bab2_subbab` (list), `bab3_subbab` (list), `daftar_referensi` (list), `output_filename` (str)

#### C. `generate_praproposal_from_topic`
One-shot generator that creates an official Pre-Proposal Form (`.odt`, format SA2-01A) directly from research topic inputs and applies automatic Canvas compliance auditing.
- **Parameters**: `topic` (str), `variabel_x` (str, opt), `variabel_y` (str, opt), `student_metadata` (dict, opt), `csv_filename` (str, opt), `retrieved_papers` (list, opt), `output_filename` (str, default: `"Praproposal Skripsi v1.0.odt"`)
- **Example Payload**:
  ```json
  {
    "topic": "Optimasi Deteksi Anomali Jaringan IoT Menggunakan Federated Learning",
    "variabel_x": "Algoritma Federated Learning Terdistribusi",
    "variabel_y": "Akurasi Deteksi dan Efisiensi Komunikasi Jaringan IoT",
    "student_metadata": {
      "nama_mahasiswa": "Alex Mercer",
      "nim": "225150200111000",
      "jurusan": "Teknik Informatika",
      "program_studi": "Teknik Informatika",
      "keminatan": "Komputasi Cerdas",
      "bidang_skripsi": "Artificial Intelligence & Data Science",
      "nama_pembimbing": "Dr. Mahrus Ali, S.Kom., M.Kom."
    },
    "output_filename": "Praproposal_SA2-01A_Alex_Mercer.odt"
  }
  ```

#### D. `generate_academic_praproposal`
Directly populates and compiles the official SA2-01A `.odt` form from structured `metadata` and `sections` dictionaries with automated canvas verification.
- **Parameters**: `metadata` (dict), `sections` (dict), `output_filename` (str)

---

### 🧪 2. Research Canvas & Methodology Validation Tools

#### A. `validate_canvas_compliance` (Proposal 3-Bab Validation)
Audits the methodological rigor of a proposal against standard Research Design Canvas rules.
- **Parameters**: `rumusan_masalah` (str), `variabel_independen` (str), `variabel_dependen` (str), `tujuan_penelitian` (str), `manfaat_penelitian` (str), `single_problem_only` (bool, default: `true`)
- **Validation Checks**:
  - `[CLB04-01]`: Ensures strictly 1 measurable problem question.
  - `[CLB04-02]`: Enforces non-descriptive, parameter-driven question formulation.
  - `[CLB04-02 / M01-01]`: Verifies explicit Variable $X$ definition.
  - `[CLB04-03 / M01-02]`: Verifies explicit Variable $Y$ definition.
  - `[CLB05-01]`: Ensures objectives test variable outcomes.
  - `[CLB06-02]`: Eliminates administrative clichés (*"syarat kelulusan", "menambah wawasan"*).
- **Example Payload**:
  ```json
  {
    "rumusan_masalah": "Sejauh manakah implementasi Adaptive Q-Routing mampu memperpanjang network lifetime dibandingkan protokol routing statis pada jaringan sensor nirkabel?",
    "variabel_independen": "Adaptive Q-Routing Mechanism",
    "variabel_dependen": "Network Operational Lifetime dan Packet Delivery Ratio",
    "tujuan_penelitian": "Menguji dan mengukur peningkatan lifetime jaringan sensor melalui algoritma Q-Routing",
    "manfaat_penelitian": "Memberikan panduan operasional bagi praktisi jaringan sensor dalam mengurangi kegagalan transmisi data"
  }
  ```

#### B. `validate_praproposal_compliance` (Pre-Proposal SA2-01A Validation)
Validates pre-proposals against Research Canvas rules and strict SA2-01A word-count budgets (can evaluate in-memory payloads OR directly inspect an existing `.odt` file in the workspace).
- **Parameters**: `metadata` (dict, opt), `sections` (dict, opt), `odt_filename` (str, opt), `variabel_independen` (str, opt), `variabel_dependen` (str, opt), `single_problem_only` (bool, default: `true`)
- **Word Limits Enforced**:
  - `[PRA-LB01]` Latar Belakang / Deskripsi Masalah: $\le 500$ words.
  - `[PRA-LR01]` Landasan Kepustakaan: $\le 250$ words.
  - `[PRA-MET01]` Rencana Metode Penelitian: $\le 250$ words.
- **Example Payload (Validating from existing file)**:
  ```json
  {
    "odt_filename": "Praproposal Skripsi v1.0.odt",
    "variabel_independen": "Algoritma Federated Learning",
    "variabel_dependen": "Akurasi Deteksi dan Komunikasi"
  }
  ```

#### C. `generate_rubric_checklist_report` (Proposal 3-Bab Audit Report)
Generates a comprehensive Markdown audit report for the 3-Chapter Proposal across 17 rubric criteria (Chapter 1 `LB01-LB06`, Chapter 2 `LR01-LR06`, Chapter 3 `M01-M05`).
- **Parameters**: `proposal_title`, `student_name`, `student_id`, `rumusan_masalah`, `variabel_independen`, `variabel_dependen`, `tujuan_penelitian`, `manfaat_penelitian`, `output_markdown_filename` (default: `"proposal_rubric_checklist_report.md"`)

#### D. `generate_praproposal_rubric_report` (Pre-Proposal SA2-01A Audit Report)
Generates an audit checklist Markdown report specifically for Form SA2-01A, featuring a dedicated **Word Count Budget Analysis** table and itemized criteria verification.
- **Parameters**: `proposal_title` (opt), `student_name` (opt), `student_id` (opt), `metadata` (dict, opt), `sections` (dict, opt), `odt_filename` (opt), `variabel_independen` (opt), `variabel_dependen` (opt), `output_markdown_filename` (default: `"praproposal_rubric_checklist_report.md"`)

#### E. `get_canvas_guidelines`
Retrieves the complete standard rubric guidelines, evaluation criteria, and violation codes across Chapter 1, Chapter 2, Chapter 3, and Form SA2-01A.
- **Parameters**: *(none)*

---

### 🔍 3. Document Inspection, Export & Version Tracking Tools

#### A. `inspect_proposal_document`
Performs deep structural health checks on either `.docx` proposals or `.odt` pre-proposals.
- For `.docx`: Returns total paragraphs, tables, approximate words, heading tree (`BAB 1`, `1.1`, etc.), and table geometry.
- For `.odt`: Returns word counts for each section (Latar Belakang, Landasan Kepustakaan, Metode) and validates word budget compliance against SA2-01A limits.
- **Parameters**: `filename` (str, default: `"Proposal Skripsi v1.0.docx"`)

#### B. `export_proposal_as_markdown`
Extracts formatted text, headings, captions, and reference lists from any `.docx` proposal into structured Markdown for fast LLM inspection.
- **Parameters**: `filename` (str, default: `"Proposal Skripsi v1.0.docx"`)

#### C. `increment_proposal_version`
Duplicates an active proposal (`.docx`) to an incremented version and records change notes in `version_history.json`.
- **Parameters**: `current_version` (e.g., `"v1.0"`), `new_version` (e.g., `"v1.1"`), `changelog` (str)

#### D. `increment_praproposal_version`
Duplicates an active pre-proposal (`.odt`) to an incremented version and records change notes in `version_history.json`.
- **Parameters**: `current_version` (e.g., `"v1.0"`), `new_version` (e.g., `"v1.1"`), `changelog` (str), `filename_prefix` (str, default: `"Praproposal Skripsi"`)

---

### 📊 4. Literature Planning & Ingestion Tools

#### A. `generate_topic_from_artefact`
Synthesizes a structured academic research proposal topic (Title, 3-dimensional Urgency, Single Measurable Problem, Variables X & Y, Objectives, Benefits, and Canvas Audit) from any real-world artifact (news articles, case stories, problem documents, OCR/image descriptions).
- **Parameters**: `artefact_content` (str), `artefact_type` (str, default: `"general_text"`), `artefact_title` (str, opt), `bidang_kajian` (str, opt), `proposed_method_or_x` (str, opt), `target_metric_or_y` (str, opt), `institutional_focus` (str, opt)
- **Example Payload**:
  ```json
  {
    "artefact_type": "news",
    "artefact_title": "Lonjakan Serangan Botnet IoT 2025",
    "artefact_content": "Laporan Keamanan Siber menunjukkan lonjakan 300% serangan botnet DDoS pada gateway IoT karena tingginya false alarm dan latensi metode deteksi konvensional.",
    "proposed_method_or_x": "Algoritma Federated Learning Terdistribusi",
    "bidang_kajian": "Keamanan Siber & Jaringan Komputer"
  }
  ```

#### B. `plan_proposal_research`
Analyzes a topic to derive variables $X$ & $Y$, a single measurable research question, and targeted academic search queries for `paper-search` MCP.
- **Parameters**: `topic` (str), `bidang_kajian` (str, opt), `variabel_x` (str, opt), `variabel_y` (str, opt)

#### C. `parse_literature_csv_data`
Parses a CSV literature matrix into a formatted comparison table (`tabel_tinjauan_pustaka`), narrative summaries for Chapter 2, and standard Harvard/IEEE citations.
- **Parameters**: `csv_filename` (str, opt), `csv_content` (str, opt)

---

### 🖼️ 5. Diagram Generation & Asset Management Tools

#### A. `generate_diagram_image`
Generates high-resolution academic vector/raster diagrams (300 DPI), automatically ensures the `/asset` workspace directory exists, saves the PNG file, and can optionally insert it directly into a target `.docx` proposal.
- **Supported Diagram Types**:
  - `"flowchart"`: Multi-stage vertical research workflow diagram (`Tahap 1`, `Tahap 2`, ...).
  - `"conceptual_framework"`: Causal variable relationship diagram ($X \rightarrow \text{Treatment} \rightarrow Y$).
  - `"architecture"`: Layered system/software architecture block diagram.
- **Parameters**: `diagram_type` (str), `title` (str), `steps_or_nodes` (list, opt), `variabel_x` (str, opt), `variabel_y` (str, opt), `layers` (list, opt), `asset_folder` (str, default: `"asset"`), `output_filename` (str, opt), `target_document_docx` (str, opt), `chapter_num` (int, default: `3`), `figure_num` (int, default: `1`)
- **Example Payload**:
  ```json
  {
    "diagram_type": "flowchart",
    "title": "Diagram Alur Pelaksanaan Penelitian",
    "steps_or_nodes": [
      "Tahap 1: Identifikasi Masalah Konsumsi Energi WSN",
      "Tahap 2: Studi Literatur Protokol Routing",
      "Tahap 3: Perancangan Model Q-Routing",
      "Tahap 4: Implementasi & Pengujian Simulasi NS-3",
      "Tahap 5: Evaluasi Metrik & Kesimpulan"
    ],
    "asset_folder": "asset",
    "output_filename": "diagram_alur_penelitian.png",
    "target_document_docx": "Proposal Skripsi v1.0.docx"
  }
  ```

#### B. `insert_diagram_to_document`
Embeds an image from `/asset` (or a given path) into an existing `.docx` proposal document with standardized, centered figure formatting and official captioning (`Gambar X.Y <Judul>`).
- **Parameters**: `document_filename` (str), `image_filename_or_path` (str), `caption_title` (str), `chapter_num` (int, default: `3`), `figure_num` (int, default: `1`), `width_inches` (float, default: `5.5`)
- **Example Payload**:
  ```json
  {
    "document_filename": "Proposal Skripsi v1.0.docx",
    "image_filename_or_path": "asset/diagram_alur_penelitian.png",
    "caption_title": "Diagram Alur Pelaksanaan Penelitian",
    "chapter_num": 3,
    "figure_num": 1
  }
  ```

---

### 📐 6. Mathematical Formula Generation & Native Equation Tools

#### A. `generate_math_formula_image`
Renders LaTeX mathematical formulas natively into Microsoft Word equations (**Office Open XML Math / OMML `<m:oMath>`**) as fully editable, crisp vector math objects directly in the `.docx` document, and/or exports 300 DPI transparent PNG images to `/asset`. Supports automatic equation numbering `(Chapter.Formula)` and variable definitions.
- **Parameters**: `latex_code` (str), `formula_title` (str, opt), `chapter_num` (int, default: `3`), `formula_num` (int, default: `1`), `variable_definitions` (dict, opt), `asset_folder` (str, default: `"asset"`), `output_filename` (str, opt), `target_document_docx` (str, opt), `intro_text` (str, opt), `use_native_equation` (bool, default: `true`)
- **Supported Math Syntax**: Greek letters ($\alpha, \beta, \gamma, \sigma, \theta$), fractions (`\frac{a}{b}`), summations (`\sum_{i=1}^n`), integrals (`\int`), square roots (`\sqrt`), accents (`\hat{y}`, `\bar{x}`), paired pipes (`|y_i - \hat{y}_i|`), sub/superscripts (`x_i^2`), matrix/vector terms.
- **Example Payload**:
  ```json
  {
    "latex_code": "F_1 = 2 \\cdot \\frac{\\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}",
    "formula_title": "F1-Score",
    "chapter_num": 3,
    "formula_num": 1,
    "variable_definitions": {
      "Precision": "Tingkat ketepatan klasifikasi kelas positif",
      "Recall": "Tingkat sensitivitas model terhadap kelas positif"
    },
    "use_native_equation": true,
    "target_document_docx": "Proposal Skripsi v1.0.docx"
  }
  ```

#### B. `insert_math_formula_to_document`
Inserts a formula into an existing `.docx` document using the standard academic layout: a borderless 1-row $\times$ 2-column table with the **native Word Equation (`<m:oMath>`)** centered in the left column (5.2 in), right-aligned equation numbering `(X.Y)` in the right column (0.8 in), and indented *"di mana: ..."* variable definitions.
- **Parameters**: `document_filename` (str), `latex_code` (str, opt), `image_filename_or_path` (str, opt), `chapter_num` (int, default: `3`), `formula_num` (int, default: `1`), `intro_text` (str, opt), `variable_definitions` (dict, opt), `use_native_equation` (bool, default: `true`), `image_width_inches` (float, default: `4.0`)
- **Example Payload**:
  ```json
  {
    "document_filename": "Proposal Skripsi v1.0.docx",
    "latex_code": "\\text{MAE} = \\frac{1}{n} \\sum_{i=1}^{n} |y_i - \\hat{y}_i|",
    "chapter_num": 3,
    "formula_num": 1,
    "intro_text": "Perhitungan nilai Mean Absolute Error (MAE) dirumuskan pada Persamaan (3.1) sebagai berikut:",
    "variable_definitions": {
      "y_i": "Nilai aktual data observasi ke-i",
      "\\hat{y}_i": "Nilai estimasi prediksi model ke-i",
      "n": "Jumlah total sampel pengujian"
    },
    "use_native_equation": true
  }
  ```

---

## 📊 CSV Literature Format

You can place a `literature.csv` in your workspace containing prior literature or benchmark studies. The columns are automatically detected:

```csv
Author,Year,Title,Method,Dataset,Findings,Gap
Zhang et al.,2023,Q-Learning for WSN Clustering,Q-Learning,WSN-Sim-100,Increased lifetime by 18%,High computational overhead on edge nodes
Al-Kandari et al.,2022,Energy-aware Routing Protocols,Heuristic Path Selection,Real-world Sensor Grid,Reliable packet delivery,Static pathing causes early node death
```

Columns detected:

- **Author / Penulis**: Citation author name(s).
- **Year / Tahun**: Publication year.
- **Title / Judul**: Paper title.
- **Method / Metode / Algoritma**: Independent variable / technique ($X$).
- **Dataset / Benchmark**: Test scenario or dataset used.
- **Results / Temuan / Hasil**: Key quantitative findings ($Y$).
- **Gap / Limitation / Kelemahan**: Identified research gap.

---

## 🤖 Multi-MCP Research Workflow (with `paper-search`)

If you have [`paper-search-mcp`](https://github.com/modelcontextprotocol/servers) installed alongside `academic-proposal-mcp`:

1. **Verify & Confirm Data**: Ensure student and supervisor personal information (*Nama, NIM, Departemen, Program Studi, Dosen Pembimbing, NIP, Lokasi*) is collected.
2. **Plan Queries**: Call `plan_proposal_research(topic="...")` to derive search queries optimized for ArXiv, Google Scholar, and Semantic Scholar.
3. **Retrieve Papers**: Run `paper-search` tools (`search_arxiv`, `search_semantic`, etc.).
4. **Assemble Document**: Pass search results into `generate_praproposal_from_topic(...)` for Pre-Proposal (`.odt`) or `generate_proposal_from_topic(...)` for Thesis Proposal (`.docx`).
5. **Prompt Automation**: Use the built-in MCP prompts (`auto_praproposal_workflow` or `auto_proposal_workflow`) in Antigravity or your AI client to execute the entire research and assembly workflow automatically.

---

## 📄 License & Contributing

Distributed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](file:///d:/Project/academic-mcp-proposal/LICENSE) for more details. Contributions, issue reports, and pull requests to expand academic formatting capabilities or validation rules are warmly welcomed.
