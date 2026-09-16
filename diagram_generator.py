"""
diagram_generator.py
Modul untuk merender gambar diagram ilmiah (Alur Penelitian, Hubungan Variabel X & Y, Arsitektur Sistem)
dan menyimpannya ke direktori /asset dalam workspace, serta menyisipkannya ke dokumen proposal.
"""
import os
import re
from typing import Dict, Any, List, Optional, Union
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server/CLI
import matplotlib.pyplot as plt
import matplotlib.patches as patches

DEFAULT_ASSET_DIR = "asset"

def ensure_asset_dir(workspace_dir: str, asset_folder: str = DEFAULT_ASSET_DIR) -> str:
    """
    Memastikan direktori asset di dalam workspace dibuat jika belum ada.
    """
    target_path = os.path.join(workspace_dir, asset_folder)
    os.makedirs(target_path, exist_ok=True)
    return target_path

def generate_flowchart_diagram(
    title: str,
    steps: List[Union[str, Dict[str, Any]]],
    output_path: str,
    dpi: int = 300
) -> str:
    """
    Menghasilkan diagram alur penelitian (flowchart) bertingkat secara vertikal
    dengan tata letak akademik yang rapi dan elegan.
    """
    num_steps = len(steps)
    if num_steps == 0:
        steps = [
            {"label": "Tahap 1", "desc": "Identifikasi Masalah & Studi Literatur"},
            {"label": "Tahap 2", "desc": "Pengumpulan & Pra-pemrosesan Data"},
            {"label": "Tahap 3", "desc": "Perancangan & Pemodelan Sistem"},
            {"label": "Tahap 4", "desc": "Implementasi & Pengujian Eksperimental"},
            {"label": "Tahap 5", "desc": "Evaluasi Metrik & Penarikan Kesimpulan"}
        ]
        num_steps = len(steps)

    # Format steps agar konsisten menjadi list dict
    clean_steps = []
    for idx, s in enumerate(steps, 1):
        if isinstance(s, dict):
            label = s.get("label", f"Tahap {idx}")
            desc = s.get("desc") or s.get("title") or s.get("text") or str(s)
        else:
            txt = str(s).strip()
            if ":" in txt:
                parts = txt.split(":", 1)
                label = parts[0].strip()
                desc = parts[1].strip()
            else:
                label = f"Tahap {idx}"
                desc = txt
        clean_steps.append({"label": label, "desc": desc})

    fig_height = max(5.0, num_steps * 1.5 + 1.2)
    fig_width = 8.0
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, num_steps * 2 + 2)
    ax.axis('off')

    # Judul Diagram
    ax.text(
        5, num_steps * 2 + 1.2, title.upper(),
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#0F172A', family='sans-serif'
    )

    box_width = 7.0
    box_height = 1.1
    center_x = 5.0

    colors = [
        {"bg": "#1E3A8A", "border": "#172554", "txt_title": "#FFFFFF", "txt_desc": "#E0E7FF"},
        {"bg": "#0D9488", "border": "#115E59", "txt_title": "#FFFFFF", "txt_desc": "#CCFBF1"},
        {"bg": "#2563EB", "border": "#1D4ED8", "txt_title": "#FFFFFF", "txt_desc": "#DBEAFE"},
        {"bg": "#4F46E5", "border": "#3730A3", "txt_title": "#FFFFFF", "txt_desc": "#EEF2FF"},
        {"bg": "#0284C7", "border": "#0369A1", "txt_title": "#FFFFFF", "txt_desc": "#E0F2FE"},
        {"bg": "#059669", "border": "#047857", "txt_title": "#FFFFFF", "txt_desc": "#D1FAE5"}
    ]

    for idx, step in enumerate(clean_steps):
        y_pos = (num_steps - idx) * 2 - 0.2
        col = colors[idx % len(colors)]

        # Gambar Kotak Tahapan (Rounded Box)
        rect = patches.FancyBboxPatch(
            (center_x - box_width / 2, y_pos - box_height / 2),
            box_width, box_height,
            boxstyle="round,pad=0.15,rounding_size=0.15",
            facecolor=col["bg"],
            edgecolor=col["border"],
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(rect)

        # Header Tahap
        ax.text(
            center_x, y_pos + 0.22, step["label"].upper(),
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=col["txt_title"], family='sans-serif', zorder=3
        )

        # Deskripsi Tahap
        wrapped_desc = step["desc"]
        if len(wrapped_desc) > 65:
            words = wrapped_desc.split()
            mid = len(words) // 2
            wrapped_desc = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

        ax.text(
            center_x, y_pos - 0.18, wrapped_desc,
            ha='center', va='center', fontsize=8.5,
            color=col["txt_desc"], family='sans-serif', zorder=3
        )

        # Panah Penghubung ke tahapan berikutnya
        if idx < num_steps - 1:
            next_y = (num_steps - (idx + 1)) * 2 - 0.2
            arrow_start_y = y_pos - box_height / 2 - 0.05
            arrow_end_y = next_y + box_height / 2 + 0.05
            ax.annotate(
                '',
                xy=(center_x, arrow_end_y),
                xytext=(center_x, arrow_start_y),
                arrowprops=dict(
                    arrowstyle="->,head_width=0.35,head_length=0.4",
                    color="#475569",
                    lw=2.0,
                    mutation_scale=15
                ),
                zorder=1
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return output_path

def generate_conceptual_framework_diagram(
    title: str,
    variabel_x: str,
    variabel_y: str,
    output_path: str,
    proses_or_treatment: Optional[str] = None,
    dpi: int = 300
) -> str:
    """
    Menghasilkan diagram Kerangka Konseptual / Hubungan Kausal Variabel X dan Y.
    """
    fig, ax = plt.subplots(figsize=(9.0, 4.5), dpi=dpi)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Judul Diagram
    ax.text(
        6, 5.3, title.upper(),
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#0F172A', family='sans-serif'
    )

    box_w = 3.2
    box_h = 2.2

    # Kotak Variabel X (Independen)
    rect_x = patches.FancyBboxPatch(
        (0.8, 1.4), box_w, box_h,
        boxstyle="round,pad=0.15,rounding_size=0.15",
        facecolor="#1E3A8A", edgecolor="#172554", linewidth=1.5, zorder=2
    )
    ax.add_patch(rect_x)

    ax.text(
        2.4, 3.1, "VARIABEL BEBAS (X)",
        ha='center', va='center', fontsize=9.5, fontweight='bold',
        color="#93C5FD", family='sans-serif', zorder=3
    )
    # Wrap teks variabel X
    vx_wrap = variabel_x
    if len(vx_wrap) > 30:
        words = vx_wrap.split()
        mid = len(words) // 2
        vx_wrap = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
    ax.text(
        2.4, 2.1, vx_wrap,
        ha='center', va='center', fontsize=9, fontweight='bold',
        color="#FFFFFF", family='sans-serif', zorder=3
    )

    # Kotak Variabel Y (Dependen)
    rect_y = patches.FancyBboxPatch(
        (8.0, 1.4), box_w, box_h,
        boxstyle="round,pad=0.15,rounding_size=0.15",
        facecolor="#047857", edgecolor="#065F46", linewidth=1.5, zorder=2
    )
    ax.add_patch(rect_y)

    ax.text(
        9.6, 3.1, "VARIABEL TERIKAT (Y)",
        ha='center', va='center', fontsize=9.5, fontweight='bold',
        color="#A7F3D0", family='sans-serif', zorder=3
    )
    # Wrap teks variabel Y
    vy_wrap = variabel_y
    if len(vy_wrap) > 30:
        words = vy_wrap.split()
        mid = len(words) // 2
        vy_wrap = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
    ax.text(
        9.6, 2.1, vy_wrap,
        ha='center', va='center', fontsize=9, fontweight='bold',
        color="#FFFFFF", family='sans-serif', zorder=3
    )

    # Kotak Proses / Intervensi di Tengah
    treatment_text = proses_or_treatment or "Pengujian Eksperimental &\nSimulasi Kuantitatif"
    rect_mid = patches.FancyBboxPatch(
        (4.4, 1.8), 3.2, 1.4,
        boxstyle="round,pad=0.1,rounding_size=0.1",
        facecolor="#F1F5F9", edgecolor="#64748B", linewidth=1.2, linestyle="--", zorder=2
    )
    ax.add_patch(rect_mid)
    ax.text(
        6.0, 2.5, treatment_text,
        ha='center', va='center', fontsize=8,
        color="#334155", family='sans-serif', zorder=3
    )

    # Panah X -> Mid -> Y
    ax.annotate(
        '', xy=(4.3, 2.5), xytext=(4.0, 2.5),
        arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.35", color="#1E293B", lw=2),
        zorder=1
    )
    ax.annotate(
        '', xy=(7.9, 2.5), xytext=(7.6, 2.5),
        arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.35", color="#1E293B", lw=2),
        zorder=1
    )

    # Label Pengaruh / Hubungan Kausal
    ax.text(
        6.0, 3.7, "Pengaruh Kausal / Efektivitas",
        ha='center', va='center', fontsize=8.5, fontstyle='italic',
        color="#475569", family='sans-serif'
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return output_path

def generate_system_architecture_diagram(
    title: str,
    layers: List[Dict[str, Any]],
    output_path: str,
    dpi: int = 300
) -> str:
    """
    Menghasilkan diagram arsitektur sistem modular berlapis (Layered Architecture).
    """
    if not layers:
        layers = [
            {"name": "Data Ingestion & Preprocessing Layer", "items": ["Dataset Input", "Data Cleaning", "Feature Normalization"]},
            {"name": "Core Processing & Algorithm Layer", "items": ["State Modeling", "Reinforcement Learning Engine", "Routing Policy Optimization"]},
            {"name": "Evaluation & Analytics Layer", "items": ["Performance Metrics Log", "Comparative Baseline", "Result Visualization"]}
        ]

    num_layers = len(layers)
    fig, ax = plt.subplots(figsize=(8.5, max(4.5, num_layers * 1.8 + 1.2)), dpi=dpi)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, num_layers * 2.2 + 1.5)
    ax.axis('off')

    ax.text(
        5, num_layers * 2.2 + 0.8, title.upper(),
        ha='center', va='center', fontsize=12, fontweight='bold',
        color='#0F172A', family='sans-serif'
    )

    box_width = 8.0
    box_height = 1.4
    center_x = 5.0

    colors = ["#1E3A8A", "#0D9488", "#4F46E5", "#0284C7"]

    for idx, layer in enumerate(layers):
        y_pos = (num_layers - idx) * 2.2 - 0.8
        col = colors[idx % len(colors)]

        # Layer container box
        rect = patches.FancyBboxPatch(
            (center_x - box_width / 2, y_pos - box_height / 2),
            box_width, box_height,
            boxstyle="round,pad=0.1,rounding_size=0.1",
            facecolor="#F8FAFC", edgecolor=col, linewidth=1.5, zorder=2
        )
        ax.add_patch(rect)

        # Layer Header Banner
        header_rect = patches.FancyBboxPatch(
            (center_x - box_width / 2, y_pos + box_height / 2 - 0.35),
            box_width, 0.35,
            boxstyle="square,pad=0",
            facecolor=col, edgecolor=col, zorder=3
        )
        ax.add_patch(header_rect)

        ax.text(
            center_x, y_pos + box_height / 2 - 0.18, layer.get("name", f"Layer {idx+1}").upper(),
            ha='center', va='center', fontsize=9, fontweight='bold',
            color="#FFFFFF", family='sans-serif', zorder=4
        )

        # Items inside layer
        items = layer.get("items", [])
        if items:
            item_count = len(items)
            item_w = (box_width - 0.4 * (item_count + 1)) / max(1, item_count)
            start_x = (center_x - box_width / 2) + 0.4
            for i_idx, item_name in enumerate(items):
                item_x = start_x + i_idx * (item_w + 0.3)
                item_rect = patches.FancyBboxPatch(
                    (item_x, y_pos - box_height / 2 + 0.15),
                    item_w, 0.65,
                    boxstyle="round,pad=0.05,rounding_size=0.08",
                    facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=1, zorder=3
                )
                ax.add_patch(item_rect)
                ax.text(
                    item_x + item_w / 2, y_pos - box_height / 2 + 0.48, str(item_name),
                    ha='center', va='center', fontsize=7.5,
                    color="#1E293B", family='sans-serif', zorder=4
                )

        if idx < num_layers - 1:
            next_y = (num_layers - (idx + 1)) * 2.2 - 0.8
            ax.annotate(
                '', xy=(center_x, next_y + box_height / 2 + 0.05),
                xytext=(center_x, y_pos - box_height / 2 - 0.05),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.35", color="#64748B", lw=1.8),
                zorder=1
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return output_path

def generate_diagram(
    diagram_type: str = "flowchart",
    title: str = "Diagram Alur Penelitian",
    steps_or_nodes: Optional[List[Union[str, Dict[str, Any]]]] = None,
    variabel_x: Optional[str] = None,
    variabel_y: Optional[str] = None,
    layers: Optional[List[Dict[str, Any]]] = None,
    workspace_dir: str = ".",
    asset_folder: str = DEFAULT_ASSET_DIR,
    output_filename: Optional[str] = None,
    dpi: int = 300
) -> Dict[str, Any]:
    """
    Fungsi utama untuk membuat diagram, memastikan direktori asset dibuat,
    dan menyimpan gambar PNG.
    """
    asset_dir = ensure_asset_dir(workspace_dir=workspace_dir, asset_folder=asset_folder)

    d_type = diagram_type.strip().lower()
    if not output_filename:
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title.lower())[:30]
        output_filename = f"{d_type}_{safe_title}.png"

    output_path = os.path.join(asset_dir, output_filename)

    if "var" in d_type or "framework" in d_type or "konseptual" in d_type:
        vx = variabel_x or "Variabel Independen (X)"
        vy = variabel_y or "Variabel Dependen (Y)"
        saved_file = generate_conceptual_framework_diagram(
            title=title,
            variabel_x=vx,
            variabel_y=vy,
            output_path=output_path,
            dpi=dpi
        )
    elif "arch" in d_type or "arsitektur" in d_type or "layer" in d_type:
        saved_file = generate_system_architecture_diagram(
            title=title,
            layers=layers or [],
            output_path=output_path,
            dpi=dpi
        )
    else:
        # Default: Flowchart / Alur Penelitian
        saved_file = generate_flowchart_diagram(
            title=title,
            steps=steps_or_nodes or [],
            output_path=output_path,
            dpi=dpi
        )

    relative_path = os.path.join(asset_folder, output_filename).replace("\\", "/")

    return {
        "status": "SUCCESS",
        "diagram_type": d_type,
        "title": title,
        "filename": output_filename,
        "asset_folder": asset_folder,
        "relative_path": relative_path,
        "full_path": os.path.abspath(saved_file),
        "file_size_bytes": os.path.getsize(saved_file)
    }
