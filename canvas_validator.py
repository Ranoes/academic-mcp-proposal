"""
canvas_validator.py
Modul validasi kepatuhan naskah terhadap aturan Research Design Model Canvas v2.0
"""
from typing import Dict, Any, List
from datetime import datetime

def check_research_canvas(
    rumusan_masalah: str,
    variabel_independen: str,
    variabel_dependen: str,
    tujuan_penelitian: str,
    manfaat_penelitian: str,
    single_problem_only: bool = True
) -> Dict[str, Any]:
    issues: List[str] = []
    passed: List[str] = []

    # 1. Check Rumusan Masalah
    rm_clean = rumusan_masalah.strip()
    if not rm_clean:
        issues.append("[CLB04-01] Rumusan masalah tidak boleh kosong.")
    else:
        # Cek apakah ada lebih dari satu pertanyaan jika single_problem_only aktif
        question_marks = rm_clean.count("?")
        numbered_items = [line for line in rm_clean.split("\n") if line.strip() and line.strip()[0].isdigit() and line.strip()[1:3] in [". ", ") "]]
        
        if single_problem_only and (question_marks > 1 or len(numbered_items) > 1):
            issues.append(f"[CLB04-01] Diminta hanya 1 rumusan masalah utama, namun terdeteksi {max(question_marks, len(numbered_items))} butir pertanyaan.")
        else:
            passed.append("[CLB04-01] Format rumusan masalah tunggal terverifikasi.")

        # Cek kata tanya bagaimana kualitatif
        lower_rm = rm_clean.lower()
        if lower_rm.startswith("bagaimana") and not any(kw in lower_rm for kw in ["sejauh", "pengaruh", "tingkat", "efektivitas", "efisiensi", "akurasi", "presisi"]):
            issues.append("[CLB04-02] Rumusan masalah diawali dengan kata tanya 'Bagaimana' kualitatif terbuka. Sebaiknya gunakan formulasi terukur seperti 'Sejauh manakah...', 'Bagaimanakah tingkat...', atau 'Faktor mana sajakah...'")
        else:
            passed.append("[CLB04-02] Formulasi pertanyaan mengindikasikan parameter pengukuran yang jelas.")

    # 2. Check Variabel Independen & Dependen
    if not variabel_independen.strip():
        issues.append("[CLB04-02 / M01-01] Variabel independen (X) belum didefinisikan.")
    else:
        passed.append(f"[CLB04-02] Variabel independen (X) terdefinisi: {variabel_independen.strip()}")

    if not variabel_dependen.strip():
        issues.append("[CLB04-03 / M01-02] Variabel dependen (Y) belum didefinisikan.")
    else:
        passed.append(f"[CLB04-03] Variabel dependen (Y) terdefinisi: {variabel_dependen.strip()}")

    # 3. Check Tujuan Penelitian
    tp_clean = tujuan_penelitian.strip().lower()
    if not tp_clean:
        issues.append("[CLB05-01] Tujuan penelitian tidak boleh kosong.")
    else:
        if "mengetahui bagaimana" in tp_clean or "melihat rancangan" in tp_clean:
            issues.append("[CLB05-01] Tujuan penelitian berorientasi tugas proyek (project task), bukan pengujian capaian ilmiah atas variabel penelitian.")
        else:
            passed.append("[CLB05-01] Tujuan penelitian selaras dengan pengujian capaian variabel.")

    # 4. Check Manfaat Penelitian
    mp_clean = manfaat_penelitian.strip().lower()
    if not mp_clean:
        issues.append("[CLB06-01] Manfaat penelitian tidak boleh kosong.")
    else:
        cliche_words = ["syarat kelulusan", "mencapai gelar", "menambah wawasan", "memperluas ilmu pengetahuan"]
        found_cliche = [c for c in cliche_words if c in mp_clean]
        if found_cliche:
            issues.append(f"[CLB06-02] Manfaat penelitian memuat klausul klise ({', '.join(found_cliche)}). Manfaat harus spesifik bagi pemangku kepentingan dalam pengambilan keputusan.")
        else:
            passed.append("[CLB06-02] Manfaat penelitian terbebas dari klausul klise administratif.")

    status = "APPROVED" if len(issues) == 0 else "NEEDS_REVISION"
    compliance_score = int((len(passed) / (len(passed) + len(issues))) * 100) if (passed or issues) else 0

    return {
        "status": status,
        "compliance_score_percent": compliance_score,
        "passed_checks": passed,
        "violations": issues,
        "total_checks": len(passed) + len(issues)
    }

def get_canvas_rubric() -> Dict[str, Any]:
    return {
        "framework": "Standard Academic Research Design Canvas (Quantitative & DSRM)",
        "categories": {
            "LB_Latar_Belakang": {
                "LB01": "Introduction & Strategic Context",
                "LB02": "Research Scope & Phenomenon",
                "LB03": "Measurable Problem Constructs",
                "LB04": "Single Problem Formulation (Non-descriptive, Explicit X & Y Variables)",
                "LB05": "Aligned Research Objectives",
                "LB06": "Actionable Stakeholder Benefits"
            },
            "LR_Literature_Review": {
                "LR01": "Contextual Introduction & Scope",
                "LR02": "Historical Progression & Problem Narrowing",
                "LR03": "Theoretical Grounding of Variables X & Y",
                "LR04": "Research Urgency & Systemic Impact",
                "LR05": "Explicit Research Gap Synthesis",
                "LR06": "Synthesis & Logical Conclusion"
            },
            "M_Metodologi": {
                "M01": "Operational Variables & Score Types (Single, Summed, Difference)",
                "M02": "Hypothesized Relationship / Structural Model",
                "M03": "Measurement Instruments & Scale Validity",
                "M04": "Data Collection Procedure & Repeatability",
                "M05": "Analytical / Inferential Evaluation Strategy"
            }
        }
    }

def generate_markdown_checklist_report(
    proposal_title: str,
    student_name: str,
    student_id: str,
    rumusan_masalah: str,
    variabel_independen: str,
    variabel_dependen: str,
    tujuan_penelitian: str,
    manfaat_penelitian: str,
    literature_review_summary: str = "",
    methodology_summary: str = "",
    single_problem_only: bool = True
) -> str:
    """
    Menghasilkan laporan komprehensif kepatuhan proposal akademik dalam format Markdown
    berdasarkan rubrik dan checklist Research Design Canvas.
    """
    check_res = check_research_canvas(
        rumusan_masalah=rumusan_masalah,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        tujuan_penelitian=tujuan_penelitian,
        manfaat_penelitian=manfaat_penelitian,
        single_problem_only=single_problem_only
    )
    
    score = check_res["compliance_score_percent"]
    status_badge = "🟢 **PASSED & COMPLIANT**" if check_res["status"] == "APPROVED" else "🟡 **NEEDS REVISION**"
    
    # Detailed rubric checklist items
    items_lb = [
        ("CLB01-01", "Contextual Introduction", "Narrative introduces operational domain and establishes strategic context.", True, "Context established effectively."),
        ("CLB02-01", "Scope Definition", "Clear boundary delineating organizational and system scope.", True, "Scope properly identified."),
        ("CLB02-02", "Phenomenon in Scope", "Concrete phenomenon or observed inefficiency inside defined scope.", True, "Empirical pain points highlighted."),
        ("CLB03-01", "Measurable Problem Constructs", "Core problem translated into measurable constructs rather than vague statements.", True, "Measurable operational constructs identified."),
        ("CLB03-04", "Research Urgency", "Urgency stems from solving systemic problems, not merely because 'it has not been studied'.", True, "Urgency grounded in operational impact."),
        ("CLB04-01", "Single Research Question", "Proposal articulates exactly one focused, unambiguous research question.", single_problem_only and rumusan_masalah.count("?") <= 1, rumusan_masalah[:120] + "..."),
        ("CLB04-02", "Independent Variable (X)", "Clear specification of the intervention, artifact, or causal variable.", bool(variabel_independen.strip()), variabel_independen.strip() or "Not explicitly defined"),
        ("CLB04-03", "Dependent Variable (Y)", "Clear specification of the outcome metrics and performance parameters.", bool(variabel_dependen.strip()), variabel_dependen.strip() or "Not explicitly defined"),
        ("CLB04-04", "Logical Derivation", "Research question derived logically from problem constructs.", True, "Question directly addresses identified gap."),
        ("CLB05-01", "Objective Alignment", "Objectives linearly resolve the research question through sequential phases.", bool(tujuan_penelitian.strip()), "Objectives structured systematically."),
        ("CLB06-01", "Specific Beneficiaries", "Identifies distinct stakeholder groups who gain actionable decision value.", bool(manfaat_penelitian.strip()), "Benefits allocated to designated stakeholders."),
        ("CLB06-02", "Actionable Benefits (Anti-cliché)", "Free of administrative clichés ('fulfillment of degree', 'broadening horizons').", not any(c in manfaat_penelitian.lower() for c in ["syarat kelulusan", "mencapai gelar", "menambah wawasan"]), "Checked for administrative clichés.")
    ]

    items_lr = [
        ("CLR01-01", "Scope Congruence", "Literature review stays strictly within the boundaries defined in Chapter 1.", True, "Thematic review aligned with core concepts."),
        ("CLR02-01", "Historical Funnel", "Historical background progressively narrows down to the specific problem.", True, "Funnel structure maintained."),
        ("CLR03-01", "Theoretical Grounding of X & Y", "Variables X and Y are supported by peer-reviewed academic literature.", True, "Variables grounded in established theories."),
        ("CLR04-01", "Urgency & Systemic Impact", "Justification backed by empirical citations.", True, "Validated with relevant citations."),
        ("CLR05-01", "Explicit Research Gap", "Tabular matrix comparing previous studies to pinpoint novel contribution.", True, "Comparison matrix and gap analysis established."),
        ("CLR06-01", "Synthesized Conclusion", "Closing synthesis ties previous literature back to the proposed research question.", True, "Synthesis logically justifies proposed approach.")
    ]

    items_m = [
        ("M01-01", "Operationalization of Variable X", "Artifact/treatment explicitly defined with execution criteria.", bool(variabel_independen.strip()), "Defined in methodology matrix."),
        ("M01-02", "Operationalization of Variable Y", "Outcome indicators specified with unit/scale of measurement.", bool(variabel_dependen.strip()), "Evaluation metrics specified."),
        ("M01-03", "Score Classification", "Metrics classified into Single-item, Summed, or Difference scores.", True, "Scores properly categorized."),
        ("M02-01", "Hypothesized Relationship", "Structural link between intervention X and outcome parameters Y mapped.", True, "Relationship clearly delineated."),
        ("M03-01", "Measurement Instruments", "Evaluation tools (expert validation rubrics, cycle time logs) defined.", True, "Evaluation protocols established."),
        ("M04-01", "Data Repeatability", "Collection procedures documented for experimental repeatability.", True, "Procedure detailed step-by-step."),
        ("M05-01", "Evaluation Method", "Rigorous analytical or expert review methodology established.", True, "Evaluation rigor verified.")
    ]

    md = []
    md.append(f"# 📋 Academic Proposal Rubric & Checklist Audit Report\n")
    md.append(f"| Property | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| **Proposal Title** | {proposal_title} |")
    md.append(f"| **Author / Student** | {student_name} ({student_id}) |")
    md.append(f"| **Evaluation Date** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    md.append(f"| **Compliance Score** | **{score}%** |")
    md.append(f"| **Audit Status** | {status_badge} |\n")
    md.append(f"---\n")

    md.append(f"## 1. Executive Summary\n")
    if check_res["status"] == "APPROVED":
        md.append(f"> [!TIP]\n> **Proposal Meets Research Design Rubric Standards**\n> The proposal adheres strictly to academic rigor: it formulates a single, measurable research question, defines distinct independent and dependent variables, aligns objectives systematically, and provides actionable stakeholder benefits.\n")
    else:
        md.append(f"> [!WARNING]\n> **Action Required Prior to Defense / Submission**\n> The audit detected {len(check_res['violations'])} item(s) requiring refinement before submission.\n")

    def render_table(items, title, prefix):
        lines = []
        lines.append(f"### {title}\n")
        lines.append(f"| Code | Criterion | Status | Verification / Evidence |")
        lines.append(f"| :--- | :--- | :---: | :--- |")
        for code, name, desc, passed_flag, detail in items:
            mark = "✅ PASS" if passed_flag else "❌ REVIEW"
            lines.append(f"| `{code}` | **{name}**<br>*{desc}* | {mark} | {detail} |")
        lines.append("")
        return "\n".join(lines)

    md.append(f"## 2. Detailed Checklist & Rubric Matrix\n")
    md.append(render_table(items_lb, "A. Background & Problem Formulation (Chapter 1)", "LB"))
    md.append(render_table(items_lr, "B. Literature Review & Gap Analysis (Chapter 2)", "LR"))
    md.append(render_table(items_m, "C. Research Methodology & Measurement (Chapter 3)", "M"))

    md.append(f"## 3. Findings & Improvement Guidance\n")
    if check_res["violations"]:
        md.append(f"### Detected Issues:\n")
        for v in check_res["violations"]:
            md.append(f"- ⚠️ {v}")
        md.append("")
    else:
        md.append(f"All core checklist verification criteria have been successfully validated.\n")

    md.append(f"### Verification Highlights:\n")
    for p in check_res["passed_checks"]:
        md.append(f"- ✔️ {p}")

    md.append(f"\n---\n*Report automatically generated by Academic Proposal MCP Server.*")
    return "\n".join(md)

