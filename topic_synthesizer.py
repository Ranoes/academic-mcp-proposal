"""
topic_synthesizer.py
Modul sintesis otomatis untuk mengubah topik penelitian dan data literatur (CSV / paper-search)
menjadi struktur naskah proposal skripsi lengkap (Bab 1, Bab 2, Bab 3, tabel, dan daftar pustaka).
"""
import re
from typing import Dict, Any, List, Optional, Tuple

def plan_research(
    topic: str,
    bidang_kajian: Optional[str] = None,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None
) -> Dict[str, Any]:
    """
    Menurunkan rumusan masalah tunggal, variabel independen (X), variabel dependen (Y),
    dan kueri pencarian literatur yang dioptimalkan untuk paper-search MCP.
    """
    clean_topic = topic.strip()

    # Ekstraksi otomatis jika X dan Y belum diberikan
    x_val = variabel_x
    y_val = variabel_y

    if not x_val or not y_val:
        # Coba pola umum: "Penerapan X untuk Meningkatkan Y" atau "Optimizing Y using X"
        match_id = re.search(r'(?:menggunakan|dengan|penerapan|implementasi|berbasis)\s+(.+?)\s+(?:untuk|terhadap|dalam|pada)\s+(.+)', clean_topic, re.IGNORECASE)
        match_en = re.search(r'(?:optimizing|improving|enhancing|predicting|evaluating)\s+(.+?)\s+(?:using|with|via|through)\s+(.+)', clean_topic, re.IGNORECASE)
        
        if match_id:
            if not x_val:
                x_val = match_id.group(1).strip()
            if not y_val:
                y_val = match_id.group(2).strip()
        elif match_en:
            if not y_val:
                y_val = match_en.group(1).strip()
            if not x_val:
                x_val = match_en.group(2).strip()
        else:
            if not x_val:
                x_val = f"Metode/Pendekatan berbasis {clean_topic}"
            if not y_val:
                y_val = f"Kinerja dan Efektivitas {clean_topic}"

    # Formulasi rumusan masalah non-deskriptif yang berorientasi pengukuran
    rumusan_masalah = (
        f"Sejauh mana implementasi {x_val} mampu meningkatkan performa {y_val} "
        f"secara signifikan dibandingkan dengan metode konvensional?"
    )

    tujuan_umum = (
        f"menganalisis, mengimplementasikan, dan menguji efektivitas {x_val} "
        f"dalam mengoptimalkan {y_val}."
    )

    tujuan_khusus = [
        f"Mengidentifikasi kendala utama dan baseline performa pada {y_val}.",
        f"Merancang dan memodelkan arsitektur {x_val}.",
        f"Mengimplementasikan dan menguji model {x_val} pada lingkungan pengujian yang representatif.",
        f"Mengevaluasi peningkatan performa {y_val} melalui metrik komparasi kuantitatif."
    ]

    # Kueri pencarian yang dioptimalkan untuk paper-search MCP
    domain_kw = bidang_kajian.strip() if bidang_kajian else ""
    arxiv_query = f"{x_val} AND {y_val}"
    scholar_query = f'"{x_val}" "{y_val}"'
    semantic_query = f"{x_val} {y_val} benchmark performance"
    if domain_kw:
        arxiv_query += f" AND {domain_kw}"
        semantic_query += f" {domain_kw}"

    return {
        "topic": clean_topic,
        "bidang_kajian": bidang_kajian or "Teknologi Informasi / Ilmu Komputer",
        "variabel_x": x_val,
        "variabel_y": y_val,
        "rumusan_masalah": rumusan_masalah,
        "tujuan_umum": tujuan_umum,
        "tujuan_khusus": tujuan_khusus,
        "search_queries_for_paper_search": {
            "arxiv": arxiv_query,
            "google_scholar": scholar_query,
            "semantic_scholar": semantic_query,
            "crossref": f"{x_val} {y_val}"
        },
        "recommended_agent_workflow": [
            "1. Jalankan paper-search MCP (search_papers, search_arxiv, search_semantic) menggunakan kueri di atas.",
            "2. Jika terdapat file CSV tinjauan pustaka di workspace, baca menggunakan parse_literature_csv.",
            "3. Panggil generate_proposal_from_topic dengan menggabungkan topic, CSV, dan paper hasil pencarian."
        ]
    }

def synthesize_proposal_from_inputs(
    topic: str,
    metadata: Dict[str, str],
    variabel_x: str,
    variabel_y: str,
    literature_records: List[Dict[str, Any]],
    table_matrix: Optional[List[List[str]]] = None,
    references: Optional[List[str]] = None,
    latar_belakang_notes: Optional[List[str]] = None,
    metode_penelitian_notes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Menyusun bab1_data, bab2_subbab, bab3_subbab, tabel, dan daftar referensi secara otomatis.
    """
    clean_topic = topic.strip()

    # --- BAB 1: PENDAHULUAN ---
    lb_paragraphs = []
    lb_paragraphs.append(
        f"Perkembangan teknologi komputasi dan sistem informasi saat ini menuntut efisiensi dan keandalan tinggi. "
        f"Dalam lingkup penelitian mengenai {clean_topic}, permasalahan terkait {variabel_y} menjadi fokus kritis "
        f"yang memerlukan pemecahan terstruktur dan terukur."
    )
    lb_paragraphs.append(
        f"Pendekatan konvensional yang ada saat ini seringkali menghadapi kendala dalam mempertahankan kinerja optimal "
        f"ketika dihadapkan pada kompleksitas dan skala data yang dinamis. Keterbatasan tersebut berdampak langsung "
        f"terhadap stabilitas {variabel_y}."
    )
    if latar_belakang_notes:
        for note in latar_belakang_notes:
            lb_paragraphs.append(note.strip())

    lb_paragraphs.append(
        f"Untuk mengatasi permasalahan tersebut, penelitian ini mengusulkan penerapan {variabel_x}. "
        f"Pendekatan ini diharapkan dapat memberikan perbaikan signifikan terhadap {variabel_y} "
        f"serta memperluas pemahaman teoritis dan praktis di bidang terkait."
    )

    rumusan_masalah_pengantar = "Berdasarkan uraian latar belakang masalah di atas, maka rumusan masalah penelitian dirumuskan sebagai berikut:"
    rumusan_masalah = f"Sejauh mana implementasi {variabel_x} mampu meningkatkan {variabel_y} secara terukur dibandingkan dengan metode pembanding?"
    rumusan_masalah_penjelasan = (
        f"Rumusan masalah tunggal ini berorientasi pada pengukuran kausalitas antara variabel independen "
        f"({variabel_x}) dan variabel dependen ({variabel_y})."
    )

    tujuan_umum = f"mengukur dan menganalisis efektivitas {variabel_x} dalam meningkatkan {variabel_y}."
    tujuan_khusus = [
        f"Menganalisis performa awal dan bottleneck sistem pada {variabel_y}.",
        f"Merancang alur kerja dan konfigurasi algoritma {variabel_x}.",
        f"Mengimplementasikan model uji pada data eksperimental / simulasi.",
        f"Mengevaluasi signifikansi peningkatan {variabel_y} menggunakan metrik performa standar."
    ]

    manfaat = [
        f"Bagi Praktisi dan Pengembang: Memberikan referensi implementasi praktis terkait penerapan {variabel_x} untuk optimasi sistem.",
        f"Bagi Akademisi dan Peneliti: Menyumbangkan data empiris dan kajian komparatif mengenai korelasi antara {variabel_x} dan {variabel_y}."
    ]

    batasan_masalah = [
        f"Fokus pengujian dibatasi pada skenario evaluasi yang mengukur indikator performa {variabel_y}.",
        f"Metode yang dievaluasi berpusat pada arsitektur {variabel_x}.",
        "Data uji dan parameter lingkungan disesuaikan dengan standar pengujian akademis yang representatif."
    ]

    sistematika = [
        "BAB 1 PENDAHULUAN: Memuat latar belakang permasalahan, rumusan masalah tunggal, tujuan penelitian, manfaat teoritis dan praktis, batasan masalah, serta sistematika pembahasan.",
        "BAB 2 TINJAUAN PUSTAKA: Menguraikan landasan teori terkait variabel penelitian, sintesis penelitian terdahulu yang relevan, dan tabel komparasi literatur.",
        "BAB 3 METODOLOGI PENELITIAN: Menjabarkan tahapan penelitian, alur perancangan sistem, instrumen evaluasi, metrik performa, dan jadwal pelaksanaan."
    ]

    bab1_data = {
        "latar_belakang": lb_paragraphs,
        "rumusan_masalah_pengantar": rumusan_masalah_pengantar,
        "rumusan_masalah": rumusan_masalah,
        "rumusan_masalah_penjelasan": rumusan_masalah_penjelasan,
        "tujuan_umum": tujuan_umum,
        "tujuan_khusus": tujuan_khusus,
        "manfaat": manfaat,
        "batasan_masalah": batasan_masalah,
        "sistematika_pembahasan": sistematika
    }

    # --- BAB 2: TINJAUAN PUSTAKA ---
    bab2_subbab = [
        {
            "title": f"Konsep Dasar dan Teori {variabel_x}",
            "level": 2,
            "paragraphs": [
                f"{variabel_x} merupakan fondasi utama dalam perancangan solusi pada penelitian ini. "
                f"Prinsip kerja metode ini menitikberatkan pada optimasi parameter dan kemampuan adaptif "
                f"terhadap karakteristik sistem yang kompleks.",
                f"Berbagai literatur menunjukkan bahwa {variabel_x} memiliki keunggulan komparatif "
                f"dalam menangani masalah konvergensi dan efisiensi pemrosesan data."
            ]
        },
        {
            "title": f"Tinjauan Kinerja {variabel_y}",
            "level": 2,
            "paragraphs": [
                f"Aspek {variabel_y} menjadi tolok ukur keberhasilan utama dalam studi ini. "
                f"Pengukuran terhadap variabel ini dilakukan secara kuantitatif guna memastikan bahwa "
                f"intervensi yang diberikan menghasilkan perbaikan yang terbukti secara empiris."
            ]
        }
    ]

    # Narasi literatur terdahulu
    lit_paragraphs = []
    if literature_records:
        for rec in literature_records:
            auth = rec.get("author", "Peneliti")
            yr = rec.get("year", "2024")
            ttl = rec.get("title", "")
            mth = rec.get("method", "-")
            res = rec.get("results", "-")
            gap = rec.get("gap", "-")

            p_text = f"Penelitian oleh {auth} ({yr}) dengan judul \"{ttl}\" mengkaji penerapan metode {mth}."
            if res != "-":
                p_text += f" Hasil studi tersebut mencatatkan bahwa {res}."
            if gap != "-":
                p_text += f" Namun, terdapat celah penelitian (research gap) yakni {gap}."
            lit_paragraphs.append(p_text)
    else:
        lit_paragraphs.append(
            f"Kajian literatur komparatif menunjukkan bahwa integrasi {variabel_x} masih menghadapi tantangan "
            f"dalam konteks stabilitas {variabel_y}, yang menjadi motivasi utama penelitian ini."
        )

    bab2_subbab.append({
        "title": "Penelitian Terdahulu dan Research Gap",
        "level": 2,
        "paragraphs": lit_paragraphs
    })

    # --- BAB 3: METODOLOGI PENELITIAN ---
    metode_paras = [
        "Metodologi penelitian dirancang secara sistematis melalui tahapan: studi literatur, "
        "analisis kebutuhan dan perancangan model, implementasi algoritma, serta pengujian dan evaluasi hasil."
    ]
    if metode_penelitian_notes:
        for note in metode_penelitian_notes:
            metode_paras.append(note.strip())

    bab3_subbab = [
        {
            "title": "Tahapan dan Alur Penelitian",
            "level": 2,
            "paragraphs": metode_paras
        },
        {
            "title": "Perancangan dan Implementasi Sistem",
            "level": 2,
            "paragraphs": [
                f"Perancangan sistem difokuskan pada integrasi modul {variabel_x}. "
                f"Setiap komponen dimodelkan untuk secara konsisten memonitor dan mengoptimalkan respon terhadap {variabel_y}."
            ]
        },
        {
            "title": "Skenario Pengujian dan Metrik Evaluasi",
            "level": 2,
            "paragraphs": [
                f"Evaluasi dilakukan dengan membandingkan performa {variabel_x} terhadap model acuan dasar. "
                f"Pengukuran kuantitatif difokuskan pada parameter capaian {variabel_y}."
            ]
        }
    ]

    # Matriks Literatur
    tabel_tp = table_matrix
    if not tabel_tp:
        tabel_tp = [
            ["No", "Peneliti & Tahun", "Judul Penelitian", "Metode / Algoritma", "Hasil & Temuan", "Research Gap"],
            ["1", "Baseline Study (2023)", f"Benchmark Study on {variabel_y}", "Metode Standar", f"Evaluasi awal {variabel_y}", f"Belum menerapkan {variabel_x}"]
        ]

    # Daftar Referensi
    final_refs = references or []
    if not final_refs:
        final_refs = [
            f"Russell, S. & Norvig, P., 2020. Artificial Intelligence: A Modern Approach. 4th ed. Pearson.",
            f"Sutton, R.S. & Barto, A.G., 2018. Reinforcement Learning: An Introduction. MIT Press."
        ]

    return {
        "bab1_data": bab1_data,
        "bab2_subbab": bab2_subbab,
        "bab3_subbab": bab3_subbab,
        "tabel_tinjauan_pustaka": tabel_tp,
        "daftar_referensi": final_refs
    }
