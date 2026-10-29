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
    get_question_options,
    calculate_score,
    calculate_category_scores
)

from scoring_map import(calculate_score, calculate_category_scores)

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

    /* Question Card */
    .question-card {
        background: #ffffff;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .question-text {
        font-size: 14.5px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 10px;
    }
    .question-id-badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        margin-bottom: 8px;
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
        "bidang": BIDANG_OPTIONS[0],
        "nama": "",
        "gender": "Laki-laki",
        "usia": "25 - 34 tahun",
        "masa_kerja": "1 - 3 tahun",
        "jabatan": "Staf Pelaksana",
        "riwayat_penyakit": "Tidak",
        "nama_penyakit": "-",
        "berat_badan": 60,
        "tinggi_badan": 165,
        "status_perkawinan": "Belum menikah"
    }

if "answers" not in st.session_state:
    st.session_state["answers"] = {}

if "submission_result" not in st.session_state:
    st.session_state["submission_result"] = None

# =====================================================================
# 3. SIDEBAR NAVIGATION & KONTROL AKSES
# =====================================================================
with st.sidebar:
    st.markdown("### 🧠 Psikologi Kerja")
    st.markdown("<p style='font-size:12px; color:#64748b; margin-top:-10px;'>Sistem Penilaian Risiko Psikososial Kerja</p>", unsafe_allow_html=True)
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
        <p>Survei ini bertujuan untuk memetakan kondisi beban kerja, kepemimpinan, dan kesejahteraan psikologis karyawan di lingkungan kerja Anda.</p>
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

            Kami mengundang Anda untuk berpartisipasi dalam **Survei Evaluasi Risiko Psikososial Kerja**. Survei ini bertujuan untuk memetakan kondisi tuntutan kerja, organisasi kerja, hubungan kerja & kepemimpinan, kepuasan kerja, serta kesehatan dan kesejahteraan psikologis pegawai.

            Sebelum melanjutkan, mohon perhatikan ketentuan etika dan kerahasiaan berikut:
            
            1. **Sifat Partisipasi Sukarela**: Partisipasi Anda dalam survei ini sepenuhnya bersifat **sukarela (voluntary)**. Anda berhak untuk menolak berpartisipasi atau menghentikan pengisian kapan saja tanpa dampak negatif maupun sanksi apa pun.
            2. **Jaminan Kerahasiaan & Anonimitas**: Seluruh data dan jawaban yang Anda berikan bersifat **rahasia**. Identitas nama dapat diisi secara anonim / menggunakan inisial. Laporan dan analisis survei disajikan secara **agregat (kelompok)**, bukan untuk evaluasi kinerja personal individu.
            3. **Tujuan Penggunaan Data**: Data yang terkumpul hanya akan digunakan untuk kepentingan evaluasi organisasi, pengembangan program Keselamatan dan Kesehatan Kerja (K3), serta perbaikan iklim lingkungan kerja.
            4. **Waktu Pengisian**: Kuesioner ini dirancang ringkas dengan estimasi waktu pengisian sekitar **5 – 7 menit**.
            5. **Objektivitas Respon**: Tidak ada penilaian benar atau salah. Kami sangat mengharapkan jawaban yang paling menggambarkan kondisi dan pengalaman kerja nyata Anda selama 3 bulan terakhir.
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
        st.markdown("### 👤 Langkah 1 dari 10: Pengisian Data Diri & Asal Bidang")
        st.info("Pilih asal bidang dan data diri Anda. Identitas nama/inisial dapat diisi dengan nama samaran/anonim jika diinginkan.")

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_bidang = st.selectbox(
                    "Asal Bidang Kerja *",
                    options=BIDANG_OPTIONS,
                    index=BIDANG_OPTIONS.index(st.session_state["biodata"]["bidang"]) if st.session_state["biodata"]["bidang"] in BIDANG_OPTIONS else 0,
                    help="Pilih salah satu dari 4 bidang penugasan kerja Anda."
                )
                nama_input = st.text_input(
                    "Nama Lengkap / Inisial (Opsional)",
                    value=st.session_state["biodata"]["nama"],
                    placeholder="Contoh: Responden A / John Doe"
                )
                gender_input = st.radio(
                    "Jenis Kelamin",
                    options=["Laki-laki", "Perempuan"],
                    index=0 if st.session_state["biodata"]["gender"] == "Laki-laki" else 1,
                    horizontal=True
                )
                riwayat_input = st.radio("Apakah Anda mempunyai riwayat penyakit?", options=["Tidak", "Ya"],
                                        index=0 if st.session_state["biodata"].get("riwayat_penyakit", "Tidak") == "Tidak" else 1,
                                        horizontal=True)
                
                # Input kondisional 
                nama_penyakit = "-"
                if riwayat_input == "Ya":
                    nama_penyakit = st.text_input("Jika iya, penyakit apa?", value="" if st.session_state["biodata"].get("nama_penyakit") == "-"
                    else st.session_state["biodata"].get("nama_penyakit", ""),
                    placeholder="Contoh: Asma, Asam Lambung, Hipertensi, dll.")
                
                # Berat badan & Tinggi badan
                col_bb, col_tb = st.columns(2)
                with col_bb:
                    bb_input = st.number_input("Berat Badan (kg)", min_value=30, max_value=200,
                                                value=int(st.session_state["biodata"].get("berat_badan", 60)), step=1)
                with col_tb:
                    tb_input = st.number_input("Tinggi Badan (cm)", min_value=100, max_value=220,
                                                value=int(st.session_state["biodata"].get("tinggi_badan", 165)), step=1)

            with col2:
                usia_options = ["< 25 tahun", "25 - 34 tahun", "35 - 44 tahun", "45 - 54 tahun", "≥ 55 tahun"]
                usia_input = st.selectbox(
                    "Rentang Usia",
                    options=usia_options,
                    index=usia_options.index(st.session_state["biodata"]["usia"]) if st.session_state["biodata"]["usia"] in usia_options else 1
                )
                masa_kerja_options = ["< 1 tahun", "1 - 3 tahun", "4 - 10 tahun", "> 10 tahun"]
                masa_kerja_input = st.selectbox(
                    "Masa Kerja",
                    options=masa_kerja_options,
                    index=masa_kerja_options.index(st.session_state["biodata"]["masa_kerja"]) if st.session_state["biodata"]["masa_kerja"] in masa_kerja_options else 1
                )
                jabatan_options = ["Staf Pelaksana", "Pengawas / Koordinator", "Fungsional Ahli", "Manajemen / Struktural", "Lainnya"]
                jabatan_input = st.selectbox(
                    "Posisi / Jabatan",
                    options=jabatan_options,
                    index=jabatan_options.index(st.session_state["biodata"]["jabatan"]) if st.session_state["biodata"]["jabatan"] in jabatan_options else 0
                )
                status_perkawinan = ["Sudah menikah", "Belum menikah", "Cerai mati", "Cerai hidup"]
                status_perkawinan = st.selectbox(
                    "Status Pernikahan",
                    options = status_perkawinan,
                    index = status_perkawinan.index(st.session_state["biodata"]["status_perkawinan"]) if st.session_state["biodata"]["status_perkawinan"] in status_perkawinan else 0
                )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns([1, 2])
        with col_b1:
            if st.button("⬅️ Lembar Persetujuan", use_container_width=True):
                st.session_state["consent_given"] = False
                st.rerun()
        with col_b2:
            if st.button("Mulai Mengisi Kuesioner ➡️", type="primary", use_container_width=True):
                st.session_state["biodata"]["bidang"] = selected_bidang
                st.session_state["biodata"]["nama"] = nama_input.strip() if nama_input.strip() else "Anonim"
                st.session_state["biodata"]["gender"] = gender_input
                st.session_state["biodata"]["usia"] = usia_input
                st.session_state["biodata"]["masa_kerja"] = masa_kerja_input
                st.session_state["biodata"]["jabatan"] = jabatan_input
                st.session_state["biodata"]["riwayat_penyakit"] = riwayat_input
                st.session_state["biodata"]["nama_penyakit"] = nama_penyakit.strip() if nama_penyakit.strip() else "-"
                st.session_state["biodata"]["berat_badan"] = bb_input
                st.session_state["biodata"]["tinggi_badan"] = tb_input
                st.session_state["biodata"]["status_perkawinan"] = status_perkawinan
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
        progress_val = int((curr_step / (len(categories_list) + 1)) * 100)
        st.progress(progress_val, text=f"Langkah {curr_step + 1} dari 10: {meta['label']} ({progress_val}% Selesai)")

        # Section Header
        st.markdown(f"### {meta['icon']} Bagian {curr_step}: {meta['label']}")
        st.caption(f"{meta['desc']} (Total: {len(questions)} butir pertanyaan)")
        st.divider()

        # Iterate Questions
        unanswered_ids = []
        for idx, q in enumerate(questions, 1):
            qid = q["id"]
            code = q["code"]
            q_text = q["text"]
            saved_val = st.session_state["answers"].get(qid, None)

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

            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <span class="question-id-badge">{qid}</span>
                    <div class="question-text">{idx}. {q_text}</div>
                </div>
                """, unsafe_allow_html=True)

                if is_5m_skipped:
                    st.info("ℹ️ Pertanyaan ini otomatis dilewati karena pada pertanyaan sebelumnya Anda memilih 'Tidak ada sama sekali'.")
                elif code == "5M":
                    options = get_question_options(code)
                    cur_val = saved_val if saved_val in options else options[-1]
                    sel_ans = st.selectbox(
                        "Pilih pihak yang bersangkutan:",
                        options=options,
                        index=options.index(cur_val) if cur_val in options else 0,
                        key=f"q_{qid}"
                    )
                    st.session_state["answers"][qid] = sel_ans
                elif code == "8":
                    # Numerical scale 0 to 10
                    default_val = int(saved_val) if saved_val is not None and str(saved_val).isdigit() else 7
                    sel_ans = st.slider(
                        "Skala 0 (Terburuk) hingga 10 (Terbaik):",
                        min_value=0,
                        max_value=10,
                        value=default_val,
                        key=f"q_{qid}"
                    )
                    st.session_state["answers"][qid] = str(sel_ans)
                else:
                    options = get_question_options(code)
                    # Radio option
                    cur_idx = None
                    if saved_val in options:
                        cur_idx = options.index(saved_val)
                    
                    sel_ans = st.radio(
                        "Pilihan Jawaban:",
                        options=options,
                        index=cur_idx,
                        key=f"q_{qid}",
                        horizontal=True
                    )
                    if sel_ans is not None:
                        st.session_state["answers"][qid] = sel_ans
                    else:
                        unanswered_ids.append(f"No. {idx} ({qid})")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        st.divider()
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.button("⬅️ Sebelumnya", use_container_width=True):
                st.session_state["step"] = curr_step - 1
                st.rerun()

        with col_next:
            next_label = "Tinjau & Kirim ➡️" if curr_step == len(categories_list) else "Selanjutnya ➡️"
            if st.button(next_label, type="primary", use_container_width=True):
                # Validasi kelengkapan pertanyaan di bagian ini
                missing = [q["id"] for q in questions if q["id"] not in st.session_state["answers"] or st.session_state["answers"][q["id"]] is None]
                if missing:
                    st.warning(f"⚠️ Masih ada {len(missing)} pertanyaan pada bagian ini yang belum dijawab. Mohon lengkapi semua sebelum melanjutkan.")
                else:
                    st.session_state["step"] = curr_step + 1
                    st.rerun()

    # -------------------------------------------------------------
    # STEP 9: RINGKASAN & KONFIRMASI PENGIRIMAN
    # -------------------------------------------------------------
    elif curr_step == 9:
        st.markdown("### 📋 Langkah 10: Tinjau dan Kirim Jawaban Survei")
        st.info("Seluruh pertanyaan telah berhasil diisi. Silakan periksa ringkasan data diri Anda sebelum menekan tombol Kirim.")

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

        with col2:
            with st.container(border=True):
                st.markdown("#### 📊 Kelengkapan Pengisian")
                total_q = sum(len(qs) for qs in SURVEY_QUESTIONS.values())
                answered_q = len(st.session_state["answers"])
                st.metric("Total Pertanyaan Terjawab", f"{answered_q} / {total_q}", "100% Lengkap")
                st.caption("Semua 8 dimensi psikologi telah siap diproses dan dikirim ke basis data.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        col_back, col_submit = st.columns([1, 2])
        with col_back:
            if st.button("⬅️ Kembali Periksa Jawaban", use_container_width=True):
                st.session_state["step"] = 8
                st.rerun()

        with col_submit:
            if st.button("🚀 Kirim Jawaban Survei Sekarang", type="primary", use_container_width=True):
                with st.spinner("Menyimpan jawaban ke database..."):
                    res = save_survey_response(st.session_state["biodata"], st.session_state["answers"])
                    st.session_state["submission_result"] = res
                    st.session_state["step"] = 10
                    st.rerun()

    # -------------------------------------------------------------
    # STEP 10: HASIL SUBMIT & PROFIL RADAR INDIVIDU
    # -------------------------------------------------------------
    elif curr_step == 10:
        res = st.session_state["submission_result"]
        st.balloons()

        st.success("🎉 Terima kasih! Jawaban survei Anda telah berhasil disimpan.")
        
        # Info penyimpanan
        if res and res.get("gsheet_saved"):
            st.caption("✅ Data telah berhasil disinkronkan ke Google Spreadsheet dan backup lokal.")
        else:
            st.caption("✅ Data telah tersimpan secara aman di penyimpanan lokal (data_survei.csv).")

        if res and "cat_scores" in res:
            cat_scores = res["cat_scores"]
            overall_score = res.get("overall_score", 0)

            col_sc1, col_sc2 = st.columns([1, 2])
            with col_sc1:
                with st.container(border=True):
                    st.markdown("#### 🏆 Ringkasan Skor Anda")
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
                    title="Grafik Radar Profil Psikososial Anda",
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=380
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        if st.button("📝 Isi Survei untuk Responden Baru", use_container_width=True):
            st.session_state["consent_given"] = False
            st.session_state["step"] = 0
            st.session_state["answers"] = {}
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
        # -------------------------------------------------------------
        # METRIC CARDS
        # -------------------------------------------------------------
        total_resp = len(df_filtered)
        avg_overall = round(df_filtered["Skor_Rata_Rata_Total"].mean(), 1) if "Skor_Rata_Rata_Total" in df_filtered.columns else 0.0
        avg_health = round(df_filtered["Skor_Kesehatan_Wellbeing"].mean(), 1) if "Skor_Kesehatan_Wellbeing" in df_filtered.columns else 0.0
        avg_demands = round(df_filtered["Skor_Tuntutan_Kerja"].mean(), 1) if "Skor_Tuntutan_Kerja" in df_filtered.columns else 0.0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
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
                <div class="metric-title">⭐ Rata-Rata Total Skor</div>
                <div class="metric-value">{avg_overall} <span style="font-size:16px;color:#64748b;">/100</span></div>
                <div class="metric-subtitle">Indeks komposit organisasi</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">❤️ Kesehatan & Well-being</div>
                <div class="metric-value">{avg_health} <span style="font-size:16px;color:#64748b;">/100</span></div>
                <div class="metric-subtitle">Indeks kesejahteraan fisik/mental</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⏳ Tuntutan Kerja</div>
                <div class="metric-value">{avg_demands} <span style="font-size:16px;color:#64748b;">/100</span></div>
                <div class="metric-subtitle">Indeks beban & tempo kerja</div>
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
        # GRAFIK 3: ANALISIS INSIDENSI PERILAKU OFENSIF (BAGIAN 6)
        # -------------------------------------------------------------
        with st.container(border=True):
            st.markdown("#### ⚠️ Pemantauan Konflik & Perilaku Ofensif di Tempat Kerja")
            st.caption("Deteksi paparan insiden perilaku tidak menyenangkan dalam 12 bulan terakhir.")

            offensive_questions = [
                ("T6_Q1", "Gosip / Fitnah"),
                ("T6_Q3", "Konflik / Pertengkaran"),
                ("T6_Q5", "Ejekan"),
                ("T6_Q7", "Gangguan Online / Pesan"),
                ("T6_Q9", "Perilaku Seksual"),
                ("T6_Q11", "Ancaman Kekerasan"),
                ("T6_Q13", "Kekerasan Fisik"),
                ("T6_Q15", "Perundungan (Bullying)")
            ]

            incident_stats = []
            for qid, label in offensive_questions:
                if qid in df_filtered.columns:
                    # Persentase yang bukan 'Tidak ada sama sekali'
                    total_cnt = len(df_filtered)
                    exposed = df_filtered[df_filtered[qid] != "Tidak ada sama sekali"]
                    cnt = len(exposed)
                    pct = round((cnt / total_cnt) * 100, 1) if total_cnt > 0 else 0
                    incident_stats.append({
                        "Jenis Insiden": label,
                        "Jumlah Responden": cnt,
                        "Persentase Terpapar (%)": pct
                    })

            if incident_stats:
                df_inc = pd.DataFrame(incident_stats)
                fig_inc = px.bar(
                    df_inc,
                    x="Persentase Terpapar (%)",
                    y="Jenis Insiden",
                    orientation="h",
                    color="Persentase Terpapar (%)",
                    color_continuous_scale="Reds",
                    text="Persentase Terpapar (%)"
                )
                fig_inc.update_traces(texttemplate='%{text}%', textposition='outside')
                fig_inc.update_layout(
                    xaxis=dict(range=[0, 100], title="Persentase Responden (%)"),
                    yaxis=dict(autorange="reversed", title=""),
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig_inc, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # TABEL DATA LENGKAP & EXPORT KE EXCEL / CSV
        # -------------------------------------------------------------
        with st.container(border=True):
            st.markdown("#### 📑 Rekapitulasi Data Responden")
            
            # Kolom ringkasan yang nyaman dibaca
            summary_cols = ["ID_Responden", "Waktu_Pengisian", "Bidang", "Nama_Inisial", "Jenis_Kelamin", "Rentang_Usia", "Masa_Kerja", "Jabatan"] + list(DIMENSION_COLUMNS.values()) + ["Skor_Rata_Rata_Total"]
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

    with st.container(border=True):
        st.markdown("### 📖 Cara Menghubungkan ke Google Spreadsheet")
        st.markdown("""
        Untuk menghubungkan aplikasi ini secara otomatis ke Google Sheets:

        1. **Buat Google Spreadsheet Baru**:
           - Buat spreadsheet baru di Google Drive Anda.
           - Buat lembar kerja dengan nama sheet default (misalnya `Sheet1`).
           - Salin link URL spreadsheet tersebut (misalnya: `https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit`).

        2. **Buat Google Cloud Service Account**:
           - Kunjungi [Google Cloud Console](https://console.cloud.google.com/).
           - Aktifkan **Google Sheets API** dan **Google Drive API**.
           - Masuk ke menu **IAM & Admin** > **Service Accounts** > Buat Service Account baru.
           - Di tab *Keys*, buat kunci baru bertipe **JSON** dan unduh filenya.

        3. **Bagikan Akses Spreadsheet ke Service Account**:
           - Buka file Google Spreadsheet Anda.
           - Klik tombol **Share (Bagikan)** di pojok kanan atas.
           - Masukkan alamat email service account (berakhiran `@...gserviceaccount.com`).
           - Berikan peran sebagai **Editor**.

        4. **Konfigurasi `.streamlit/secrets.toml`**:
           - Buka file `.streamlit/secrets.toml` pada folder proyek ini.
           - Masukkan konfigurasi berikut:
           ```toml
           [connections.gsheets]
           spreadsheet = "https://docs.google.com/spreadsheets/d/ID_SPREADSHEET_ANDA/edit"
           type = "service_account"
           project_id = "your-project-id"
           private_key_id = "your-private-key-id"
           private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
           client_email = "your-service-account@your-project.iam.gserviceaccount.com"
           client_id = "your-client-id"
           auth_uri = "https://accounts.google.com/o/oauth2/auth"
           token_uri = "https://oauth2.googleapis.com/token"
           auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
           client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account"
           ```
        """)
