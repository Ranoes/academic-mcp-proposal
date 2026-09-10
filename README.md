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
| `generate_praproposal_from_topic` | One-shot generator for academic pre-proposal form (`.odt`, format SA2-01A) directly from topic, student metadata, CSV data, or paper-search results. | `topic`, `variabel_x`, `variabel_y`, `student_metadata`, `csv_filename`, `retrieved_papers`, `output_filename` |
| `generate_academic_praproposal` | Assembles and generates a complete academic pre-proposal document (`.odt`, format SA2-01A). | `metadata`, `sections`, `output_filename` |
| `generate_rubric_checklist_report` | Generates a comprehensive academic audit checklist report in Markdown format based on standard evaluation rubrics. | `proposal_title`, `student_name`, `student_id`, `rumusan_masalah`, `variabel_independen`, `variabel_dependen`, `tujuan_penelitian`, `manfaat_penelitian`, `output_markdown_filename` |
| `validate_canvas_compliance` | Validates research proposal rigor against standard academic research design principles. | `rumusan_masalah`, `variabel_independen`, `variabel_dependen`, `tujuan_penelitian`, `manfaat_penelitian`, `single_problem_only` |
| `get_canvas_guidelines` | Retrieves the complete rubric and checklist for academic research design criteria. | *(none)* |
| `generate_academic_proposal` | Assembles and generates a complete, publication-grade academic proposal DOCX file. | `metadata`, `bab1_data`, `bab2_subbab`, `bab3_subbab`, `daftar_referensi`, `output_filename` |
| `generate_proposal_from_topic` | One-shot proposal generator combining research topic, CSV literature data, and paper-search results. | `topic`, `variabel_x`, `variabel_y`, `csv_filename`, `retrieved_papers`, `output_filename` |
| `plan_proposal_research` | Analyzes a topic to derive variables (X & Y), single research question, and search queries for `paper-search` MCP. | `topic`, `bidang_kajian`, `variabel_x`, `variabel_y` |
| `parse_literature_csv_data` | Parses a literature review or benchmark CSV file from workspace into DOCX comparison table and references. | `csv_filename`, `csv_content` |
| `inspect_proposal_document` | Analyzes the structural health of a proposal document (paragraph count, table count, sections, words, heading tree). | `filename` (default: `"Proposal Skripsi v1.0.docx"`) |
| `increment_proposal_version` | Duplicates active proposal to an updated version and records changelog entries. | `current_version`, `new_version`, `changelog` |
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
        "${workspaceFolder}:/workspace",
        "academic-proposal-mcp:latest"
      ]
    }
  }
}
```

> **Note:** `${workspaceFolder}` automatically expands to your current project directory in Antigravity. If using other clients, replace `${workspaceFolder}` with your local path (e.g. `C:/Projects/MyThesis` or `/home/user/thesis`).

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

## 📋 Sample Tool Invocation (`generate_academic_proposal`)

Here is an example payload using fictional student and institutional data:

```json
{
  "metadata": {
    "judul": "OPTIMIZING DISTRIBUTED SENSOR NETWORK LIFETIME USING REINFORCEMENT LEARNING ROUTING ALGORITHMS",
    "nama_mahasiswa": "Alex Mercer",
    "nim": "STD-2026-94821",
    "program_studi": "Department of Computer Science & Informatics",
    "departemen": "School of Computing",
    "fakultas": "Faculty of Engineering and Technology",
    "universitas": "Metropolis Institute of Technology",
    "kota": "Metropolis",
    "tahun": "2026"
  },
  "bab1_data": {
    "latar_belakang": [
      "The rapid proliferation of Internet of Things (IoT) devices in environmental monitoring has introduced critical challenges regarding power efficiency and network longevity in wireless sensor networks (WSNs).",
      "Conventional routing protocols, such as static shortest-path routing, frequently exhaust intermediate relay nodes prematurely, resulting in network fragmentation and degraded data reliability.",
      "To overcome these operational constraints, this research proposes an adaptive reinforcement learning routing mechanism that dynamically balances energy expenditure across network nodes while sustaining throughput."
    ],
    "rumusan_masalah_pengantar": "Based on the operational challenges and efficiency gaps identified above, the primary research question is formulated as follows:",
    "rumusan_masalah": "To what extent does the proposed reinforcement learning routing algorithm improve overall network lifetime and packet delivery ratio compared to conventional static routing protocols in large-scale wireless sensor networks?",
    "rumusan_masalah_penjelasan": "This single research question evaluates the causal relationship between the independent variable (reinforcement learning routing mechanism) and key dependent performance indicators (network operational lifetime and packet delivery ratio).",
    "tujuan_umum": "evaluate and quantify the network longevity and transmission efficiency improvements achieved by the reinforcement learning routing protocol compared to baseline routing approaches.",
    "tujuan_khusus": [
      "Analyze the energy consumption profiles and bottleneck factors in baseline sensor routing workflows.",
      "Design and model the adaptive reinforcement learning routing algorithm.",
      "Develop a proof-of-concept simulation environment for multi-hop sensor networks.",
      "Evaluate network lifetime, packet delivery ratio, and convergence time through rigorous benchmark simulations."
    ],
    "manfaat": [
      "For Sensor Network Practitioners: Provides an operational blueprint for resilient and energy-balanced wireless sensor deployments.",
      "For Academic Researchers: Contributes empirical evidence and benchmark datasets regarding reinforcement learning applications in low-power communication systems."
    ],
    "batasan_masalah": [
      "Evaluation is conducted within a simulated network environment consisting of 100 to 500 heterogeneous nodes.",
      "Hardware-level physical layer modifications are outside the scope of this investigation.",
      "Channel conditions are modeled based on standard log-distance path loss propagation."
    ],
    "sistematika_pembahasan": [
      "CHAPTER 1 INTRODUCTION: Details background context, research problem formulation, objectives, practical and theoretical benefits, scope limitations, and outline.",
      "CHAPTER 2 LITERATURE REVIEW: Synthesizes foundational networking concepts, reinforcement learning formulations, prior benchmark studies, and identified research gaps.",
      "CHAPTER 3 METHODOLOGY: Defines research design, experimental testbed parameters, evaluation metrics, and timeline."
    ]
  },
  "bab2_subbab": [
    {
      "title": "Wireless Sensor Network Routing Protocols",
      "level": 2,
      "paragraphs": [
        "Routing protocols in sensor networks must strike a delicate balance between routing overhead and battery conservation. Standard multi-hop schemes often incur uneven drain rates on central clusters."
      ]
    },
    {
      "title": "Reinforcement Learning in Dynamic Networks",
      "level": 2,
      "paragraphs": [
        "Q-learning and policy-gradient algorithms enable decentralized agents to discover optimal forwarding policies through continuous environmental reward feedback."
      ]
    }
  ],
  "bab3_subbab": [
    {
      "title": "Simulation Design and Experimental Setup",
      "level": 2,
      "paragraphs": [
        "The experimental framework is implemented using an event-driven network simulator modeling randomized node deployments and Poisson packet arrival processes."
      ]
    }
  ],
  "daftar_referensi": [
    "Akyildiz, I.F., Su, W., Sankarasubramaniam, Y. & Cayirci, E., 2002. Wireless sensor networks: a survey. Computer Networks, 38(4), pp.393–422.",
    "Sutton, R.S. & Barto, A.G., 2018. Reinforcement learning: An introduction. 2nd ed. Cambridge: MIT Press."
  ],
  "output_filename": "Proposal Skripsi v1.0.docx"
}
```

---

## ⚡ One-Shot Proposal Generation (`generate_proposal_from_topic`)

Instead of writing out every chapter by hand, you can generate a complete proposal by prompting with just a **Topic**, an optional literature **CSV file**, or retrieved research papers:

```json
{
  "topic": "Optimizing Distributed Sensor Network Lifetime using Reinforcement Learning Routing Algorithms",
  "variabel_x": "Reinforcement Learning Adaptive Q-Routing",
  "variabel_y": "Network Operational Longevity and Packet Delivery Ratio",
  "csv_filename": "literature.csv",
  "output_filename": "Proposal Skripsi v1.0.docx"
}
```

The server will automatically:

1. Formulate a single, measurable research question: *"Sejauh mana implementasi [X] mampu meningkatkan [Y] secara terukur..."*
2. Parse the CSV file and generate the literature review comparison matrix (`tabel_tinjauan_pustaka`) and Harvard citations (`daftar_referensi`).
3. Generate Chapters 1, 2, and 3 formatted according to academic guidelines.
4. Run Research Design Canvas v2.0 validation checks.
5. Save the final `.docx` directly into your mounted workspace.

---

## 📝 Sample Tool Invocation (`generate_praproposal_from_topic`)

Generate an official pre-proposal form document (`.odt`, format SA2-01A) directly from a topic prompt:

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
    "jenis_penelitian": "Implementatif",
    "tipe_penelitian": "Pengembangan Sistem & Komparasi Algoritma",
    "asal_judul": "Usulan Sendiri",
    "lokasi": "Malang",
    "nama_pembimbing": "Dr. Mahrus Ali, S.Kom., M.Kom.",
    "nip_pembimbing": "-"
  },
  "output_filename": "Praproposal_Skripsi_SA2-01A.odt"
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
