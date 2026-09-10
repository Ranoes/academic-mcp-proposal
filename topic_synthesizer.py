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
            "2. Jalankan paper-search MCP (search_papers, search_arxiv, search_semantic) menggunakan kueri di atas.",
            "3. Jika terdapat file CSV tinjauan pustaka di workspace, baca menggunakan parse_literature_csv_data.",
            "4. Panggil generate_praproposal_from_topic atau generate_proposal_from_topic dengan menyertakan student_metadata yang telah dikonfirmasi.",
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
        "tipe_penelitian": metadata.get("tipe_penelitian", "Pengembangan Sistem & Komparasi Algoritma"),
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

