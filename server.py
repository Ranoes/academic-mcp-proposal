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
from praproposal_builder import (
    build_praproposal_odt,
    DEFAULT_PRA_TEMPLATE_PATH
)
from csv_ingestor import parse_literature_csv
from topic_synthesizer import (
    plan_research,
    synthesize_proposal_from_inputs,
    synthesize_praproposal_from_inputs,
    check_missing_student_metadata
)



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
    record_status = record_version_change(
        workspace_dir=WORKSPACE_DIR,
        from_version=current_version,
        to_version=new_version,
        notes=changelog,
        doc_type="proposal",
        filename=os.path.basename(dst_file)
    )

    return {
        "status": "SUCCESS",
        "created_file": os.path.basename(dst_file),
        "source_file": os.path.basename(src_file),
        "document_type": "proposal",
        "changelog": changelog,
        "log_status": record_status
    }

@mcp.tool()
def increment_praproposal_version(
    current_version: str,
    new_version: str,
    changelog: str,
    filename_prefix: str = "Praproposal Skripsi"
) -> dict:
    """
    Menduplikasi versi aktif pra-proposal skripsi (.odt) ke versi baru dan mencatat riwayat perubahan ke version_history.json.
    Contoh: current_version='v1.0', new_version='v1.1', changelog='Penyesuaian rumusan masalah tunggal dan metode riset'
    """
    c_ver = current_version if current_version.startswith("v") else f"v{current_version}"
    n_ver = new_version if new_version.startswith("v") else f"v{new_version}"

    # Cari file sumber baik format 'Praproposal Skripsi v1.0.odt' maupun nama kustom
    src_file = os.path.join(WORKSPACE_DIR, f"{filename_prefix} {c_ver}.odt")
    dst_file = os.path.join(WORKSPACE_DIR, f"{filename_prefix} {n_ver}.odt")

    if not os.path.exists(src_file):
        # Fallback jika nama file hanya 'Praproposal_Skripsi_v1.0.odt'
        alt_src = os.path.join(WORKSPACE_DIR, f"{filename_prefix}_{c_ver}.odt")
        if os.path.exists(alt_src):
            src_file = alt_src
            dst_file = os.path.join(WORKSPACE_DIR, f"{filename_prefix}_{n_ver}.odt")
        else:
            return {
                "status": "ERROR",
                "message": f"Berkas sumber pra-proposal {src_file} tidak ditemukan di workspace."
            }

    shutil.copy2(src_file, dst_file)
    record_status = record_version_change(
        workspace_dir=WORKSPACE_DIR,
        from_version=c_ver,
        to_version=n_ver,
        notes=changelog,
        doc_type="praproposal",
        filename=os.path.basename(dst_file)
    )

    return {
        "status": "SUCCESS",
        "created_file": os.path.basename(dst_file),
        "source_file": os.path.basename(src_file),
        "document_type": "praproposal",
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

    meta_check = check_missing_student_metadata(student_metadata, is_praproposal=False)

    return {
        "status": doc_result.get("status", "SUCCESS"),
        "output_filename": output_filename,
        "saved_path": out_path,
        "topic": topic,
        "variabel_x": vx,
        "variabel_y": vy,
        "total_literature_records": len(records),
        "canvas_compliance": canvas_check,
        "student_metadata_status": meta_check,
        "document_stats": doc_result
    }

@mcp.tool()
def generate_academic_praproposal(
    metadata: Dict[str, Any],
    sections: Dict[str, Any],
    output_filename: str = "Praproposal Skripsi v1.0.odt",
    custom_template_filename: Optional[str] = None
) -> dict:
    """
    Membuat berkas Dokumen Pra-Proposal Skripsi (.odt) berbasis template resmi SA2-01A.
    Menerima metadata mahasiswa dan struktur konten (latar_belakang, landasan_kepustakaan,
    rumusan_masalah, metode, daftar_pustaka).
    """
    out_path = os.path.join(WORKSPACE_DIR, output_filename)
    tpl_path = None
    if custom_template_filename:
        custom_p = os.path.join(WORKSPACE_DIR, custom_template_filename)
        if os.path.exists(custom_p):
            tpl_path = custom_p

    try:
        res_path = build_praproposal_odt(
            metadata=metadata,
            sections=sections,
            output_path=out_path,
            template_path=tpl_path
        )
        record_version_change(
            workspace_dir=WORKSPACE_DIR,
            from_version="init",
            to_version="v1.0",
            notes="Pembuatan awal dokumen pra-proposal skripsi (SA2-01A)",
            doc_type="praproposal",
            filename=output_filename
        )
        return {
            "status": "SUCCESS",
            "output_filename": output_filename,
            "saved_path": res_path,
            "message": f"Dokumen pra-proposal berhasil dibuat di {output_filename}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Gagal membuat dokumen pra-proposal: {str(e)}"
        }

@mcp.tool()
def generate_praproposal_from_topic(
    topic: str,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None,
    student_metadata: Optional[Dict[str, str]] = None,
    csv_filename: Optional[str] = None,
    csv_content: Optional[str] = None,
    retrieved_papers: Optional[List[Dict[str, Any]]] = None,
    latar_belakang_notes: Optional[List[str]] = None,
    metode_penelitian_notes: Optional[List[str]] = None,
    output_filename: str = "Praproposal Skripsi v1.0.odt",
    custom_template_filename: Optional[str] = None
) -> dict:
    """
    Menghasilkan dokumen pra-proposal skripsi (.odt) SA2-01A secara otomatis dari topik penelitian,
    data CSV literatur di workspace, dan/atau data paper yang diperoleh dari MCP paper-search.
    Menyusun Latar Belakang (<= 500 kata), Landasan Kepustakaan (<= 250 kata),
    Rumusan Masalah (numbering), Metode (<= 250 kata), dan Daftar Pustaka.
    """
    # 1. Turunkan atau validasi X dan Y
    plan = plan_research(topic=topic, variabel_x=variabel_x, variabel_y=variabel_y)
    vx = plan["variabel_x"]
    vy = plan["variabel_y"]

    # 2. Metadata default
    meta = {
        "judul": topic.upper(),
        "nama_mahasiswa": "Mahasiswa Peneliti",
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
    }
    if student_metadata:
        meta.update(student_metadata)

    # 3. Proses literatur dari CSV jika ada
    records = []
    references = []

    if csv_filename or csv_content:
        csv_file_path = os.path.join(WORKSPACE_DIR, csv_filename) if csv_filename else None
        csv_res = parse_literature_csv(file_path=csv_file_path, csv_content=csv_content)
        if csv_res.get("status") == "SUCCESS":
            records.extend(csv_res.get("records", []))
            references.extend(csv_res.get("references", []))

    # 4. Tambahkan data dari retrieved_papers (hasil paper-search MCP)
    if retrieved_papers:
        for p in retrieved_papers:
            title = p.get("title", "Paper Referensi")
            authors = p.get("authors") or p.get("author") or "Peneliti Terkait"
            if isinstance(authors, list):
                authors = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
            year = str(p.get("year") or p.get("published") or "2024")[:4]
            method = p.get("method") or p.get("snippet") or "-"
            results = p.get("results") or p.get("abstract") or "-"
            gap = p.get("gap") or "Perlu optimasi kinerja pada skala data nyata"

            records.append({
                "author": str(authors),
                "year": year,
                "title": title,
                "method": str(method)[:150],
                "results": str(results)[:200],
                "gap": gap
            })

            ref_str = f"{authors}, {year}. {title}."
            if p.get("doi"):
                ref_str += f" DOI: {p.get('doi')}."
            elif p.get("url"):
                ref_str += f" Tersedia di: {p.get('url')}."
            references.append(ref_str)

    # 5. Sintesis konten pra-proposal
    pra_payload = synthesize_praproposal_from_inputs(
        topic=topic,
        metadata=meta,
        variabel_x=vx,
        variabel_y=vy,
        literature_records=records,
        references=references,
        latar_belakang_notes=latar_belakang_notes,
        metode_notes=metode_penelitian_notes
    )

    # 6. Validasi Research Canvas
    rm_str = "\n".join(pra_payload["sections"]["rumusan_masalah"])
    canvas_check = check_research_canvas(
        rumusan_masalah=rm_str,
        variabel_independen=vx,
        variabel_dependen=vy,
        tujuan_penelitian=plan["tujuan_umum"],
        manfaat_penelitian="Membantu pengambil keputusan dalam optimasi kinerja sistem",
        single_problem_only=True
    )

    # 7. Generate berkas ODT
    out_path = os.path.join(WORKSPACE_DIR, output_filename)
    tpl_path = None
    if custom_template_filename:
        custom_p = os.path.join(WORKSPACE_DIR, custom_template_filename)
        if os.path.exists(custom_p):
            tpl_path = custom_p

    res_path = build_praproposal_odt(
        metadata=pra_payload["metadata"],
        sections=pra_payload["sections"],
        output_path=out_path,
        template_path=tpl_path
    )

    # Catat riwayat versi
    record_version_change(
        workspace_dir=WORKSPACE_DIR,
        from_version="init",
        to_version="v1.0",
        notes=f"Pembuatan awal naskah pra-proposal untuk topik '{topic}'",
        doc_type="praproposal",
        filename=output_filename
    )

    meta_check = check_missing_student_metadata(student_metadata, is_praproposal=True)

    return {
        "status": "SUCCESS",
        "output_filename": output_filename,
        "saved_path": res_path,
        "topic": topic,
        "variabel_x": vx,
        "variabel_y": vy,
        "total_literature_records": len(records),
        "canvas_compliance": canvas_check,
        "student_metadata_status": meta_check,
        "praproposal_data": pra_payload
    }

@mcp.prompt()
def auto_praproposal_workflow(topic: str, csv_filename: str = "") -> str:
    """
    Panduan alur orkestrasi pembuatan pra-proposal skripsi (Form SA2-01A .odt) bagi asisten AI:
    Mewajibkan konfirmasi data diri mahasiswa/dosen, meneliti literatur, dan menghasilkan naskah pra-proposal.
    """
    return f"""Anda bertindak sebagai asisten akademis ahli untuk penyusunan Dokumen Pra-Proposal Skripsi (Form SA2-01A).
Topik yang diajukan pengguna: "{topic}"
Berkas CSV literatur di workspace: "{csv_filename or 'Tidak ada (gunakan paper-search jika diperlukan)'}"

Langkah-langkah WAJIB yang harus dilakukan oleh agen:
1. WAJIB KONFIRMASI DATA DIRI MAHASISWA & PEMBIMBING:
   Agen WAJIB menanyakan dan mengonfirmasikan ulang data diri pengguna secara eksplisit:
   - Nama Lengkap Mahasiswa
   - NIM
   - Jurusan / Departemen (contoh: Teknik Informatika)
   - Program Studi (contoh: Teknik Informatika / Sistem Informasi / Teknik Komputer)
   - Keminatan & Bidang Skripsi (contoh: Komputasi Cerdas / Artificial Intelligence)
   - Nama Dosen Pembimbing beserta gelar (contoh: Dr. Eng. Herman Tolle, S.T., M.T.)
   - NIP Dosen Pembimbing
   - Lokasi / Kota Pengesahan (default: Malang)
   - Jenis Penelitian (Implementatif / Non-implementatif)
   - Asal Judul (Usulan Sendiri / Usulan Pembimbing)
   Jika data di atas belum diberikan atau belum lengkap, AJUKAN PERTANYAAN LANGSUNG KEPADA PENGGUNA sebelum atau setelah membuat dokumen.

2. Panggil tool `plan_proposal_research` dengan parameter topic='{topic}' untuk menurunkan rumusan masalah tunggal, variabel X, variabel Y, dan kata kunci pencarian literatur.
3. Jika dibutuhkan bukti empiris/sitasi tambahan, gunakan MCP `paper-search` (seperti `search_papers`, `search_arxiv`, atau `search_semantic`).
4. Panggil tool `generate_praproposal_from_topic` dengan menyertakan student_metadata yang telah dikonfirmasi.
5. WAJIB TAMPILKAN CHECKLIST KONFIRMASI: Sajikan tabel ringkasan data diri yang tercantum di dokumen (.odt) kepada pengguna untuk verifikasi final.
"""

@mcp.prompt()
def auto_proposal_workflow(topic: str, csv_filename: str = "") -> str:
    """
    Panduan alur orkestrasi otomatis bagi asisten AI (Antigravity):
    Mewajibkan konfirmasi data diri mahasiswa/dosen, meneliti literatur via paper-search MCP, mengolah CSV, dan menyusun proposal DOCX.
    """
    return f"""Anda bertindak sebagai asisten akademis ahli untuk penyusunan proposal skripsi/tesis (3 Bab).
Topik yang diberikan pengguna: "{topic}"
Berkas CSV literatur di workspace: "{csv_filename or 'Tidak ada (gunakan paper-search)'}"

Langkah-langkah WAJIB yang harus dilakukan oleh agen:
1. WAJIB KONFIRMASI DATA DIRI MAHASISWA & PEMBIMBING:
   Agen WAJIB menanyakan dan mengonfirmasikan ulang data diri pengguna secara eksplisit:
   - Nama Lengkap Mahasiswa
   - NIM
   - Departemen / Jurusan
   - Program Studi
   - Fakultas & Universitas
   - Nama Dosen Pembimbing beserta gelar
   - NIP Dosen Pembimbing
   - Lokasi / Kota Pengesahan & Tahun
   Jika data di atas belum diberikan atau belum lengkap, AJUKAN PERTANYAAN LANGSUNG KEPADA PENGGUNA.

2. Panggil tool `plan_proposal_research` dengan parameter topic='{topic}' untuk mendapatkan rumusan masalah tunggal, variabel X, variabel Y, dan kueri pencarian.
3. Gunakan MCP `paper-search` (seperti `search_papers`, `search_arxiv`, atau `search_semantic`) dengan kueri yang dihasilkan untuk mencari 3-5 paper terkini yang relevan.
4. Jika terdapat berkas CSV di workspace, gunakan `parse_literature_csv_data` untuk mengekstraksi data studi literatur.
5. Panggil `generate_proposal_from_topic` dengan menyertakan topik, variabel X dan Y, berkas CSV, daftar paper hasil pencarian `retrieved_papers`, serta `student_metadata` yang telah dikonfirmasi.
6. Periksa dokumen hasil menggunakan `inspect_proposal_document` dan sampaikan ringkasan struktur proposal, hasil audit kepatuhan Research Canvas, serta konfirmasi data identitas mahasiswa kepada pengguna.
"""

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
