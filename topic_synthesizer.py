"""
topic_synthesizer.py
Modul sintesis otomatis untuk mengubah topik penelitian dan data literatur (CSV / paper-search)
menjadi struktur naskah proposal skripsi lengkap (Bab 1, Bab 2, Bab 3, tabel, dan daftar pustaka).
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from canvas_validator import check_research_canvas

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

    # Anti-Rancang Bangun / Anti-Project automatic cleaning:
    # Memastikan topik berorientasi pada temuan pengetahuan ilmiah empiris (bukan proyek pembuatan aplikasi/sistem)
    PROJECT_PREFIX_PATTERNS = [
        r"^rancang\s+bangun\s+(?:aplikasi|sistem|website|web|platform|game)?\s*(?:berbasis)?\s*",
        r"^pengembangan\s+(?:aplikasi|sistem|website|web|platform|game)?\s*(?:berbasis)?\s*",
        r"^pembuatan\s+(?:aplikasi|sistem|website|web|platform|game)?\s*(?:berbasis)?\s*",
        r"^membangun\s+(?:aplikasi|sistem|website|web|platform|game)?\s*(?:berbasis)?\s*",
        r"^desain\s+dan\s+implementasi\s+(?:aplikasi|sistem|website)?\s*(?:berbasis)?\s*"
    ]
    for pat in PROJECT_PREFIX_PATTERNS:
        clean_topic = re.sub(pat, "", clean_topic, flags=re.IGNORECASE).strip()

    # Ekstraksi otomatis jika X dan Y belum diberikan
    x_val = variabel_x
    y_val = variabel_y

    if not x_val or not y_val:
        # Coba pola umum: "Penerapan X untuk Meningkatkan Y" atau "Optimizing Y using X"
        match_id = re.search(r'(?:menggunakan|dengan|penerapan|implementasi|berbasis|analisis)\s+(.+?)\s+(?:untuk|terhadap|dalam|pada)\s+(.+)', clean_topic, re.IGNORECASE)
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
                x_val = f"Model/Algoritma berbasis {clean_topic}"
            if not y_val:
                y_val = f"Kinerja, Akurasi, dan Efisiensi {clean_topic}"

    # Formulasi rumusan masalah non-deskriptif yang berorientasi pengukuran empiris ilmiah (X -> Y)
    rumusan_masalah = (
        f"Sejauh mana implementasi {x_val} mampu meningkatkan performa {y_val} "
        f"secara signifikan dibandingkan dengan metode baseline/konvensional?"
    )

    tujuan_umum = (
        f"menganalisis dan menguji secara empiris efektivitas {x_val} "
        f"dalam mengoptimalkan {y_val}."
    )

    tujuan_khusus = [
        f"Mengidentifikasi kendala utama dan mengukur performa baseline pada {y_val}.",
        f"Memodelkan dan memformulasi arsitektur algoritma {x_val}.",
        f"Melakukan pengujian eksperimental model {x_val} pada skenario dataset empiris yang representatif.",
        f"Mengevaluasi peningkatan performa {y_val} melalui metrik komparasi kuantitatif dan uji signifikansi statistik."
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
            "search_papers": f"{x_val} {y_val}",
            "arxiv": arxiv_query,
            "google_scholar": scholar_query,
            "semantic_scholar": semantic_query,
            "crossref": f"{x_val} {y_val}",
            "scihub_mirror_recommendation": "https://sci-hub.ren"
        },
        "required_student_information": {
            "nama_mahasiswa": "Nama lengkap mahasiswa (wajib)",
            "nim": "Nomor Induk Mahasiswa (wajib)",
            "departemen": "Departemen / Jurusan (contoh: Departemen Teknik Informatika)",
            "program_studi": "Program Studi (contoh: Teknik Informatika / Sistem Informasi / Teknik Komputer)",
            "keminatan": "Keminatan / Kelompok Keahlian (contoh: Komputasi Cerdas, Rekayasa Perangkat Lunak, Jaringan)",
            "bidang_skripsi": "Bidang kajian skripsi (contoh: Artificial Intelligence, Data Science, IoT)",
            "nama_pembimbing": "Nama Dosen Calon Pembimbing beserta gelar lengkap (wajib)",
            "nip_pembimbing": "NIP Dosen Calon Pembimbing (wajib)",
            "lokasi": "Lokasi / Kota pengesahan (contoh: Malang)",
            "jenis_penelitian": "Implementatif / Non-implementatif (default: Implementatif)",
            "asal_judul": "Usulan Sendiri / Usulan Pembimbing (default: Usulan Sendiri)"
        },
        "recommended_agent_workflow": [
            "1. WAJIB: Tanyakan dan konfirmasi ulang data diri mahasiswa (Nama, NIM, Departemen, Program Studi, Dosen Pembimbing, NIP, Lokasi, dll.) kepada pengguna.",
            "2. Jalankan paper-search MCP (search_papers, search_arxiv, search_semantic, atau download_scihub bila membutuhkan naskah lengkap paywalled) menggunakan kueri di atas.",
            "3. Jika terdapat file CSV tinjauan pustaka di workspace, baca menggunakan parse_literature_csv_data.",
            "4. Panggil generate_praproposal_from_topic atau generate_proposal_from_topic dengan menyertakan daftar paper hasil pencarian retrieved_papers dan student_metadata yang telah dikonfirmasi.",
            "5. Tampilkan checklist konfirmasi identitas dokumen kepada pengguna untuk verifikasi final."
        ]
    }

def check_missing_student_metadata(
    metadata: Optional[Dict[str, Any]] = None,
    is_praproposal: bool = False
) -> Dict[str, Any]:
    """
    Memeriksa kelengkapan metadata mahasiswa dan dosen.
    Mengembalikan daftar field yang belum terisi atau masih berupa nilai default placeholder,
    serta checklist konfirmasi yang wajib ditampilkan oleh agen ke pengguna.
    """
    meta = metadata or {}
    missing_fields: List[str] = []
    
    # Nilai-nilai placeholder default yang dianggap belum dikonfirmasi pengguna
    placeholders = [
        "mahasiswa peneliti", "alex mercer", "test student", "[nama]",
        "225150200111000", "std-2026-94821", "202612345", "[nim]",
        "dr. mahrus ali, s.kom., m.kom.", "[nama dosen pembimbing]", "[dosen]",
        "-", "[lokasi]"
    ]

    nama = str(meta.get("nama_mahasiswa", "")).strip()
    if not nama or nama.lower() in placeholders:
        missing_fields.append("nama_mahasiswa")

    nim = str(meta.get("nim", "")).strip()
    if not nim or nim.lower() in placeholders:
        missing_fields.append("nim")

    prodi = str(meta.get("program_studi", "")).strip()
    if not prodi:
        missing_fields.append("program_studi")

    dept = str(meta.get("departemen") or meta.get("jurusan", "")).strip()
    if not dept:
        missing_fields.append("departemen")

    pembimbing = str(meta.get("nama_pembimbing", "")).strip()
    if not pembimbing or pembimbing.lower() in placeholders:
        missing_fields.append("nama_pembimbing")

    nip = str(meta.get("nip_pembimbing", "")).strip()
    if not nip or nip in ["-", "NIP :-", "NIP: -"]:
        missing_fields.append("nip_pembimbing")

    lokasi = str(meta.get("lokasi", "")).strip()
    if not lokasi or lokasi.lower() in ["[lokasi]"]:
        missing_fields.append("lokasi")

    if is_praproposal:
        keminatan = str(meta.get("keminatan", "")).strip()
        if not keminatan:
            missing_fields.append("keminatan")

        bidang = str(meta.get("bidang_skripsi", "")).strip()
        if not bidang:
            missing_fields.append("bidang_skripsi")

    is_complete = len(missing_fields) == 0

    confirmation_data = {
        "nama_mahasiswa": meta.get("nama_mahasiswa", "- (perlu dikonfirmasi)"),
        "nim": meta.get("nim", "- (perlu dikonfirmasi)"),
        "departemen": meta.get("departemen") or meta.get("jurusan", "- (perlu dikonfirmasi)"),
        "program_studi": meta.get("program_studi", "- (perlu dikonfirmasi)"),
        "dosen_pembimbing": meta.get("nama_pembimbing", "- (perlu dikonfirmasi)"),
        "nip_pembimbing": meta.get("nip_pembimbing", "- (perlu dikonfirmasi)"),
        "lokasi": meta.get("lokasi", "Malang")
    }
    if is_praproposal:
        confirmation_data["keminatan"] = meta.get("keminatan", "-")
        confirmation_data["bidang_skripsi"] = meta.get("bidang_skripsi", "-")

    return {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "confirmation_checklist": confirmation_data,
        "mandatory_action": "WAJIB: Agen harus mengonfirmasikan rincian data diri di atas (Nama, NIM, Departemen, Program Studi, Dosen Pembimbing, NIP, Lokasi) secara langsung kepada pengguna.",
        "message": (
            "Semua data identitas mahasiswa dan pembimbing telah terisi. Harap konfirmasikan kembali ke pengguna."
            if is_complete else
            f"Terdapat informasi penting yang belum dikonfirmasi/disediakan: {', '.join(missing_fields)}. "
            "WAJIB: Agen harus menanyakan dan mengonfirmasi data ini kepada pengguna agar dokumen resmi valid."
        )
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

def synthesize_praproposal_from_inputs(
    topic: str,
    metadata: Dict[str, Any],
    variabel_x: str,
    variabel_y: str,
    literature_records: Optional[List[Dict[str, Any]]] = None,
    references: Optional[List[str]] = None,
    latar_belakang_notes: Optional[List[str]] = None,
    metode_notes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Menyusun payload naskah pra-proposal skripsi (SA2-01A) secara otomatis:
    - Metadata mahasiswa & judul penelitian
    - Latar Belakang (<= 500 kata dengan sitasi)
    - Landasan Kepustakaan (<= 250 kata)
    - Rumusan Masalah (numbering)
    - Metode yang digunakan (<= 250 kata)
    - Daftar Pustaka
    """
    clean_topic = topic.strip()
    
    # Normalisasi Metadata Mahasiswa
    mhs_meta = {
        "nama_mahasiswa": metadata.get("nama_mahasiswa", ""),
        "nim": metadata.get("nim", ""),
        "jurusan": metadata.get("jurusan", "Teknik Informatika"),
        "program_studi": metadata.get("program_studi", "Teknik Informatika"),
        "keminatan": metadata.get("keminatan", "Komputasi Cerdas"),
        "bidang_skripsi": metadata.get("bidang_skripsi", "Artificial Intelligence & Data Science"),
        "jenis_penelitian": metadata.get("jenis_penelitian", "Implementatif"),
        "tipe_penelitian": metadata.get("tipe_penelitian", "Penelitian Eksperimental Empiris & Komparasi Algoritma"),
        "asal_judul": metadata.get("asal_judul", "Usulan Sendiri"),
        "judul": metadata.get("judul", clean_topic.upper()),
        "lokasi": metadata.get("lokasi", "Malang"),
        "tanggal_mahasiswa": metadata.get("tanggal_mahasiswa"),
        "tanggal_pembimbing": metadata.get("tanggal_pembimbing"),
        "nama_pembimbing": metadata.get("nama_pembimbing", "Dr. Mahrus Ali, S.Kom., M.Kom."),
        "nip_pembimbing": metadata.get("nip_pembimbing", "-")
    }

    # 1. Latar Belakang (<= 500 kata, selaras Research Design Canvas LB01-LB04)
    lb_paragraphs = []
    if latar_belakang_notes:
        lb_paragraphs.extend(latar_belakang_notes)
    else:
        lb_paragraphs.append(
            f"Perkembangan teknologi komputasi dan pengolahan data saat ini menuntut efisiensi serta akurasi yang semakin tinggi. "
            f"Dalam lingkup topik penelitian '{clean_topic}', permasalahan terkait {variabel_y} merupakan tantangan utama "
            f"yang dihadapi pada implementasi sistem di lapangan. Keterbatasan metode konvensional seringkali mengakibatkan "
            f"penurunan performa dan efisiensi ketika dihadapkan pada skala data yang besar dan kondisi lingkungan yang dinamis."
        )
        if literature_records:
            first_lit = literature_records[0]
            auth = first_lit.get("peneliti") or first_lit.get("author") or "Penelitian sebelumnya"
            year = first_lit.get("tahun") or first_lit.get("year") or "2024"
            find = first_lit.get("temuan") or first_lit.get("findings") or f"analisis pada {variabel_y}"
            lb_paragraphs.append(
                f"Kajian oleh {auth} ({year}) menunjukkan bahwa {find}. Namun demikian, masih terdapat tantangan "
                f"terkait optimasi integrasi algoritma adaptif untuk mengatasi disparitas kinerja tersebut."
            )
        lb_paragraphs.append(
            f"Untuk mengatasi permasalahan tersebut, penelitian ini mengusulkan penerapan {variabel_x}. Pendekatan ini "
            f"diharapkan mampu memberikan peningkatan signifikan terhadap performa {variabel_y} melalui pemodelan "
            f"yang adaptif, presisi, dan teruji secara empiris."
        )

    # 2. Landasan Kepustakaan (<= 250 kata, selaras Research Design Canvas LR01-LR04)
    landasan_paragraphs = []
    landasan_paragraphs.append(
        f"Landasan kepustakaan penelitian ini bertumpu pada teori dan konsep dasar {variabel_x} serta karakteristik {variabel_y}. "
        f"Prinsip fundamental dari {variabel_x} berfokus pada optimasi pengolahan informasi dan adaptasi model terhadap variasi fitur data."
    )
    if literature_records and len(literature_records) > 1:
        lit_synth = []
        for r in literature_records[:3]:
            a = r.get("peneliti") or r.get("author") or "Studi terkait"
            y = r.get("tahun") or r.get("year") or "2024"
            m = r.get("metode") or r.get("method") or "metode komputasi"
            lit_synth.append(f"{a} ({y}) yang menerapkan {m}")
        landasan_paragraphs.append(
            f"Sejumlah penelitian terdahulu yang mendasari kajian ini meliputi penelitian oleh {', serta oleh '.join(lit_synth)}. "
            f"Studi-studi tersebut membuktikan kelayakan metode komputasi cerdas dalam mengoptimalkan performa sistem."
        )
    else:
        landasan_paragraphs.append(
            f"Kajian literatur terkini menunjukkan bahwa pemanfaatan algoritma berbasis data memberikan kestabilan yang lebih baik "
            f"dibandingkan aturan heuristik statis dalam pengelolaan {variabel_y}."
        )

    # 3. Rumusan Masalah (TETAP SATU & Kuantitatif/Komparatif Berorientasi Pengukuran sesuai CLB04-01 & CLB04-02)
    rm_list = [
        f"Sejauh manakah implementasi {variabel_x} mampu meningkatkan efektivitas dan performa {variabel_y} secara signifikan dibandingkan dengan metode konvensional?"
    ]

    # 4. Metode yang Digunakan (<= 250 kata, selaras Research Design Canvas M01-M05: Alur 4 Tahap)
    metode_paragraphs = []
    if metode_notes:
        metode_paragraphs.extend(metode_notes)
    else:
        metode_paragraphs.append(
            f"Metodologi penelitian dilaksanakan melalui empat tahapan terstruktur: "
            f"(1) Pengumpulan dan pra-pemrosesan data representatif terkait {variabel_y}; "
            f"(2) Perancangan, pemodelan, dan integrasi modul arsitektur {variabel_x}; "
            f"(3) Skenario pengujian eksperimental komparatif terhadap metode baseline; serta "
            f"(4) Evaluasi kinerja kuantitatif dan analisis signifikansi peningkatan performa {variabel_y}."
        )

    # 5. Daftar Pustaka (Standar Harvard / IEEE)
    final_refs = references or []
    if not final_refs and literature_records:
        for r in literature_records:
            cit = r.get("citation") or f"{r.get('author', 'Peneliti')}, {r.get('year', '2024')}. {r.get('title', clean_topic)}."
            final_refs.append(cit)
    if not final_refs:
        final_refs = [
            f"Goodfellow, I., Bengio, Y. & Courville, A., 2016. Deep Learning. MIT Press.",
            f"Russell, S. & Norvig, P., 2020. Artificial Intelligence: A Modern Approach. 4th ed. Pearson."
        ]

    return {
        "metadata": mhs_meta,
        "sections": {
            "latar_belakang": lb_paragraphs,
            "landasan_kepustakaan": landasan_paragraphs,
            "rumusan_masalah": rm_list,
            "metode": metode_paragraphs,
            "daftar_pustaka": final_refs
        }
    }

def generate_topic_from_artefact(
    artefact_content: str,
    artefact_type: str = "general_text",
    artefact_title: Optional[str] = None,
    bidang_kajian: Optional[str] = None,
    proposed_method_or_x: Optional[str] = None,
    target_metric_or_y: Optional[str] = None,
    institutional_focus: Optional[str] = None
) -> Dict[str, Any]:
    """
    Menghasilkan usulan topik penelitian ilmiah yang terstruktur, lengkap dengan Judul,
    Urgensi Penelitian, Rumusan Masalah Tunggal Terukur, Variabel X & Y, Tujuan, Manfaat,
    serta Audit Kepatuhan Research Design Canvas (v2.0) secara otomatis berbasis artefak dunia nyata
    (artikel berita, dokumen masalah, rekaman kasus, deskripsi citra/OCR, dsb.).
    """
    content_raw = artefact_content.strip()
    if not content_raw:
        content_raw = "Tantangan optimasi performa dan efisiensi sistem komputasi cerdas."

    # 1. Identifikasi Bidang Kajian
    content_lower = content_raw.lower()
    title_lower = (artefact_title or "").lower()
    combined_text = f"{title_lower} {content_lower}"

    detected_domain = bidang_kajian
    if not detected_domain:
        if any(k in combined_text for k in ["keamanan", "cyber", "serangan", "malware", "ddos", "enkripsi", "intrusi", "firewall"]):
            detected_domain = "Keamanan Siber & Jaringan Komputer"
        elif any(k in combined_text for k in ["citra", "gambar", "kamera", "vision", "segmentasi", "yolo", "deteksi objek", "wajah"]):
            detected_domain = "Computer Vision & Pengolahan Citra Digital"
        elif any(k in combined_text for k in ["teks", "bahasa", "nlp", "sentimen", "chat", "terjemahan", "llm", "bert"]):
            detected_domain = "Natural Language Processing & Kecerdasan Artifisial"
        elif any(k in combined_text for k in ["sensor", "iot", "energi", "baterai", "node", "wsn", "mikrokontroler", "esp32"]):
            detected_domain = "Internet of Things & Jaringan Sensor Nirkabel"
        elif any(k in combined_text for k in ["kesehatan", "medis", "pasien", "penyakit", "diagnosis", "rekam medis", "dokter"]):
            detected_domain = "Informatika Medis & Health Data Science"
        elif any(k in combined_text for k in ["pertanian", "tanaman", "hama", "irigasi", "panen", "tanah", "pupuk"]):
            detected_domain = "Smart Agriculture & Agroteknologi Cerdas"
        elif any(k in combined_text for k in ["sistem informasi", "web", "aplikasi", "erp", "user experience", "ux", "bisnis"]):
            detected_domain = "Rekayasa Perangkat Lunak & Sistem Informasi"
        else:
            detected_domain = "Teknologi Informasi & Komputasi Cerdas"

    # 2. Identifikasi / Sintesis Variabel Independen (X - Metode/Algoritma/Intervensi)
    var_x = proposed_method_or_x
    if not var_x:
        # Cari metode spesifik yang disebutkan di teks
        method_candidates = []
        if "federated learning" in combined_text:
            method_candidates.append("Algoritma Federated Learning Terdistribusi")
        if "yolo" in combined_text or "yolov8" in combined_text:
            method_candidates.append("Arsitektur Deep Learning YOLOv8")
        if "reinforcement learning" in combined_text or "q-learning" in combined_text:
            method_candidates.append("Mekanisme Adaptive Q-Learning Routing")
        if "transformer" in combined_text or "attention" in combined_text:
            method_candidates.append("Model Transformer Berbasis Self-Attention Mechanism")
        if "lstm" in combined_text or "gru" in combined_text:
            method_candidates.append("Arsitektur Recurrent Neural Network (Bi-LSTM)")
        if "cnn" in combined_text or "convolutional" in combined_text:
            method_candidates.append("Deep Convolutional Neural Network (CNN)")
        if "genetic algorithm" in combined_text or "genetika" in combined_text:
            method_candidates.append("Algoritma Optimasi Genetika (Genetic Algorithm)")
        if "random forest" in combined_text or "ensemble" in combined_text:
            method_candidates.append("Ensemble Learning Random Forest & Gradient Boosting")
        if "blockchain" in combined_text:
            method_candidates.append("Protokol Konsensus Smart Contract Blockchain")

        if method_candidates:
            var_x = method_candidates[0]
        else:
            # Sintesis metode canggih sesuai domain
            if "Vision" in detected_domain:
                var_x = "Model Multi-Scale Deep Convolutional Neural Network"
            elif "Natural Language" in detected_domain:
                var_x = "Arsitektur Transformer Berbasis Contextual Embedding"
            elif "IoT" in detected_domain or "Sensor" in detected_domain:
                var_x = "Algoritma Adaptive Clustering & Energy-Efficient Routing"
            elif "Keamanan" in detected_domain:
                var_x = "Model Hybrid Deep Learning & Anomaly Detection Engine"
            elif "Medis" in detected_domain:
                var_x = "Deep Learning ResNet Berbasis Attention Transfer"
            elif "Agriculture" in detected_domain:
                var_x = "Algoritma Computer Vision Berbasis Lightweight CNN"
            else:
                var_x = "Pendekatan Machine Learning Berbasis Ensemble Optimization"

    # 3. Identifikasi / Sintesis Variabel Dependen (Y - Metrik Kinerja / Masalah Sasaran)
    var_y = target_metric_or_y
    if not var_y:
        metric_candidates = []
        if any(k in combined_text for k in ["akurasi", "ketepatan", "presisi", "f1-score"]):
            metric_candidates.append("Akurasi Deteksi dan Tingkat Presisi Klasifikasi")
        if any(k in combined_text for k in ["energi", "baterai", "daya", "konsumsi"]):
            metric_candidates.append("Efisiensi Konsumsi Energi dan Network Lifetime")
        if any(k in combined_text for k in ["latensi", "latency", "waktu tanggap", "kecepatan", "delay"]):
            metric_candidates.append("Latensi Pemrosesan dan Throughput Komputasi")
        if any(k in combined_text for k in ["intrusi", "kebocoran", "anomali", "serangan"]):
            metric_candidates.append("Sensitivitas Deteksi Anomali dan False Positive Rate")
        if any(k in combined_text for k in ["segmentasi", "lokalisasi", "iou"]):
            metric_candidates.append("Mean Average Precision (mAP) dan Skor IoU")

        if metric_candidates:
            var_y = metric_candidates[0]
        else:
            if "Vision" in detected_domain:
                var_y = "Mean Average Precision (mAP) dan Kecepatan Inferensi Real-Time"
            elif "Natural Language" in detected_domain:
                var_y = "Akurasi Klasifikasi Semantik dan F1-Score"
            elif "IoT" in detected_domain:
                var_y = "Masa Hidup Jaringan (Network Lifetime) dan Packet Delivery Ratio"
            elif "Keamanan" in detected_domain:
                var_y = "Tingkat Akurasi Deteksi Ancaman dan Minimasi False Alarm Rate"
            elif "Medis" in detected_domain:
                var_y = "Sensitivitas Diagnostik dan Spesifisitas Klasifikasi Medis"
            elif "Agriculture" in detected_domain:
                var_y = "Akurasi Identifikasi Penyakit dan Waktu Pemrosesan"
            else:
                var_y = "Efektivitas Kinerja Sistem dan Akurasi Prediksi Kuantitatif"

    # 4. Konteks Lingkup / Studi Kasus
    context_scope = institutional_focus
    if not context_scope:
        if artefact_title:
            context_scope = artefact_title.strip()
        else:
            first_sentence = content_raw.split(".")[0].strip()
            if len(first_sentence) > 15 and len(first_sentence) < 80:
                context_scope = first_sentence
            else:
                context_scope = f"Studi Kasus Lingkungan {detected_domain}"

    # 5. Sintesis Urgensi Penelitian (Latar Belakang Masalah Faktual, Urgensi Teknis, Dampak)
    clean_snippet = content_raw[:350].strip()
    if not clean_snippet.endswith("."):
        clean_snippet += "..."

    urgensi_fenomena = (
        f"Berdasarkan fenomena empiris pada artefak sumber ({artefact_type}): {clean_snippet} "
        f"Kondisi ini memperlihatkan adanya kesenjangan nyata antara target keandalan yang diharapkan pada "
        f"{var_y} dengan kenyataan operasional di lapangan saat ini."
    )

    urgensi_teknis = (
        f"Pendekatan konvensional atau metode statis baseline yang selama ini diterapkan menghadapi keterbatasan "
        f"dalam menangani kompleksitas data, variabilitas kondisi operasional, serta kebutuhan adaptabilitas tinggi. "
        f"Oleh karena itu, diperlukan intervensi teknologi mutakhir melalui {var_x} yang memiliki kapasitas adaptif "
        f"untuk mengatasi bottleneck teknis tersebut secara terukur."
    )

    urgensi_dampak = (
        f"Apabila permasalahan pada {var_y} ini tidak segera diintervensi dengan solusi komputasi cerdas, "
        f"maka akan timbul degradasi performa sistem yang berkepanjangan, peningkatan risiko kerugian operasional, "
        f"serta ketidakefisienan alokasi sumber daya."
    )

    # 6. Formulasi Judul Formal Akademik
    # Standar Judul: Jelas, memuat X dan Y, tanpa singkatan ambigu
    judul_utama = f"OPTIMASI {var_y.upper()} MENGGUNAKAN {var_x.upper()} PADA {context_scope.upper()}"
    judul_alt_1 = f"PENERAPAN {var_x.title()} UNTUK PENINGKATAN {var_y.title()} PADA {context_scope.title()}"
    judul_alt_2 = f"ANALISIS KOMPARATIF PERFORMA DAN IMPLEMENTASI {var_x.title()} TERHADAP {var_y.title()}"
    
    # Title English
    title_en = f"{var_x} for Enhancing {var_y} in {context_scope}"

    # 7. Formulasi Rumusan Masalah Tunggal Terukur (Sesuai Kepatuhan Canvas CLB04-01 & CLB04-02)
    rumusan_masalah = (
        f"Sejauh manakah implementasi {var_x} mampu meningkatkan performa {var_y} "
        f"secara signifikan dan terukur dibandingkan dengan metode baseline konvensional pada {context_scope}?"
    )

    # 8. Tujuan Penelitian (Umum & Khusus 4 Tahap)
    tujuan_umum = (
        f"menganalisis, merancang, mengimplementasikan, dan menguji efektivitas {var_x} "
        f"dalam mengoptimalkan {var_y} pada {context_scope}."
    )
    tujuan_khusus = [
        f"Mengidentifikasi kendala utama, karakteristik data, dan baseline performa awal pada {var_y}.",
        f"Merancang dan memodelkan arsitektur serta mekanisme kerja {var_x}.",
        f"Mengimplementasikan model {var_x} ke dalam lingkungan pengujian yang representatif.",
        f"Mengevaluasi dan membandingkan performa {var_y} menggunakan metrik kuantitatif terstandar terhadap metode acuan."
    ]

    # 9. Manfaat Penelitian (Praktis & Akademis, Bebas Klise Sesuai CLB06-01 & CLB06-02)
    manfaat_praktis = (
        f"Memberikan solusi teknologi terukur dan pedoman teknis siap terap bagi praktisi serta pengembang sistem "
        f"dalam mengatasi kendala {var_y} melalui pemanfaatan {var_x}."
    )
    manfaat_akademis = (
        f"Memberikan kontribusi empiris terhadap khazanah literatur ilmiah di bidang {detected_domain} "
        f"mengenai efektivitas dan batas kapabilitas {var_x} terhadap optimalisasi {var_y}."
    )

    # 10. Batasan Masalah
    batasan_masalah = [
        f"Penelitian difokuskan pada implementasi dan pengujian {var_x} pada skenario {context_scope}.",
        f"Evaluasi keberhasilan dibatasi pada pengukuran parameter kuantitatif {var_y}.",
        f"Data pengujian dan benchmark disesuaikan dengan karakteristik permasalahan pada artefak sumber.",
        f"Aspek komputasi diuji pada lingkungan komputasi terstandar dengan parameter yang telah ditentukan."
    ]

    # 11. Audit Kepatuhan Research Design Canvas (v2.0)
    canvas_audit = check_research_canvas(
        rumusan_masalah=rumusan_masalah,
        variabel_independen=var_x,
        variabel_dependen=var_y,
        tujuan_penelitian=tujuan_umum,
        manfaat_penelitian=f"{manfaat_praktis}; {manfaat_akademis}",
        single_problem_only=True
    )

    # 12. Kueri Pencarian Literatur untuk paper-search MCP
    q_base = f"{var_x} {var_y}"
    queries = {
        "search_papers": q_base,
        "arxiv": f"{var_x} AND {var_y}",
        "google_scholar": f'"{var_x}" "{var_y}"',
        "semantic_scholar": f"{var_x} {var_y} benchmark performance",
        "crossref": q_base
    }

    return {
        "status": "SUCCESS",
        "artefact_summary": {
            "type": artefact_type,
            "title": artefact_title or "(Tanpa Judul)",
            "domain": detected_domain,
            "context_scope": context_scope
        },
        "judul_usulan": {
            "judul_utama": judul_utama,
            "judul_alternatif_1": judul_alt_1,
            "judul_alternatif_2": judul_alt_2,
            "title_english": title_en
        },
        "urgensi_penelitian": {
            "latar_belakang_fenomena": urgensi_fenomena,
            "urgensi_teknis_dan_teoritis": urgensi_teknis,
            "dampak_jika_tidak_diselesaikan": urgensi_dampak
        },
        "rumusan_masalah": rumusan_masalah,
        "variabel_penelitian": {
            "variabel_independen_x": var_x,
            "variabel_dependen_y": var_y,
            "konteks_lingkup": context_scope
        },
        "tujuan_penelitian": {
            "tujuan_umum": tujuan_umum,
            "tujuan_khusus": tujuan_khusus
        },
        "manfaat_penelitian": {
            "manfaat_praktis": manfaat_praktis,
            "manfaat_akademis": manfaat_akademis
        },
        "batasan_masalah": batasan_masalah,
        "canvas_compliance_audit": canvas_audit,
        "search_queries_for_paper_search": queries,
        "recommended_next_steps": [
            "1. Lakukan verifikasi dan konfirmasi data diri mahasiswa/dosen pembimbing.",
            "2. Gunakan query pencarian di atas pada MCP paper-search untuk mengumpulkan literatur acuan terkini.",
            "3. Panggil generate_praproposal_from_topic untuk menyusun formulir Pra-Proposal SA2-01A (.odt), atau generate_proposal_from_topic untuk naskah proposal 3 Bab (.docx)."
        ]
    }


