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
            index=current_idx,
            key="admin_menu_selector"
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
        - Estimasi waktu: **5 - 7 menit**.
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
# 4. HALAMAN 1: FORM SURVEI
# =====================================================================
categories_list = list(SURVEY_QUESTIONS.keys())
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
            
            1. **Sifat Partisipasi Sukarela**: Partisipasi Anda dalam survei ini sepenuhnya bersifat **sukarela (voluntary)**. Anda berhak untuk menolak berpartisipasi atau menghentikan pengisian kapan saja tanpa dampak negatif maupun sanksi apa pun.
            2. **Jaminan Kerahasiaan & Anonimitas**: Seluruh data dan jawaban yang Anda berikan bersifat **rahasia**. Identitas nama dapat diisi secara anonim / menggunakan inisial. Laporan dan analisis survei disajikan secara **agregat (kelompok)**, bukan untuk evaluasi kinerja personal individu.
            3. **Tujuan Penggunaan Data**: Data yang terkumpul hanya akan digunakan untuk kepentingan evaluasi organisasi, pengembangan program Keselamatan dan Kesehatan Kerja (K3), serta perbaikan iklim lingkungan kerja.
            4. **Waktu Pengisian**: Kuesioner ini dirancang ringkas dengan estimasi waktu pengisian sekitar **5 – 7 menit**.
            5. **Objektivitas Respon**: Tidak ada penilaian benar atau salah. Kami sangat mengharapkan jawaban yang paling menggambarkan kondisi dan pengalaman kerja nyata Anda selama 12 bulan terakhir.
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
            next_label = "Lanjut ke Segmen 2 (Kesehatan Mental) ➡️" if curr_step == len(categories_list) else "Selanjutnya ➡️"
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
        st.progress(90, text="Langkah 10 dari 11: Segmen 2 - Skala Depresi, Kecemasan, & Stress (90% Selesai)")

        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); color: white; padding: 22px 26px; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 8px 20px -4px rgba(49, 46, 129, 0.3);">
            <h2 style="color: white; margin: 0 0 8px 0; font-size: 22px;">🌿 Segmen 2: Kondisi Depresi, Kecemasan, dan Stress (DASS-21)</h2>
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
    # STEP 11: HASIL SUBMIT & PROFIL RADAR INDIVIDU
    # -------------------------------------------------------------
    elif curr_step == 11:
        res = st.session_state["submission_result"]
        st.balloons()

        st.success("🎉 Terima kasih! Jawaban survei Anda (Segmen 1 & Segmen 2) telah berhasil disimpan.")
        
        # Info penyimpanan
        if res and res.get("gsheet_saved"):
            st.caption("✅ Data telah berhasil disinkronkan ke Google Spreadsheet dan backup lokal.")
        else:
            st.caption("✅ Data telah tersimpan secara aman di penyimpanan lokal (data_survei.csv).")

        # Visualisasi Skor Segmen 1
        if res and "cat_scores" in res:
            cat_scores = res["cat_scores"]
            overall_score = res.get("overall_score", 0)

            st.markdown("### 📊 Hasil Segmen 1: Profil Risiko Psikososial Kerja")

            col_sc1, col_sc2 = st.columns([1, 2])
            with col_sc1:
                with st.container(border=True):
                    st.markdown("#### 🏆 Ringkasan Skor Segmen 1")
                    st.metric("ID Responden", res.get("id_responden", "-"))
                    st.metric("Skor Rata-Rata Total", f"{overall_score} / 100")
                    st.divider()
                    st.caption("Skor dihitung dari skala 0 (Terendah) sampai 100 (Tertinggi) berdasarkan bobot penilaian standar psikososial kerja.")

            with col_sc2:
                # Radar Chart Skor Pribadi
                categories = [CATEGORY_METADATA[k]["short"] for k in categories_list]
                scores = [cat_scores.get(k, 0) for k in categories_list]
                categories_closed = categories + [categories[0]]
                scores_closed = scores + [scores[0]]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=scores_closed,
                    theta=categories_closed,
                    fill='toself',
                    fillcolor='rgba(37, 99, 235, 0.25)',
                    line=dict(color='#2563eb', width=2),
                    name='Skor Anda'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    title="Grafik Radar Profil Psikososial Anda (Segmen 1)",
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=360
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # Visualisasi Rincian Skor per Sub-Dimensi Segmen 1
            sub_scores = res.get("sub_scores") if res else None
            if not sub_scores and res and "answers" in st.session_state:
                sub_scores = calculate_subdimension_scores(st.session_state["answers"])

            if sub_scores:
                with st.expander("🔬 Lihat Visualisasi Barchart Horizontal Sub-Dimensi (45 Sub-Bidang)", expanded=True):
                    st.caption("Visualisasi barchart horizontal per sub-bidang dengan batas kategori **Rendah (0 - 33,33)**, **Sedang (33,34 - 66,66)**, dan **Tinggi (66,67 - 100)**.")

                    selected_view_cat = st.selectbox(
                        "Pilih Dimensi untuk Melihat Detail Sub-Bidang:",
                        options=categories_list,
                        format_func=lambda x: f"{CATEGORY_METADATA.get(x, {}).get('icon', '📁')} {CATEGORY_METADATA.get(x, {}).get('label', x)}",
                        key="resp_sub_dim_selector"
                    )

                    c_meta = CATEGORY_METADATA.get(selected_view_cat, {"label": selected_view_cat, "icon": "📁"})
                    sub_list = SUBDIMENSIONS_BY_CATEGORY.get(selected_view_cat, [])

                    resp_chart_items = []
                    resp_tbl_rows = []
                    for idx, s in enumerate(sub_list, 1):
                        val = float(sub_scores.get(s, 0.0))
                        lbl_info = SUBDIMENSION_LABELS.get(s, {"en": s, "id": s})
                        disp_name = f"{lbl_info['en']} ({lbl_info['id']})"
                        lvl = get_score_level(val)
                        pol = SUBDIMENSION_POLARITY.get(s, "Favorable")
                        _, stat_text, clr = get_subdimension_status(s, val)

                        resp_chart_items.append({
                            "name": disp_name,
                            "score": val,
                            "level": lvl,
                            "color": clr,
                            "polarity": pol,
                            "status": stat_text
                        })
                        resp_tbl_rows.append({
                            "No": idx,
                            "Sub-Bidang": disp_name,
                            "Sifat": pol,
                            "Skor Anda": val,
                            "Kategori": lvl,
                            "Status Risiko": stat_text
                        })

                    fig_resp_hbar = go.Figure()
                    fig_resp_hbar.add_trace(go.Bar(
                        y=[it["name"] for it in resp_chart_items],
                        x=[it["score"] for it in resp_chart_items],
                        orientation="h",
                        marker=dict(
                            color=[it["color"] for it in resp_chart_items],
                            line=dict(color="rgba(0,0,0,0.15)", width=1)
                        ),
                        text=[f" <b>{it['score']:.1f}</b> ({it['level']})" for it in resp_chart_items],
                        textposition="outside",
                        cliponaxis=False,
                        customdata=[[it["level"], it["polarity"], it["status"]] for it in resp_chart_items],
                        hovertemplate="<b>%{y}</b><br>Skor Anda: <b>%{x:.1f}</b> / 100<br>Kategori: <b>%{customdata[0]}</b><br>Sifat: %{customdata[1]}<br>Status: %{customdata[2]}<extra></extra>"
                    ))

                    fig_resp_hbar.add_vline(x=33.33, line_dash="dash", line_color="#94a3b8", line_width=1.5,
                                            annotation_text="Batas Rendah (33.33)", annotation_position="top right")
                    fig_resp_hbar.add_vline(x=66.67, line_dash="dash", line_color="#94a3b8", line_width=1.5,
                                            annotation_text="Batas Tinggi (66.67)", annotation_position="top right")

                    fig_resp_hbar.update_layout(
                        title=dict(
                            text=f"Detail Subdimensi: {c_meta.get('label', selected_view_cat)}",
                            font=dict(size=15, color="#0f172a")
                        ),
                        xaxis=dict(range=[0, 115], title="Skor Penilaian (0 - 100)", gridcolor="#f1f5f9"),
                        yaxis=dict(title="", autorange="reversed", tickfont=dict(size=12)),
                        height=max(320, len(sub_list) * 55),
                        margin=dict(l=20, r=40, t=60, b=40),
                        plot_bgcolor="white",
                        paper_bgcolor="white"
                    )
                    st.plotly_chart(fig_resp_hbar, use_container_width=True)
                    st.dataframe(pd.DataFrame(resp_tbl_rows), use_container_width=True, hide_index=True)

        # Visualisasi Skor Segmen 2
        if res and "seg2_scores" in res:
            seg2_scores = res["seg2_scores"]
            seg2_severity = res.get("seg2_severity", {})

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("### 🌿 Hasil Segmen 2: Kondisi Kesehatan Mental (DASS-21)")
            st.caption("Skor rentang 0-42 per dimensi (skor total dikalikan 2) dengan kategori standar DASS-21.")

            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                dep_score = seg2_scores.get("Depresi", 0)
                dep_sev = seg2_severity.get("Depresi", "Normal")
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #3b82f6;">
                    <div class="metric-title">🌧️ Depresi</div>
                    <div class="metric-value">{dep_score} <span style="font-size:16px;color:#64748b;">/ 42</span></div>
                    <div class="metric-subtitle">Tingkat: <b>{dep_sev}</b></div>
                </div>
                """, unsafe_allow_html=True)

            with col_d2:
                anx_score = seg2_scores.get("Kecemasan", 0)
                anx_sev = seg2_severity.get("Kecemasan", "Normal")
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                    <div class="metric-title">⚡ Kecemasan</div>
                    <div class="metric-value">{anx_score} <span style="font-size:16px;color:#64748b;">/ 42</span></div>
                    <div class="metric-subtitle">Tingkat: <b>{anx_sev}</b></div>
                </div>
                """, unsafe_allow_html=True)

            with col_d3:
                str_score = seg2_scores.get("Stress", 0)
                str_sev = seg2_severity.get("Stress", "Normal")
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #ef4444;">
                    <div class="metric-title">🔥 Stress</div>
                    <div class="metric-value">{str_score} <span style="font-size:16px;color:#64748b;">/ 42</span></div>
                    <div class="metric-subtitle">Tingkat: <b>{str_sev}</b></div>
                </div>
                """, unsafe_allow_html=True)

            # Bar Chart Visualisasi DASS-21
            dass_df = pd.DataFrame([
                {"Dimensi": "Depresi", "Skor": dep_score, "Tingkat": dep_sev},
                {"Dimensi": "Kecemasan", "Skor": anx_score, "Tingkat": anx_sev},
                {"Dimensi": "Stress", "Skor": str_score, "Tingkat": str_sev}
            ])
            fig_dass_bar = px.bar(
                dass_df,
                x="Dimensi",
                y="Skor",
                color="Tingkat",
                color_discrete_map={
                    "Normal": "#10b981",
                    "Ringan": "#3b82f6",
                    "Sedang": "#f59e0b",
                    "Berat": "#ea580c",
                    "Sangat Berat": "#dc2626"
                },
                text="Skor"
            )
            fig_dass_bar.update_layout(
                yaxis=dict(range=[0, 44], title="Skor DASS-21 (0 - 42)"),
                height=280,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_dass_bar, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        if st.button("📝 Isi Survei untuk Responden Baru", use_container_width=True):
            st.session_state["consent_given"] = False
            st.session_state["step"] = 0
            st.session_state["answers"] = {}
            st.session_state["answers_segmen2"] = {}
            st.session_state["submission_result"] = None
            st.rerun()

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

    # Info Sumber Data
    st.markdown(f"**Sumber Data Terkoneksi:** `{source_info}` | Total Baris: **{len(df)} Responden**")

    # -------------------------------------------------------------
    # FILTER BAR
    # -------------------------------------------------------------
    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
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

    # Terapkan Filter
    df_filtered = df.copy()
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
                <div class="metric-title">🌧️ Rata-Rata Skor Depresi (Segmen 2)</div>
                <div class="metric-value">{avg_dep} <span style="font-size:16px;color:#64748b;">/42</span></div>
                <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m6:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                <div class="metric-title">⚡ Rata-Rata Skor Kecemasan (Segmen 2)</div>
                <div class="metric-value">{avg_anx} <span style="font-size:16px;color:#64748b;">/42</span></div>
                <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m7:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #ef4444;">
                <div class="metric-title">🔥 Rata-Rata Skor Stress (Segmen 2)</div>
                <div class="metric-value">{avg_str} <span style="font-size:16px;color:#64748b;">/42</span></div>
                <div class="metric-subtitle">Rentang DASS-21 (0 - 42)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # GRAFIK 1: RADAR CHART PROFIL 8 DIMENSI
        # -------------------------------------------------------------
        col_g1, col_g2 = st.columns([3, 2])

        with col_g1:
            with st.container(border=True):
                st.markdown("#### 🕸️ Profil Rata-Rata 8 Dimensi Psikososial")
                st.caption("Diagram radar menunjukkan keseimbangan antara aspek tuntutan kerja, sumber daya kerja, dan status kesehatan.")

                dim_names = [CATEGORY_METADATA[k]["short"] for k in categories_list]
                dim_cols = [DIMENSION_COLUMNS[k] for k in categories_list]
                
                # Rata-rata terfilter
                filtered_avgs = [round(df_filtered[col].mean(), 1) if col in df_filtered.columns else 0.0 for col in dim_cols]
                
                # Rata-rata benchmark seluruh populasi
                population_avgs = [round(df[col].mean(), 1) if col in df.columns else 0.0 for col in dim_cols]

                # Tutup loop radar
                dim_names_closed = dim_names + [dim_names[0]]
                filtered_avgs_closed = filtered_avgs + [filtered_avgs[0]]
                population_avgs_closed = population_avgs + [population_avgs[0]]

                fig_radar_dash = go.Figure()

                fig_radar_dash.add_trace(go.Scatterpolar(
                    r=filtered_avgs_closed,
                    theta=dim_names_closed,
                    fill='toself',
                    fillcolor='rgba(13, 148, 136, 0.25)',
                    line=dict(color='#0d9488', width=2.5),
                    name='Rata-Rata Terfilter'
                ))

                fig_radar_dash.add_trace(go.Scatterpolar(
                    r=population_avgs_closed,
                    theta=dim_names_closed,
                    line=dict(color='#94a3b8', width=1.5, dash='dash'),
                    name='Benchmark Seluruh Data'
                ))

                fig_radar_dash.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                    margin=dict(l=30, r=30, t=30, b=30),
                    height=420
                )
                st.plotly_chart(fig_radar_dash, use_container_width=True)

        with col_g2:
            with st.container(border=True):
                st.markdown("#### 🏢 Distribusi Responden per Bidang")
                st.caption("Proporsi kontribusi responden dari masing-masing 4 bidang kerja.")

                if "Bidang" in df_filtered.columns:
                    bidang_counts = df_filtered["Bidang"].value_counts().reset_index()
                    bidang_counts.columns = ["Bidang", "Jumlah"]

                    color_map = {
                        "Keselamatan Kerja": "#ef4444",
                        "Kesehatan Kerja": "#10b981",
                        "Psikologi": "#3b82f6",
                        "Hiegene Industri dan Bahan Berbahaya": "#f59e0b"
                    }

                    fig_donut = px.pie(
                        bidang_counts,
                        names="Bidang",
                        values="Jumlah",
                        hole=0.45,
                        color="Bidang",
                        color_discrete_map=color_map
                    )
                    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                    fig_donut.update_layout(
                        showlegend=False,
                        margin=dict(l=10, r=10, t=20, b=20),
                        height=420
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # GRAFIK 2: PERBANDINGAN SKOR DIMENSI ANTAR 4 BIDANG
        # -------------------------------------------------------------
        with st.container(border=True):
            st.markdown("#### 📊 Perbandingan Rata-Rata Dimensi Antara 4 Bidang Kerja")
            st.caption("Menganalisis disparitas kondisi kerja antar bidang (Keselamatan Kerja, Kesehatan Kerja, Psikologi, Hiegene Industri).")

            # Hitung rata-rata per bidang
            comparison_rows = []
            for b in BIDANG_OPTIONS:
                b_df = df[df["Bidang"] == b] if "Bidang" in df.columns else pd.DataFrame()
                if not b_df.empty:
                    for k in categories_list:
                        col = DIMENSION_COLUMNS[k]
                        short_name = CATEGORY_METADATA[k]["short"]
                        val = round(b_df[col].mean(), 1) if col in b_df.columns else 0.0
                        comparison_rows.append({
                            "Bidang": b,
                            "Dimensi": short_name,
                            "Skor": val
                        })

            if comparison_rows:
                df_comp = pd.DataFrame(comparison_rows)
                fig_bar = px.bar(
                    df_comp,
                    x="Dimensi",
                    y="Skor",
                    color="Bidang",
                    barmode="group",
                    color_discrete_map={
                        "Keselamatan Kerja": "#ef4444",
                        "Kesehatan Kerja": "#10b981",
                        "Psikologi": "#3b82f6",
                        "Hiegene Industri dan Bahan Berbahaya": "#f59e0b"
                    },
                    text="Skor"
                )
                fig_bar.update_traces(textposition="outside", cliponaxis=False)
                fig_bar.update_layout(
                    yaxis=dict(range=[0, 110], title="Skor Rata-Rata (0 - 100)"),
                    xaxis=dict(title=""),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=450,
                    margin=dict(l=20, r=20, t=60, b=40)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

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
                chart_items = []
                tbl_rows = []
                for idx, s_name in enumerate(subs_in_cat, 1):
                    col_s = SUBDIMENSION_COLUMNS.get(s_name)
                    if col_s and col_s in df_scope.columns:
                        s_series = pd.to_numeric(df_scope[col_s], errors='coerce').dropna()
                        avg_val = round(s_series.mean(), 1) if not s_series.empty else 0.0
                    else:
                        avg_val = 0.0

                    label_info = SUBDIMENSION_LABELS.get(s_name, {"en": s_name, "id": s_name})
                    display_label = f"{label_info['en']} ({label_info['id']})"
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
                    tbl_rows.append({
                        "No": idx,
                        "Sub-Bidang": display_label,
                        "Sifat": polarity,
                        "Skor": avg_val,
                        "Kategori": level,
                        "Status Risiko": status_text
                    })

                # Visualisasi Barchart Horizontal Plotly
                y_labels = [item["name"] for item in chart_items]
                scores = [item["score"] for item in chart_items]
                colors = [item["color"] for item in chart_items]
                texts = [f" <b>{item['score']:.1f}</b> ({item['level']})" for item in chart_items]
                customdata = [[item["level"], item["polarity"], item["status"]] for item in chart_items]

                fig_sub_hbar = go.Figure()
                fig_sub_hbar.add_trace(go.Bar(
                    y=y_labels,
                    x=scores,
                    orientation="h",
                    marker=dict(
                        color=colors,
                        line=dict(color="rgba(0,0,0,0.15)", width=1)
                    ),
                    text=texts,
                    textposition="outside",
                    cliponaxis=False,
                    customdata=customdata,
                    hovertemplate="<b>%{y}</b><br>Skor Rata-Rata: <b>%{x:.1f}</b> / 100<br>Kategori: <b>%{customdata[0]}</b><br>Sifat: %{customdata[1]}<br>Status Risiko: %{customdata[2]}<extra></extra>"
                ))

                # Garis batas ketentuan kategori
                fig_sub_hbar.add_vline(
                    x=33.33, line_dash="dash", line_color="#94a3b8", line_width=1.5,
                    annotation_text="Batas Rendah (33.33)", annotation_position="top right",
                    annotation_font=dict(size=10.5, color="#64748b")
                )
                fig_sub_hbar.add_vline(
                    x=66.67, line_dash="dash", line_color="#94a3b8", line_width=1.5,
                    annotation_text="Batas Tinggi (66.67)", annotation_position="top right",
                    annotation_font=dict(size=10.5, color="#64748b")
                )

                fig_sub_hbar.update_layout(
                    title=dict(
                        text=f"📊 Barchart Horizontal: {c_meta.get('label', selected_sub_category)} — {scope_label}",
                        font=dict(size=15, color="#0f172a")
                    ),
                    xaxis=dict(
                        range=[0, 115],
                        title="Skor Rata-Rata Sub-Bidang (0 - 100)",
                        tickvals=[0, 20, 33.33, 50, 66.67, 80, 100],
                        gridcolor="#f1f5f9"
                    ),
                    yaxis=dict(
                        title="",
                        autorange="reversed",
                        tickfont=dict(size=12, color="#1e293b")
                    ),
                    height=max(360, len(y_labels) * 58),
                    margin=dict(l=20, r=40, t=60, b=40),
                    plot_bgcolor="white",
                    paper_bgcolor="white"
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
            st.markdown("#### 🌿 Analisis Segmen 2: Kondisi Depresi, Kecemasan, & Stress (DASS-21)")
            st.caption("Pemantauan tingkat Depresi, Kecemasan, dan Stress berdasarkan bidang kerja dan kategori keparahan.")

            col_dass1, col_dass2 = st.columns([3, 2])
            with col_dass1:
                # Perbandingan Rata-Rata DASS-21 per Bidang Kerja
                dass_comp_rows = []
                for b in BIDANG_OPTIONS:
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
                        text="Skor",
                        title="Rata-Rata Skor DASS-21 per Bidang Kerja"
                    )
                    fig_dass_bidang.update_traces(textposition="outside")
                    fig_dass_bidang.update_layout(
                        yaxis=dict(range=[0, 45], title="Skor Rata-Rata (0 - 42)"),
                        xaxis=dict(title=""),
                        height=360,
                        margin=dict(l=20, r=20, t=40, b=30)
                    )
                    st.plotly_chart(fig_dass_bidang, use_container_width=True)

            with col_dass2:
                # Distribusi Tingkat Keparahan Stress / Depresi / Kecemasan
                dim_choice = st.selectbox("Pilih Dimensi untuk Distribusi Keparahan:", ["Depresi", "Kecemasan", "Stress"], key="dash_dass_dim_sel")
                sev_col = f"Tingkat_{dim_choice}"
                if sev_col in df_filtered.columns:
                    cat_order = ["Normal", "Ringan", "Sedang", "Berat", "Sangat Berat"]
                    sev_series = pd.Categorical(df_filtered[sev_col], categories=cat_order, ordered=True)
                    sev_counts = sev_series.value_counts().reset_index()
                    sev_counts.columns = ["Tingkat", "Jumlah"]
                    sev_counts = sev_counts[sev_counts["Jumlah"] > 0]

                    fig_sev_pie = px.pie(
                        sev_counts,
                        names="Tingkat",
                        values="Jumlah",
                        hole=0.4,
                        title=f"Distribusi Tingkat {dim_choice}",
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
                    fig_sev_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_sev_pie.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=20))
                    st.plotly_chart(fig_sev_pie, use_container_width=True)
                else:
                    st.info(f"Belum ada data rekaman tingkat {dim_choice} Segmen 2 pada dataset ini.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # TABEL DATA LENGKAP & EXPORT KE EXCEL / CSV
        # -------------------------------------------------------------
        with st.container(border=True):
            st.markdown("#### 📑 Rekapitulasi Data Responden")
            
            # Kolom ringkasan yang nyaman dibaca mencakup Segmen 1, Sub-Dimensi, dan Segmen 2
            summary_cols = (
                ["ID_Responden", "Waktu_Pengisian", "Bidang", "Nama_Inisial", "Jenis_Kelamin", "Rentang_Usia", "Masa_Kerja", "Jabatan"]
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
