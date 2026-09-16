"""
formula_generator.py
Modul untuk merender rumus matematika (LaTeX math) menjadi gambar beresolusi tinggi,
menyimpannya ke direktori /asset, serta menyisipkannya ke dalam dokumen proposal akademik
lengkap dengan nomor persamaan resmi (X.Y) dan keterangan variabel.
"""
import os
import re
from typing import Dict, Any, List, Optional, Union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import docx

DEFAULT_ASSET_DIR = "asset"

def ensure_asset_dir(workspace_dir: str, asset_folder: str = DEFAULT_ASSET_DIR) -> str:
    """Memastikan folder asset dibuat di dalam workspace."""
    target_path = os.path.join(workspace_dir, asset_folder)
    os.makedirs(target_path, exist_ok=True)
    return target_path

def clean_latex_string(latex_code: str) -> str:
    """
    Membersihkan dan menormalisasi string LaTeX untuk dirender oleh matplotlib.mathtext.
    """
    s = latex_code.strip()
    # Hapus delimiter $$ atau $ di awal/akhir jika ada
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()

    # Pastikan dibungkus tanda dolar tunggal untuk matplotlib mathtext parser
    return f"${s}$"

def render_latex_formula_image(
    latex_code: str,
    output_path: str,
    fontsize: int = 14,
    dpi: int = 300,
    text_color: str = "#0F172A"
) -> str:
    """
    Merender rumus matematika LaTeX menjadi gambar PNG transparan beresolusi tinggi (300 DPI).
    """
    formatted_latex = clean_latex_string(latex_code)

    fig = plt.figure(figsize=(7.0, 1.2), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_alpha(0.0)

    try:
        ax.text(
            0.5, 0.5, formatted_latex,
            fontsize=fontsize, ha='center', va='center',
            color=text_color
        )
    except Exception as e:
        # Fallback jika ada ekspresi TeX yang tidak didukung mathtext
        plain_text = latex_code.replace("$", "").strip()
        ax.text(
            0.5, 0.5, plain_text,
            fontsize=fontsize - 2, ha='center', va='center',
            fontfamily='serif', fontstyle='italic', color=text_color
        )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', transparent=True, pad_inches=0.08)
    plt.close(fig)
    return output_path

def add_formula_to_docx_doc(
    doc: docx.Document,
    image_path: str,
    chapter_num: int = 3,
    formula_num: int = 1,
    intro_text: Optional[str] = None,
    variable_definitions: Optional[Dict[str, str]] = None,
    image_width_inches: float = 4.0
):
    """
    Menyisipkan rumus matematika ke dokumen DOCX dengan format resmi:
    1. Paragraf pengantar (opsional).
    2. Tabel 1 baris x 2 kolom borderless:
       - Kolom kiri (5.2 inci): Rumus matematika terpusat (Center).
       - Kolom kanan (0.8 inci): Nomor persamaan (X.Y) rata kanan (Right).
    3. Keterangan simbol variabel 'di mana:' (opsional).
    """
    if intro_text:
        p_intro = doc.add_paragraph(intro_text)
        p_intro.paragraph_format.space_after = Pt(4)

    # 1. Buat tabel borderless 1x2 untuk tata letak rumus & nomor persamaan
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Hilangkan border tabel
    tblPr = tbl._tbl.tblPr
    borders_xml = (
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
        f'<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(parse_xml(borders_xml))

    # Kolom 0: Rumus Matematika (Center)
    cell_eq = tbl.rows[0].cells[0]
    cell_eq.width = Inches(5.2)
    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_before = Pt(4)
    p_eq.paragraph_format.space_after = Pt(4)

    if os.path.exists(image_path):
        run_img = p_eq.add_run()
        run_img.add_picture(image_path, width=Inches(image_width_inches))

    # Kolom 1: Nomor Persamaan (Right)
    cell_num = tbl.rows[0].cells[1]
    cell_num.width = Inches(0.8)
    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(8)
    p_num.paragraph_format.space_after = Pt(4)
    run_num = p_num.add_run(f"({chapter_num}.{formula_num})")
    run_num.bold = False

    # 2. Tambahkan keterangan variabel jika ada
    if variable_definitions:
        p_dimana = doc.add_paragraph("di mana:")
        p_dimana.paragraph_format.space_before = Pt(4)
        p_dimana.paragraph_format.space_after = Pt(2)

        for sym, desc in variable_definitions.items():
            p_var = doc.add_paragraph()
            p_var.paragraph_format.left_indent = Inches(0.25)
            p_var.paragraph_format.space_before = Pt(1)
            p_var.paragraph_format.space_after = Pt(2)

            r_sym = p_var.add_run(f"{sym}")
            r_sym.italic = True
            p_var.add_run(f" = {desc}")

def generate_math_formula(
    latex_code: str,
    formula_title: str = "Persamaan Matematika",
    chapter_num: int = 3,
    formula_num: int = 1,
    variable_definitions: Optional[Dict[str, str]] = None,
    workspace_dir: str = ".",
    asset_folder: str = DEFAULT_ASSET_DIR,
    output_filename: Optional[str] = None,
    target_document_docx: Optional[str] = None,
    intro_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fungsi orkestrasi untuk membuat gambar rumus matematika di /asset,
    dan menyisipkannya ke dokumen DOCX jika ditentukan.
    """
    asset_dir = ensure_asset_dir(workspace_dir=workspace_dir, asset_folder=asset_folder)

    if not output_filename:
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', formula_title.lower())[:25]
        output_filename = f"formula_{chapter_num}_{formula_num}_{safe_title}.png"

    img_path = os.path.join(asset_dir, output_filename)
    rendered_file = render_latex_formula_image(
        latex_code=latex_code,
        output_path=img_path
    )

    relative_path = os.path.join(asset_folder, output_filename).replace("\\", "/")
    inserted_info = None

    if target_document_docx:
        doc_path = os.path.join(workspace_dir, target_document_docx)
        if os.path.exists(doc_path):
            doc = docx.Document(doc_path)
            add_formula_to_docx_doc(
                doc=doc,
                image_path=img_path,
                chapter_num=chapter_num,
                formula_num=formula_num,
                intro_text=intro_text or f"Persamaan {formula_title} dirumuskan sebagai berikut:",
                variable_definitions=variable_definitions
            )
            doc.save(doc_path)
            inserted_info = {
                "document": target_document_docx,
                "equation_number": f"({chapter_num}.{formula_num})",
                "status": "INSERTED"
            }

    return {
        "status": "SUCCESS",
        "formula_title": formula_title,
        "latex_code": latex_code,
        "equation_number": f"({chapter_num}.{formula_num})",
        "image_filename": output_filename,
        "asset_folder": asset_folder,
        "relative_path": relative_path,
        "full_path": os.path.abspath(rendered_file),
        "file_size_bytes": os.path.getsize(rendered_file),
        "variable_definitions": variable_definitions or {},
        "inserted_into_document": inserted_info
    }
