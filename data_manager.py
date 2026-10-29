import os
import io
import datetime
import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from scoring_map import (
    BIDANG_OPTIONS,
    SURVEY_QUESTIONS,
    DIMENSION_COLUMNS,
    CATEGORY_METADATA,
    get_question_options,
    calculate_score,
    calculate_category_scores
)
from scoring_map import CATEGORY_METADATA
from scoring_map import calculate_score

LOCAL_DATA_FILE = "data_survei.csv"

def is_gsheets_configured():
    """Mengecek apakah kredensial gsheets telah terisi di st.secrets"""
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            cfg = st.secrets["connections"]["gsheets"]
            # Pastikan bukan default placeholder
            if "spreadsheet" in cfg and "ID_SPREADSHEET_ANDA" not in cfg["spreadsheet"]:
                return True
    except Exception:
        pass
    return False

def get_gsheets_connection():
    """Menginisialisasi koneksi GSheets jika terkonfigurasi"""
    if is_gsheets_configured():
        try:
            return st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            st.sidebar.warning(f"GSheets Connection Warning: {e}")
    return None

def generate_sample_data(num_samples=24):
    """
    Membuat data sampel realistis untuk pengujian dan demo dashboard awal
    sebelum responden sungguhan mengisi survei.
    """
    records = []
    genders = ["Laki-laki", "Perempuan"]
    age_groups = ["< 25 tahun", "25 - 34 tahun", "35 - 44 tahun", "45 - 54 tahun", "≥ 55 tahun"]
    tenures = ["< 1 tahun", "1 - 3 tahun", "4 - 10 tahun", "> 10 tahun"]
    positions = ["Staf Pelaksana", "Pengawas / Koordinator", "Fungsional Ahli", "Manajemen / Struktural"]
    names = [
        "Responden A", "Responden B", "Responden C", "Responden D", "Responden E",
        "Responden F", "Responden G", "Responden H", "Responden I", "Responden J",
        "Responden K", "Responden L", "Responden M", "Responden N", "Responden O",
        "Responden P", "Responden Q", "Responden R", "Responden S", "Responden T",
        "Responden U", "Responden V", "Responden W", "Responden X"
    ]

    base_time = datetime.datetime.now() - datetime.timedelta(days=14)

    for i in range(num_samples):
        bidang = BIDANG_OPTIONS[i % len(BIDANG_OPTIONS)]
        created_time = base_time + datetime.timedelta(days=i * 0.5, hours=random.randint(1, 8))
        
        # Buat jawaban dummy untuk setiap pertanyaan
        dummy_answers = {}
        for cat, qs in SURVEY_QUESTIONS.items():
            for q in qs:
                qid = q["id"]
                code = q["code"]
                opts = get_question_options(code)
                if code == "5M":
                    # Pelaku ofensif
                    dummy_answers[qid] = random.choice(opts)
                elif code == "8":
                    # Nilai kesehatan 0-10
                    dummy_answers[qid] = str(random.randint(6, 10))
                else:
                    if opts:
                        # Pilih opsi condong ke nilai baik/sedang
                        dummy_answers[qid] = random.choice(opts)
                    else:
                        dummy_answers[qid] = "-"

        cat_scores, overall_score = calculate_category_scores(dummy_answers)

        record = {
            "ID_Responden": f"RSP-{i+1:04d}",
            "Waktu_Pengisian": created_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Bidang": bidang,
            "Nama_Inisial": names[i % len(names)],
            "Jenis_Kelamin": random.choice(genders),
            "Rentang_Usia": random.choice(age_groups),
            "Masa_Kerja": random.choice(tenures),
            "Jabatan": random.choice(positions),
            "Nama_Penyakit": "Tidak Ada",
            "Berat_Badan": random.randint(50, 90),
            "Tinggi_Badan": random.randint(150, 180),
            "Status_Pernikahan": random.choice(["Sudah menikah", "Belum menikah", "Cerai mati", "Cerai hidup"])
        }

        # Tambahkan skor per dimensi
        for cat, col_name in DIMENSION_COLUMNS.items():
            record[col_name] = cat_scores.get(cat, 50.0)
        record["Skor_Rata_Rata_Total"] = overall_score

        # Tambahkan butir jawaban individual
        for qid, ans in dummy_answers.items():
            record[qid] = ans

        records.append(record)

    df_sample = pd.DataFrame(records)
    return df_sample

def load_data():
    """
    Membaca data survei dari Google Sheets jika tersedia,
    atau dari file CSV lokal. Jika keduanya belum ada data,
    akan membuat file data_survei.csv dengan sample data awal.
    """
    # 1. Coba dari GSheets jika terkonfigurasi
    conn = get_gsheets_connection()
    if conn is not None:
        try:
            df_gsheet = conn.read(worksheet="Data_Responden", ttl="0m")
            if df_gsheet is not None and not df_gsheet.empty:
                # Pastikan kolom numerik terformat dengan benar
                for col in DIMENSION_COLUMNS.values():
                    if col in df_gsheet.columns:
                        df_gsheet[col] = pd.to_numeric(df_gsheet[col], errors="coerce").fillna(0)
                if "Skor_Rata_Rata_Total" in df_gsheet.columns:
                    df_gsheet["Skor_Rata_Rata_Total"] = pd.to_numeric(df_gsheet["Skor_Rata_Rata_Total"], errors="coerce").fillna(0)
                return df_gsheet, "Google Sheets"
        except Exception as e:
            st.sidebar.warning(f"Gagal membaca Google Sheets ({e}), beralih ke penyimpanan lokal.")

    # 2. Coba dari file CSV lokal
    if os.path.exists(LOCAL_DATA_FILE):
        try:
            df_local = pd.read_csv(LOCAL_DATA_FILE)
            if not df_local.empty:
                for col in DIMENSION_COLUMNS.values():
                    if col in df_local.columns:
                        df_local[col] = pd.to_numeric(df_local[col], errors="coerce").fillna(0)
                if "Skor_Rata_Rata_Total" in df_local.columns:
                    df_local["Skor_Rata_Rata_Total"] = pd.to_numeric(df_local["Skor_Rata_Rata_Total"], errors="coerce").fillna(0)
                return df_local, "File Lokal (data_survei.csv)"
        except Exception:
            pass

    # 3. Jika file lokal belum ada, inisialisasi dengan sample data realistis
    sample_df = generate_sample_data(num_samples=24)
    sample_df.to_csv(LOCAL_DATA_FILE, index=False)
    return sample_df, "Sample Awal (data_survei.csv)"

def save_survey_response(biodata, answers):
    """
    Menyimpan respons responden ke file lokal dan Google Sheets jika aktif.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_resp = f"RSP-{random.randint(1000, 9999)}"

    # Hitung skor per kategori
    cat_scores, overall_avg = calculate_category_scores(answers)

    # Susun dict rekaman data lengkap
    record = {
        "ID_Responden": id_resp,
        "Waktu_Pengisian": timestamp,
        "Bidang": biodata.get("bidang", ""),
        "Nama_Inisial": biodata.get("nama", "Anonim"),
        "Jenis_Kelamin": biodata.get("gender", ""),
        "Rentang_Usia": biodata.get("usia", ""),
        "Masa_Kerja": biodata.get("masa_kerja", ""),
        "Jabatan": biodata.get("jabatan", ""),
        "Riwayat_Penyakit": biodata.get("riwayat_penyakit", "Tidak"),
        "Nama_Penyakit": biodata.get("nama_penyakit", "-"),
        "Berat_Badan": biodata.get("berat_badan", 0),
        "Tinggi_Badan": biodata.get("tinggi_badan", 0),
        "Status_Perkawinan": biodata.get("status_perkawinan", 0)
    }

    # Skor dimensi
    for cat, col_name in DIMENSION_COLUMNS.items():
        record[col_name] = cat_scores.get(cat, 0.0)
    record["Skor_Rata_Rata_Total"] = overall_avg

    # Jawaban individual per butir pertanyaan
    for cat, qs in SURVEY_QUESTIONS.items():
        for q in qs:
            qid = q["id"]
            record[qid] = answers.get(qid, "")

    df_new_row = pd.DataFrame([record])

    # 1. Simpan ke CSV lokal
    try:
        if os.path.exists(LOCAL_DATA_FILE):
            df_existing = pd.read_csv(LOCAL_DATA_FILE)
            df_updated = pd.concat([df_existing, df_new_row], ignore_index=True)
        else:
            df_updated = df_new_row
        df_updated.to_csv(LOCAL_DATA_FILE, index=False)
        local_saved = True
    except Exception as e:
        local_saved = False
        print(f"Error saving to local CSV: {e}")

    # 2. Simpan ke Google Sheets jika terkonfigurasi
    gsheet_saved = False
    conn = get_gsheets_connection()
    if conn is not None:
        try:
            try:
                existing_gsheet = conn.read(worksheet="Data_Responden", ttl="0m")
                if existing_gsheet is not None and not existing_gsheet.empty:
                    updated_gsheet = pd.concat([existing_gsheet, df_new_row], ignore_index=True)
                else:
                    updated_gsheet = df_new_row
            except Exception:
                updated_gsheet = df_new_row

            conn.update(worksheet="Data_Responden", data=updated_gsheet)
            gsheet_saved = True
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")

    return {
        "success": local_saved or gsheet_saved,
        "local_saved": local_saved,
        "gsheet_saved": gsheet_saved,
        "cat_scores": cat_scores,
        "overall_score": overall_avg,
        "id_responden": id_resp
    }

def convert_df_to_excel(df):
    """Mengonversi DataFrame ke file binary Excel bytes untuk tombol download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Survei_ErgoPsiko')
    processed_data = output.getvalue()
    return processed_data
