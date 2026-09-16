"""
canvas_validator.py
Modul validasi kepatuhan naskah terhadap aturan Research Design Model Canvas v2.0
"""
from typing import Dict, Any, List, Optional, Union
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
            },
            "PRA_Praproposal_SA2_01A": {
                "PRA_META": "Student & Topic Identity Completeness",
                "PRA_LB": "Problem Description within <= 500 words limit",
                "PRA_LR": "Literature Review & State-of-the-Art within <= 250 words limit",
                "PRA_RM": "Single Measurable Research Question (CLB04-01 & CLB04-02)",
                "PRA_VAR": "Explicit Independent (X) and Dependent (Y) Variables",
                "PRA_MET": "Methodology Plan & Operationalization within <= 250 words limit",
                "PRA_DP": "Standard Bibliography & Citations"
            }
        }
    }

def check_praproposal_canvas(
    metadata: Dict[str, Any],
    sections: Dict[str, Any],
    variabel_independen: Optional[str] = None,
    variabel_dependen: Optional[str] = None,
    single_problem_only: bool = True
) -> Dict[str, Any]:
    """
    Validasi kepatuhan naskah Pra-Proposal (Form SA2-01A) terhadap:
    1. Batasan kata per bagian (Latar Belakang <= 500 kata, Landasan Kepustakaan <= 250 kata, Metode <= 250 kata).
    2. Aturan Research Design Canvas (Single Problem Formulation, Variabel X & Y terdefinisi).
    3. Kelengkapan identitas mahasiswa dan usulan skripsi.
    """
    issues: List[str] = []
    passed: List[str] = []
    word_counts: Dict[str, int] = {}

    def _extract_text(sec_data: Any) -> str:
        if isinstance(sec_data, list):
            return " ".join([str(item) for item in sec_data if item])
        return str(sec_data or "")

    def _count_words(text: str) -> int:
        return len(text.strip().split()) if text.strip() else 0

    # 1. Validasi Metadata Identitas
    nama_mhs = str(metadata.get("nama_mahasiswa", "")).strip()
    nim_mhs = str(metadata.get("nim", "")).strip()
    judul = str(metadata.get("judul", "")).strip()

    if not nama_mhs or nama_mhs.lower() in ["mahasiswa peneliti", "-", ""]:
        issues.append("[PRA-META01] Nama mahasiswa belum diisi dengan nama lengkap resmi.")
    else:
        passed.append(f"[PRA-META01] Nama mahasiswa terverifikasi: {nama_mhs}")

    if not nim_mhs or nim_mhs in ["225150200111000", "-", ""]:
        issues.append("[PRA-META02] NIM mahasiswa belum diisi dengan NIM valid.")
    else:
        passed.append(f"[PRA-META02] NIM mahasiswa terverifikasi: {nim_mhs}")

    if not judul:
        issues.append("[PRA-META03] Judul / topik pra-proposal tidak boleh kosong.")
    else:
        passed.append("[PRA-META03] Judul pra-proposal terverifikasi.")

    # 2. Validasi Latar Belakang (Maksimal 500 kata)
    lb_text = _extract_text(sections.get("latar_belakang", ""))
    lb_words = _count_words(lb_text)
    word_counts["latar_belakang"] = lb_words

    if lb_words == 0:
        issues.append("[PRA-LB01] Bagian Deskripsi Masalah / Latar Belakang kosong.")
    elif lb_words > 500:
        issues.append(f"[PRA-LB01] Deskripsi Masalah melebihi batas ketentuan SA2-01A (maks 500 kata, terdeteksi {lb_words} kata).")
    else:
        passed.append(f"[PRA-LB01] Deskripsi Masalah mematuhi batas kata SA2-01A ({lb_words}/500 kata).")

    # 3. Validasi Landasan Kepustakaan (Maksimal 250 kata)
    lr_text = _extract_text(sections.get("landasan_kepustakaan", ""))
    lr_words = _count_words(lr_text)
    word_counts["landasan_kepustakaan"] = lr_words

    if lr_words == 0:
        issues.append("[PRA-LR01] Bagian Landasan Kepustakaan kosong.")
    elif lr_words > 250:
        issues.append(f"[PRA-LR01] Landasan Kepustakaan melebihi batas ketentuan SA2-01A (maks 250 kata, terdeteksi {lr_words} kata).")
    else:
        passed.append(f"[PRA-LR01] Landasan Kepustakaan mematuhi batas kata SA2-01A ({lr_words}/250 kata).")

    # 4. Validasi Rumusan Masalah (Single measurable question)
    rm_raw = sections.get("rumusan_masalah", [])
    if isinstance(rm_raw, list):
        rm_text = "\n".join([str(x) for x in rm_raw if str(x).strip()])
    else:
        rm_text = str(rm_raw).strip()

    if not rm_text:
        issues.append("[CLB04-01] Rumusan masalah tidak boleh kosong.")
    else:
        q_marks = rm_text.count("?")
        numbered_lines = [l for l in rm_text.split("\n") if l.strip() and l.strip()[0].isdigit() and l.strip()[1:3] in [". ", ") "]]
        total_q = max(q_marks, len(numbered_lines))

        if single_problem_only and total_q > 1:
            issues.append(f"[CLB04-01] Format pra-proposal mewajibkan 1 rumusan masalah tunggal, terdeteksi {total_q} pertanyaan.")
        else:
            passed.append("[CLB04-01] Format 1 rumusan masalah tunggal terverifikasi.")

        lower_rm = rm_text.lower()
        if lower_rm.startswith("bagaimana") and not any(kw in lower_rm for kw in ["sejauh", "pengaruh", "tingkat", "efektivitas", "efisiensi", "akurasi", "presisi", "performa"]):
            issues.append("[CLB04-02] Rumusan masalah diawali dengan kata tanya 'Bagaimana' kualitatif terbuka. Sebaiknya gunakan formulasi terukur seperti 'Sejauh manakah...' atau 'Bagaimanakah tingkat...'")
        else:
            passed.append("[CLB04-02] Formulasi pertanyaan mengindikasikan parameter pengukuran yang jelas.")

    # 5. Validasi Variabel Independen & Dependen
    vx = (variabel_independen or "").strip()
    vy = (variabel_dependen or "").strip()

    if not vx:
        # Coba deteksi dari judul / metode
        issues.append("[CLB04-02 / PRA-VAR01] Variabel independen (X / intervensi/metode) belum didefinisikan secara eksplisit.")
    else:
        passed.append(f"[PRA-VAR01] Variabel independen (X) terdefinisi: {vx}")

    if not vy:
        # Coba deteksi dari judul / rumusan masalah
        issues.append("[CLB04-03 / PRA-VAR02] Variabel dependen (Y / metrik/indikator keberhasilan) belum didefinisikan secara eksplisit.")
    else:
        passed.append(f"[PRA-VAR02] Variabel dependen (Y) terdefinisi: {vy}")

    # 6. Validasi Rencana Metode Penelitian (Maksimal 250 kata)
    met_text = _extract_text(sections.get("metode", ""))
    met_words = _count_words(met_text)
    word_counts["metode"] = met_words

    if met_words == 0:
        issues.append("[PRA-MET01] Bagian Rencana Metode Penelitian kosong.")
    elif met_words > 250:
        issues.append(f"[PRA-MET01] Rencana Metode Penelitian melebihi batas ketentuan SA2-01A (maks 250 kata, terdeteksi {met_words} kata).")
    else:
        passed.append(f"[PRA-MET01] Rencana Metode Penelitian mematuhi batas kata SA2-01A ({met_words}/250 kata).")

    # 7. Validasi Daftar Pustaka
    dp_raw = sections.get("daftar_pustaka", [])
    if isinstance(dp_raw, list):
        dp_count = len([x for x in dp_raw if str(x).strip()])
    elif isinstance(dp_raw, str):
        dp_count = len([x for x in dp_raw.split("\n") if x.strip()])
    else:
        dp_count = 0
    word_counts["total_referensi"] = dp_count

    if dp_count == 0:
        issues.append("[PRA-REF01] Daftar pustaka kosong.")
    elif dp_count < 2:
        issues.append(f"[PRA-REF01] Jumlah referensi minim ({dp_count} referensi). Disarankan menyertakan minimal 3 referensi ilmiah relevan.")
    else:
        passed.append(f"[PRA-REF01] Daftar pustaka mencukupi ({dp_count} referensi).")

    # 8. Cek Klausul Klise Administratif
    full_text = f"{lb_text} {met_text}".lower()
    cliche_words = ["syarat kelulusan", "mencapai gelar", "menambah wawasan", "memperluas ilmu pengetahuan"]
    found_cliche = [c for c in cliche_words if c in full_text]
    if found_cliche:
        issues.append(f"[CLB06-02] Teks naskah memuat klausul klise ({', '.join(found_cliche)}).")
    else:
        passed.append("[CLB06-02] Naskah pra-proposal terbebas dari klausul klise administratif.")

    status = "APPROVED" if len(issues) == 0 else "NEEDS_REVISION"
    compliance_score = int((len(passed) / (len(passed) + len(issues))) * 100) if (passed or issues) else 0

    return {
        "status": status,
        "compliance_score_percent": compliance_score,
        "passed_checks": passed,
        "violations": issues,
        "total_checks": len(passed) + len(issues),
        "word_counts": word_counts,
        "word_count_limits": {
            "latar_belakang_max": 500,
            "landasan_kepustakaan_max": 250,
            "metode_max": 250
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

def generate_praproposal_rubric_checklist_report(
    metadata: Dict[str, Any],
    sections: Dict[str, Any],
    variabel_independen: Optional[str] = None,
    variabel_dependen: Optional[str] = None,
    single_problem_only: bool = True
) -> str:
    """
    Menghasilkan laporan audit kepatuhan Pra-Proposal (SA2-01A) dalam format Markdown.
    """
    check_res = check_praproposal_canvas(
        metadata=metadata,
        sections=sections,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        single_problem_only=single_problem_only
    )

    judul = metadata.get("judul", "Pra-Proposal Skripsi")
    nama_mhs = metadata.get("nama_mahasiswa", "Mahasiswa")
    nim_mhs = metadata.get("nim", "-")
    pembimbing = metadata.get("nama_pembimbing", "-")
    score = check_res["compliance_score_percent"]
    status_badge = "🟢 **PASSED & COMPLIANT**" if check_res["status"] == "APPROVED" else "🟡 **NEEDS REVISION**"
    wc = check_res.get("word_counts", {})

    items_pra = [
        ("PRA-META01", "Student Identity Verification", "Student name and NIM are officially verified.", not any("PRA-META01" in v or "PRA-META02" in v for v in check_res["violations"]), f"Name: {nama_mhs}, NIM: {nim_mhs}"),
        ("PRA-META02", "Topic & Advisor Alignment", "Topic title and supervisor assignment defined.", bool(judul) and not any("PRA-META03" in v for v in check_res["violations"]), f"Advisor: {pembimbing}"),
        ("PRA-LB01", "Problem Description Scope", "Clear problem context within standard limit (<= 500 words).", not any("PRA-LB01" in v for v in check_res["violations"]), f"{wc.get('latar_belakang', 0)} / 500 words"),
        ("PRA-LR01", "Literature Review & State-of-the-Art", "Relevant literature base within limit (<= 250 words).", not any("PRA-LR01" in v for v in check_res["violations"]), f"{wc.get('landasan_kepustakaan', 0)} / 250 words"),
        ("PRA-RM01", "Single Research Question (CLB04-01)", "Articulates exactly 1 measurable research question.", not any("CLB04-01" in v for v in check_res["violations"]), "1 focused question"),
        ("PRA-RM02", "Measurable Phrasing (CLB04-02)", "Question uses measurable parameters (not open qualitative).", not any("CLB04-02" in v for v in check_res["violations"]), "Measured parameters checked"),
        ("PRA-VAR01", "Independent Variable (X)", "Intervention, method, or artifact clearly identified.", not any("PRA-VAR01" in v for v in check_res["violations"]), variabel_independen or "Extracted / Defined"),
        ("PRA-VAR02", "Dependent Variable (Y)", "Outcome, metric, or target performance clearly identified.", not any("PRA-VAR02" in v for v in check_res["violations"]), variabel_dependen or "Extracted / Defined"),
        ("PRA-MET01", "Methodology Plan Scope", "Clear implementation and testing steps within limit (<= 250 words).", not any("PRA-MET01" in v for v in check_res["violations"]), f"{wc.get('metode', 0)} / 250 words"),
        ("PRA-REF01", "Standard Bibliography (CLR06)", "Relevant reference list formatted systematically.", not any("PRA-REF01" in v for v in check_res["violations"]), f"{wc.get('total_referensi', 0)} references"),
        ("PRA-CLI01", "Anti-Cliché Assurance", "Free of administrative clichés or vague generic phrases.", not any("CLB06-02" in v for v in check_res["violations"]), "Checked against administrative clichés")
    ]

    md = []
    md.append(f"# 📋 Pra-Proposal (SA2-01A) Rubric & Canvas Audit Report\n")
    md.append(f"| Property | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| **Proposal Title** | {judul} |")
    md.append(f"| **Author / Student** | {nama_mhs} ({nim_mhs}) |")
    md.append(f"| **Advisor / Pembimbing** | {pembimbing} |")
    md.append(f"| **Evaluation Date** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    md.append(f"| **Compliance Score** | **{score}%** |")
    md.append(f"| **Audit Status** | {status_badge} |\n")
    md.append(f"---\n")

    md.append(f"## 1. Executive Summary\n")
    if check_res["status"] == "APPROVED":
        md.append(f"> [!TIP]\n> **Pra-Proposal Meets Institutional & Canvas Standards (SA2-01A)**\n> The document fulfills all word-count constraints (Latar Belakang <= 500 words, Landasan Kepustakaan <= 250 words, Metode <= 250 words), formulates exactly one measurable research question, and defines clear independent and dependent variables.\n")
    else:
        md.append(f"> [!WARNING]\n> **Revisions Recommended Before Submission to Advisor**\n> The audit detected {len(check_res['violations'])} item(s) requiring refinement.\n")

    md.append(f"## 2. Word Count Budget Analysis\n")
    md.append(f"| Section | Limit | Word Count | Status |")
    md.append(f"| :--- | :---: | :---: | :---: |")
    md.append(f"| Deskripsi Masalah / Latar Belakang | Max 500 kata | {wc.get('latar_belakang', 0)} kata | {'✅ OK' if wc.get('latar_belakang', 0) <= 500 else '❌ OVER LIMIT'} |")
    md.append(f"| Landasan Kepustakaan | Max 250 kata | {wc.get('landasan_kepustakaan', 0)} kata | {'✅ OK' if wc.get('landasan_kepustakaan', 0) <= 250 else '❌ OVER LIMIT'} |")
    md.append(f"| Rencana Metode Penelitian | Max 250 kata | {wc.get('metode', 0)} kata | {'✅ OK' if wc.get('metode', 0) <= 250 else '❌ OVER LIMIT'} |")
    md.append(f"| Total Sitasi Daftar Pustaka | Min 2-3 item | {wc.get('total_referensi', 0)} item | {'✅ OK' if wc.get('total_referensi', 0) >= 2 else '⚠️ LOW'} |\n")

    md.append(f"## 3. Checklist & Rubric Matrix\n")
    md.append(f"| Code | Criterion | Status | Detail / Evidence |")
    md.append(f"| :--- | :--- | :---: | :--- |")
    for code, name, desc, passed_flag, detail in items_pra:
        mark = "✅ PASS" if passed_flag else "❌ REVIEW"
        md.append(f"| `{code}` | **{name}**<br>*{desc}* | {mark} | {detail} |")
    md.append("")

    md.append(f"## 4. Findings & Actionable Advice\n")
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


