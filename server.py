"""
server.py
Independent Academic Proposal MCP Server
Kompatibel dengan Model Context Protocol (MCP) untuk otomatisasi penyusunan dan validasi proposal skripsi.
"""
import os
import shutil
import subprocess
from typing import Dict, Any, List, Optional
try:
    from mcp.server import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP  # type: ignore
from canvas_validator import (
    check_research_canvas,
    get_canvas_rubric,
    generate_markdown_checklist_report
)
from builder_engine import (
    create_generic_proposal,
    inspect_doc,
    record_version_change,
    DEFAULT_TEMPLATE_PATH
)
from csv_ingestor import parse_literature_csv
from topic_synthesizer import plan_research, synthesize_proposal_from_inputs


mcp = FastMCP("academic-proposal-mcp")

WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", "/workspace")
if not os.path.exists(WORKSPACE_DIR):
    WORKSPACE_DIR = os.getcwd()

@mcp.tool()
def generate_rubric_checklist_report(
    proposal_title: str,
    student_name: str,
    student_id: str,
    rumusan_masalah: str,
    variabel_independen: str,
    variabel_dependen: str,
    tujuan_penelitian: str,
    manfaat_penelitian: str,
    output_markdown_filename: str = "proposal_rubric_checklist_report.md",
    save_to_workspace: bool = True
) -> dict:
    """
    Menghasilkan laporan audit kepatuhan proposal skripsi dalam format Markdown
    berdasarkan rubrik evaluasi dan checklist Research Design Canvas (Chapter 1, 2, dan 3).
    Dapat langsung disimpan ke workspace sebagai berkas Markdown (.md).
    """
    md_content = generate_markdown_checklist_report(
        proposal_title=proposal_title,
        student_name=student_name,
        student_id=student_id,
        rumusan_masalah=rumusan_masalah,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        tujuan_penelitian=tujuan_penelitian,
        manfaat_penelitian=manfaat_penelitian
    )
    
    file_path = None
    if save_to_workspace:
        file_path = os.path.join(WORKSPACE_DIR, output_markdown_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    return {
        "status": "SUCCESS",
        "output_file": output_markdown_filename if save_to_workspace else None,
        "saved_path": file_path,
        "markdown_report": md_content
    }

@mcp.tool()
def validate_canvas_compliance(
    rumusan_masalah: str,
    variabel_independen: str,
    variabel_dependen: str,
    tujuan_penelitian: str,
    manfaat_penelitian: str,
    single_problem_only: bool = True
) -> dict:
    """
    Memvalidasi kepatuhan naskah proposal terhadap panduan Research Design Model Canvas v2.0.
    Dapat digunakan untuk segala topik skripsi/tesis.
    Memeriksa:
    1. Rumusan masalah tunggal dan berorientasi pengukuran (non-deskriptif).
    2. Variabel independen (X) dan dependen (Y) yang terdefinisi eksplisit.
    3. Tujuan penelitian yang linier dengan capaian variabel.
    4. Manfaat penelitian spesifik bagi stakeholders (bebas klausul klise).
    """
    return check_research_canvas(
        rumusan_masalah=rumusan_masalah,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        tujuan_penelitian=tujuan_penelitian,
        manfaat_penelitian=manfaat_penelitian,
        single_problem_only=single_problem_only
    )

@mcp.tool()
def get_canvas_guidelines() -> dict:
    """
    Mengambil rubrik lengkap checklist Research Design Model Canvas v2.0 (LB01-LB06, LR01-LR06, M01-M05)
    sebagai panduan bagi pengguna atau asisten AI dalam menyusun naskah ilmiah.
    """
    return get_canvas_rubric()

@mcp.tool()
def generate_academic_proposal(
    metadata: Dict[str, str],
    bab1_data: Dict[str, Any],
    bab2_subbab: List[Dict[str, Any]],
    bab3_subbab: List[Dict[str, Any]],
    daftar_referensi: List[str],
    tabel_tinjauan_pustaka: Optional[List[List[str]]] = None,
    tabel_operasionalisasi_variabel: Optional[List[List[str]]] = None,
    tabel_tahapan_metode: Optional[List[List[str]]] = None,
    tabel_jadwal: Optional[List[List[str]]] = None,
    output_filename: str = "Proposal Skripsi v1.0.docx",
    custom_template_filename: Optional[str] = None
) -> dict:
    """
    Membuat dokumen DOCX proposal skripsi lengkap berbasis template resmi FILKOM UB.
    Dapat digunakan oleh mahasiswa mana pun dengan mengisi parameter metadata dan teks bab.
    """
    out_path = os.path.join(WORKSPACE_DIR, output_filename)
    tpl_path = None
    if custom_template_filename:
        custom_p = os.path.join(WORKSPACE_DIR, custom_template_filename)
        if os.path.exists(custom_p):
            tpl_path = custom_p

    try:
        res = create_generic_proposal(
            metadata=metadata,
            bab1_data=bab1_data,
            bab2_subbab=bab2_subbab,
            bab3_subbab=bab3_subbab,
            daftar_referensi=daftar_referensi,
            tabel_tinjauan_pustaka=tabel_tinjauan_pustaka,
            tabel_operasionalisasi_variabel=tabel_operasionalisasi_variabel,
            tabel_tahapan_metode=tabel_tahapan_metode,
            tabel_jadwal=tabel_jadwal,
            output_path=out_path,
            template_path=tpl_path
        )
        return res
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
def inspect_proposal_document(filename: str = "Proposal Skripsi v1.0.docx") -> dict:
    """
    Memeriksa struktur dokumen proposal skripsi (.docx) di dalam workspace.
    Mengembalikan informasi: jumlah paragraf, tabel, seksi, perkiraan kata, dan daftar heading bab/subbab.
    """
    docx_path = os.path.join(WORKSPACE_DIR, filename)
    return inspect_doc(docx_path)

@mcp.tool()
def increment_proposal_version(
    current_version: str,
    new_version: str,
    changelog: str
) -> dict:
    """
    Menduplikasi versi aktif proposal skripsi ke versi baru dan mencatat riwayat perubahan ke version_history.json.
    Contoh: current_version='v1.0', new_version='v1.1', changelog='Penyelarasan rumusan masalah tunggal'
    """
    src_file = os.path.join(WORKSPACE_DIR, f"Proposal Skripsi {current_version}.docx")
    dst_file = os.path.join(WORKSPACE_DIR, f"Proposal Skripsi {new_version}.docx")

    if not os.path.exists(src_file):
        return {
            "status": "ERROR",
            "message": f"Berkas sumber {src_file} tidak ditemukan di workspace."
        }

    shutil.copy2(src_file, dst_file)
    record_status = record_version_change(WORKSPACE_DIR, current_version, new_version, changelog)

    return {
        "status": "SUCCESS",
        "created_file": os.path.basename(dst_file),
        "source_file": os.path.basename(src_file),
        "changelog": changelog,
        "log_status": record_status
    }

@mcp.tool()
def export_proposal_as_markdown(filename: str = "Proposal Skripsi v1.0.docx") -> dict:
    """
    Mengekstraksi seluruh isi dokumen proposal .docx menjadi format Markdown bersih
    yang mudah dibaca dan diolah oleh LLM / pengguna.
    """
    import docx
    docx_path = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(docx_path):
        return {"status": "ERROR", "message": f"Berkas {docx_path} tidak ditemukan."}

    doc = docx.Document(docx_path)
    md_lines = [f"# Ekstraksi Markdown: {filename}\n"]

    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        style = p.style.name.lower()
        if style == "title":
            md_lines.append(f"# {txt}\n")
        elif style == "heading 1":
            md_lines.append(f"\n## {txt}\n")
        elif style == "heading 2":
            md_lines.append(f"\n### {txt}\n")
        elif style == "heading 3":
            md_lines.append(f"\n#### {txt}\n")
        elif style == "reference heading":
            md_lines.append(f"\n## {txt}\n")
        elif style == "caption":
            md_lines.append(f"\n**{txt}**\n")
        elif style == "references":
            md_lines.append(f"- {txt}")
        else:
            md_lines.append(f"{txt}\n")

    return {
        "status": "SUCCESS",
        "filename": filename,
        "markdown_content": "\n".join(md_lines)
    }

@mcp.tool()
def plan_proposal_research(
    topic: str,
    bidang_kajian: Optional[str] = None,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None
) -> dict:
    """
    Menurunkan rumusan masalah tunggal, variabel independen (X), variabel dependen (Y),
    tujuan penelitian terukur, serta kueri pencarian literatur yang dioptimalkan
    khusus untuk dijalankan pada MCP paper-search (search_arxiv, search_semantic, search_google_scholar).
    """
    return plan_research(
        topic=topic,
        bidang_kajian=bidang_kajian,
        variabel_x=variabel_x,
        variabel_y=variabel_y
    )

@mcp.tool()
def parse_literature_csv_data(
    csv_filename: str = "literature.csv",
    csv_content: Optional[str] = None
) -> dict:
    """
    Membaca dan mem-parsing berkas CSV literatur penelitian dari workspace (misal: literature.csv).
    Mengekstrak kolom peneliti, tahun, judul, metode, hasil, dan research gap,
    serta menghasilkan matriks tabel tinjauan pustaka dan daftar referensi Harvard.
    """
    file_p = None
    if not csv_content:
        file_p = os.path.join(WORKSPACE_DIR, csv_filename)
    return parse_literature_csv(file_path=file_p, csv_content=csv_content)

@mcp.tool()
def generate_proposal_from_topic(
    topic: str,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None,
    csv_filename: Optional[str] = None,
    csv_content: Optional[str] = None,
    retrieved_papers: Optional[List[Dict[str, Any]]] = None,
    student_metadata: Optional[Dict[str, str]] = None,
    latar_belakang_notes: Optional[List[str]] = None,
    metode_penelitian_notes: Optional[List[str]] = None,
    output_filename: str = "Proposal Skripsi v1.0.docx",
    custom_template_filename: Optional[str] = None
) -> dict:
    """
    Menghasilkan dokumen proposal skripsi (.docx) lengkap hanya dengan memberikan topik penelitian,
    data CSV literatur di workspace, dan/atau data paper yang diperoleh dari MCP paper-search.
    Secara otomatis menyusun Bab 1, Bab 2 (beserta tabel tinjauan pustaka), Bab 3,
    dan daftar referensi, lalu menyimpannya langsung ke workspace.
    """
    # 1. Turunkan atau validasi X dan Y
    plan = plan_research(topic=topic, variabel_x=variabel_x, variabel_y=variabel_y)
    vx = plan["variabel_x"]
    vy = plan["variabel_y"]

    # 2. Metadata default jika belum lengkap
    meta = {
        "judul": topic.upper(),
        "nama_mahasiswa": "Mahasiswa Peneliti",
        "nim": "225150200111000",
        "program_studi": "Teknik Informatika",
        "departemen": "Departemen Teknik Informatika",
        "fakultas": "Fakultas Ilmu Komputer",
        "universitas": "Universitas Brawijaya",
        "kota": "Malang",
        "tahun": "2026"
    }
    if student_metadata:
        meta.update(student_metadata)

    # 3. Proses literatur dari CSV jika tersedia
    records = []
    table_matrix = None
    references = []

    if csv_filename or csv_content:
        csv_file_path = os.path.join(WORKSPACE_DIR, csv_filename) if csv_filename else None
        csv_res = parse_literature_csv(file_path=csv_file_path, csv_content=csv_content)
        if csv_res.get("status") == "SUCCESS":
            records.extend(csv_res.get("records", []))
            table_matrix = csv_res.get("table_matrix")
            references.extend(csv_res.get("references", []))

    # 4. Tambahkan data dari retrieved_papers (hasil paper-search MCP)
    if retrieved_papers:
        if not table_matrix:
            table_matrix = [["No", "Peneliti & Tahun", "Judul Penelitian", "Metode / Algoritma", "Hasil & Temuan", "Research Gap"]]
        
        current_no = len(table_matrix)
        for p in retrieved_papers:
            title = p.get("title", f"Paper Studi {current_no}")
            authors = p.get("authors") or p.get("author") or "Peneliti Terkait"
            if isinstance(authors, list):
                authors = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
            year = str(p.get("year") or p.get("published") or "2024")[:4]
            method = p.get("method") or p.get("snippet") or "-"
            results = p.get("results") or p.get("abstract") or "-"
            gap = p.get("gap") or "Perlu eksplorasi performa pada skenario lanjutan"

            records.append({
                "no": current_no,
                "author": str(authors),
                "year": year,
                "title": title,
                "method": str(method)[:150],
                "results": str(results)[:200],
                "gap": gap
            })

            table_matrix.append([
                str(current_no),
                f"{authors} ({year})",
                title,
                str(method)[:120],
                str(results)[:150],
                str(gap)[:120]
            ])

            ref_str = f"{authors}, {year}. {title}."
            if p.get("doi"):
                ref_str += f" DOI: {p.get('doi')}."
            elif p.get("url"):
                ref_str += f" Tersedia di: {p.get('url')}."
            references.append(ref_str)
            current_no += 1

    # 5. Sintesis konten proposal
    proposal_content = synthesize_proposal_from_inputs(
        topic=topic,
        metadata=meta,
        variabel_x=vx,
        variabel_y=vy,
        literature_records=records,
        table_matrix=table_matrix,
        references=references,
        latar_belakang_notes=latar_belakang_notes,
        metode_penelitian_notes=metode_penelitian_notes
    )

    # 6. Validasi Research Canvas v2.0
    canvas_check = check_research_canvas(
        rumusan_masalah=proposal_content["bab1_data"]["rumusan_masalah"],
        variabel_independen=vx,
        variabel_dependen=vy,
        tujuan_penelitian=proposal_content["bab1_data"]["tujuan_umum"],
        manfaat_penelitian="; ".join(proposal_content["bab1_data"]["manfaat"]),
        single_problem_only=True
    )

    # 7. Generate berkas Word DOCX
    out_path = os.path.join(WORKSPACE_DIR, output_filename)
    tpl_path = None
    if custom_template_filename:
        custom_p = os.path.join(WORKSPACE_DIR, custom_template_filename)
        if os.path.exists(custom_p):
            tpl_path = custom_p

    doc_result = create_generic_proposal(
        metadata=meta,
        bab1_data=proposal_content["bab1_data"],
        bab2_subbab=proposal_content["bab2_subbab"],
        bab3_subbab=proposal_content["bab3_subbab"],
        daftar_referensi=proposal_content["daftar_referensi"],
        tabel_tinjauan_pustaka=proposal_content["tabel_tinjauan_pustaka"],
        output_path=out_path,
        template_path=tpl_path
    )

    return {
        "status": doc_result.get("status", "SUCCESS"),
        "output_filename": output_filename,
        "saved_path": out_path,
        "topic": topic,
        "variabel_x": vx,
        "variabel_y": vy,
        "total_literature_records": len(records),
        "canvas_compliance": canvas_check,
        "document_stats": doc_result
    }

@mcp.prompt()
def auto_proposal_workflow(topic: str, csv_filename: str = "") -> str:
    """
    Panduan alur orkestrasi otomatis bagi asisten AI (Antigravity):
    Meneliti literatur menggunakan paper-search MCP, mengolah CSV, dan menyusun proposal DOCX.
    """
    return f"""Anda bertindak sebagai asisten akademis ahli untuk penyusunan proposal skripsi/tesis.
Topik yang diberikan pengguna: "{topic}"
Berkas CSV literatur di workspace: "{csv_filename or 'Tidak ada (gunakan paper-search)'}"

Langkah-langkah yang harus dilakukan:
1. Panggil tool `plan_proposal_research` dengan parameter topic='{topic}' untuk mendapatkan rumusan masalah, variabel X, variabel Y, dan kueri pencarian.
2. Gunakan MCP `paper-search` (seperti `search_papers`, `search_arxiv`, atau `search_semantic`) dengan kueri yang dihasilkan untuk mencari 3-5 paper terkini yang relevan.
3. Jika terdapat berkas CSV di workspace, gunakan `parse_literature_csv_data` untuk mengekstraksi data studi literatur.
4. Panggil `generate_proposal_from_topic` dengan menyertakan topik, variabel X dan Y, berkas CSV, serta daftar paper hasil pencarian `retrieved_papers`.
5. Periksa dokumen hasil menggunakan `inspect_proposal_document` dan sampaikan ringkasan struktur proposal serta hasil audit kepada pengguna.
"""

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
