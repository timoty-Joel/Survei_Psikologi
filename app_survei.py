import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from scoring_map import (
    BIDANG_OPTIONS,
    SURVEY_QUESTIONS,
    CATEGORY_METADATA,
    DIMENSION_COLUMNS,
    SUBDIMENSIONS_BY_CATEGORY,
    SUBDIMENSION_COLUMNS,
    get_question_options,
    calculate_score,
    calculate_category_scores,
    calculate_subdimension_scores,
    SEGMEN2_OPTIONS,
    SCORING_MAP_SEGMEN2,
    SURVEY_QUESTIONS_SEGMEN2,
    CATEGORY_METADATA_SEGMEN2,
    DIMENSION_COLUMNS_SEGMEN2,
    calculate_score_segmen2,
    calculate_segmen2_scores,
    get_dass_severity,
    SUBDIMENSION_POLARITY,
    get_score_level,
    get_subdimension_status,
    SUBDIMENSION_LABELS
)

from data_manager import (
    load_data,
    save_survey_response,
    is_gsheets_configured,
    convert_df_to_excel,
    LOCAL_DATA_FILE
)

# =====================================================================
# 1. KONFIGURASI HALAMAN & TEMA CSS
# =====================================================================
st.set_page_config(
    page_title="Survei Psikologi Kerja",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan modern, elegan, dan profesional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Card */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0d9488 100%);
        color: white;
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
    }
    .hero-banner h1 {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .hero-banner p {
        color: #cbd5e1;
        font-size: 14px;
        margin: 0;
    }

    /* Metric Card Modern */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Hook Cards & Executive Summary */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 14px !important;
        background: #ffffff !important;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover > div {
        border-color: #3b82f6 !important;
        box-shadow: 0 10px 22px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-2px) !important;
    }

    .hook-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
        margin-bottom: 8px;
        min-height: 215px;
        transition: all 0.25s ease;
    }
    .hook-container:hover {
        border-color: #3b82f6;
        box-shadow: 0 10px 22px rgba(59, 130, 246, 0.1);
        transform: translateY(-2px);
    }
    .hook-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .hook-tag-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .hook-tag-green { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .hook-tag-red { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .hook-tag-yellow { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
    .hook-tag-purple { background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; }

    .hook-val {
        font-size: 25px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.15;
        margin-bottom: 4px;
    }
    .hook-title {
        font-size: 14px;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .hook-text {
        font-size: 12px;
        color: #64748b;
        line-height: 1.45;
        margin-bottom: 4px;
    }

    /* Question Card - Default / Belum Dijawab */
    .question-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-left: 5px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        transition: all 0.25s ease-in-out;
    }
    
    /* Question Card - Sudah Dijawab (Highlight Biru Terang) */
    .question-card.answered {
        background: #f0f7ff;
        background: linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%);
        border: 1.5px solid #93c5fd;
        border-left: 5px solid #2563eb;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.09);
    }

    .question-text {
        font-size: 14.5px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 6px;
        line-height: 1.5;
    }

    .question-id-badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }

    .question-card.answered .question-id-badge {
        background: #2563eb;
        color: #ffffff;
    }

    .status-badge-unanswered {
        display: inline-block;
        background: #f8fafc;
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    .status-badge-answered {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 12px;
        border: 1px solid #bfdbfe;
    }

    /* Step Badge */
    .step-pill {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        color: #334155;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .step-pill.active {
        background: #2563eb;
        color: #ffffff;
        border-color: #2563eb;
    }

    /* Status Badges */
    .badge-success {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-warning {
        background-color: #fef3c7;
        color: #b45309;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. KONFIGURASI KODE AKSES ADMIN & SESSION STATE
# =====================================================================
DEFAULT_ADMIN_CODE = "ADMIN2026"
try:
    ADMIN_ACCESS_CODE = str(st.secrets.get("ADMIN_CODE", DEFAULT_ADMIN_CODE)).strip()
except Exception:
    ADMIN_ACCESS_CODE = DEFAULT_ADMIN_CODE

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "active_menu" not in st.session_state:
    st.session_state["active_menu"] = "📝 Form Survei"

# Dukungan akses langsung via query parameter (?code=... atau ?admin=...)
try:
    qp = st.query_params
    url_code = qp.get("code") or qp.get("admin")
    if url_code and str(url_code).strip() == ADMIN_ACCESS_CODE:
        st.session_state["is_admin"] = True
except Exception:
    pass

if "consent_given" not in st.session_state:
    st.session_state["consent_given"] = False

if "step" not in st.session_state:
    st.session_state["step"] = 0

if "biodata" not in st.session_state:
    st.session_state["biodata"] = {
        "bidang": "",
        "nama": "",
        "gender": "",
        "usia": "",
        "masa_kerja": "",
        "jabatan": "",
        "riwayat_penyakit": "",
        "nama_penyakit": "-",
        "berat_badan": None,
        "tinggi_badan": None,
        "status_perkawinan": ""
    }

if "answers" not in st.session_state:
    st.session_state["answers"] = {}

if "answers_segmen2" not in st.session_state:
    st.session_state["answers_segmen2"] = {}

if "submission_result" not in st.session_state:
    st.session_state["submission_result"] = None

# =====================================================================
# 3. SIDEBAR NAVIGATION & KONTROL AKSES
# =====================================================================
with st.sidebar:
    st.markdown("### 🧠 Psikologi Kerja")
    st.markdown("<p style='font-size:12px; color:#64748b; margin-top:-10px;'>Sistem Pemetaan Faktor Psikososial dan Stress Kerja</p>", unsafe_allow_html=True)
    st.divider()

    if st.session_state["is_admin"]:
        # --- TAMPILAN KHUSUS ADMIN ---
        st.markdown("<span class='badge-success' style='display:inline-block; margin-bottom:12px;'>👨‍💼 Mode Administrator</span>", unsafe_allow_html=True)
        
        admin_options = ["📊 Dashboard Hasil Survei", "📝 Form Survei", "⚙️ Konfigurasi Spreadsheet"]
        current_idx = admin_options.index(st.session_state["active_menu"]) if st.session_state["active_menu"] in admin_options else 0
        
        menu = st.radio(
            "Pilih Halaman:",
            options=admin_options,
            index=current_idx
        )
        st.session_state["active_menu"] = menu

        st.divider()
        
        # Status Penyimpanan (Hanya terlihat oleh Admin)
        gsheet_active = is_gsheets_configured()
        if gsheet_active:
            st.markdown("**Status Penyimpanan:**")
            st.markdown("<span class='badge-success'>🟢 Google Sheets Aktif</span>", unsafe_allow_html=True)
        else:
            st.markdown("**Status Penyimpanan:**")
            st.markdown("<span class='badge-warning'>🟡 File Lokal (data_survei.csv)</span>", unsafe_allow_html=True)
            st.caption("Google Sheets belum diatur di secrets.toml. Data tersimpan di file lokal.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout Admin", use_container_width=True):
            st.session_state["is_admin"] = False
            st.session_state["active_menu"] = "📝 Form Survei"
            st.rerun()

    else:
        # --- TAMPILAN UNTUK RESPONDEN BIASA ---
        menu = "📝 Form Survei"
        st.session_state["active_menu"] = "📝 Form Survei"

        st.markdown("""
        **📋 Informasi Pengisian:**
        - Jawab setiap butir pernyataan secara jujur sesuai pengalaman kerja Anda.
        - Identitas diri bersifat **rahasia / anonim**.
        - Estimasi waktu: **15 - 20 menit**.
        """)
        
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        st.divider()
        
        # Area Login Akses Admin
        with st.expander("🔐 Akses Admin (Dashboard)"):
            st.caption("Halaman dashboard dan konfigurasi dilindungi kode akses administrator.")
            sidebar_code = st.text_input("Kode Akses Admin:", type="password", key="sidebar_admin_code_input")
            if st.button("Buka Dashboard", use_container_width=True, type="primary"):
                if sidebar_code.strip() == ADMIN_ACCESS_CODE:
                    st.session_state["is_admin"] = True
                    st.session_state["active_menu"] = "📊 Dashboard Hasil Survei"
                    st.success("Kode benar! Membuka dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Kode akses salah.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.caption("Versi 1.1.0 | Standar Evaluasi K3 & Psikososial Kerja")

# =====================================================================
# KONSTANTA & HELPER VISUALISASI DASHBOARD
# =====================================================================
BIDANG_COLOR_MAP = {
    "Keselamatan Kerja": "#ef4444",
    "Kesehatan Kerja": "#10b981",
    "Ergonomi & Psikologi": "#3b82f6",
    "Psikologi": "#3b82f6",
    "Hiegene Industri dan Bahan Berbahaya": "#f59e0b",
    "Tata Usaha": "#8b5cf6"
}

def collect_subdimension_items_from_df(df_scope, selected_categories):
    """Mengumpulkan daftar skor dan kategori risiko sub-dimensi Segmen 1 dari dataframe."""
    chart_items = []
    tbl_rows = []
    idx = 0
    for cat_key in selected_categories:
        subs = SUBDIMENSIONS_BY_CATEGORY.get(cat_key, [])
        cat_short = CATEGORY_METADATA.get(cat_key, {}).get("short", cat_key)
        for s_name in subs:
            idx += 1
            col_s = SUBDIMENSION_COLUMNS.get(s_name)
            if col_s and col_s in df_scope.columns:
                s_series = pd.to_numeric(df_scope[col_s], errors="coerce").dropna()
                avg_val = round(s_series.mean(), 1) if not s_series.empty else 0.0
            else:
                avg_val = 0.0

            label_info = SUBDIMENSION_LABELS.get(s_name, {"en": s_name, "id": s_name})
            full_label = f"{label_info['en']} ({label_info['id']})"
            display_label = f"[{cat_short}] {full_label}" if len(selected_categories) > 1 else full_label
            level = get_score_level(avg_val)
            polarity = SUBDIMENSION_POLARITY.get(s_name, "Favorable")
            _, status_text, color = get_subdimension_status(s_name, avg_val)

            chart_items.append({
                "name": display_label,
                "raw_name": s_name,
                "score": avg_val,
                "level": level,
                "polarity": polarity,
                "status": status_text,
                "color": color
            })
            row_dict = {
                "No": idx,
                "Sub-Bidang": full_label,
                "Sifat": polarity,
                "Skor": avg_val,
                "Kategori": level,
                "Status Risiko": status_text
            }
            if len(selected_categories) > 1:
                row_dict = {"No": idx, "Dimensi": cat_short, **{k: v for k, v in row_dict.items() if k != "No"}}
            tbl_rows.append(row_dict)
    return chart_items, tbl_rows

def build_subdimension_hbar_chart(items, title_text, xaxis_title="Skor Rata-Rata Sub-Bidang (0 - 100)"):
    """
    Membangun barchart horizontal Plotly untuk sub-dimensi Segmen 1.
    - Favorable: Hijau dengan lowered opacity (rgba(34, 197, 94, 0.45))
    - Unfavorable: Merah dengan lowered opacity (rgba(239, 68, 68, 0.45))
    - Batas bar: Bold berwarna abu-abu gelap (#334155, width 2)
    - Garis batas kategori: Bold solid abu-abu gelap (#334155, width 2.5) pada 33.33 & 66.67
    """
    y_labels = [item["name"] for item in items]
    scores = [item["score"] for item in items]
    
    # Warna berdasarkan Favorable (Hijau) vs Unfavorable (Merah) dengan opacity diturunkan
    bar_colors = [
        "rgba(34, 197, 94, 0.45)" if item.get("polarity", "Favorable") == "Favorable" else "rgba(239, 68, 68, 0.45)"
        for item in items
    ]
    texts = [f" <b>{item['score']:.1f}</b> ({item['level']})" for item in items]
    customdata = [[item["level"], item["polarity"], item["status"]] for item in items]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_labels,
        x=scores,
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color="#334155", width=2)  # Batas bold abu-abu gelap
        ),
        text=texts,
        textposition="outside",
        cliponaxis=False,
        customdata=customdata,
        hovertemplate="<b>%{y}</b><br>Skor Rata-Rata: <b>%{x:.1f}</b> / 100<br>Sifat: <b>%{customdata[1]}</b><br>Kategori: <b>%{customdata[0]}</b><br>Status Risiko: %{customdata[2]}<extra></extra>"
    ))

    # Garis batas kategori bold berwarna abu-abu gelap (#334155)
    fig.add_vline(
        x=33.33, line_dash="solid", line_color="#334155", line_width=2.5,
        annotation_text="<b>Batas Rendah (33.33)</b>", annotation_position="top right",
        annotation_font=dict(size=10.5, color="#1e293b")
    )
    fig.add_vline(
        x=66.67, line_dash="solid", line_color="#334155", line_width=2.5,
        annotation_text="<b>Batas Tinggi (66.67)</b>", annotation_position="top right",
        annotation_font=dict(size=10.5, color="#1e293b")
    )

    row_height = 42 if len(y_labels) > 15 else 58
    fig.update_layout(
        title=dict(
            text=f"{title_text}<br><span style='font-size:12px;color:#475569;font-weight:normal;'>🟢 <b>Favorable</b> (Aspek Positif - Hijau) | 🔴 <b>Unfavorable</b> (Beban/Stres - Merah) | ➖ <b>Batas Kategori (33.33 & 66.67)</b>: Abu-Abu Gelap</span>",
            font=dict(size=14, color="#0f172a")
        ),
        xaxis=dict(
            range=[0, 115],
            title=xaxis_title,
            tickvals=[0, 20, 33.33, 50, 66.67, 80, 100],
            gridcolor="#f1f5f9"
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            tickfont=dict(size=12, color="#1e293b")
        ),
        height=max(360, len(y_labels) * row_height),
        margin=dict(l=20, r=40, t=75, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    return fig

# =====================================================================
# MODAL POP-UP DIALOGS UNTUK HALAMAN HOOK (@st.dialog)
# =====================================================================
categories_list = list(SURVEY_QUESTIONS.keys())

@st.dialog("📊 Analitik Detail: Dimensi Utama Tertinggi", width="large")
def dialog_top_dimension(dim_key, dim_score, df_scope):
    dim_meta = CATEGORY_METADATA.get(dim_key, {"label": dim_key, "icon": "📁", "desc": "", "short": dim_key})
    st.markdown(f"### {dim_meta.get('icon', '📁')} {dim_meta.get('label', dim_key)}")
    st.caption(dim_meta.get("desc", ""))
    
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Skor Rata-Rata", f"{dim_score:.1f} / 100")
    with col_d2:
        level = get_score_level(dim_score)
        st.metric("Kategori Level", level)
    with col_d3:
        st.metric("Basis Responden", f"{len(df_scope)} Orang")
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏢 Skor Rata-Rata Dimensi Ini Antar Bidang Kerja")
    col_name = DIMENSION_COLUMNS.get(dim_key)
    if col_name and col_name in df_scope.columns and "Bidang" in df_scope.columns:
        bidang_dim = df_scope.groupby("Bidang")[col_name].mean().reset_index()
        bidang_dim.columns = ["Bidang", "Skor"]
        bidang_dim["Skor"] = bidang_dim["Skor"].round(1)
        fig_b = px.bar(
            bidang_dim,
            x="Bidang",
            y="Skor",
            color="Bidang",
            color_discrete_map=BIDANG_COLOR_MAP,
            text="Skor"
        )
        fig_b.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
        fig_b.update_layout(yaxis=dict(range=[0, 115], title="Skor (0 - 100)", gridcolor="#f1f5f9"), height=300, showlegend=False, margin=dict(l=10, r=10, t=30, b=20))
        st.plotly_chart(fig_b, use_container_width=True)

    st.markdown("#### 🔬 Rincian Seluruh Sub-Dimensi di Dalam Dimensi Ini")
    subs = SUBDIMENSIONS_BY_CATEGORY.get(dim_key, [])
    if subs:
        sub_items, sub_tbl = collect_subdimension_items_from_df(df_scope, [dim_key])
        fig_subs = build_subdimension_hbar_chart(
            sub_items,
            title_text=f"Sub-Dimensi: {dim_meta.get('label', dim_key)}"
        )
        st.plotly_chart(fig_subs, use_container_width=True)
        st.dataframe(pd.DataFrame(sub_tbl), use_container_width=True, hide_index=True)

    st.markdown("""
    💡 **Rekomendasi Evaluasi K3**:
    - Dimensi ini memiliki rata-rata tertinggi di organisasi; perhatikan sub-dimensi mana yang paling dominan menggerakkan tingginya skor ini.
    - Lakukan penyesuaian berkala pada bidang dengan skor ekstrem agar distribusi beban dan dukungan tetap seimbang.
    """)

@st.dialog("🟢 Analitik Kekuatan Utama: Sub-Dimensi Favorable Tertinggi", width="large")
def dialog_top_favorable(sub_name, sub_score, df_scope):
    lbl = SUBDIMENSION_LABELS.get(sub_name, {"en": sub_name, "id": sub_name})
    st.markdown(f"### 🟢 {lbl['en']} ({lbl['id']})")
    st.caption("Sub-dimensi dengan sifat **Favorable (Aspek Positif / Pelindung)** tertinggi di lingkungan kerja.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.metric("Skor Rata-Rata Sub-Dimensi", f"{sub_score:.1f} / 100")
    with col_f2:
        st.metric("Status Evaluasi", "🟢 Kekuatan Utama (Risiko Rendah)")
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏢 Skor Sub-Dimensi Ini per Bidang Kerja")
    col_s = SUBDIMENSION_COLUMNS.get(sub_name)
    if col_s and col_s in df_scope.columns and "Bidang" in df_scope.columns:
        b_df = df_scope.groupby("Bidang")[col_s].mean().reset_index()
        b_df.columns = ["Bidang", "Skor"]
        b_df["Skor"] = b_df["Skor"].round(1)
        fig_b = px.bar(
            b_df, x="Bidang", y="Skor", color="Bidang", color_discrete_map=BIDANG_COLOR_MAP, text="Skor"
        )
        fig_b.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
        fig_b.update_layout(yaxis=dict(range=[0, 115], title="Skor (0 - 100)", gridcolor="#f1f5f9"), height=290, showlegend=False, margin=dict(l=10, r=10, t=30, b=20))
        st.plotly_chart(fig_b, use_container_width=True)
    
    # 5 Sub-dimensi Favorable tertinggi di organisasi
    st.markdown("#### 🏆 Top 5 Aspek Favorable (Kekuatan) Organisasi Lainnya")
    all_fav = {}
    for s, c in SUBDIMENSION_COLUMNS.items():
        if SUBDIMENSION_POLARITY.get(s) == "Favorable" and c in df_scope.columns:
            all_fav[s] = df_scope[c].mean()
    top5_fav = sorted(all_fav.items(), key=lambda x: x[1], reverse=True)[:5]
    top5_rows = []
    for rank, (s, sc) in enumerate(top5_fav, 1):
        slbl = SUBDIMENSION_LABELS.get(s, {"en": s, "id": s})
        top5_rows.append({"Peringkat": f"#{rank}", "Sub-Dimensi": f"{slbl['en']} ({slbl['id']})", "Skor": round(sc, 1), "Kategori": get_score_level(sc)})
    st.dataframe(pd.DataFrame(top5_rows), use_container_width=True, hide_index=True)

    st.markdown("""
    💡 **Rekomendasi Manajemen**:
    - Aspek ini menjadi modal sosial dan psikologis terbesar karyawan yang menjaga resiliensi kerja.
    - Pertahankan praktik positif, sistem apresiasi, dan komunikasi yang sudah berjalan baik pada aspek ini.
    """)

@st.dialog("🔴 Analitik Titik Kritis: Beban Kerja / Stressor Tertinggi", width="large")
def dialog_top_unfavorable(sub_name, sub_score, df_scope):
    lbl = SUBDIMENSION_LABELS.get(sub_name, {"en": sub_name, "id": sub_name})
    st.markdown(f"### 🔴 {lbl['en']} ({lbl['id']})")
    st.caption("Sub-dimensi dengan sifat **Unfavorable (Beban Kerja / Pemicu Stres)** dengan skor tertinggi yang perlu dimitigasi.")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.metric("Skor Rata-Rata Beban", f"{sub_score:.1f} / 100")
    with col_u2:
        st.metric("Tingkat Prioritas", "🔴 Prioritas Intervensi K3")
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏢 Bidang Kerja Paling Terbebani oleh Aspek Ini")
    col_s = SUBDIMENSION_COLUMNS.get(sub_name)
    if col_s and col_s in df_scope.columns and "Bidang" in df_scope.columns:
        b_df = df_scope.groupby("Bidang")[col_s].mean().reset_index().sort_values(by="Skor", ascending=False)
        b_df.columns = ["Bidang", "Skor"]
        b_df["Skor"] = b_df["Skor"].round(1)
        fig_b = px.bar(
            b_df, x="Bidang", y="Skor", color="Bidang", color_discrete_map=BIDANG_COLOR_MAP, text="Skor"
        )
        fig_b.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
        fig_b.update_layout(yaxis=dict(range=[0, 115], title="Skor Beban (0 - 100)", gridcolor="#f1f5f9"), height=290, showlegend=False, margin=dict(l=10, r=10, t=30, b=20))
        st.plotly_chart(fig_b, use_container_width=True)

    # 5 Sub-dimensi Unfavorable tertinggi
    st.markdown("#### ⚠️ Top 5 Aspek Beban Kerja (Stressor) Organisasi")
    all_unfav = {}
    for s, c in SUBDIMENSION_COLUMNS.items():
        if SUBDIMENSION_POLARITY.get(s) == "Unfavorable" and c in df_scope.columns:
            all_unfav[s] = df_scope[c].mean()
    top5_unfav = sorted(all_unfav.items(), key=lambda x: x[1], reverse=True)[:5]
    top5_unfav_rows = []
    for rank, (s, sc) in enumerate(top5_unfav, 1):
        slbl = SUBDIMENSION_LABELS.get(s, {"en": s, "id": s})
        top5_unfav_rows.append({"Peringkat": f"#{rank}", "Sub-Dimensi Beban": f"{slbl['en']} ({slbl['id']})", "Skor Beban": round(sc, 1), "Kategori": get_score_level(sc)})
    st.dataframe(pd.DataFrame(top5_unfav_rows), use_container_width=True, hide_index=True)

    st.markdown("""
    ⚠️ **Rekomendasi Ergonomi & Pencegahan Stres K3**:
    - Tinjau ulang beban tugas dan ritme kerja pada unit/bidang dengan skor tertinggi.
    - Sediakan saluran konseling rahasia dan forum dialog berkala antara staf dan pengawas untuk mengurai hambatan kerja.
    """)

@st.dialog("🟡 Analitik Defisit Dukungan: Aspek Favorable Terendah", width="large")
def dialog_lowest_favorable(sub_name, sub_score, df_scope):
    lbl = SUBDIMENSION_LABELS.get(sub_name, {"en": sub_name, "id": sub_name})
    st.markdown(f"### 🟡 {lbl['en']} ({lbl['id']})")
    st.caption("Sub-dimensi aspek positif (**Favorable**) dengan skor terendah yang paling mendesak ditingkatkan.")

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.metric("Skor Rata-Rata Saat Ini", f"{sub_score:.1f} / 100")
    with col_l2:
        st.metric("Status Evaluasi", "🟡 Defisit Sumber Daya Kerja")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏢 Skor per Bidang Kerja")
    col_s = SUBDIMENSION_COLUMNS.get(sub_name)
    if col_s and col_s in df_scope.columns and "Bidang" in df_scope.columns:
        b_df = df_scope.groupby("Bidang")[col_s].mean().reset_index()
        b_df.columns = ["Bidang", "Skor"]
        b_df["Skor"] = b_df["Skor"].round(1)
        fig_b = px.bar(
            b_df, x="Bidang", y="Skor", color="Bidang", color_discrete_map=BIDANG_COLOR_MAP, text="Skor"
        )
        fig_b.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
        fig_b.update_layout(yaxis=dict(range=[0, 115], title="Skor (0 - 100)", gridcolor="#f1f5f9"), height=290, showlegend=False, margin=dict(l=10, r=10, t=30, b=20))
        st.plotly_chart(fig_b, use_container_width=True)

    st.markdown("""
    🛠️ **Rekomendasi Tindak Lanjut**:
    - Skor rendah pada aspek favorable menandakan karyawan merasa kurang memperoleh dukungan, kejelasan peran, atau pengakuan.
    - Programkan pelatihan kepemimpinan empati untuk supervisor dan tinjau kembali kejelasan deskripsi pekerjaan.
    """)

@st.dialog("🚻 Analitik Gender & Ketegangan Kerja (Segmen 2)", width="large")
def dialog_gender_stress(df_scope):
    st.markdown("### 🚻 Perbandingan Gejala Kesehatan Mental Berdasarkan Jenis Kelamin")
    st.caption("Analisis komparatif gejala Depresi, Kecemasan, dan Ketegangan/Stres (DASS-21) antara karyawan Laki-laki dan Perempuan.")

    if "Jenis_Kelamin" in df_scope.columns:
        gender_data = []
        for g in ["Laki-laki", "Perempuan"]:
            gdf = df_scope[df_scope["Jenis_Kelamin"] == g]
            if not gdf.empty:
                for dim, col_name in DIMENSION_COLUMNS_SEGMEN2.items():
                    s_dim = CATEGORY_METADATA_SEGMEN2.get(dim, {}).get("short", dim)
                    val = round(gdf[col_name].mean(), 1) if col_name in gdf.columns else 0.0
                    gender_data.append({"Jenis Kelamin": g, "Dimensi": s_dim, "Skor Rata-Rata": val})

        if gender_data:
            df_g = pd.DataFrame(gender_data)
            fig_g = px.bar(
                df_g,
                x="Dimensi",
                y="Skor Rata-Rata",
                color="Jenis Kelamin",
                barmode="group",
                color_discrete_map={"Laki-laki": "#3b82f6", "Perempuan": "#ec4899"},
                text="Skor Rata-Rata"
            )
            fig_g.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
            fig_g.update_layout(yaxis=dict(range=[0, 45], title="Skor Rata-Rata (0 - 42)", gridcolor="#f1f5f9"), height=330, margin=dict(l=10, r=10, t=30, b=20))
            st.plotly_chart(fig_g, use_container_width=True)

        # Distribusi keparahan tingkat ketegangan / stres
        if "Tingkat_Stress" in df_scope.columns:
            st.markdown("#### 📊 Distribusi Tingkat Keparahan Ketegangan (Stres) per Gender")
            col_cg1, col_cg2 = st.columns(2)
            cat_order = ["Normal", "Ringan", "Sedang", "Berat", "Sangat Berat"]
            for idx, g in enumerate(["Laki-laki", "Perempuan"]):
                target_col = col_cg1 if idx == 0 else col_cg2
                with target_col:
                    gdf = df_scope[df_scope["Jenis_Kelamin"] == g]
                    if not gdf.empty:
                        s_counts = pd.Categorical(gdf["Tingkat_Stress"], categories=cat_order, ordered=True).value_counts().reset_index()
                        s_counts.columns = ["Tingkat", "Jumlah"]
                        s_counts = s_counts[s_counts["Jumlah"] > 0]
                        total_g = int(s_counts["Jumlah"].sum())
                        fig_g_pie = px.pie(
                            s_counts,
                            names="Tingkat",
                            values="Jumlah",
                            hole=0.4,
                            title=f"Ketegangan: {g} ({total_g} pengisi)",
                            color="Tingkat",
                            color_discrete_map={"Normal": "#10b981", "Ringan": "#3b82f6", "Sedang": "#f59e0b", "Berat": "#ea580c", "Sangat Berat": "#dc2626"},
                            category_orders={"Tingkat": cat_order}
                        )
                        fig_g_pie.update_traces(textposition="inside", texttemplate="<b>%{label}</b><br>%{value} orang (%{percent})")
                        fig_g_pie.update_layout(height=280, showlegend=False, margin=dict(l=10, r=10, t=35, b=10))
                        st.plotly_chart(fig_g_pie, use_container_width=True)

    st.markdown("""
    💡 **Wawasan Ergonomi & K3 Berbasis Gender**:
    - Perbedaan skor ketegangan kerja dapat dipengaruhi oleh perbedaan beban ganda (*work-life balance*), karakter pekerjaan fisik/administratif, atau gaya koping stres.
    - Sediakan program kebugaran mental dan pendampingan psikologi kerja yang inklusif untuk seluruh staf.
    """)

@st.dialog("🎂 Analitik Demografi Rentang Usia & Beban Mental", width="large")
def dialog_age_demographics(df_scope):
    st.markdown("### 🎂 Pola Kesehatan Mental Berdasarkan Kelompok Usia")
    st.caption("Pemantauan skor akumulatif DASS-21 dan kecenderungan gejala psikologis di setiap rentang usia kerja.")

    if "Rentang_Usia" in df_scope.columns:
        age_data = []
        age_order = ["< 25 tahun", "25 - 34 tahun", "35 - 44 tahun", "45 - 54 tahun", "≥ 55 tahun"]
        for age in age_order:
            adf = df_scope[df_scope["Rentang_Usia"] == age]
            if not adf.empty:
                val_dep = round(adf["Skor_Segmen2_Depresi"].mean(), 1) if "Skor_Segmen2_Depresi" in adf.columns else 0.0
                val_anx = round(adf["Skor_Segmen2_Kecemasan"].mean(), 1) if "Skor_Segmen2_Kecemasan" in adf.columns else 0.0
                val_str = round(adf["Skor_Segmen2_Stress"].mean(), 1) if "Skor_Segmen2_Stress" in adf.columns else 0.0
                val_tot = round(adf["Total_Skor_Segmen2"].mean(), 1) if "Total_Skor_Segmen2" in adf.columns else 0.0
                age_data.append({
                    "Rentang Usia": age,
                    "Total DASS": val_tot,
                    "Depresi": val_dep,
                    "Kecemasan": val_anx,
                    "Stress": val_str,
                    "Jumlah Pengisi": len(adf)
                })

        if age_data:
            df_age = pd.DataFrame(age_data)
            fig_age = px.bar(
                df_age,
                x="Rentang Usia",
                y="Total DASS",
                color="Rentang Usia",
                text="Total DASS",
                title="Total Akumulasi Skor DASS-21 per Kelompok Usia (0 - 126)"
            )
            fig_age.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}</b>")
            fig_age.update_layout(yaxis=dict(title="Skor Total DASS-21", gridcolor="#f1f5f9"), height=330, showlegend=False, margin=dict(l=10, r=10, t=35, b=20))
            st.plotly_chart(fig_age, use_container_width=True)

            st.markdown("#### 📋 Tabel Rincian Rata-Rata per Kelompok Usia")
            st.dataframe(df_age, use_container_width=True, hide_index=True)

    st.markdown("""
    💡 **Wawasan Adaptasi Usia Kerja**:
    - **Pekerja Muda (<25 & 25-34 th)**: Kerap menghadapi kecemasan adaptasi karir, kejelasan peran, dan tuntutan kecepatan kerja yang tinggi.
    - **Pekerja Senior (≥45 th)**: Memerlukan perhatian lebih pada kenyamanan fisik ergonomi dan pemeliharaan kesehatan jangka panjang.
    """)

@st.dialog("⚡ Analitik Prevalensi Gejala DASS-21 Organisasi", width="large")
def dialog_dass_prevalence(df_scope):
    st.markdown("### ⚡ Prevalensi Gejala Kesehatan Mental Kerja Organisasi")
    st.caption("Proporsi keseluruhan karyawan yang terindikasi Normal vs Bergejala (Ringan, Sedang, Berat, Sangat Berat).")

    dims = ["Depresi", "Kecemasan", "Stress"]
    prev_summary = []
    for d in dims:
        col_t = f"Tingkat_{d}"
        if col_t in df_scope.columns and not df_scope.empty:
            total_n = len(df_scope)
            normal_n = (df_scope[col_t] == "Normal").sum()
            gejala_n = total_n - normal_n
            pct_gejala = round((gejala_n / total_n) * 100, 1) if total_n > 0 else 0.0
            berat_n = (df_scope[col_t].isin(["Berat", "Sangat Berat"])).sum()
            pct_berat = round((berat_n / total_n) * 100, 1) if total_n > 0 else 0.0
            prev_summary.append({
                "Dimensi": d,
                "Prevalensi Bergejala (%)": pct_gejala,
                "Jumlah Bergejala": f"{gejala_n} / {total_n}",
                "Proporsi Berat/Sangat Berat (%)": pct_berat
            })

    if prev_summary:
        df_prev = pd.DataFrame(prev_summary)
        fig_prev = px.bar(
            df_prev,
            x="Dimensi",
            y="Prevalensi Bergejala (%)",
            color="Dimensi",
            text="Prevalensi Bergejala (%)",
            color_discrete_map={"Depresi": "#3b82f6", "Kecemasan": "#f59e0b", "Stress": "#ef4444"},
            title="Prevalensi Karyawan Terindikasi Gejala (Ringan s/d Sangat Berat)"
        )
        fig_prev.update_traces(textposition="outside", texttemplate="<b>%{y:.1f}%</b>")
        fig_prev.update_layout(yaxis=dict(range=[0, 105], title="Persentase (%)", gridcolor="#f1f5f9"), height=320, showlegend=False, margin=dict(l=10, r=10, t=35, b=20))
        st.plotly_chart(fig_prev, use_container_width=True)

        st.dataframe(df_prev, use_container_width=True, hide_index=True)

    st.markdown("""
    💡 **Rekomendasi Intervensi K3 Organisasi**:
    - Prevalensi gejala merupakan indikator dini untuk mencegah absensi sakit (*sickness absence*) dan kejenuhan kerja.
    - Jadwalkan sesi relaksasi ergonomi dan evaluasi beban kerja berkala untuk menjaga stabilitas kesehatan mental tim.
    """)

# =====================================================================
# FUNGSI RENDER HALAMAN HOOK (RINGKASAN EKSEKUTIF)
# =====================================================================
def render_hook_dashboard(df_filtered, df):
    """
    Menampilkan Halaman Hook (Ringkasan Eksekutif) dalam bentuk kartu-kartu metrik kunci.
    Ketika tombol pada kartu diklik, akan memunculkan pop-up dialog analitik mendalam (@st.dialog).
    """

    # --- CALL TO ACTION UNTUK MEMBUKA HALAMAN DETAIL ---
    with st.container(border=True):
        col_cta1, col_cta2 = st.columns([3, 1])
        with col_cta1:
            st.markdown("#### 📊 Ingin Menganalisis Seluruh Grafik & Data Mendalam?")
            st.write("Buka **Halaman Detail** untuk melihat diagram batang profil 8 dimensi, distribusi per bidang, barchart horizontal sub-bidang, perbandingan filter Segmen 2, serta tabel data responden.")
        with col_cta2:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("Buka Halaman Detail ➡️", type="primary", use_container_width=True, key="btn_switch_to_detail"):
                st.session_state["dash_view_mode"] = "detail"
                st.rerun()

    # Dimensi Faktor Psikososial Tertinggi
    dim_avgs = {dim: df_filtered[col].mean() for dim, col in DIMENSION_COLUMNS.items() if col in df_filtered.columns}
    top_dim = max(dim_avgs, key=dim_avgs.get) if dim_avgs else categories_list[0]
    top_dim_score = round(dim_avgs.get(top_dim, 0.0), 1)
    top_dim_meta = CATEGORY_METADATA.get(top_dim, {"label": top_dim, "icon": "📁", "short": top_dim})
    top_dim_level = get_score_level(top_dim_score)

    # Dimensi Faktor Psikososial Terendah
    low_dim = min(dim_avgs, key=dim_avgs.get) if dim_avgs else categories_list[0]
    low_dim_score = round(dim_avgs.get(low_dim, 0.0), 1)
    low_dim_meta = CATEGORY_METADATA.get(low_dim, {"label": low_dim, "icon": "📁", "short": low_dim})
    low_dim_level = get_score_level(low_dim_score)

    # Temukan subdimensi tertinggi di dalam dimensi tertinggi ini
    subs_top_dim = SUBDIMENSIONS_BY_CATEGORY.get(top_dim, [])
    top_sub_in_dim = None
    top_sub_in_dim_score = -1.0
    for s in subs_top_dim:
        col_s = SUBDIMENSION_COLUMNS.get(s)
        if col_s and col_s in df_filtered.columns:
            sc = df_filtered[col_s].mean()
            if sc > top_sub_in_dim_score:
                top_sub_in_dim_score = sc
                top_sub_in_dim = s

    # Sub-Dimensi Favorable Tertinggi & Terendah
    sub_avgs = {sub: df_filtered[col].mean() for sub, col in SUBDIMENSION_COLUMNS.items() if col in df_filtered.columns}
    fav_subs = {sub: val for sub, val in sub_avgs.items() if SUBDIMENSION_POLARITY.get(sub) == 'Favorable' and pd.notna(val)}
    top_fav = max(fav_subs, key=fav_subs.get) if fav_subs else list(SUBDIMENSION_COLUMNS.keys())[0]
    top_fav_score = round(fav_subs.get(top_fav, 0.0), 1)
    top_fav_lbl = SUBDIMENSION_LABELS.get(top_fav, {"en": top_fav, "id": top_fav})

    lowest_fav = min(fav_subs, key=fav_subs.get) if fav_subs else list(SUBDIMENSION_COLUMNS.keys())[0]
    lowest_fav_score = round(fav_subs.get(lowest_fav, 0.0), 1)
    lowest_fav_lbl = SUBDIMENSION_LABELS.get(lowest_fav, {"en": lowest_fav, "id": lowest_fav})

    # 3. Sub-Dimensi Unfavorable Tertinggi (Beban / Risiko)
    unfav_subs = {sub: val for sub, val in sub_avgs.items() if SUBDIMENSION_POLARITY.get(sub) == 'Unfavorable' and pd.notna(val)}
    top_unfav = max(unfav_subs, key=unfav_subs.get) if unfav_subs else list(SUBDIMENSION_COLUMNS.keys())[0]
    top_unfav_score = round(unfav_subs.get(top_unfav, 0.0), 1)
    top_unfav_lbl = SUBDIMENSION_LABELS.get(top_unfav, {"en": top_unfav, "id": top_unfav})

    # Sub-dimensi tertinggi per kategori
    highest_sub_per_category = []
    for cat_name in categories_list:
        sub_list = SUBDIMENSIONS_BY_CATEGORY.get(cat_name, [])
        cat_meta = CATEGORY_METADATA.get(cat_name, {"label": cat_name, "icon": "📁", "short": cat_name})
        
        best_sub_name = None
        best_sub_score = -1.0
        for s_name in sub_list:
            col_s = SUBDIMENSION_COLUMNS.get(s_name)
            if col_s and col_s in df_filtered.columns:
                val = df_filtered[col_s].mean()
                if pd.notna(val) and val > best_sub_score:
                    best_sub_score = val
                    best_sub_name = s_name

        if best_sub_name is not None:
            sub_lbl = SUBDIMENSION_LABELS.get(best_sub_name, {"en": best_sub_name, "id": best_sub_name})
            polarity = SUBDIMENSION_POLARITY.get(best_sub_name, "Favorable")
            highest_sub_per_category.append({
                "category_key": cat_name,
                "category_short": cat_meta.get("short", cat_name),
                "category_icon": cat_meta.get("icon", "📁"),
                "sub_name": best_sub_name,
                "sub_en": sub_lbl["en"],
                "sub_id": sub_lbl["id"],
                "score": round(best_sub_score, 1),
                "polarity": polarity,
                "level": get_score_level(best_sub_score)
            })

    # Gender & Ketegangan (Stres)
    if "Jenis_Kelamin" in df_filtered.columns and "Skor_Segmen2_Stress" in df_filtered.columns:
        gender_stress = df_filtered.groupby("Jenis_Kelamin")["Skor_Segmen2_Stress"].mean().dropna()
        if not gender_stress.empty:
            hi_gender = gender_stress.idxmax()
            hi_gender_val = round(gender_stress.max(), 1)
            low_gender = gender_stress.idxmin()
            low_gender_val = round(gender_stress.min(), 1)
            gender_tag_txt = f"{hi_gender}: {hi_gender_val} / 42"
            gender_desc_txt = f"Responden <b>{hi_gender}</b> mencatat rata-rata ketegangan lebih tinggi ({hi_gender_val}) dibanding {low_gender} ({low_gender_val})."
        else:
            gender_tag_txt = "Belum Ada Data"
            gender_desc_txt = "-"
    else:
        gender_tag_txt = "Belum Ada Data"
        gender_desc_txt = "-"

    # Demografi Usia & Total DASS
    if "Rentang_Usia" in df_filtered.columns and "Total_Skor_Segmen2" in df_filtered.columns:
        age_dass = df_filtered.groupby("Rentang_Usia")["Total_Skor_Segmen2"].mean().dropna()
        if not age_dass.empty:
            hi_age = age_dass.idxmax()
            hi_age_val = round(age_dass.max(), 1)
            age_tag_txt = f"{hi_age}"
            age_desc_txt = f"Kelompok umur <b>{hi_age}</b> menunjukkan akumulasi skor DASS-21 tertinggi (rata-rata: <b>{hi_age_val}</b>/126)."
        else:
            age_tag_txt = "Belum Ada Data"
            age_desc_txt = "-"
    else:
        age_tag_txt = "Belum Ada Data"
        age_desc_txt = "-"

    # Prevalensi Gejala DASS-21
    dass_prev_counts = {}
    for d in ["Depresi", "Kecemasan", "Stress"]:
        col_t = f"Tingkat_{d}"
        if col_t in df_filtered.columns:
            tot_n = len(df_filtered)
            norm_n = (df_filtered[col_t] == "Normal").sum()
            dass_prev_counts[d] = round(((tot_n - norm_n) / tot_n) * 100, 1) if tot_n > 0 else 0.0
    if dass_prev_counts:
        top_prev_d = max(dass_prev_counts, key=dass_prev_counts.get)
        top_prev_v = dass_prev_counts[top_prev_d]
        prev_tag_txt = f"{top_prev_d}: {top_prev_v}%"
        prev_desc_txt = f"Dimensi <b>{top_prev_d}</b> memiliki persentase karyawan terindikasi gejala tertinggi di organisasi."
    else:
        prev_tag_txt = "Belum Ada Data"
        prev_desc_txt = "-"

    # --- BAGIAN 1: KARTU HIGHLIGHT PSIKOSOSIAL KERJA ---
    st.markdown("#### 🏆 Highlight Faktor Psikososial Kerja")
    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)

    # 1. Dimensi Tertinggi
    with col_h1:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 140px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-blue">📊 Dimensi Tertinggi</span>
                <div class="hook-val">{top_dim_score:.1f} <span style="font-size:13px;color:#64748b;">/100</span></div>
                <div class="hook-title">{top_dim_meta.get('icon', '📁')} {top_dim_meta.get('short', top_dim)}</div>
                <div class="hook-text">Rata-rata skor dimensi tertinggi. Kategori: <b>{top_dim_level}</b>.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Analitik", key="btn_hk_top_dim", use_container_width=True):
                dialog_top_dimension(top_dim, top_dim_score, df_filtered)

    # 2. Dimensi Terendah (KARTU BARU)
    with col_h2:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 140px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-purple">📉 Dimensi Terendah</span>
                <div class="hook-val">{low_dim_score:.1f} <span style="font-size:13px;color:#64748b;">/100</span></div>
                <div class="hook-title">{low_dim_meta.get('icon', '📁')} {low_dim_meta.get('short', low_dim)}</div>
                <div class="hook-text">Rata-rata skor dimensi terendah. Kategori: <b>{low_dim_level}</b>.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Analitik", key="btn_hk_low_dim", use_container_width=True):
                dialog_top_dimension(low_dim, low_dim_score, df_filtered)

    # 3. Kekuatan Utama (Top Favorable)
    with col_h3:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 140px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-green">🟢 Kekuatan Utama</span>
                <div class="hook-val">{top_fav_score:.1f} <span style="font-size:13px;color:#64748b;">/100</span></div>
                <div class="hook-title">{top_fav_lbl['en']}</div>
                <div class="hook-text">({top_fav_lbl['id']}). Aspek positif paling kuat di organisasi.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Analitik", key="btn_hk_top_fav", use_container_width=True):
                dialog_top_favorable(top_fav, top_fav_score, df_filtered)

    # 4. Titik Kritis Beban (Top Unfavorable)
    with col_h4:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 140px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-red">🔴 Titik Kritis Beban</span>
                <div class="hook-val">{top_unfav_score:.1f} <span style="font-size:13px;color:#64748b;">/100</span></div>
                <div class="hook-title">{top_unfav_lbl['en']}</div>
                <div class="hook-text">({top_unfav_lbl['id']}). Pemicu beban kerja/stres tertinggi.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚠️ Analitik", key="btn_hk_top_unfav", use_container_width=True):
                dialog_top_unfavorable(top_unfav, top_unfav_score, df_filtered)

    # 5. Defisit Dukungan (Lowest Favorable)
    with col_h5:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 140px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-yellow">🟡 Defisit Dukungan</span>
                <div class="hook-val">{lowest_fav_score:.1f} <span style="font-size:13px;color:#64748b;">/100</span></div>
                <div class="hook-title">{lowest_fav_lbl['en']}</div>
                <div class="hook-text">({lowest_fav_lbl['id']}). Aspek positif terendah butuh penguatan.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Analitik", key="btn_hk_low_fav", use_container_width=True):
                dialog_lowest_favorable(lowest_fav, lowest_fav_score, df_filtered)
    
    # Rincian Sub-Dimensi Tertinggi per Dimensi Utama (Segmen 1)
    with st.expander("📌 **Rincian Sub-Dimensi Tertinggi dari Setiap Dimensi Utama (8 Dimensi)**", expanded=True):
        st.caption("Pendorong skor tertinggi di dalam masing-masing dari 8 dimensi psikososial Segmen 1.")

        grid_cols = st.columns(4)
        for idx, item in enumerate(highest_sub_per_category):
            col_target = grid_cols[idx % 4]
            with col_target:
                tag_class = "hook-tag-green" if item["polarity"] == "Favorable" else "hook-tag-red"
                tag_label = "🟢 Favorable" if item["polarity"] == "Favorable" else "🔴 Unfavorable"
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="min-height: 110px; margin-bottom: 6px;">
                        <div style="font-size: 11.5px; font-weight: 700; color: #64748b; margin-bottom: 3px;">
                            {item['category_icon']} {item['category_short']}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                            <span class="hook-val" style="font-size: 20px;">{item['score']:.1f}</span>
                            <span class="hook-tag {tag_class}" style="font-size: 9.5px; padding: 2px 7px;">{tag_label}</span>
                        </div>
                        <div style="font-size: 13px; font-weight: 700; color: #0f172a; line-height: 1.25;">
                            {item['sub_en']}
                        </div>
                        <div style="font-size: 11.5px; color: #64748b; margin-top: 2px;">
                            ({item['sub_id']})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_key = f"btn_hk_sub_top_cat_{idx}"
                    if item["polarity"] == "Favorable":
                        if st.button("🔍 Analitik", key=btn_key, use_container_width=True):
                            dialog_top_favorable(item["sub_name"], item["score"], df_filtered)
                    else:
                        if st.button("⚠️ Analitik", key=btn_key, use_container_width=True):
                            dialog_top_unfavorable(item["sub_name"], item["score"], df_filtered)
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # --- BAGIAN 2: KARTU HIGHLIGHT KESEHATAN MENTAL & DEMOGRAFI ---
    st.markdown("#### 🌿 Highlight Segmen 2: Kesehatan Mental Kerja & Demografi (DASS-21)")
    col_dh1, col_dh2, col_dh3 = st.columns(3)

    with col_dh1:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 125px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-purple">🚻 Demografi Gender</span>
                <div class="hook-val" style="font-size:20px;">{gender_tag_txt}</div>
                <div class="hook-title">Gejala Ketegangan (Stres Kerja)</div>
                <div class="hook-text">{gender_desc_txt}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Buka Analitik Gender & Ketegangan", key="btn_hk_gender", use_container_width=True):
                dialog_gender_stress(df_filtered)

    with col_dh2:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 125px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-blue">🎂 Demografi Usia</span>
                <div class="hook-val" style="font-size:20px;">{age_tag_txt}</div>
                <div class="hook-title">Kelompok Usia Paling Berisiko Gejala</div>
                <div class="hook-text">{age_desc_txt}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Buka Analitik Demografi Usia", key="btn_hk_age", use_container_width=True):
                dialog_age_demographics(df_filtered)

    with col_dh3:
        with st.container(border=True):
            st.markdown(f"""
            <div style="min-height: 125px; margin-bottom: 8px;">
                <span class="hook-tag hook-tag-red">⚡ Prevalensi Tertinggi</span>
                <div class="hook-val" style="font-size:20px;">{prev_tag_txt}</div>
                <div class="hook-title">Prevalensi Gejala DASS-21 Terbanyak</div>
                <div class="hook-text">{prev_desc_txt}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍 Buka Analitik Prevalensi", key="btn_hk_prev", use_container_width=True):
                dialog_dass_prevalence(df_filtered)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

total_steps = len(categories_list) + 2  # Step 0: Biodata, 1-8: Kategori, 9: Review, 10: Hasil

if menu == "📝 Form Survei":
    
    # Banner Header
    st.markdown("""
    <div class="hero-banner">
        <h1>📋 Formulir Survei Psikologi Kerja</h1>
        <p>Survei ini bertujuan untuk memetakan kondisi beban kerja, kepemimpinan, dan kesejahteraan psikologis karyawan di lingkungan kerja Bina Pengujian K3.</p>
    </div>
    """, unsafe_allow_html=True)

    curr_step = st.session_state["step"]

    # -------------------------------------------------------------
    # TAHAP 0: INFORMED CONSENT (LEMBAR PERSETUJUAN RESPONDEN)
    # -------------------------------------------------------------
    if not st.session_state.get("consent_given", False):
        st.markdown("### 📑 Lembar Persetujuan Responden (Informed Consent)")
        st.markdown("<p style='color:#64748b; font-size:14px; margin-top:-6px;'>Mohon membaca penjelasan dan ketentuan survei berikut sebelum memulai pengisian.</p>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("""
            #### **Yth. Rekan Karyawan / Responden,**

            Kami mengundang Anda untuk berpartisipasi dalam **Survei Evaluasi Faktor Psikososial dan Stress Kerja**. Survei ini bertujuan untuk memetakan kondisi tuntutan kerja, organisasi kerja, hubungan kerja & kepemimpinan, kepuasan kerja, serta kesehatan dan kesejahteraan psikologis pegawai.

            Sebelum melanjutkan, mohon perhatikan ketentuan etika dan kerahasiaan berikut:
            
            1. **Sifat Partisipasi Sukarela**: Partisipasi Anda dalam survei ini sepenuhnya bersifat **sukarela**. Anda berhak untuk menolak berpartisipasi atau menghentikan pengisian kapan saja tanpa dampak negatif maupun sanksi apa pun.
            2. **Jaminan Kerahasiaan & Anonimitas**: Seluruh data dan jawaban yang Anda berikan bersifat **rahasia**. Identitas nama dapat diisi secara anonim / menggunakan inisial. Laporan dan analisis survei disajikan secara **agregat (kelompok)**, bukan untuk evaluasi kinerja personal individu.
            3. **Tujuan Penggunaan Data**: Data yang terkumpul hanya akan digunakan untuk kepentingan evaluasi organisasi, pengembangan program Keselamatan dan Kesehatan Kerja (K3), serta perbaikan iklim lingkungan kerja.
            4. **Waktu Pengisian**: Kuesioner ini dirancang ringkas dengan estimasi waktu pengisian sekitar **15 – 20 menit**.
            5. **Objektivitas Respon**: Tidak ada penilaian benar atau salah. Kami sangat mengharapkan jawaban yang paling menggambarkan kondisi dan pengalaman kerja nyata Anda.
            """)

            st.divider()

            st.markdown("#### **Pernyataan Persetujuan:**")
            consent_check = st.checkbox(
                "Saya telah membaca dan memahami seluruh penjelasan di atas, serta dengan ini MENYETUJUI secara sukarela untuk berpartisipasi sebagai responden dalam survei ini.",
                key="consent_agreement_checkbox"
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            if st.button("Saya Setuju & Lanjutkan ke Data Diri ➡️", type="primary", use_container_width=True):
                if consent_check:
                    st.session_state["consent_given"] = True
                    st.session_state["step"] = 0
                    st.rerun()
                else:
                    st.warning("⚠️ Mohon centang kotak persetujuan di atas untuk dapat melanjutkan ke pengisian data diri.")
        with col_c2:
            if st.button("Tidak Bersedia", use_container_width=True):
                st.info("Anda memilih untuk tidak melanjutkan. Terima kasih banyak atas waktu dan perhatian Anda. Anda dapat menutup tab peramban ini.")

    # -------------------------------------------------------------
    # STEP 0: PENGISIAN DATA DIRI & BIDANG
    # -------------------------------------------------------------
    elif curr_step == 0:
        st.markdown("### 👤 Langkah 1 dari 11: Pengisian Data Diri & Asal Bidang")
        st.info("ℹ️ **Seluruh kolom isian bertanda bintang (*) wajib diisi**. Untuk identitas nama, Anda dapat menggunakan nama lengkap, inisial, atau nama samaran jika ingin menjaga kerahasiaan.")

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                cur_bidang = st.session_state["biodata"].get("bidang", "")
                bidang_idx = BIDANG_OPTIONS.index(cur_bidang) if cur_bidang in BIDANG_OPTIONS else None
                selected_bidang = st.selectbox(
                    "Asal Bidang Kerja *",
                    options=BIDANG_OPTIONS,
                    index=bidang_idx,
                    placeholder="-- Pilih Asal Bidang Kerja * --",
                    help="Pilih salah satu dari bidang penugasan kerja Anda."
                )
                nama_input = st.text_input(
                    "Nama Lengkap / Inisial *",
                    value=st.session_state["biodata"].get("nama", ""),
                    placeholder="Contoh: Responden A / John Doe / JD (Wajib diisi)"
                )
                gender_opts = ["Laki-laki", "Perempuan"]
                cur_gender = st.session_state["biodata"].get("gender", "")
                gender_idx = gender_opts.index(cur_gender) if cur_gender in gender_opts else None
                gender_input = st.radio(
                    "Jenis Kelamin *",
                    options=gender_opts,
                    index=gender_idx,
                    horizontal=True
                )
                riwayat_opts = ["Tidak", "Ya"]
                cur_riwayat = st.session_state["biodata"].get("riwayat_penyakit", "")
                riwayat_idx = riwayat_opts.index(cur_riwayat) if cur_riwayat in riwayat_opts else None
                riwayat_input = st.radio(
                    "Apakah Anda mempunyai riwayat penyakit? *",
                    options=riwayat_opts,
                    index=riwayat_idx,
                    horizontal=True
                )
                
                # Input kondisional
                nama_penyakit = "-"
                if riwayat_input == "Ya":
                    saved_np = st.session_state["biodata"].get("nama_penyakit", "")
                    nama_penyakit = st.text_input(
                        "Jika ya, sebutkan riwayat penyakit Anda *",
                        value="" if saved_np == "-" else saved_np,
                        placeholder="Contoh: Asma, Asam Lambung, Hipertensi, dll."
                    )
                
                # Berat badan & Tinggi badan
                col_bb, col_tb = st.columns(2)
                with col_bb:
                    bb_val = int(st.session_state["biodata"]["berat_badan"]) if st.session_state["biodata"].get("berat_badan") is not None else None
                    bb_input = st.number_input(
                        "Berat Badan (kg) *",
                        min_value=30,
                        max_value=200,
                        value=bb_val,
                        placeholder="Contoh: 60",
                        step=1
                    )
                with col_tb:
                    tb_val = int(st.session_state["biodata"]["tinggi_badan"]) if st.session_state["biodata"].get("tinggi_badan") is not None else None
                    tb_input = st.number_input(
                        "Tinggi Badan (cm) *",
                        min_value=100,
                        max_value=220,
                        value=tb_val,
                        placeholder="Contoh: 165",
                        step=1
                    )

            with col2:
                usia_options = ["< 25 tahun", "25 - 34 tahun", "35 - 44 tahun", "45 - 54 tahun", "≥ 55 tahun"]
                cur_usia = st.session_state["biodata"].get("usia", "")
                usia_idx = usia_options.index(cur_usia) if cur_usia in usia_options else None
                usia_input = st.selectbox(
                    "Rentang Usia *",
                    options=usia_options,
                    index=usia_idx,
                    placeholder="-- Pilih Rentang Usia * --"
                )
                masa_kerja_options = ["< 1 tahun", "1 - 3 tahun", "4 - 10 tahun", "> 10 tahun"]
                cur_mk = st.session_state["biodata"].get("masa_kerja", "")
                mk_idx = masa_kerja_options.index(cur_mk) if cur_mk in masa_kerja_options else None
                masa_kerja_input = st.selectbox(
                    "Masa Kerja *",
                    options=masa_kerja_options,
                    index=mk_idx,
                    placeholder="-- Pilih Masa Kerja * --"
                )
                jabatan_options = ["Staf Pelaksana", "Pengawas / Koordinator", "Fungsional Ahli", "Manajemen / Struktural", "Lainnya"]
                cur_jab = st.session_state["biodata"].get("jabatan", "")
                jab_idx = jabatan_options.index(cur_jab) if cur_jab in jabatan_options else None
                jabatan_input = st.selectbox(
                    "Posisi / Jabatan *",
                    options=jabatan_options,
                    index=jab_idx,
                    placeholder="-- Pilih Posisi / Jabatan * --"
                )
                status_perkawinan_opts = ["Sudah menikah", "Belum menikah", "Cerai mati", "Cerai hidup"]
                cur_kawin = st.session_state["biodata"].get("status_perkawinan", "")
                kawin_idx = status_perkawinan_opts.index(cur_kawin) if cur_kawin in status_perkawinan_opts else None
                status_perkawinan_input = st.selectbox(
                    "Status Pernikahan *",
                    options=status_perkawinan_opts,
                    index=kawin_idx,
                    placeholder="-- Pilih Status Pernikahan * --"
                )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns([1, 2])
        with col_b1:
            if st.button("⬅️ Lembar Persetujuan", use_container_width=True):
                st.session_state["consent_given"] = False
                st.rerun()
        with col_b2:
            if st.button("Mulai Mengisi Kuesioner ➡️", type="primary", use_container_width=True):
                errors = []
                if not selected_bidang:
                    errors.append("Asal Bidang Kerja wajib dipilih.")
                if not nama_input or not nama_input.strip():
                    errors.append("Nama Lengkap / Inisial wajib diisi (bisa inisial atau samaran).")
                if not gender_input:
                    errors.append("Jenis Kelamin wajib dipilih.")
                if not riwayat_input:
                    errors.append("Pertanyaan riwayat penyakit wajib dijawab.")
                elif riwayat_input == "Ya" and (not nama_penyakit or not nama_penyakit.strip() or nama_penyakit.strip() == "-"):
                    errors.append("Karena Anda memilih memiliki riwayat penyakit, mohon sebutkan nama riwayat penyakit Anda.")
                if bb_input is None:
                    errors.append("Berat Badan (kg) wajib diisi.")
                if tb_input is None:
                    errors.append("Tinggi Badan (cm) wajib diisi.")
                if not usia_input:
                    errors.append("Rentang Usia wajib dipilih.")
                if not masa_kerja_input:
                    errors.append("Masa Kerja wajib dipilih.")
                if not jabatan_input:
                    errors.append("Posisi / Jabatan wajib dipilih.")
                if not status_perkawinan_input:
                    errors.append("Status Pernikahan wajib dipilih.")

                if errors:
                    err_lines = "\n".join([f"- {e}" for e in errors])
                    st.warning(f"⚠️ **Mohon lengkapi seluruh kolom isian berikut sebelum melanjutkan:**\n\n{err_lines}")
                else:
                    st.session_state["biodata"]["bidang"] = selected_bidang
                    st.session_state["biodata"]["nama"] = nama_input.strip()
                    st.session_state["biodata"]["gender"] = gender_input
                    st.session_state["biodata"]["usia"] = usia_input
                    st.session_state["biodata"]["masa_kerja"] = masa_kerja_input
                    st.session_state["biodata"]["jabatan"] = jabatan_input
                    st.session_state["biodata"]["riwayat_penyakit"] = riwayat_input
                    st.session_state["biodata"]["nama_penyakit"] = nama_penyakit.strip() if riwayat_input == "Ya" else "-"
                    st.session_state["biodata"]["berat_badan"] = bb_input
                    st.session_state["biodata"]["tinggi_badan"] = tb_input
                    st.session_state["biodata"]["status_perkawinan"] = status_perkawinan_input
                    st.session_state["step"] = 1
                    st.rerun()


    # -------------------------------------------------------------
    # STEP 1 s/d 8: PENGISIAN 8 KATEGORI SURVEI
    # -------------------------------------------------------------
    elif 1 <= curr_step <= len(categories_list):
        category_index = curr_step - 1
        category_key = categories_list[category_index]
        meta = CATEGORY_METADATA.get(category_key, {
            "label": category_key,
            "short": category_key,
            "icon": "📝",
            "desc": ""
        })
        questions = SURVEY_QUESTIONS[category_key]

        # Progress bar
        progress_val = int((curr_step / 10) * 100)
        st.progress(progress_val, text=f"Segmen 1 (Langkah {curr_step + 1} dari 11): {meta['label']} ({progress_val}% Selesai)")

        # Section Header
        answered_in_cat = sum(1 for q in questions if (st.session_state.get(f"q_{q['id']}") is not None and str(st.session_state.get(f"q_{q['id']}")).strip() != "") or (st.session_state["answers"].get(q["id"]) is not None and str(st.session_state["answers"].get(q["id"])).strip() != ""))

        st.markdown(f"### {meta['icon']} Segmen 1 - Bagian {curr_step}: {meta['label']}")
        st.caption(f"{meta['desc']} (Total: {len(questions)} butir pertanyaan • **{answered_in_cat} dari {len(questions)}** telah dijawab)")
        st.divider()

        # Iterate Questions
        unanswered_ids = []
        last_sub = None
        for idx, q in enumerate(questions, 1):
            qid = q["id"]
            code = q["code"]
            q_text = q["text"]
            sub_name = q.get("sub", "")
            sub_note = q.get("sub_note", "")

            # Ambil nilai tersimpan atau nilai terkini dari state
            val_in_state = st.session_state.get(f"q_{qid}")
            if val_in_state is not None:
                saved_val = val_in_state
                st.session_state["answers"][qid] = val_in_state
            else:
                saved_val = st.session_state["answers"].get(qid, None)

            # Header Sub-Dimensi jika berganti
            if sub_name and sub_name != last_sub:
                last_sub = sub_name
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%); border-left: 4px solid #0284c7; padding: 12px 18px; border-radius: 8px; margin: 22px 0 14px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; letter-spacing: 0.5px;">📌 Sub-Dimensi</div>
                    <div style="font-size: 15px; font-weight: 700; color: #0f172a; margin-top: 2px;">{sub_name}</div>
                    {f"<div style='font-size: 12.5px; color: #475569; margin-top: 3px; font-style: italic;'>{sub_note}</div>" if sub_note else ""}
                </div>
                """, unsafe_allow_html=True)

            # Special case for 5M follow-up questions in Konflik & Perilaku Ofensif
            # If the preceding question was 'Tidak ada sama sekali', skip/auto-fill 5M
            is_5m_skipped = False
            if code == "5M":
                # Find previous question id
                prev_idx = idx - 2
                if prev_idx >= 0:
                    prev_q = questions[prev_idx]
                    prev_ans = st.session_state["answers"].get(prev_q["id"])
                    if prev_ans == "Tidak ada sama sekali":
                        is_5m_skipped = True
                        st.session_state["answers"][qid] = "Tidak ada"

            is_answered = is_5m_skipped or (saved_val is not None and str(saved_val).strip() != "")
            card_class = "question-card answered" if is_answered else "question-card"
            status_badge = (
                '<span class="status-badge-answered">✓ Sudah Dijawab</span>'
                if is_answered
                else '<span class="status-badge-unanswered">⏳ Belum Dijawab</span>'
            )

            with st.container():
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <span class="question-id-badge">{qid}</span>
                            <span style="font-size: 11.5px; color: #64748b; font-weight: 600; margin-left: 6px;">• {sub_name}</span>
                        </div>
                        {status_badge}
                    </div>
                    <div class="question-text">{idx}. {q_text} <span style="color:#ef4444;">*</span></div>
                </div>
                """, unsafe_allow_html=True)

                if is_5m_skipped:
                    st.info("ℹ️ Pertanyaan ini otomatis dilewati karena pada pertanyaan sebelumnya Anda memilih 'Tidak ada sama sekali'.")
                elif code == "5M":
                    options = get_question_options(code)
                    cur_idx = options.index(saved_val) if saved_val in options else None
                    sel_ans = st.selectbox(
                        "Pilih pihak yang bersangkutan: *",
                        options=options,
                        index=cur_idx,
                        placeholder="-- Pilih pihak yang bersangkutan * --",
                        key=f"q_{qid}"
                    )
                    if sel_ans is not None:
                        st.session_state["answers"][qid] = sel_ans
                    else:
                        st.session_state["answers"].pop(qid, None)
                elif code == "8":
                    scale_options = [str(i) for i in range(11)]
                    cur_idx = scale_options.index(str(saved_val)) if saved_val is not None and str(saved_val) in scale_options else None
                    sel_ans = st.radio(
                        "Pilihan Skala 0 (Terburuk) hingga 10 (Terbaik): *",
                        options=scale_options,
                        index=cur_idx,
                        key=f"q_{qid}",
                        horizontal=True
                    )
                    if sel_ans is not None:
                        st.session_state["answers"][qid] = str(sel_ans)
                    else:
                        st.session_state["answers"].pop(qid, None)
                else:
                    options = get_question_options(code)
                    # Radio option
                    cur_idx = None
                    if saved_val in options:
                        cur_idx = options.index(saved_val)
                    
                    sel_ans = st.radio(
                        "Pilihan Jawaban: *",
                        options=options,
                        index=cur_idx,
                        key=f"q_{qid}",
                        horizontal=True
                    )
                    if sel_ans is not None:
                        st.session_state["answers"][qid] = sel_ans
                    else:
                        st.session_state["answers"].pop(qid, None)
                        unanswered_ids.append(f"No. {idx} ({qid})")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        st.divider()
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.button("⬅️ Sebelumnya", use_container_width=True):
                st.session_state["step"] = curr_step - 1
                st.rerun()

        with col_next:
            next_label = "Lanjut ke Segmen 2 (Gambaran Aspek Emosional dan Psikologis) ➡️" if curr_step == len(categories_list) else "Selanjutnya ➡️"
            if st.button(next_label, type="primary", use_container_width=True):
                # Validasi kelengkapan pertanyaan di bagian ini
                missing = [q["id"] for q in questions if q["id"] not in st.session_state["answers"] or st.session_state["answers"][q["id"]] is None or str(st.session_state["answers"][q["id"]]).strip() == ""]
                if missing:
                    idx_map = {q["id"]: i for i, q in enumerate(questions, 1)}
                    missing_num_str = ", ".join([f"No. {idx_map[m]} ({m})" for m in missing[:5]])
                    if len(missing) > 5:
                        missing_num_str += f" dan {len(missing) - 5} butir lainnya"
                    st.warning(f"⚠️ Masih ada **{len(missing)} butir pertanyaan** pada bagian ini yang belum dijawab ({missing_num_str}). Seluruh pertanyaan wajib diisi sebelum melanjutkan.")
                else:
                    st.session_state["step"] = curr_step + 1
                    st.rerun()

    # -------------------------------------------------------------
    # STEP 9: PENGISIAN SEGMEN 2 (KESEHATAN MENTAL - DASS-21)
    # -------------------------------------------------------------
    elif curr_step == 9:
        st.progress(90, text="Langkah 10 dari 11: Segmen 2 - Skala Aspek Emosional dan Psikologis (90% Selesai)")

        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); color: white; padding: 22px 26px; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 8px 20px -4px rgba(49, 46, 129, 0.3);">
            <h2 style="color: white; margin: 0 0 8px 0; font-size: 22px;">🌿 Segmen 2: Gambaran Aspek Emosional dan Psikologis (DASS-21)</h2>
            <p style="color: #c7d2fe; margin: 0; font-size: 14px;">
                Segmen ini bertujuan untuk memetakan kondisi kesejahteraan emosional dan kesehatan mental dengan instrumen baku DASS-21.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 📌 Petunjuk Pengisian Segmen 2:")
            st.markdown("""
            Bacalah setiap butir pernyataan di bawah ini dan pilih salah satu pilihan yang **paling menggambarkan kondisi atau perasaan yang Anda alami selama 1 (satu) minggu terakhir**.
            
            **Ketentuan Penilaian (Skala Likert 4 Rentang):**
            * **0** = **Tidak sesuai dengan diri saya** *(tidak pernah atau tidak dialami sama sekali)*
            * **1** = **Sesuai dengan diri pada tingkat tertentu** *(kadang-kadang atau dalam tingkat ringan)*
            * **2** = **Sesuai dengan diri saya pada tingkat yang cukup besar** *(sering atau dalam taraf cukup besar)*
            * **3** = **Sangat sesuai dengan diri saya** *(hampir setiap waktu atau dalam taraf sangat besar)*
            """)

        st.divider()

        # Render 3 Dimensi: Depresi, Kecemasan, Stress
        for dim_key, questions in SURVEY_QUESTIONS_SEGMEN2.items():
            dim_meta = CATEGORY_METADATA_SEGMEN2.get(dim_key, {"label": dim_key, "icon": "📝", "desc": ""})
            
            # Hitung jumlah butir yang telah dijawab di dimensi ini
            ans_dim_cnt = sum(1 for q in questions if (st.session_state.get(f"q_seg2_{q['id']}") is not None and str(st.session_state.get(f"q_seg2_{q['id']}")).strip() != "") or (st.session_state["answers_segmen2"].get(q["id"]) is not None and str(st.session_state["answers_segmen2"].get(q["id"])).strip() != ""))
            st.markdown(f"### {dim_meta['icon']} Dimensi {dim_meta['label']}")
            st.caption(f"{dim_meta['desc']} (Total: {len(questions)} butir • **{ans_dim_cnt} dari {len(questions)}** telah dijawab)")

            for idx, q in enumerate(questions, 1):
                qid = q["id"]
                q_text = q["text"]
                
                # Cek status jawaban saat ini
                val_in_state = st.session_state.get(f"q_seg2_{qid}")
                if val_in_state is not None:
                    saved_val = val_in_state
                    st.session_state["answers_segmen2"][qid] = val_in_state
                else:
                    saved_val = st.session_state["answers_segmen2"].get(qid, None)

                is_answered = bool(saved_val is not None and str(saved_val).strip() != "")
                card_class = "question-card answered" if is_answered else "question-card"
                status_badge = (
                    '<span class="status-badge-answered">✓ Sudah Dijawab</span>'
                    if is_answered
                    else '<span class="status-badge-unanswered">⏳ Belum Dijawab</span>'
                )

                with st.container():
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span class="question-id-badge">{qid}</span>
                                <span style="font-size: 11.5px; color: #64748b; font-weight: 600; margin-left: 6px;">• {dim_key}</span>
                            </div>
                            {status_badge}
                        </div>
                        <div class="question-text">{idx}. {q_text} <span style="color:#ef4444;">*</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    cur_idx = None
                    if saved_val in SEGMEN2_OPTIONS:
                        cur_idx = SEGMEN2_OPTIONS.index(saved_val)

                    sel_ans = st.radio(
                        "Pilihan Jawaban: *",
                        options=SEGMEN2_OPTIONS,
                        index=cur_idx,
                        key=f"q_seg2_{qid}",
                        horizontal=True
                    )

                    if sel_ans is not None:
                        st.session_state["answers_segmen2"][qid] = sel_ans
                    else:
                        st.session_state["answers_segmen2"].pop(qid, None)

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        st.divider()
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.button("⬅️ Kembali ke Segmen 1 (Bagian 8)", use_container_width=True):
                st.session_state["step"] = 8
                st.rerun()

        with col_next:
            if st.button("Tinjau & Kirim ➡️", type="primary", use_container_width=True):
                # Validasi kelengkapan semua 21 butir Segmen 2
                missing = []
                for dim_key, qs in SURVEY_QUESTIONS_SEGMEN2.items():
                    for q in qs:
                        val = st.session_state["answers_segmen2"].get(q["id"])
                        if val is None or str(val).strip() == "":
                            missing.append(q["id"])

                if missing:
                    idx_map2 = {q["id"]: f"No. {i} ({q['id']})" for qs in SURVEY_QUESTIONS_SEGMEN2.values() for i, q in enumerate(qs, 1)}
                    missing_num_str = ", ".join([idx_map2.get(m, m) for m in missing[:5]])
                    if len(missing) > 5:
                        missing_num_str += f" dan {len(missing) - 5} butir lainnya"
                    st.warning(f"⚠️ Masih ada **{len(missing)} butir pertanyaan** pada Segmen 2 yang belum dijawab ({missing_num_str}). Seluruh pertanyaan wajib diisi sebelum melanjutkan.")
                else:
                    st.session_state["step"] = 10
                    st.rerun()

    # -------------------------------------------------------------
    # STEP 10: RINGKASAN & KONFIRMASI PENGIRIMAN
    # -------------------------------------------------------------
    elif curr_step == 10:
        st.markdown("### 📋 Langkah 11: Tinjau dan Kirim Jawaban Survei")
        st.info("Seluruh pertanyaan Segmen 1 dan Segmen 2 telah berhasil diisi. Silakan periksa ringkasan data sebelum menekan tombol Kirim.")

        col1, col2 = st.columns([1, 1])
        with col1:
            with st.container(border=True):
                st.markdown("#### 👤 Ringkasan Biodata")
                st.write(f"**Asal Bidang:** `{st.session_state['biodata']['bidang']}`")
                st.write(f"**Nama / Inisial:** {st.session_state['biodata']['nama']}")
                st.write(f"**Jenis Kelamin:** {st.session_state['biodata']['gender']}")
                st.write(f"**Rentang Usia:** {st.session_state['biodata']['usia']}")
                st.write(f"**Masa Kerja:** {st.session_state['biodata']['masa_kerja']}")
                st.write(f"**Posisi / Jabatan:** {st.session_state['biodata']['jabatan']}")
                st.write(f"**Riwayat Penyakit:** {st.session_state['biodata']['riwayat_penyakit']}" + (f" ({st.session_state['biodata']['nama_penyakit']})" if st.session_state['biodata']['riwayat_penyakit'] == 'Ya' else ""))
                st.write(f"**BB / TB:** {st.session_state['biodata']['berat_badan']} kg / {st.session_state['biodata']['tinggi_badan']} cm")
                st.write(f"**Status Pernikahan:** {st.session_state['biodata']['status_perkawinan']}")

        with col2:
            with st.container(border=True):
                st.markdown("#### 📊 Kelengkapan Pengisian")
                total_q1 = sum(len(qs) for qs in SURVEY_QUESTIONS.values())
                answered_q1 = len(st.session_state["answers"])
                total_q2 = sum(len(qs) for qs in SURVEY_QUESTIONS_SEGMEN2.values())
                answered_q2 = len(st.session_state["answers_segmen2"])
                
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    st.metric("Segmen 1 (Psikososial)", f"{answered_q1} / {total_q1}", "100% Lengkap")
                with col_k2:
                    st.metric("Segmen 2 (DASS-21)", f"{answered_q2} / {total_q2}", "100% Lengkap")
                st.caption("Kedua segmen kuesioner siap diproses dan dikirimkan secara aman.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        col_back, col_submit = st.columns([1, 2])
        with col_back:
            if st.button("⬅️ Kembali Periksa Jawaban Segmen 2", use_container_width=True):
                st.session_state["step"] = 9
                st.rerun()

        with col_submit:
            if st.button("🚀 Kirim Jawaban Survei Sekarang", type="primary", use_container_width=True):
                # Double check all inputs are complete
                missing_q1 = [q["id"] for qs in SURVEY_QUESTIONS.values() for q in qs if q["id"] not in st.session_state["answers"] or st.session_state["answers"][q["id"]] is None or str(st.session_state["answers"][q["id"]]).strip() == ""]
                missing_q2 = [q["id"] for qs in SURVEY_QUESTIONS_SEGMEN2.values() for q in qs if q["id"] not in st.session_state["answers_segmen2"] or st.session_state["answers_segmen2"][q["id"]] is None or str(st.session_state["answers_segmen2"][q["id"]]).strip() == ""]
                
                if missing_q1 or missing_q2:
                    st.error("⚠️ Terdapat butir pertanyaan yang belum terisi lengkap. Mohon periksa kembali kuesioner Anda sebelum mengirim.")
                else:
                    with st.spinner("Menyimpan jawaban ke database..."):
                        res = save_survey_response(st.session_state["biodata"], st.session_state["answers"], st.session_state["answers_segmen2"])
                        st.session_state["submission_result"] = res
                        st.session_state["step"] = 11
                        st.rerun()

    # -------------------------------------------------------------
    # STEP 11: HALAMAN TERIMA KASIH (SELESAI PENGISIAN)
    # -------------------------------------------------------------
    elif curr_step == 11:
        res = st.session_state["submission_result"]
        st.balloons()

        # Banner Utama Terima Kasih
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 36px 28px; border-radius: 16px; color: white; text-align: center; margin-bottom: 24px; box-shadow: 0 4px 18px rgba(16, 185, 129, 0.22);">
            <div style="font-size: 56px; margin-bottom: 10px;">🎉</div>
            <h2 style="color: white; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">Terima Kasih Atas Partisipasi Anda!</h2>
            <p style="color: #ecfdf5; font-size: 15.5px; margin: 0 auto; max-width: 680px; line-height: 1.6;">
                Jawaban kuesioner Anda untuk <b>Segmen 1 (Faktor Psikososial Kerja)</b> dan <b>Segmen 2 (Kesehatan Mental Kerja)</b> telah berhasil dikirim dan tersimpan dengan aman ke dalam sistem database.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Informasi Tanda Terima Pengisian (Receipt Information)
        id_resp = res.get("id_responden", "-") if res else "-"
        waktu_sekarang = datetime.now().strftime("%d %B %Y, %H:%M WIB")
        bidang_user = st.session_state.get("biodata", {}).get("bidang", "-")
        storage_info = "Tersinkronisasi ke Google Spreadsheet & Database Lokal" if (res and res.get("gsheet_saved")) else "Tersimpan di Database Lokal Sistem"

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #10b981;">
                <div class="metric-title">🏷️ ID Responden</div>
                <div class="metric-value" style="font-size: 22px;">{id_resp}</div>
                <div class="metric-subtitle">Nomor bukti pengisian survei</div>
            </div>
            """, unsafe_allow_html=True)

        with col_r2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #3b82f6;">
                <div class="metric-title">🏢 Asal Bidang Kerja</div>
                <div class="metric-value" style="font-size: 18px; word-break: break-word;">{bidang_user}</div>
                <div class="metric-subtitle">Unit / Bidang Responden</div>
            </div>
            """, unsafe_allow_html=True)

        with col_r3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                <div class="metric-title">🕒 Waktu Pengiriman</div>
                <div class="metric-value" style="font-size: 17px;">{waktu_sekarang}</div>
                <div class="metric-subtitle">Status: Berhasil Terkirim</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Informasi Tambahan & Jaminan Kerahasiaan
        with st.container(border=True):
            st.markdown("#### ℹ️ Catatan & Informasi untuk Responden")
            st.markdown("""
            * 🛡️ **Kerahasiaan & Anonimitas Terjamin**:
              Seluruh data, respon, dan jawaban yang Anda berikan bersifat **rahasia dan anonim**. Data diolah secara agregat (kelompok) oleh tim pengkaji K3 dan Ergonomi untuk mengevaluasi iklim lingkungan kerja organisasi, bukan untuk evaluasi kinerja personal individu.
            * 🤝 **Apresiasi Atas Kontribusi Nyata Anda**:
              Partisipasi jujur dan objektif Anda sangat berharga dalam membantu organisasi mengidentifikasi potensi risiko beban kerja dan tuntutan psikososial, serta merumuskan program perbaikan lingkungan kerja yang lebih aman, nyaman, dan sehat.
            * 🌿 **Dukungan Kesejahteraan & Layanan K3**:
              Bina Pengujian K3 senantiasa berkomitmen untuk mendukung kesejahteraan dan keselamatan seluruh pegawai. Apabila Anda memerlukan informasi lebih lanjut mengenai kenyamanan ergonomi atau konsultasi kesehatan kerja, silakan hubungi tim Keselamatan dan Kesehatan Kerja (K3).
            """)
            st.caption(f"Status Sistem: {storage_info}")

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Tombol Aksi
        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            if st.button("📝 Isi Survei untuk Responden Baru", use_container_width=True, type="primary"):
                st.session_state["consent_given"] = False
                st.session_state["step"] = 0
                st.session_state["answers"] = {}
                st.session_state["answers_segmen2"] = {}
                st.session_state["submission_result"] = None
                st.rerun()

        with col_act2:
            if st.session_state.get("is_admin", False):
                if st.button("📊 Buka Dashboard Analisis (Mode Admin)", use_container_width=True):
                    st.session_state["active_menu"] = "📊 Dashboard Hasil Survei"
                    st.rerun()
            else:
                st.caption("🔒 *Hasil rekapitulasi data agregat dan analisis statistik hanya dapat diakses oleh Administrator.*")

# =====================================================================
# 5. HALAMAN 2: DASHBOARD ANALISIS & REKAPITULASI
# =====================================================================
elif menu == "📊 Dashboard Hasil Survei":
    
    # Verifikasi Hak Akses Admin
    if not st.session_state.get("is_admin", False):
        st.error("🔒 Akses Ditolak: Halaman Dashboard rekapitulasi hanya dapat diakses oleh Administrator.")
        with st.container(border=True):
            st.markdown("### 🔐 Masukkan Kode Akses Admin")
            st.write("Silakan masukkan kode akses administrator untuk membuka dashboard hasil survei dan rekapitulasi data responden.")
            direct_code = st.text_input("Kode Akses Administrator:", type="password", key="direct_login_code_dashboard")
            if st.button("Buka Dashboard Sekarang", type="primary"):
                if direct_code.strip() == ADMIN_ACCESS_CODE:
                    st.session_state["is_admin"] = True
                    st.session_state["active_menu"] = "📊 Dashboard Hasil Survei"
                    st.rerun()
                else:
                    st.error("❌ Kode akses yang Anda masukkan salah.")
        st.stop()
    
    # Load dataset
    df, source_info = load_data()

    # Header Dashboard
    st.markdown(f"""
    <div class="hero-banner">
        <h1>📊 Dashboard Analisis Psikologi Kerja</h1>
        <p>Visualisasi rekapitulasi skor per bidang kerja, profil dimensi psikososial, dan analisis risiko kesehatan kerja.</p>
    </div>
    """, unsafe_allow_html=True)

    # Info Sumber Data & Validitas
    valid_count = int((df["Status_Validitas"] == "Valid").sum()) if "Status_Validitas" in df.columns else len(df)
    invalid_count = int((df["Status_Validitas"] == "Tidak Valid").sum()) if "Status_Validitas" in df.columns else 0
    st.markdown(f"**Sumber Data Terkoneksi:** `{source_info}` | Total: **{len(df)} Responden** (🟢 Valid: **{valid_count}**, 🔴 Tidak Valid: **{invalid_count}**)")

    # -------------------------------------------------------------
    # FILTER BAR
    # -------------------------------------------------------------
    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1.1, 1, 1, 1, 1.2])
        
        with col_f1:
            all_bidang = list(df["Bidang"].unique()) if "Bidang" in df.columns else BIDANG_OPTIONS
            selected_bidang_filter = st.multiselect(
                "Filter Asal Bidang:",
                options=all_bidang,
                default=all_bidang
            )
        
        with col_f2:
            all_usia = list(df["Rentang_Usia"].dropna().unique()) if "Rentang_Usia" in df.columns else []
            selected_usia_filter = st.multiselect(
                "Filter Rentang Usia:",
                options=all_usia,
                default=all_usia
            )

        with col_f3:
            all_masa_kerja = list(df["Masa_Kerja"].dropna().unique()) if "Masa_Kerja" in df.columns else []
            selected_masa_kerja_filter = st.multiselect(
                "Filter Masa Kerja:",
                options=all_masa_kerja,
                default=all_masa_kerja
            )

        with col_f4:
            all_gender = list(df["Jenis_Kelamin"].dropna().unique()) if "Jenis_Kelamin" in df.columns else []
            selected_gender_filter = st.multiselect(
                "Filter Jenis Kelamin:",
                options=all_gender,
                default=all_gender
            )

        with col_f5:
            validity_filter = st.selectbox(
                "Filter Validitas Data:",
                options=["Hanya Data Valid (Default)", "Semua Data", "Hanya Data Tidak Valid"],
                index=0
            )

    # Terapkan Filter
    df_filtered = df.copy()
    if "Status_Validitas" in df_filtered.columns:
        if validity_filter == "Hanya Data Valid (Default)":
            df_filtered = df_filtered[df_filtered["Status_Validitas"] == "Valid"]
        elif validity_filter == "Hanya Data Tidak Valid":
            df_filtered = df_filtered[df_filtered["Status_Validitas"] == "Tidak Valid"]

    if selected_bidang_filter:
        df_filtered = df_filtered[df_filtered["Bidang"].isin(selected_bidang_filter)]
    if selected_usia_filter:
        df_filtered = df_filtered[df_filtered["Rentang_Usia"].isin(selected_usia_filter)]
    if selected_masa_kerja_filter:
        df_filtered = df_filtered[df_filtered["Masa_Kerja"].isin(selected_masa_kerja_filter)]
    if selected_gender_filter:
        df_filtered = df_filtered[df_filtered["Jenis_Kelamin"].isin(selected_gender_filter)]

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan kombinasi filter yang dipilih.")
    else:
        # Selector Tampilan Halaman Dashboard: HOOK vs DETAIL
        current_view_idx = 1 if st.session_state.get("dash_view_mode") == "detail" else 0
        dash_view = st.radio(
            "Pilih Mode Tampilan Visualisasi:",
            options=["🪝 Halaman Hook (Ringkasan Eksekutif & Pop-Up Card)", "📊 Halaman Detail (Analisis Mendalam & Seluruh Grafik)"],
            index=current_view_idx,
            horizontal=True
        )
        st.session_state["dash_view_mode"] = "detail" if "Detail" in dash_view else "hook"
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        if st.session_state["dash_view_mode"] == "hook":
            render_hook_dashboard(df_filtered, df)
        else:
            # METRIC CARDS
            total_resp = len(df_filtered)
            avg_overall = round(df_filtered["Skor_Rata_Rata_Total"].mean(), 1) if "Skor_Rata_Rata_Total" in df_filtered.columns else 0.0
            avg_health = round(df_filtered["Skor_Kesehatan_Wellbeing"].mean(), 1) if "Skor_Kesehatan_Wellbeing" in df_filtered.columns else 0.0
            avg_demands = round(df_filtered["Skor_Tuntutan_Kerja"].mean(), 1) if "Skor_Tuntutan_Kerja" in df_filtered.columns else 0.0

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">👥 Total Responden</div>
                    <div class="metric-value">{total_resp}</div>
                    <div class="metric-subtitle">Responden terfilter</div>
                </div>
                """, unsafe_allow_html=True)

            with col_m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">❤️ Kesehatan & Well-being</div>
                    <div class="metric-value">{avg_health} <span style="font-size:16px;color:#64748b;">/100</span></div>
                    <div class="metric-subtitle">Indeks kesejahteraan fisik/mental</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Metrik Ringkasan Segmen 2 (Kesehatan Mental DASS-21)
            avg_dep = round(df_filtered["Skor_Segmen2_Depresi"].mean(), 1) if "Skor_Segmen2_Depresi" in df_filtered.columns else 0.0
            avg_anx = round(df_filtered["Skor_Segmen2_Kecemasan"].mean(), 1) if "Skor_Segmen2_Kecemasan" in df_filtered.columns else 0.0
            avg_str = round(df_filtered["Skor_Segmen2_Stress"].mean(), 1) if "Skor_Segmen2_Stress" in df_filtered.columns else 0.0

            col_m5, col_m6, col_m7 = st.columns(3)
            with col_m5:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #3b82f6;">
                    <div class="metric-title">🌧️ Rata-Rata Skor Tingkat Energi dan Suasana Hati (Segmen 2)</div>
                    <div class="metric-value">{avg_dep} <span style="font-size:16px;color:#64748b;">/42</span></div>
                    <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m6:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                    <div class="metric-title">⚡ Rata-Rata Skor Respons Fisik dan Tingkat Kenyamanan Situasional (Segmen 2)</div>
                    <div class="metric-value">{avg_anx} <span style="font-size:16px;color:#64748b;">/42</span></div>
                    <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m7:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #ef4444;">
                    <div class="metric-title">🔥 Rata-Rata Skor Pengelolaan Tekanan atau Ketegangan Kerja (Segmen 2)</div>
                    <div class="metric-value">{avg_str} <span style="font-size:16px;color:#64748b;">/42</span></div>
                    <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # -------------------------------------------------------------
            # GRAFIK 1: DIAGRAM BATANG PROFIL 8 DIMENSI
            # -------------------------------------------------------------
            col_g1, col_g2 = st.columns([3, 2])

            with col_g1:
                with st.container(border=True):
                    st.markdown("#### 📊 Profil Rata-Rata 8 Dimensi Psikososial")
                    st.caption(f"Diagram batang skor rata-rata pada 8 dimensi psikososial (skala 0 - 100) — Filter Validitas: <b>{validity_filter}</b> ({len(df_filtered)} Responden).")

                    dim_names = [CATEGORY_METADATA[k]["short"] for k in categories_list]
                    dim_cols = [DIMENSION_COLUMNS[k] for k in categories_list]
                    
                    # Rata-rata data terfilter (hanya pengisian valid secara default)
                    filtered_avgs = [round(df_filtered[col].mean(), 1) if col in df_filtered.columns else 0.0 for col in dim_cols]

                    fig_profile_bar = go.Figure()

                    fig_profile_bar.add_trace(go.Bar(
                        x=dim_names,
                        y=filtered_avgs,
                        name='Rata-Rata Skor',
                        marker=dict(
                            color='#0d9488',
                            line=dict(color='#0f766e', width=1.5)
                        ),
                        text=[f"<b>{v:.1f}</b>" for v in filtered_avgs],
                        textposition='outside',
                        textfont=dict(size=11, color='#0f172a'),
                        cliponaxis=False,
                        hovertemplate="<b>%{x}</b><br>Skor Rata-Rata: <b>%{y:.1f}</b> / 100<extra></extra>"
                    ))

                    fig_profile_bar.update_layout(
                        yaxis=dict(range=[0, 115], title="Skor Rata-Rata (0 - 100)", gridcolor="#f1f5f9"),
                        xaxis=dict(title="", tickangle=-25, tickfont=dict(size=11)),
                        showlegend=False,
                        height=380,
                        margin=dict(l=20, r=20, t=30, b=50),
                        plot_bgcolor="white",
                        paper_bgcolor="white"
                    )

                    st.plotly_chart(fig_profile_bar, use_container_width=True)

            with col_g2:
                with st.container(border=True):
                    st.markdown("#### 🍩 Distribusi Responden per Bidang")
                    st.caption("Proporsi dan jumlah responden terfilter berdasarkan bidang kerja.")

                    if "Bidang" in df_filtered.columns and not df_filtered.empty:
                        bidang_counts = df_filtered["Bidang"].value_counts().reset_index()
                        bidang_counts.columns = ["Bidang", "Jumlah"]
                        total_pengisi = len(df_filtered)

                        fig_donut = px.pie(
                            bidang_counts,
                            names="Bidang",
                            values="Jumlah",
                            hole=0.45,
                            color="Bidang",
                            color_discrete_map=BIDANG_COLOR_MAP
                        )
                        fig_donut.update_traces(
                            textposition='inside',
                            texttemplate="<b>%{label}</b><br>%{value} orang<br>(%{percent})",
                            hovertemplate="<b>%{label}</b><br>Jumlah Pengisi: <b>%{value} orang</b><br>Proporsi: <b>%{percent}</b><extra></extra>"
                        )
                        fig_donut.update_layout(
                            height=380,
                            margin=dict(l=10, r=10, t=30, b=20),
                            showlegend=False,
                            annotations=[dict(text=f"Total Pengisi<br><b>{total_pengisi}</b>", x=0.5, y=0.5, font_size=13, showarrow=False, font=dict(color="#0f172a"))]
                        )
                        st.plotly_chart(fig_donut, use_container_width=True)
                    else:
                        st.info("Belum ada data distribusi bidang.")

            # -------------------------------------------------------------
            # GRAFIK 2: PERBANDINGAN SKOR DIMENSI ANTAR BIDANG + RINCIAN SUB-DIMENSI
            # -------------------------------------------------------------
            with st.container(border=True):
                st.markdown("#### 📊 Rata-Rata Dimensi Antar Bidang Kerja (Segmen 1)")
                st.caption("Bandingkan skor rata-rata dimensi antar bidang kerja, filter per bidang/dimensi, serta masuk ke bidang tertentu untuk melihat rincian per sub-dimensi Segmen 1.")

                available_bidang_in_df = [b for b in BIDANG_OPTIONS if "Bidang" in df_filtered.columns and b in df_filtered["Bidang"].unique()]
                extra_bidang = [b for b in df_filtered["Bidang"].dropna().unique() if b not in available_bidang_in_df] if "Bidang" in df_filtered.columns else []
                bidang_opts_comp = available_bidang_in_df + extra_bidang

                col_cmp_f1, col_cmp_f2 = st.columns([1.2, 1.8])
                with col_cmp_f1:
                    bidang_mode_opts = ["Semua Bidang", "Pilih Beberapa Bidang..."] + bidang_opts_comp
                    selected_bidang_mode = st.selectbox(
                        "🏢 Filter Per Bidang:",
                        options=bidang_mode_opts,
                        key="dash_comp_bidang_mode"
                    )
                with col_cmp_f2:
                    selected_dims_comp = st.multiselect(
                        "📁 Filter Dimensi Faktor Psikososia:",
                        options=categories_list,
                        default=categories_list,
                        format_func=lambda x: CATEGORY_METADATA.get(x, {}).get("short", x),
                        key="dash_comp_dim_multiselect"
                    )

                if selected_bidang_mode == "Semua Bidang":
                    active_bidang_list = bidang_opts_comp
                elif selected_bidang_mode == "Pilih Beberapa Bidang...":
                    active_bidang_list = st.multiselect(
                        "Pilih Bidang Kerja yang Dibandingkan:",
                        options=bidang_opts_comp,
                        default=bidang_opts_comp[:2] if len(bidang_opts_comp) >= 2 else bidang_opts_comp,
                        key="dash_comp_bidang_multi"
                    )
                else:
                    active_bidang_list = [selected_bidang_mode]

                active_dims_list = selected_dims_comp if selected_dims_comp else categories_list

                if not active_bidang_list:
                    st.info("Pilih minimal satu bidang kerja pada filter di atas untuk menampilkan visualisasi.")
                else:
                    comparison_rows = []
                    for b in active_bidang_list:
                        b_df = df_filtered[df_filtered["Bidang"] == b] if "Bidang" in df_filtered.columns else pd.DataFrame()
                        if not b_df.empty:
                            for k in active_dims_list:
                                col = DIMENSION_COLUMNS[k]
                                short_name = CATEGORY_METADATA[k]["short"]
                                val = round(b_df[col].mean(), 1) if col in b_df.columns else 0.0
                                comparison_rows.append({
                                    "Bidang": b,
                                    "Dimensi": short_name,
                                    "Skor": val
                                })

                    if not comparison_rows:
                        st.warning("Tidak ada data responden untuk kombinasi bidang dan filter yang dipilih.")
                    else:
                        df_comp = pd.DataFrame(comparison_rows)
                        if len(active_bidang_list) == 1:
                            single_bidang = active_bidang_list[0]
                            b_count = len(df_filtered[df_filtered["Bidang"] == single_bidang]) if "Bidang" in df_filtered.columns else 0
                            fig_bar = px.bar(
                                df_comp,
                                x="Dimensi",
                                y="Skor",
                                color="Bidang",
                                color_discrete_map=BIDANG_COLOR_MAP,
                                text="Skor",
                                title=f"Profil Skor Dimensi Faktor Psikososial — Bidang {single_bidang} ({b_count} Responden)"
                            )
                            fig_bar.update_layout(showlegend=False)
                        else:
                            fig_bar = px.bar(
                                df_comp,
                                x="Dimensi",
                                y="Skor",
                                color="Bidang",
                                barmode="group",
                                color_discrete_map=BIDANG_COLOR_MAP,
                                text="Skor",
                                title="Rata-Rata Dimensi Antar Bidang Kerja Terpilih"
                            )
                            fig_bar.update_layout(
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )

                        fig_bar.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=10.5))
                        fig_bar.update_layout(
                            yaxis=dict(range=[0, 112], title="Skor Rata-Rata (0 - 100)", gridcolor="#f1f5f9"),
                            xaxis=dict(title="", tickangle=-15),
                            height=440,
                            margin=dict(l=20, r=20, t=65, b=50),
                            plot_bgcolor="white",
                            paper_bgcolor="white"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

                        # RINCIAN PER SUB-DIMENSI SEGMEN 1
                        st.divider()
                        if len(active_bidang_list) == 1:
                            single_bidang = active_bidang_list[0]
                            df_single_b = df_filtered[df_filtered["Bidang"] == single_bidang]
                            st.markdown(f"##### 🔬 Rincian Per Sub-Dimensi Faktor Psikososial — Bidang {single_bidang}")
                            st.caption("Detail skor per sub-dimensi Faktor Psikososial di dalam bidang yang dipilih beserta status risiko Favorable/Unfavorable.")

                            subdim_cat_opts = ["SEMUA"] + categories_list
                            selected_cat_inside = st.selectbox(
                                "📁 Pilih Dimensi Segmen 1 untuk Melihat Sub-Dimensi:",
                                options=subdim_cat_opts,
                                index=1,
                                format_func=lambda x: "📋 Semua Dimensi (45 Sub-Dimensi)" if x == "SEMUA" else f"{CATEGORY_METADATA.get(x, {}).get('icon', '📁')} {CATEGORY_METADATA.get(x, {}).get('label', x)}",
                                key="dash_comp_inside_subdim_cat"
                            )

                            cats_to_show = categories_list if selected_cat_inside == "SEMUA" else [selected_cat_inside]
                            sub_items, sub_tbl = collect_subdimension_items_from_df(df_single_b, cats_to_show)
                            cat_title = "Semua Dimensi (45 Sub-Dimensi)" if selected_cat_inside == "SEMUA" else CATEGORY_METADATA.get(selected_cat_inside, {}).get("label", selected_cat_inside)

                            fig_inside_sub = build_subdimension_hbar_chart(
                                sub_items,
                                title_text=f"Sub-Dimensi Faktor Psikososial: {cat_title} — {single_bidang}",
                                xaxis_title="Skor Rata-Rata Sub-Dimensi (0 - 100)"
                            )
                            st.plotly_chart(fig_inside_sub, use_container_width=True)
                            with st.expander(f"📋 Tabel Rincian Skor ({len(sub_tbl)} Sub-Dimensi)", expanded=(selected_cat_inside != "SEMUA")):
                                st.dataframe(pd.DataFrame(sub_tbl), use_container_width=True, hide_index=True)
                        else:
                            with st.expander("🔍 Bandingkan Per Sub-Dimensi Antar Bidang Terpilih", expanded=False):
                                st.caption("Pilih satu dimensi faktor psikososia untuk membandingkan skor setiap sub-dimensi antar bidang terpilih, atau pilih satu bidang spesifik pada dropdown 'Filter Per Bidang' di atas untuk melihat rincian sub-dimensi di dalam bidangnya.")
                                comp_sub_cat = st.selectbox(
                                    "📁 Pilih Dimensi Faktor Psikososial:",
                                    options=categories_list,
                                    format_func=lambda x: f"{CATEGORY_METADATA.get(x, {}).get('icon', '📁')} {CATEGORY_METADATA.get(x, {}).get('label', x)}",
                                    key="dash_comp_multi_subdim_cat"
                                )
                                subs_for_cat = SUBDIMENSIONS_BY_CATEGORY.get(comp_sub_cat, [])
                                sub_comp_rows = []
                                for b in active_bidang_list:
                                    b_df = df_filtered[df_filtered["Bidang"] == b] if "Bidang" in df_filtered.columns else pd.DataFrame()
                                    if not b_df.empty:
                                        for s_name in subs_for_cat:
                                            col_s = SUBDIMENSION_COLUMNS.get(s_name)
                                            val = round(pd.to_numeric(b_df[col_s], errors="coerce").dropna().mean(), 1) if col_s and col_s in b_df.columns else 0.0
                                            lbl = SUBDIMENSION_LABELS.get(s_name, {"en": s_name, "id": s_name})
                                            sub_comp_rows.append({
                                                "Bidang": b,
                                                "Sub-Dimensi": f"{lbl['en']} ({lbl['id']})",
                                                "Skor": val
                                            })
                                if sub_comp_rows:
                                    df_sub_comp = pd.DataFrame(sub_comp_rows)
                                    fig_sub_comp = px.bar(
                                        df_sub_comp,
                                        y="Sub-Dimensi",
                                        x="Skor",
                                        color="Bidang",
                                        barmode="group",
                                        orientation="h",
                                        color_discrete_map=BIDANG_COLOR_MAP,
                                        text="Skor",
                                        title=f"Sub-Dimensi: {CATEGORY_METADATA.get(comp_sub_cat, {}).get('label', comp_sub_cat)}"
                                    )
                                    fig_sub_comp.update_traces(textposition="outside", cliponaxis=False, textfont=dict(size=10))
                                    fig_sub_comp.update_layout(
                                        xaxis=dict(range=[0, 115], title="Skor Rata-Rata (0 - 100)", gridcolor="#f1f5f9"),
                                        yaxis=dict(title="", autorange="reversed"),
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                        height=max(420, len(subs_for_cat) * 85),
                                        margin=dict(l=20, r=40, t=70, b=40),
                                        plot_bgcolor="white",
                                        paper_bgcolor="white"
                                    )
                                    st.plotly_chart(fig_sub_comp, use_container_width=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # -------------------------------------------------------------
            # GRAFIK: ANALISIS MENDALAM SKOR SUB-DIMENSI (45 SUB-BIDANG)
            # -------------------------------------------------------------
            with st.container(border=True):
                st.markdown("#### 🔬 Visualisasi Horizontal Barchart per Sub-Bidang")
                st.caption("Pilih asal bidang kerja dan dimensi utama untuk menganalisis skor profil sub-dimensi dalam bentuk grafik batang horizontal.")

                st.info("""
                📌 **Ketentuan Penilaian Sub-Bidang**:
                * **Rumus Skor Sub-Bidang**: $\\text{Skor} = \\frac{\\sum \\text{Skor Butir}}{\\text{Jumlah Butir}}$
                * **Rentang Kategori**: **Rendah** (0 - 33,33) | **Sedang** (33,34 - 66,66) | **Tinggi** (66,67 - 100)
                * **Sifat Favorable**: Skor Tinggi = 🟢 **Baik / Risiko Rendah**, Skor Rendah = 🔴 **Kurang / Risiko Tinggi**
                * **Sifat Unfavorable**: Skor Rendah = 🟢 **Baik / Risiko Rendah**, Skor Tinggi = 🔴 **Bahaya / Risiko Tinggi**
                """)

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    bidang_selector_options = ["Semua Bidang (Rata-rata Keseluruhan)"] + BIDANG_OPTIONS
                    selected_bidang_dash = st.selectbox(
                        "🏢 Pilih Asal Bidang Kerja:",
                        options=bidang_selector_options,
                        key="dash_selected_bidang_filter"
                    )

                with col_d2:
                    selected_sub_category = st.selectbox(
                        "📁 Pilih Dimensi Utama (Kategori):",
                        options=categories_list,
                        format_func=lambda x: f"{CATEGORY_METADATA.get(x, {}).get('icon', '📁')} {CATEGORY_METADATA.get(x, {}).get('label', x)}",
                        key="dash_selected_sub_cat"
                    )

                # Filter data sesuai bidang yang dipilih
                if selected_bidang_dash == "Semua Bidang (Rata-rata Keseluruhan)":
                    df_scope = df_filtered
                    scope_label = "Seluruh Bidang (Rata-rata Keseluruhan)"
                else:
                    df_scope = df_filtered[df_filtered["Bidang"] == selected_bidang_dash] if "Bidang" in df_filtered.columns else pd.DataFrame()
                    scope_label = f"Bidang {selected_bidang_dash}"

                subs_in_cat = SUBDIMENSIONS_BY_CATEGORY.get(selected_sub_category, [])
                c_meta = CATEGORY_METADATA.get(selected_sub_category, {"label": selected_sub_category, "icon": "📁"})

                if df_scope.empty:
                    st.warning(f"Belum ada data responden untuk {scope_label}.")
                elif subs_in_cat:
                    chart_items, tbl_rows = collect_subdimension_items_from_df(df_scope, [selected_sub_category])
                    fig_sub_hbar = build_subdimension_hbar_chart(
                        chart_items,
                        title_text=f"📊 Barchart Horizontal: {c_meta.get('label', selected_sub_category)} — {scope_label}",
                        xaxis_title="Skor Rata-Rata Sub-Bidang (0 - 100)"
                    )
                    st.plotly_chart(fig_sub_hbar, use_container_width=True)

                    # Tabel Rincian Data Native Streamlit
                    st.markdown(f"**Tabel Rincian Skor ({len(subs_in_cat)} Sub-Bidang):**")
                    st.dataframe(pd.DataFrame(tbl_rows), use_container_width=True, hide_index=True)
                    

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)


            # -------------------------------------------------------------
            # GRAFIK 4: ANALISIS KESEHATAN MENTAL SEGMEN 2 (DASS-21)
            # -------------------------------------------------------------
            with st.container(border=True):
                st.markdown("#### 🌿 Analisis DASS: Kondisi Tingkat Energi dan Suasana Hati, Respons Fisik dan  tingkat Kenyamanan Situasional, & Pengelolaan Tekanan atau Ketegangan Kerja (DASS-21)")
                st.caption("Pemantauan skor dan tingkat keparahan DASS-21 berdasarkan bidang kerja dan kategori keparahan.")

                # Filter Per Bidang untuk Segmen 2
                available_bidang_seg2 = [b for b in BIDANG_OPTIONS if "Bidang" in df_filtered.columns and b in df_filtered["Bidang"].unique()]
                extra_b_seg2 = [b for b in df_filtered["Bidang"].dropna().unique() if b not in available_bidang_seg2] if "Bidang" in df_filtered.columns else []
                all_b_seg2 = available_bidang_seg2 + extra_b_seg2

                col_fb1, col_fb2 = st.columns([1.2, 1.8])
                with col_fb1:
                    selected_seg2_bidang = st.selectbox(
                        "🏢 Filter Asal Bidang Kerja (Segmen 2):",
                        options=["Semua Bidang"] + all_b_seg2,
                        key="dash_seg2_bidang_filter"
                    )
                with col_fb2:
                    dim_choice = st.selectbox(
                        "📊 Pilih Dimensi untuk Distribusi Keparahan:",
                        ["Depresi", "Kecemasan", "Stress"],
                        key="dash_dass_dim_sel"
                    )

                # Tentukan dataset scope untuk Segmen 2
                if selected_seg2_bidang == "Semua Bidang":
                    df_seg2_scope = df_filtered
                    seg2_title_suffix = "Semua Bidang"
                else:
                    df_seg2_scope = df_filtered[df_filtered["Bidang"] == selected_seg2_bidang] if "Bidang" in df_filtered.columns else pd.DataFrame()
                    seg2_title_suffix = f"Bidang {selected_seg2_bidang}"

                col_dass1, col_dass2 = st.columns([3, 2])
                with col_dass1:
                    if selected_seg2_bidang == "Semua Bidang":
                        # Perbandingan Rata-Rata DASS-21 per Bidang Kerja
                        dass_comp_rows = []
                        for b in all_b_seg2:
                            b_df = df_filtered[df_filtered["Bidang"] == b] if "Bidang" in df_filtered.columns else pd.DataFrame()
                            if not b_df.empty:
                                for dim, col_name in DIMENSION_COLUMNS_SEGMEN2.items():
                                    val = round(b_df[col_name].mean(), 1) if col_name in b_df.columns else 0.0
                                    short_dim = CATEGORY_METADATA_SEGMEN2.get(dim, {}).get("short", dim)
                                    dass_comp_rows.append({"Bidang": b, "Dimensi": short_dim, "Skor": val})

                        if dass_comp_rows:
                            df_dass_comp = pd.DataFrame(dass_comp_rows)
                            fig_dass_bidang = px.bar(
                                df_dass_comp,
                                x="Dimensi",
                                y="Skor",
                                color="Bidang",
                                barmode="group",
                                color_discrete_map=BIDANG_COLOR_MAP,
                                text="Skor",
                                title="Rata-Rata Skor DASS-21 per Bidang Kerja"
                            )
                            fig_dass_bidang.update_traces(
                                texttemplate="<b>%{y:.1f}</b>",
                                textposition="outside",
                                cliponaxis=False
                            )
                            fig_dass_bidang.update_layout(
                                yaxis=dict(range=[0, 45], title="Skor Rata-Rata (0 - 42)", gridcolor="#f1f5f9"),
                                xaxis=dict(title=""),
                                height=380,
                                margin=dict(l=20, r=20, t=40, b=30),
                                plot_bgcolor="white",
                                paper_bgcolor="white"
                            )
                            st.plotly_chart(fig_dass_bidang, use_container_width=True)
                        else:
                            st.info("Belum ada data rekaman DASS-21.")
                    else:
                        # Tampilkan Skor Rata-rata 3 Dimensi untuk bidang yang dipilih
                        single_dass_rows = []
                        for dim, col_name in DIMENSION_COLUMNS_SEGMEN2.items():
                            short_dim = CATEGORY_METADATA_SEGMEN2.get(dim, {}).get("short", dim)
                            val = round(df_seg2_scope[col_name].mean(), 1) if col_name in df_seg2_scope.columns and not df_seg2_scope.empty else 0.0
                            sev = get_dass_severity(short_dim, val)
                            single_dass_rows.append({"Dimensi": short_dim, "Skor": val, "Kategori Keparahan": sev})
                    
                        if single_dass_rows:
                            df_single_dass = pd.DataFrame(single_dass_rows)
                            fig_dass_single = px.bar(
                                df_single_dass,
                                x="Dimensi",
                                y="Skor",
                                color="Dimensi",
                                color_discrete_map={"Depresi": "#3b82f6", "Kecemasan": "#f59e0b", "Stress": "#ef4444"},
                                text="Skor",
                                title=f"Skor Rata-Rata DASS-21: {selected_seg2_bidang} ({len(df_seg2_scope)} Responden)"
                            )
                            fig_dass_single.update_traces(
                                texttemplate="<b>%{y:.1f}</b>",
                                textposition="outside",
                                cliponaxis=False
                            )
                            fig_dass_single.update_layout(
                                yaxis=dict(range=[0, 45], title="Skor Rata-Rata (0 - 42)", gridcolor="#f1f5f9"),
                                xaxis=dict(title=""),
                                showlegend=False,
                                height=380,
                                margin=dict(l=20, r=20, t=40, b=30),
                                plot_bgcolor="white",
                                paper_bgcolor="white"
                            )
                            st.plotly_chart(fig_dass_single, use_container_width=True)
                        else:
                            st.info(f"Belum ada data responden untuk {selected_seg2_bidang}.")

                with col_dass2:
                    # Distribusi Tingkat Keparahan Stress / Depresi / Kecemasan (berdasarkan df_seg2_scope)
                    sev_col = f"Tingkat_{dim_choice}"
                    if sev_col in df_seg2_scope.columns and not df_seg2_scope.empty:
                        cat_order = ["Normal", "Ringan", "Sedang", "Berat", "Sangat Berat"]
                        sev_series = pd.Categorical(df_seg2_scope[sev_col], categories=cat_order, ordered=True)
                        sev_counts = sev_series.value_counts().reset_index()
                        sev_counts.columns = ["Tingkat", "Jumlah"]
                        sev_counts = sev_counts[sev_counts["Jumlah"] > 0]
                        total_sev_pengisi = int(sev_counts["Jumlah"].sum())

                        if not sev_counts.empty:
                            fig_sev_pie = px.pie(
                                sev_counts,
                                names="Tingkat",
                                values="Jumlah",
                                hole=0.4,
                                title=f"Distribusi Tingkat {dim_choice} ({seg2_title_suffix})",
                                color="Tingkat",
                                color_discrete_map={
                                    "Normal": "#10b981",
                                    "Ringan": "#3b82f6",
                                    "Sedang": "#f59e0b",
                                    "Berat": "#ea580c",
                                    "Sangat Berat": "#dc2626"
                                },
                                category_orders={"Tingkat": cat_order}
                            )
                            fig_sev_pie.update_traces(
                                textposition='inside',
                                texttemplate="<b>%{label}</b><br>%{value} orang<br>(%{percent})",
                                hovertemplate="<b>Tingkat %{label}</b><br>Jumlah Pengisi: <b>%{value} orang</b><br>Proporsi: <b>%{percent}</b><extra></extra>"
                            )
                            fig_sev_pie.update_layout(
                                height=380,
                                margin=dict(l=10, r=10, t=40, b=20),
                                annotations=[dict(text=f"Total Pengisi<br><b>{total_sev_pengisi}</b>", x=0.5, y=0.5, font_size=13, showarrow=False, font=dict(color="#0f172a"))]
                            )
                            st.plotly_chart(fig_sev_pie, use_container_width=True)
                        else:
                            st.info(f"Tidak ada data tingkat {dim_choice} pada filter ini.")
                    else:
                        st.info(f"Belum ada data rekaman tingkat {dim_choice} Segmen 2 untuk {seg2_title_suffix}.")

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # -------------------------------------------------------------
            # TABEL DATA LENGKAP & EXPORT KE EXCEL / CSV
            # -------------------------------------------------------------
            with st.container(border=True):
                st.markdown("#### 📑 Rekapitulasi Data Responden")
            
                # Kolom ringkasan yang nyaman dibaca mencakup Segmen 1, Sub-Dimensi, dan Segmen 2
                summary_cols = (
                    ["ID_Responden", "Status_Validitas", "Skor_Validitas", "Waktu_Pengisian", "Bidang", "Nama_Inisial", "Jenis_Kelamin", "Rentang_Usia", "Masa_Kerja", "Jabatan"]
                    + list(DIMENSION_COLUMNS.values())
                    + ["Skor_Rata_Rata_Total"]
                    + list(SUBDIMENSION_COLUMNS.values())
                    + list(DIMENSION_COLUMNS_SEGMEN2.values())
                    + ["Total_Skor_Segmen2", "Tingkat_Depresi", "Tingkat_Kecemasan", "Tingkat_Stress"]
                )
                available_summary_cols = [c for c in summary_cols if c in df_filtered.columns]

                st.dataframe(df_filtered[available_summary_cols], use_container_width=True, height=320)

                col_exp1, col_exp2 = st.columns([1, 1])
                with col_exp1:
                    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Unduh Data Lengkap (.CSV)",
                        data=csv_bytes,
                        file_name=f"Rekap_Survei_ErgoPsiko_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col_exp2:
                    try:
                        excel_bytes = convert_df_to_excel(df_filtered)
                        st.download_button(
                            label="📥 Unduh Data Lengkap (.Excel / .XLSX)",
                            data=excel_bytes,
                            file_name=f"Rekap_Survei_ErgoPsiko_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Gagal generate file Excel: {e}")

    # =====================================================================
# 6. HALAMAN 3: PENGATURAN & GOOGLE SHEETS
# =====================================================================
elif menu == "⚙️ Konfigurasi Spreadsheet":
    
    # Verifikasi Hak Akses Admin
    if not st.session_state.get("is_admin", False):
        st.error("🔒 Akses Ditolak: Halaman Konfigurasi Spreadsheet hanya dapat diakses oleh Administrator.")
        st.stop()
    st.markdown("""
    <div class="hero-banner">
        <h1>⚙️ Integrasi Google Spreadsheet & Pengaturan</h1>
        <p>Panduan langkah demi langkah menghubungkan aplikasi ini ke Google Spreadsheet menggunakan streamlit-gsheets.</p>
    </div>
    """, unsafe_allow_html=True)

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        with st.container(border=True):
            st.markdown("#### 📡 Status Koneksi Cloud")
            if is_gsheets_configured():
                st.success("✅ Google Sheets telah terkonfigurasi di secrets.toml!")
                st.write(f"URL Spreadsheet: `{st.secrets['connections']['gsheets']['spreadsheet']}`")
            else:
                st.warning("⚠️ Google Sheets belum terkonfigurasi. Data saat ini tersimpan di file lokal `data_survei.csv`.")

    with col_stat2:
        with st.container(border=True):
            st.markdown("#### 💾 Penyimpanan File Lokal")
            st.write(f"Lokasi File: `{LOCAL_DATA_FILE}`")
            if st.button("🔄 Segarkan Data (Reload Dataset)", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache berhasil disegarkan!")
                st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
