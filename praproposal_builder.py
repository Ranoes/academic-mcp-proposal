"""
praproposal_builder.py
Modul builder untuk menghasilkan berkas Dokumen Pra-Proposal Skripsi (SA2-01A)
berbasis template OpenDocument Text (template_SA2-01A.odt).
"""
import os
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

DEFAULT_PRA_TEMPLATE_PATH = "/app/assets/templates/template_SA2-01A.odt"
if not os.path.exists(DEFAULT_PRA_TEMPLATE_PATH):
    DEFAULT_PRA_TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__), "assets", "templates", "template_SA2-01A.odt"
    )

# XML Namespaces standard for OpenDocument Text
NAMESPACES = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
    'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
    'xlink': 'http://www.w3.org/1999/xlink',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'meta': 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
    'number': 'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0',
    'svg': 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
    'loext': 'http://org.documentfoundation.names/experimental/office/xmlns/loext/1.0'
}

for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)

def _create_p_element(text: str, style_name: str = "P7") -> ET.Element:
    """Helper untuk membuat elemen text:p baru."""
    p = ET.Element(f"{{{NAMESPACES['text']}}}p")
    if style_name:
        p.set(f"{{{NAMESPACES['text']}}}style-name", style_name)
    p.text = text
    return p

def _set_cell_paragraphs(
    cell: ET.Element,
    paragraphs: Union[str, List[str]],
    default_style: str = "P7"
):
    """
    Mengosongkan isi text:p / list yang ada di dalam cell,
    lalu mengisinya dengan paragraf-paragraf baru.
    """
    # Cari style-name dari p pertama jika ada untuk mempertahankan style asli
    detected_style = default_style
    first_p = cell.find(f".//{{{NAMESPACES['text']}}}p")
    if first_p is not None:
        style_attr = first_p.get(f"{{{NAMESPACES['text']}}}style-name")
        if style_attr:
            detected_style = style_attr

    # Hapus semua anak cell (paragraf/list/annotation/gambar)
    for child in list(cell):
        cell.remove(child)

    if isinstance(paragraphs, str):
        # Pisahkan newline jika string multi-line
        lines = [line.strip() for line in paragraphs.split("\n") if line.strip()]
        if not lines:
            lines = [paragraphs]
    elif isinstance(paragraphs, list):
        lines = paragraphs
    else:
        lines = [str(paragraphs)]

    for line in lines:
        if isinstance(line, dict):
            # Jika objek referensi / structured item
            text_str = line.get("text") or line.get("citation") or str(line)
        else:
            text_str = str(line)
        cell.append(_create_p_element(text_str, detected_style))

def build_praproposal_odt(
    metadata: Dict[str, Any],
    sections: Dict[str, Any],
    output_path: str,
    template_path: Optional[str] = None
) -> str:
    """
    Membangun berkas pra-proposal skripsi .odt dari template resmi SA2-01A.
    """
    tpl_path = template_path or DEFAULT_PRA_TEMPLATE_PATH
    if not os.path.exists(tpl_path):
        raise FileNotFoundError(f"Template SA2-01A tidak ditemukan di {tpl_path}")

    # Baca file ODT (zip) ke memory
    with open(tpl_path, "rb") as f:
        odt_bytes = io.BytesIO(f.read())

    with zipfile.ZipFile(odt_bytes, "r") as z_in:
        content_xml = z_in.read("content.xml")
        file_map = {name: z_in.read(name) for name in z_in.namelist() if name != "content.xml"}

    root = ET.fromstring(content_xml)
    tables = root.findall(f".//{{{NAMESPACES['table']}}}table")

    if len(tables) < 3:
        raise ValueError("Struktur template SA2-01A tidak sesuai: tabel kurang dari 3.")

    table_meta = tables[1]      # Table 1: Metadata Mahasiswa & Judul
    table_sections = tables[2]  # Table 2: Isi Pra-Proposal & Tanda Tangan

    # ==========================================
    # 1. Update Table 1: Metadata Mahasiswa & Skripsi
    # ==========================================
    meta_rows = table_meta.findall(f"./{{{NAMESPACES['table']}}}table-row")
    
    meta_mapping = {
        0: metadata.get("nama_mahasiswa", ""),
        1: metadata.get("nim", ""),
        2: metadata.get("jurusan", "Teknik Informatika"),
        3: metadata.get("program_studi", "Teknik Informatika"),
        4: metadata.get("keminatan", "Komputasi Cerdas"),
        5: metadata.get("bidang_skripsi", "Artificial Intelligence & Data Science"),
        6: metadata.get("jenis_penelitian", "Implementatif"),
        7: metadata.get("tipe_penelitian", "Pengembangan Sistem & Komparasi Algoritma"),
        8: metadata.get("asal_judul", "Usulan Sendiri"),
        9: metadata.get("judul", "")
    }

    for row_idx, val in meta_mapping.items():
        if row_idx < len(meta_rows):
            cells = meta_rows[row_idx].findall(f"./{{{NAMESPACES['table']}}}table-cell")
            if len(cells) >= 3:
                _set_cell_paragraphs(cells[2], str(val), default_style="P5")

    # ==========================================
    # 2. Update Table 2: Bagian Konten Praproposal
    # ==========================================
    sec_rows = table_sections.findall(f"./{{{NAMESPACES['table']}}}table-row")

    # Nilai default lokasi dan tanggal
    current_date = datetime.now()
    bulan_id = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    date_str = f"{current_date.day:02d} {bulan_id[current_date.month - 1]} {current_date.year}"
    lokasi = metadata.get("lokasi", "Malang")
    tgl_mahasiswa = metadata.get("tanggal_mahasiswa", date_str)
    tgl_pembimbing = metadata.get("tanggal_pembimbing", date_str)
    nama_pembimbing = metadata.get("nama_pembimbing", "Dr. Mahrus Ali, S.Kom., M.Kom.")
    nip_pembimbing = metadata.get("nip_pembimbing", "-")
    nama_mhs = metadata.get("nama_mahasiswa", "")
    nim_mhs = metadata.get("nim", "")

    # Format Rumusan Masalah (TETAP SATU rumusan masalah sesuai Research Design Canvas CLB04-01)
    rm_raw = sections.get("rumusan_masalah", [])
    if isinstance(rm_raw, str):
        rm_lines = [l.strip() for l in rm_raw.split("\n") if l.strip()]
    else:
        rm_lines = list(rm_raw)
    
    # Ambil pertanyaan utama pertama untuk menjamin kepatuhan single problem formulation
    primary_rm = rm_lines[0] if rm_lines else "Sejauh mana efektivitas implementasi metode yang diusulkan?"
    clean_rm = re.sub(r'^\d+[\.\)]\s*', '', str(primary_rm)).strip()
    rm_formatted = [f"1. {clean_rm}"]

    # Format Daftar Pustaka
    dp_raw = sections.get("daftar_pustaka", [])
    if isinstance(dp_raw, str):
        dp_lines = [l.strip() for l in dp_raw.split("\n") if l.strip()]
    else:
        dp_lines = list(dp_raw)

    dp_formatted = []
    for idx, item in enumerate(dp_lines, 1):
        clean_item = re.sub(r'^\d+[\.\)]\s*', '', str(item)).strip()
        dp_formatted.append(f"[{idx}] {clean_item}")

    sections_mapping = {
        0: sections.get("latar_belakang", []),
        1: sections.get("landasan_kepustakaan", []),
        2: rm_formatted,
        3: sections.get("metode", []),
        4: dp_formatted,
        5: [
            "Diteruskan menjadi proposal / Ditolak *)",
            "Keterangan: (apabila ditolak)"
        ],
        6: [
            "(diisi oleh calon pembimbing)"
        ],
        7: [
            f"{lokasi}, {tgl_mahasiswa}",
            "",
            "",
            f"{nama_mhs}",
            f"NIM. {nim_mhs}"
        ],
        8: [
            f"{lokasi}, {tgl_pembimbing}",
            "",
            "",
            f"{nama_pembimbing}",
            f"NIP: {nip_pembimbing}"
        ]
    }

    for row_idx, content in sections_mapping.items():
        if row_idx < len(sec_rows):
            cells = sec_rows[row_idx].findall(f"./{{{NAMESPACES['table']}}}table-cell")
            if len(cells) >= 2:
                _set_cell_paragraphs(cells[1], content, default_style="P7")

    # ==========================================
    # 3. Simpan XML Baru dan Export ke File .odt
    # ==========================================
    new_content_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    # Pastikan direktori output tersedia
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
        # Masukkan content.xml yang telah diupdate
        z_out.writestr("content.xml", new_content_xml)
        # Masukkan file-file lainnya dari template (mimetype, styles, manifest, images, fonts)
        for name, data in file_map.items():
            z_out.writestr(name, data)

    return output_path
