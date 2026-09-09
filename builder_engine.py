"""
builder_engine.py
Independent Academic Proposal Builder Engine
Kompatibel dengan Template Resmi FILKOM UB v3.0 dan berbagai variasi proposal akademik.
"""
import os
import json
import docx
from datetime import datetime
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from typing import Dict, Any, List, Optional

DEFAULT_TEMPLATE_PATH = "/app/assets/templates/template_filkom_ub_v3.0.docx"
# Fallback lokal jika dijalankan di luar docker
if not os.path.exists(DEFAULT_TEMPLATE_PATH):
    DEFAULT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "assets", "templates", "template_filkom_ub_v3.0.docx")

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def format_cell_header(cell, text):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(10)
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F2F2"/>')
    tcPr.append(shd)
    set_cell_margins(cell, top=120, bottom=120, left=140, right=140)

def format_cell_body(cell, text, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = align
    for r in p.runs:
        r.font.bold = bold
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

def create_generic_proposal(
    metadata: Dict[str, str],
    bab1_data: Dict[str, Any],
    bab2_subbab: List[Dict[str, Any]],
    bab3_subbab: List[Dict[str, Any]],
    daftar_referensi: List[str],
    tabel_tinjauan_pustaka: Optional[List[List[str]]] = None,
    tabel_operasionalisasi_variabel: Optional[List[List[str]]] = None,
    tabel_tahapan_metode: Optional[List[List[str]]] = None,
    tabel_jadwal: Optional[List[List[str]]] = None,
    output_path: str = "Proposal Skripsi.docx",
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Membangun dokumen DOCX proposal lengkap dan generik dengan mengadopsi format template FILKOM UB.
    """
    tpl = template_path or DEFAULT_TEMPLATE_PATH
    if not os.path.exists(tpl):
        raise FileNotFoundError(f"Template berkas tidak ditemukan di path: {tpl}")

    doc = docx.Document(tpl)

    # 1. Update Halaman Judul (Cover)
    doc.paragraphs[0].text = metadata.get("judul", "JUDUL PROPOSAL SKRIPSI").upper()
    doc.paragraphs[6].text = metadata.get("nama_mahasiswa", "Nama Mahasiswa")
    doc.paragraphs[7].text = f"NIM: {metadata.get('nim', 'NIM Mahasiswa')}"
    doc.paragraphs[18].text = metadata.get("program_studi", "PROGRAM STUDI SISTEM INFORMASI").upper()
    doc.paragraphs[19].text = metadata.get("departemen", "DEPARTEMEN SISTEM INFORMASI").upper()
    doc.paragraphs[20].text = metadata.get("fakultas", "FAKULTAS ILMU KOMPUTER").upper()
    doc.paragraphs[21].text = metadata.get("universitas", "UNIVERSITAS BRAWIJAYA").upper()
    doc.paragraphs[22].text = metadata.get("kota", "MALANG").upper()
    doc.paragraphs[23].text = str(metadata.get("tahun", datetime.now().year))

    # 2. Hapus panduan placeholder (elemen body dari index 75 sampai sebelum final sectPr)
    body = doc._body._body
    to_remove = body[75:-1]
    for elem in to_remove:
        body.remove(elem)

    def add_p(text, style='Body Text First Indent'):
        return doc.add_paragraph(text, style=style)

    def add_h1(text):
        return doc.add_paragraph(text, style='Heading 1')

    def add_h2(text):
        return doc.add_paragraph(text, style='Heading 2')

    def add_h3(text):
        return doc.add_paragraph(text, style='Heading 3')

    def add_caption(text):
        return doc.add_paragraph(text, style='Caption')

    def add_ref(text):
        return doc.add_paragraph(text, style='References')

    # =========================================================================
    # BAB 1 PENDAHULUAN
    # =========================================================================
    add_h1("PENDAHULUAN")
    
    add_h2("Latar Belakang")
    for para in bab1_data.get("latar_belakang", []):
        add_p(para)

    add_h2("Rumusan Masalah")
    add_p(bab1_data.get("rumusan_masalah_pengantar", "Berdasarkan konteks latar belakang yang telah diuraikan, rumusan masalah utama dalam penelitian ini adalah:"))
    add_p(bab1_data.get("rumusan_masalah", ""))
    if bab1_data.get("rumusan_masalah_penjelasan"):
        add_p(bab1_data.get("rumusan_masalah_penjelasan"))

    add_h2("Tujuan")
    if bab1_data.get("tujuan_umum"):
        add_p(f"Tujuan umum dari penelitian ini adalah {bab1_data.get('tujuan_umum')}")
    if bab1_data.get("tujuan_khusus"):
        add_p("Tujuan khusus dari penelitian ini dijabarkan sebagai berikut:")
        for idx, tk in enumerate(bab1_data.get("tujuan_khusus", []), 1):
            add_p(f"{idx}. {tk}")

    add_h2("Manfaat")
    add_p("Pelaksanaan penelitian ini diharapkan memberikan manfaat teoritis dan praktis:")
    for idx, mf in enumerate(bab1_data.get("manfaat", []), 1):
        add_p(f"{idx}. {mf}")

    add_h2("Batasan Masalah")
    for idx, bm in enumerate(bab1_data.get("batasan_masalah", []), 1):
        add_p(f"{idx}. {bm}")

    add_h2("Sistematika Pembahasan")
    for sp in bab1_data.get("sistematika_pembahasan", []):
        add_p(sp)

    # =========================================================================
    # BAB 2 LANDASAN KEPUSTAKAAN
    # =========================================================================
    add_h1("LANDASAN KEPUSTAKAAN")
    for section in bab2_subbab:
        lvl = section.get("level", 2)
        if lvl == 2:
            add_h2(section.get("title", ""))
        else:
            add_h3(section.get("title", ""))
        for para in section.get("paragraphs", []):
            add_p(para)

    if tabel_tinjauan_pustaka:
        add_caption("Tabel 2.1 Matriks Kajian Penelitian Terdahulu")
        t = doc.add_table(rows=len(tabel_tinjauan_pustaka), cols=len(tabel_tinjauan_pustaka[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t)
        for col_idx, h in enumerate(tabel_tinjauan_pustaka[0]):
            format_cell_header(t.cell(0, col_idx), h)
        for row_idx, row_data in enumerate(tabel_tinjauan_pustaka[1:], start=1):
            for col_idx, text in enumerate(row_data):
                align = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                format_cell_body(t.cell(row_idx, col_idx), text, align=align)

    # =========================================================================
    # BAB 3 METODOLOGI
    # =========================================================================
    add_h1("METODOLOGI")
    for section in bab3_subbab:
        lvl = section.get("level", 2)
        if lvl == 2:
            add_h2(section.get("title", ""))
        else:
            add_h3(section.get("title", ""))
        for para in section.get("paragraphs", []):
            add_p(para)

    if tabel_operasionalisasi_variabel:
        add_caption("Tabel 3.1 Operasionalisasi Konstruk dan Variabel Penelitian")
        t = doc.add_table(rows=len(tabel_operasionalisasi_variabel), cols=len(tabel_operasionalisasi_variabel[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t)
        for col_idx, h in enumerate(tabel_operasionalisasi_variabel[0]):
            format_cell_header(t.cell(0, col_idx), h)
        for row_idx, row_data in enumerate(tabel_operasionalisasi_variabel[1:], start=1):
            for col_idx, text in enumerate(row_data):
                align = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 4] else WD_ALIGN_PARAGRAPH.LEFT
                format_cell_body(t.cell(row_idx, col_idx), text, align=align)

    if tabel_tahapan_metode:
        add_caption("Tabel 3.2 Matriks Tahapan Metodologi dan Luaran Artefak")
        t = doc.add_table(rows=len(tabel_tahapan_metode), cols=len(tabel_tahapan_metode[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t)
        for col_idx, h in enumerate(tabel_tahapan_metode[0]):
            format_cell_header(t.cell(0, col_idx), h)
        for row_idx, row_data in enumerate(tabel_tahapan_metode[1:], start=1):
            for col_idx, text in enumerate(row_data):
                align = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                format_cell_body(t.cell(row_idx, col_idx), text, align=align)

    if tabel_jadwal:
        add_caption("Tabel 3.3 Rencana Jadwal Pelaksanaan Penelitian")
        t = doc.add_table(rows=len(tabel_jadwal), cols=len(tabel_jadwal[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t)
        for col_idx, h in enumerate(tabel_jadwal[0]):
            format_cell_header(t.cell(0, col_idx), h)
        for row_idx, row_data in enumerate(tabel_jadwal[1:], start=1):
            for col_idx, text in enumerate(row_data):
                align = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                format_cell_body(t.cell(row_idx, col_idx), text, align=align, bold=(col_idx > 0))

    # =========================================================================
    # DAFTAR REFERENSI
    # =========================================================================
    doc.add_paragraph("DAFTAR REFERENSI", style='Reference Heading')
    for r in daftar_referensi:
        add_ref(r)

    # Aktifkan updateFields otomatis pada Word settings
    update_fields = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    doc.settings.element.append(update_fields)

    doc.save(output_path)
    return {
        "status": "SUCCESS",
        "output_path": output_path,
        "judul": metadata.get("judul"),
        "penulis": metadata.get("nama_mahasiswa"),
        "file_size_bytes": os.path.getsize(output_path)
    }

def inspect_doc(docx_path: str) -> Dict[str, Any]:
    if not os.path.exists(docx_path):
        return {"error": f"File {docx_path} tidak ditemukan."}
    
    doc = docx.Document(docx_path)
    headings = []
    total_words = 0
    for p in doc.paragraphs:
        total_words += len(p.text.split())
        if p.style.name.startswith("Heading") or p.style.name == "Reference Heading":
            headings.append({"style": p.style.name, "text": p.text.strip()})
            
    return {
        "file": os.path.basename(docx_path),
        "total_paragraphs": len(doc.paragraphs),
        "total_tables": len(doc.tables),
        "total_sections": len(doc.sections),
        "approx_words": total_words,
        "headings": headings
    }

def record_version_change(workspace_dir: str, from_version: str, to_version: str, notes: str) -> str:
    log_file = os.path.join(workspace_dir, "version_history.json")
    history = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.append({
        "timestamp": datetime.now().isoformat(),
        "from_version": from_version,
        "to_version": to_version,
        "notes": notes
    })
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        
    return f"Versi {to_version} berhasil dicatat di version_history.json."
