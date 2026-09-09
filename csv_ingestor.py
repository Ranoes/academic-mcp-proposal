"""
csv_ingestor.py
Modul untuk membaca, mem-parsing, dan mengekstraksi data literatur & dataset dari berkas CSV.
Mengonversi matriks literatur menjadi tabel tinjauan pustaka DOCX dan daftar referensi standar.
"""
import os
import csv
import io
from typing import Dict, Any, List, Optional, Tuple

def _find_column(headers: List[str], candidates: List[str]) -> Optional[int]:
    lower_headers = [h.strip().lower() for h in headers]
    for cand in candidates:
        for idx, h in enumerate(lower_headers):
            if cand in h:
                return idx
    return None

def parse_literature_csv(
    file_path: Optional[str] = None,
    csv_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Membaca dan mem-parsing CSV literatur menjadi struktur terstandarisasi:
    - tabel_tinjauan_pustaka (matrix teks untuk tabel DOCX)
    - daftar_referensi (daftar sitasi format Harvard/IEEE)
    - bab2_literature_summary (sintesis narasi per studi untuk Bab 2)
    - raw_records (list dictionary)
    """
    if not csv_content:
        if not file_path or not os.path.exists(file_path):
            return {
                "status": "ERROR",
                "message": f"Berkas CSV tidak ditemukan di path: {file_path}",
                "records": [],
                "table_matrix": [],
                "references": [],
                "summary_paragraphs": []
            }
        with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            csv_text = f.read()
    else:
        csv_text = csv_content

    # Deteksi delimiter (koma, titik koma, atau tab)
    delimiter = ","
    try:
        sample = csv_text[:2048]
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=";,|\t,")
        delimiter = dialect.delimiter
    except Exception:
        if ";" in sample and "," not in sample:
            delimiter = ";"

    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
    rows = [r for r in reader if any(field.strip() for field in r)]

    if not rows:
        return {
            "status": "EMPTY",
            "message": "Berkas CSV kosong atau tidak memiliki baris data.",
            "records": [],
            "table_matrix": [],
            "references": [],
            "summary_paragraphs": []
        }

    headers = [h.strip() for h in rows[0]]
    data_rows = rows[1:]

    # Deteksi indeks kolom penting
    idx_author = _find_column(headers, ["author", "penulis", "researcher", "nama"])
    idx_year = _find_column(headers, ["year", "tahun"])
    idx_title = _find_column(headers, ["title", "judul", "paper"])
    idx_method = _find_column(headers, ["method", "metode", "algorithm", "pendekatan", "model", "arsitektur"])
    idx_dataset = _find_column(headers, ["dataset", "data", "benchmark", "skenario"])
    idx_results = _find_column(headers, ["result", "hasil", "finding", "temuan", "metric", "akurasi", "f1"])
    idx_gap = _find_column(headers, ["gap", "research gap", "limitation", "kelemahan", "kekurangan", "kendala"])

    records = []
    table_matrix = []
    references = []
    summary_paragraphs = []

    # Baris header tabel tinjauan pustaka
    table_header = ["No", "Peneliti & Tahun", "Judul Penelitian", "Metode / Algoritma", "Hasil & Temuan", "Research Gap"]
    table_matrix.append(table_header)

    for i, row in enumerate(data_rows, start=1):
        def get_val(idx: Optional[int]) -> str:
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return ""

        author = get_val(idx_author) or f"Peneliti {i}"
        year = get_val(idx_year) or "2024"
        title = get_val(idx_title) or f"Studi Literatur {i}"
        method = get_val(idx_method) or "-"
        dataset = get_val(idx_dataset)
        results = get_val(idx_results) or "-"
        gap = get_val(idx_gap) or "-"

        rec = {
            "no": i,
            "author": author,
            "year": year,
            "title": title,
            "method": method,
            "dataset": dataset,
            "results": results,
            "gap": gap
        }
        records.append(rec)

        # Baris tabel
        peneliti_tahun = f"{author} ({year})"
        hasil_text = results
        if dataset:
            hasil_text = f"Dataset: {dataset}. {results}"

        table_matrix.append([
            str(i),
            peneliti_tahun,
            title,
            method,
            hasil_text,
            gap
        ])

        # Referensi format Harvard
        ref_entry = f"{author}, {year}. {title}."
        if method != "-":
            ref_entry += f" Penerapan metode {method}."
        references.append(ref_entry)

        # Narasi sintesis untuk Bab 2
        p_text = (
            f"Penelitian yang dilakukan oleh {author} ({year}) berjudul \"{title}\" "
            f"menerapkan pendekatan {method}."
        )
        if dataset:
            p_text += f" Pengujian dilakukan dengan menggunakan dataset {dataset}."
        if results != "-":
            p_text += f" Hasil penelitian menunjukkan bahwa {results}."
        if gap != "-":
            p_text += f" Namun demikian, terdapat keterbatasan berupa {gap}."
        summary_paragraphs.append(p_text)

    return {
        "status": "SUCCESS",
        "total_records": len(records),
        "records": records,
        "table_matrix": table_matrix,
        "references": references,
        "summary_paragraphs": summary_paragraphs
    }
