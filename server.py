"""
server.py
Independent Academic Proposal MCP Server
Kompatibel dengan Model Context Protocol (MCP) untuk otomatisasi penyusunan dan validasi proposal skripsi.
"""
import os
import shutil
import subprocess
from typing import Dict, Any, List, Optional, Union
try:
    from mcp.server import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except ImportError:
        class FastMCP:  # type: ignore
            def __init__(self, name: str = "academic-proposal-mcp"):
                self.name = name
            def tool(self, **kwargs):
                def decorator(fn):
                    return fn
                return decorator
            def prompt(self, **kwargs):
                def decorator(fn):
                    return fn
                return decorator
            def run(self, transport="stdio"):
                pass
from canvas_validator import (
    check_research_canvas,
    check_praproposal_canvas,
    get_canvas_rubric,
    generate_markdown_checklist_report,
    generate_praproposal_rubric_checklist_report
)
from builder_engine import (
    create_generic_proposal,
    insert_diagram_to_docx,
    insert_formula_to_docx,
    inspect_doc,
    record_version_change,
    DEFAULT_TEMPLATE_PATH
)
from diagram_generator import (
    generate_diagram,
    ensure_asset_dir
)
from formula_generator import (
    generate_math_formula
)
from praproposal_builder import (
    build_praproposal_odt,
    extract_praproposal_from_odt,
    inspect_praproposal_odt,
    DEFAULT_PRA_TEMPLATE_PATH
)
from csv_ingestor import parse_literature_csv
from topic_synthesizer import (
    plan_research,
    generate_topic_from_artefact as synth_topic_from_artefact,
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
def validate_praproposal_compliance(
    metadata: Optional[Dict[str, Any]] = None,
    sections: Optional[Dict[str, Any]] = None,
    odt_filename: Optional[str] = None,
    variabel_independen: Optional[str] = None,
    variabel_dependen: Optional[str] = None,
    single_problem_only: bool = True
) -> dict:
    """
    Memvalidasi kepatuhan naskah pra-proposal skripsi (Form SA2-01A) terhadap kaidah
    Research Design Canvas dan batasan alokasi kata resmi:
    - Latar Belakang / Deskripsi Masalah: maksimal 500 kata
    - Landasan Kepustakaan: maksimal 250 kata
    - Rencana Metode Penelitian: maksimal 250 kata
    - Rumusan Masalah: tepat 1 pertanyaan terukur (CLB04-01 & CLB04-02)
    - Variabel X & Y terdefinisi eksplisit
    Dapat menerima payload data (metadata & sections) atau nama berkas .odt yang ada di workspace.
    """
    target_meta = dict(metadata or {})
    target_sections = dict(sections or {})

    if odt_filename:
        odt_path = os.path.join(WORKSPACE_DIR, odt_filename)
        if not os.path.exists(odt_path):
            return {
                "status": "ERROR",
                "message": f"Berkas pra-proposal {odt_filename} tidak ditemukan di workspace."
            }
        try:
            extracted = extract_praproposal_from_odt(odt_path)
            if not target_meta:
                target_meta = extracted["metadata"]
            if not target_sections:
                target_sections = extracted["sections"]
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Gagal membaca berkas pra-proposal ODT: {str(e)}"
            }

    if not target_meta and not target_sections:
        return {
            "status": "ERROR",
            "message": "Harap sertakan parameter metadata & sections atau odt_filename yang valid untuk divalidasi."
        }

    return check_praproposal_canvas(
        metadata=target_meta,
        sections=target_sections,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        single_problem_only=single_problem_only
    )

@mcp.tool()
def generate_praproposal_rubric_report(
    proposal_title: Optional[str] = None,
    student_name: Optional[str] = None,
    student_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    sections: Optional[Dict[str, Any]] = None,
    odt_filename: Optional[str] = None,
    variabel_independen: Optional[str] = None,
    variabel_dependen: Optional[str] = None,
    output_markdown_filename: str = "praproposal_rubric_checklist_report.md",
    save_to_workspace: bool = True
) -> dict:
    """
    Menghasilkan laporan audit kepatuhan Pra-Proposal (SA2-01A) dalam format Markdown
    berdasarkan rubrik evaluasi resmi dan batasan alokasi kata.
    """
    target_meta = dict(metadata or {})
    target_sections = dict(sections or {})

    if odt_filename:
        odt_path = os.path.join(WORKSPACE_DIR, odt_filename)
        if os.path.exists(odt_path):
            try:
                extracted = extract_praproposal_from_odt(odt_path)
                if not target_meta:
                    target_meta = extracted["metadata"]
                if not target_sections:
                    target_sections = extracted["sections"]
            except Exception:
                pass

    if proposal_title:
        target_meta["judul"] = proposal_title
    if student_name:
        target_meta["nama_mahasiswa"] = student_name
    if student_id:
        target_meta["nim"] = student_id

    md_report = generate_praproposal_rubric_checklist_report(
        metadata=target_meta,
        sections=target_sections,
        variabel_independen=variabel_independen,
        variabel_dependen=variabel_dependen,
        single_problem_only=True
    )

    saved_path = None
    if save_to_workspace:
        saved_path = os.path.join(WORKSPACE_DIR, output_markdown_filename)
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(md_report)

    return {
        "status": "SUCCESS",
        "output_filename": output_markdown_filename,
        "saved_path": saved_path,
        "report_markdown": md_report
    }

@mcp.tool()
def get_canvas_guidelines() -> dict:
    """
    Mengambil rubrik lengkap checklist Research Design Model Canvas v2.0 (LB01-LB06, LR01-LR06, M01-M05, PRA_Praproposal_SA2_01A)
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
def generate_diagram_image(
    diagram_type: str = "flowchart",
    title: str = "Diagram Alur Penelitian",
    steps_or_nodes: Optional[List[Union[str, Dict[str, Any]]]] = None,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None,
    layers: Optional[List[Dict[str, Any]]] = None,
    asset_folder: str = "asset",
    output_filename: Optional[str] = None,
    caption: Optional[str] = None,
    target_document_docx: Optional[str] = None,
    chapter_num: int = 3,
    figure_num: int = 1,
    width_inches: float = 5.5
) -> dict:
    """
    Menghasilkan gambar diagram ilmiah (Flowchart Alur Penelitian / Hubungan Variabel X & Y / Arsitektur Sistem),
    memastikan direktori /asset dibuat di workspace, dan menyimpan file gambar PNG beresolusi tinggi (300 DPI).
    Jika target_document_docx ditentukan, diagram otomatis langsung disisipkan ke dalam dokumen proposal .docx.
    """
    try:
        diag_res = generate_diagram(
            diagram_type=diagram_type,
            title=title,
            steps_or_nodes=steps_or_nodes,
            variabel_x=variabel_x,
            variabel_y=variabel_y,
            layers=layers,
            workspace_dir=WORKSPACE_DIR,
            asset_folder=asset_folder,
            output_filename=output_filename
        )

        inserted_doc_info = None
        if target_document_docx:
            doc_path = os.path.join(WORKSPACE_DIR, target_document_docx)
            cap_title = caption or title
            inserted_doc_info = insert_diagram_to_docx(
                docx_path=doc_path,
                image_path=diag_res["full_path"],
                caption_title=cap_title,
                chapter_num=chapter_num,
                figure_num=figure_num,
                width_inches=width_inches
            )

        return {
            "status": "SUCCESS",
            "diagram_info": diag_res,
            "image_path": diag_res["relative_path"],
            "full_path": diag_res["full_path"],
            "inserted_into_document": inserted_doc_info,
            "message": f"Diagram '{title}' berhasil dibuat dan disimpan di {diag_res['relative_path']}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Gagal menghasilkan diagram: {str(e)}"
        }

@mcp.tool()
def insert_diagram_to_document(
    document_filename: str,
    image_filename_or_path: str,
    caption_title: str = "Diagram Penelitian",
    chapter_num: int = 3,
    figure_num: int = 1,
    width_inches: float = 5.5
) -> dict:
    """
    Menyisipkan berkas gambar diagram dari folder /asset ke dalam naskah proposal (.docx) di workspace
    disertai penomoran caption resmi (format: Gambar X.Y <Judul>).
    """
    if os.path.isabs(image_filename_or_path):
        img_path = image_filename_or_path
    else:
        direct_p = os.path.join(WORKSPACE_DIR, image_filename_or_path)
        asset_p = os.path.join(WORKSPACE_DIR, "asset", image_filename_or_path)
        if os.path.exists(direct_p):
            img_path = direct_p
        elif os.path.exists(asset_p):
            img_path = asset_p
        else:
            img_path = direct_p

    doc_path = os.path.join(WORKSPACE_DIR, document_filename)
    return insert_diagram_to_docx(
        docx_path=doc_path,
        image_path=img_path,
        caption_title=caption_title,
        chapter_num=chapter_num,
        figure_num=figure_num,
        width_inches=width_inches
    )

@mcp.tool()
def generate_math_formula_image(
    latex_code: str,
    formula_title: str = "Persamaan Matematika",
    chapter_num: int = 3,
    formula_num: int = 1,
    variable_definitions: Optional[Dict[str, str]] = None,
    asset_folder: str = "asset",
    output_filename: Optional[str] = None,
    target_document_docx: Optional[str] = None,
    intro_text: Optional[str] = None,
    use_native_equation: bool = True
) -> dict:
    """
    Merender rumus matematika (notasi LaTeX) menjadi Objek Persamaan Native Word (OMML / <m:oMath>)
    yang dapat diedit langsung di dokumen DOCX, dan/atau citra PNG beresolusi tinggi (300 DPI) di folder /asset.
    Mendukung format penomoran resmi persamaan akademis (X.Y), keterangan simbol variabel 'di mana:',
    serta opsi penyisipan otomatis langsung ke naskah proposal (.docx).
    Contoh latex_code: "f(x) = \\sigma(W^T x + b)", "MAE = \\frac{1}{n} \\sum_{i=1}^{n} |y_i - \\hat{y}_i|".
    """
    try:
        res = generate_math_formula(
            latex_code=latex_code,
            formula_title=formula_title,
            chapter_num=chapter_num,
            formula_num=formula_num,
            variable_definitions=variable_definitions,
            workspace_dir=WORKSPACE_DIR,
            asset_folder=asset_folder,
            output_filename=output_filename,
            target_document_docx=target_document_docx,
            intro_text=intro_text,
            use_native_equation=use_native_equation
        )
        return res
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Gagal menghasilkan rumus matematika: {str(e)}"
        }

@mcp.tool()
def insert_math_formula_to_document(
    document_filename: str,
    latex_code: Optional[str] = None,
    image_filename_or_path: Optional[str] = None,
    chapter_num: int = 3,
    formula_num: int = 1,
    intro_text: Optional[str] = None,
    variable_definitions: Optional[Dict[str, str]] = None,
    use_native_equation: bool = True,
    image_width_inches: float = 4.0
) -> dict:
    """
    Menyisipkan rumus matematika ke dalam naskah proposal (.docx) di workspace
    secara default sebagai Objek Persamaan Native Word (<m:oMath>) yang dapat diedit,
    dengan format tabel 1x2 borderless resmi: Rumus di tengah (Center), Nomor Persamaan (X.Y) rata kanan (Right),
    serta keterangan simbol variabel 'di mana:' di bawah persamaan.
    """
    img_path = None
    if image_filename_or_path:
        if os.path.isabs(image_filename_or_path):
            img_path = image_filename_or_path
        else:
            direct_p = os.path.join(WORKSPACE_DIR, image_filename_or_path)
            asset_p = os.path.join(WORKSPACE_DIR, "asset", image_filename_or_path)
            if os.path.exists(direct_p):
                img_path = direct_p
            elif os.path.exists(asset_p):
                img_path = asset_p
            else:
                img_path = direct_p

    doc_path = os.path.join(WORKSPACE_DIR, document_filename)
    return insert_formula_to_docx(
        docx_path=doc_path,
        latex_code=latex_code,
        image_path=img_path,
        chapter_num=chapter_num,
        formula_num=formula_num,
        intro_text=intro_text,
        variable_definitions=variable_definitions,
        use_native_equation=use_native_equation,
        image_width_inches=image_width_inches
    )

@mcp.tool()
def inspect_proposal_document(filename: str = "Proposal Skripsi v1.0.docx") -> dict:
    """
    Memeriksa struktur dokumen proposal (.docx) atau pra-proposal (.odt) di dalam workspace.
    Mengembalikan informasi: jumlah paragraf, tabel, kata, alokasi budget kata, dan kelengkapan struktur.
    """
    file_path = os.path.join(WORKSPACE_DIR, filename)
    if filename.lower().endswith(".odt"):
        return inspect_praproposal_odt(file_path)
    return inspect_doc(file_path)

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
def generate_topic_from_artefact(
    artefact_content: str,
    artefact_type: str = "general_text",
    artefact_title: Optional[str] = None,
    bidang_kajian: Optional[str] = None,
    proposed_method_or_x: Optional[str] = None,
    target_metric_or_y: Optional[str] = None,
    institutional_focus: Optional[str] = None
) -> dict:
    """
    Menghasilkan usulan topik penelitian ilmiah komprehensif berbasis artefak dunia nyata
    (artikel berita, rekaman kasus, dokumen masalah, transkrip OCR / deskripsi citra, cerita lapangan, dsb.).
    Secara otomatis menghasilkan:
    1. Judul Formal Akademik (Bahasa Indonesia & English).
    2. Urgensi Penelitian (Latar Belakang Fenomena, Urgensi Teknis/Teoretis, Dampak Risiko).
    3. Rumusan Masalah Tunggal Terukur (Sesuai kaidah Research Design Canvas).
    4. Variabel Independen (X) dan Variabel Dependen (Y).
    5. Tujuan Penelitian (Umum & Khusus 4 Tahap).
    6. Manfaat Penelitian (Praktis & Akademis, bebas dari klausul klise).
    7. Batasan Masalah & Kueri Pencarian Literatur untuk paper-search MCP.
    8. Hasil Audit Kepatuhan Langsung terhadap Research Design Canvas (v2.0).
    """
    return synth_topic_from_artefact(
        artefact_content=artefact_content,
        artefact_type=artefact_type,
        artefact_title=artefact_title,
        bidang_kajian=bidang_kajian,
        proposed_method_or_x=proposed_method_or_x,
        target_metric_or_y=target_metric_or_y,
        institutional_focus=institutional_focus
    )

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

def _normalize_retrieved_papers(retrieved_papers: Any) -> List[Dict[str, Any]]:
    """
    Menstandardisasi daftar paper dari MCP paper-search (baik dari search_papers,
    search_arxiv, search_semantic, search_crossref, dsb.) menjadi format terstruktur
    yang siap disintesis ke dalam tabel tinjauan pustaka dan daftar pustaka.
    """
    if not retrieved_papers:
        return []
    
    # Tangani jika caller mem-passing seluruh objek dict response dari search_papers
    if isinstance(retrieved_papers, dict):
        if "papers" in retrieved_papers and isinstance(retrieved_papers["papers"], list):
            retrieved_papers = retrieved_papers["papers"]
        elif "results" in retrieved_papers and isinstance(retrieved_papers["results"], list):
            retrieved_papers = retrieved_papers["results"]
        else:
            retrieved_papers = [retrieved_papers]
    elif not isinstance(retrieved_papers, list):
        return []

    normalized = []
    for p in retrieved_papers:
        if not isinstance(p, dict):
            continue
        title = p.get("title") or "Paper Referensi"
        
        # 1. Format penulis akademis (mendukung nama string dengan pemisah titik koma / list)
        authors = p.get("authors") or p.get("author") or "Peneliti Terkait"
        if isinstance(authors, str) and ";" in authors:
            author_list = [a.strip() for a in authors.split(";") if a.strip()]
            if len(author_list) > 2:
                authors = f"{author_list[0]} et al."
            elif len(author_list) == 2:
                authors = f"{author_list[0]} & {author_list[1]}"
            elif author_list:
                authors = author_list[0]
        elif isinstance(authors, list):
            if len(authors) > 2:
                authors = f"{authors[0]} et al."
            elif len(authors) == 2:
                authors = f"{authors[0]} & {authors[1]}"
            elif authors:
                authors = str(authors[0])
        
        # 2. Ekstrak tahun publikasi (mendukung published_date, published, year)
        raw_year = p.get("year") or p.get("published_date") or p.get("published") or ""
        year = str(raw_year)[:4] if raw_year else "2024"
        
        # 3. Metode dan Temuan
        categories = p.get("categories") or ""
        method = p.get("method") or p.get("snippet") or (f"Kategori/Bidang: {categories}" if categories else "-")
        
        results = p.get("results") or p.get("abstract") or "-"
        if results != "-" and len(results) > 250:
            first_sentence = results.split(". ")[0]
            if len(first_sentence) > 30 and len(first_sentence) < 250:
                results = first_sentence + "."
            else:
                results = results[:247] + "..."
        
        gap = p.get("gap") or "Perlu evaluasi komprehensif pada skala data produksi dan variasi parameter pengujian"
        doi = p.get("doi") or ""
        url = p.get("url") or p.get("pdf_url") or ""
        
        normalized.append({
            "title": title,
            "authors": str(authors),
            "year": year,
            "method": str(method)[:150],
            "results": str(results)[:200],
            "gap": gap,
            "doi": doi,
            "url": url
        })
    return normalized

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
        clean_papers = _normalize_retrieved_papers(retrieved_papers)
        if clean_papers:
            if not table_matrix:
                table_matrix = [["No", "Peneliti & Tahun", "Judul Penelitian", "Metode / Algoritma", "Hasil & Temuan", "Research Gap"]]
            
            current_no = len(table_matrix)
            for p in clean_papers:
                title = p["title"]
                authors = p["authors"]
                year = p["year"]
                method = p["method"]
                results = p["results"]
                gap = p["gap"]

                records.append({
                    "no": current_no,
                    "author": authors,
                    "year": year,
                    "title": title,
                    "method": method,
                    "results": results,
                    "gap": gap
                })

                table_matrix.append([
                    str(current_no),
                    f"{authors} ({year})",
                    title,
                    method[:120],
                    results[:150],
                    gap[:120]
                ])

                ref_str = f"{authors}, {year}. {title}."
                if p.get("doi"):
                    ref_str += f" DOI: {p['doi']}."
                elif p.get("url"):
                    ref_str += f" Tersedia di: {p['url']}."
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

    # 7. Render diagram alur penelitian ke /asset dan siapkan untuk dokumen DOCX
    diag_images = []
    try:
        diag_res = generate_diagram(
            diagram_type="flowchart",
            title="Diagram Alur Pelaksanaan Penelitian",
            steps_or_nodes=[
                f"Tahap 1: Identifikasi Permasalahan {vy}",
                f"Tahap 2: Studi Literatur & Benchmark Terkait {vx}",
                f"Tahap 3: Perancangan Model Arsitektur {vx}",
                f"Tahap 4: Implementasi & Pengujian Eksperimental",
                f"Tahap 5: Evaluasi Metrik Kuantitatif & Kesimpulan"
            ],
            workspace_dir=WORKSPACE_DIR,
            asset_folder="asset",
            output_filename="diagram_alur_penelitian.png"
        )
        diag_images.append({
            "image_path": diag_res["full_path"],
            "title": "Diagram Alur Pelaksanaan Penelitian",
            "chapter_num": 3,
            "figure_num": 1,
            "width_inches": 5.5
        })
    except Exception:
        diag_images = None

    # 8. Generate berkas Word DOCX
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
        diagram_images=diag_images,
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
        # Validasi Kepatuhan Canvas & Alokasi Kata SA2-01A
        canvas_check = check_praproposal_canvas(
            metadata=metadata,
            sections=sections,
            single_problem_only=True
        )

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
            "canvas_compliance": canvas_check,
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
        clean_papers = _normalize_retrieved_papers(retrieved_papers)
        for p in clean_papers:
            title = p["title"]
            authors = p["authors"]
            year = p["year"]
            method = p["method"]
            results = p["results"]
            gap = p["gap"]

            records.append({
                "author": authors,
                "year": year,
                "title": title,
                "method": method,
                "results": results,
                "gap": gap
            })

            ref_str = f"{authors}, {year}. {title}."
            if p.get("doi"):
                ref_str += f" DOI: {p['doi']}."
            elif p.get("url"):
                ref_str += f" Tersedia di: {p['url']}."
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

    # 6. Validasi Research Canvas Khusus Pra-Proposal SA2-01A
    canvas_check = check_praproposal_canvas(
        metadata=pra_payload["metadata"],
        sections=pra_payload["sections"],
        variabel_independen=vx,
        variabel_dependen=vy,
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
