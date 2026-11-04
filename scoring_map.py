import pandas as pd

# KONFIGURASI SKOR DAN JAWABAN
SCORING_MAP = {
    "1": {"Selalu": 100, "Sering": 75, "Kadang-kadang": 50, "Jarang": 25, "Tidak Pernah": 0},
    "1R": {"Selalu": 0, "Sering": 25, "Kadang-kadang": 50, "Jarang": 75, "Tidak Pernah": 100},
    "2": {"Dalam tingkat yang sangat besar": 100, "Dalam tingkat yang besar": 75, "Sedang": 50, "Dalam tingkat yang kecil": 25, "Dalam tingkat yang sangat kecil": 0},
    "2R": {"Dalam tingkat yang sangat besar": 0, "Dalam tingkat yang besar": 25, "Sedang": 50, "Dalam tingkat yang kecil": 75, "Dalam tingkat yang sangat kecil": 100},
    "3": {"Tidak Pernah": 0, "Jarang": 25, "Kadang kadang": 50, "Sering": 75, "Selalu": 100},
    "4": {"Setiap hari": 100, "Setiap minggu": 75, "Setiap bulan": 50, "Beberapa kali": 25, "Tidak ada sama sekali": 0},
    "6": {"Sangat puas": 100, "Puas": 75, "Cukup puas": 50, "Kurang puas": 25, "Sangat tidak puas": 0},
    "7": {"Sangat baik sekali": 100, "Sangat baik": 75, "Baik": 50, "Cukup": 25, "Kurang": 0},
    "8": {str(i): i * 10 for i in range(11)},
    "9": {"Sepanjang waktu": 100, "sebagian besar waktu": 75, "sebagian waktu": 50, "sebagian kecil waktu": 25, "sama sekali tidak": 0},
    "10": {"Sangat sesuai": 100, "Cukup sesuai": 67, "Sedikit sesuai": 33, "Tidak sesuai": 0},
}

PILIHAN_5M = ["Teman Kerja", "Atasan/Pimpinan", "Masyarakat/Pengguna", "Layanan Pihak Luar"]

def get_question_options(code):
    """Mengembalikan daftar opsi jawaban berdasarkan kode bobot"""
    if code in SCORING_MAP:
        return list(SCORING_MAP[code].keys())
    elif code == "5M":
        return PILIHAN_5M
    elif code == "8":
        return [str(i) for i in range(11)]
    return []

def calculate_score(code, answer):
    """Menghitung skor numerik (0-100) dari jawaban"""
    if answer is None:
        return None
    if code in SCORING_MAP:
        if str(answer) in SCORING_MAP[code]:
            return SCORING_MAP[code][str(answer)]
        # Tangani kemungkinan sedikit variasi penulisan seperti kadang-kadang vs kadang kadang
        normalized = str(answer).strip()
        for k, v in SCORING_MAP[code].items():
            if k.lower().replace("-", " ") == normalized.lower().replace("-", " "):
                return v
    elif code == "8":
        try:
            val = float(answer)
            return min(max(val * 10, 0), 100)
        except (ValueError, TypeError):
            return None
    return None

BIDANG_OPTIONS = ["Keselamatan Kerja", "Kesehatan Kerja", "Ergonomi & Psikologi", "Hiegene Industri dan Bahan Berbahaya", "Tata Usaha"]

# questions
SURVEY_QUESTIONS = {
    "TUNTUTAN PEKERJAAN": [
        {"id": "T1_Q1", "text": "Apakah pekerjaan Anda sering menumpuk karena pembagian beban kerja tidak merata?", "code": "1", "sub": "Tuntutan Kuantitatif"},
        {"id": "T1_Q2", "text": "Seberapa sering Anda tidak memiliki cukup waktu untuk menyelesaikan semua tugas pekerjaan?", "code": "1", "sub": "Tuntutan Kuantitatif"},
        {"id": "T1_Q3", "text": "Seberapa sering pekerjaan Anda tertunda atau belum selesai sesuai rencana?", "code": "1", "sub": "Tuntutan Kuantitatif"},
        {"id": "T1_Q4", "text": "Apakah waktu yang tersedia cukup untuk menyelesaikan tugas pekerjaan Anda?", "code": "1R", "sub": "Tuntutan Kuantitatif"},
        {"id": "T1_Q5", "text": "Apakah Anda dituntut untuk bekerja dengan sangat cepat?", "code": "1", "sub": "Laju Kerja"},
        {"id": "T1_Q6", "text": "Apakah Anda harus bekerja dengan cepat hampir sepanjang hari?", "code": "2", "sub": "Laju Kerja"},
        {"id": "T1_Q7", "text": "Apakah Anda harus terus bekerja dengan cepat?", "code": "2", "sub": "Laju Kerja"},
        {"id": "T1_Q8", "text": "Apakah saat bekerja Anda harus memperhatikan banyak hal sekaligus?", "code": "1", "sub": "Tuntutan Kognitif"},
        {"id": "T1_Q9", "text": "Apakah pekerjaan Anda mengharuskan Anda mengingat banyak informasi atau hal?", "code": "1", "sub": "Tuntutan Kognitif"},
        {"id": "T1_Q10", "text": "Apakah pekerjaan Anda menuntut Anda untuk menghasilkan ide-ide baru?", "code": "1", "sub": "Tuntutan Kognitif"},
        {"id": "T1_Q11", "text": "Apakah pekerjaan Anda mengharuskan Anda mengambil keputusan yang sulit?", "code": "1", "sub": "Tuntutan Kognitif"},
        {"id": "T1_Q12", "text": "Apakah pekerjaan Anda membuat Anda menghadapi situasi yang mengganggu perasaan?", "code": "1", "sub": "Tuntutan Emosional"},
        {"id": "T1_Q13", "text": "Apakah dalam pekerjaan Anda, Anda perlu menangani masalah pribadi orang lain?", "code": "1", "sub": "Tuntutan Emosional"},
        {"id": "T1_Q14", "text": "Apakah pekerjaan Anda menuntut banyak tenaga atau keterlibatan emosional?", "code": "2", "sub": "Tuntutan Emosional"},
        {"id": "T1_Q15", "text": "Apakah Anda harus memperlakukan semua orang dengan setara, meskipun perasaan Anda sedang tidak mendukung?", "code": "1", "sub": "Tuntutan untuk Menyembunyikan Emosi"},
        {"id": "T1_Q16", "text": "Apakah Anda harus menyembunyikan perasaan saat bekerja?", "code": "2", "sub": "Tuntutan untuk Menyembunyikan Emosi"},
        {"id": "T1_Q17", "text": "Apakah Anda harus tetap bersikap ramah dan terbuka kepada semua orang, apa pun sikap mereka kepada Anda?", "code": "2", "sub": "Tuntutan untuk Menyembunyikan Emosi"},
        {"id": "T1_Q18", "text": "Apakah Anda harus menahan diri untuk tidak menyampaikan pendapat saat bekerja?", "code": "1", "sub": "Tuntutan untuk Menyembunyikan Emosi"},
    ],
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": [
        {"id": "T2_Q1", "text": "Apakah Anda memiliki kesempatan untuk ikut memengaruhi keputusan yang berkaitan dengan pekerjaan Anda?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q2", "text": "Apakah Anda dapat ikut menentukan dengan siapa Anda bekerja?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q3", "text": "Apakah Anda dapat memengaruhi banyaknya pekerjaan yang diberikan kepada Anda?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q4", "text": "Apakah Anda dapat memengaruhi jenis atau kegiatan pekerjaan yang Anda lakukan?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q5", "text": "Apakah Anda dapat memengaruhi kecepatan dalam menyelesaikan pekerjaan?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q6", "text": "Apakah Anda dapat menentukan cara untuk menyelesaikan pekerjaan Anda?", "code": "1", "sub": "Pengaruh di Tempat Kerja"},
        {"id": "T2_Q7", "text": "Apakah pekerjaan Anda memberi kesempatan untuk mempelajari hal-hal baru?", "code": "2", "sub": "Kemungkinan Pengembangan"},
        {"id": "T2_Q8", "text": "Apakah Anda dapat menggunakan keterampilan atau keahlian yang Anda miliki dalam pekerjaan?", "code": "2", "sub": "Kemungkinan Pengembangan"},
        {"id": "T2_Q9", "text": "Apakah pekerjaan Anda memberi kesempatan untuk meningkatkan keterampilan?", "code": "2", "sub": "Kemungkinan Pengembangan"},
        {"id": "T2_Q10", "text": "Apakah tugas-tugas yang Anda kerjakan cukup beragam?", "code": "1", "sub": "Variasi Pekerjaan"},
        {"id": "T2_Q11", "text": "Apakah Anda harus melakukan tugas yang sama berulang kali?", "code": "1R", "sub": "Variasi Pekerjaan"},
        {"id": "T2_Q12", "text": "Apakah Anda dapat menentukan sendiri kapan akan beristirahat?", "code": "1", "sub": "Kendali atas Waktu Kerja"},
        {"id": "T2_Q13", "text": "Apakah Anda dapat mengambil cuti pada waktu yang Anda inginkan?", "code": "1", "sub": "Kendali atas Waktu Kerja"},
        {"id": "T2_Q14", "text": "Apakah Anda dapat meninggalkan pekerjaan sebentar untuk berbincang dengan rekan kerja?", "code": "1", "sub": "Kendali atas Waktu Kerja"},
        {"id": "T2_Q15", "text": "Jika ada urusan pribadi, apakah Anda dapat meninggalkan tempat kerja selama sekitar 30 menit tanpa harus meminta izin khusus?", "code": "1", "sub": "Kendali atas Waktu Kerja"},
        {"id": "T2_Q16", "text": "Apakah Anda perlu bekerja melebihi jam kerja yang ditetapkan (lembur)?", "code": "1R", "sub": "Kendali atas Waktu Kerja"},
        {"id": "T2_Q17", "text": "Apakah pekerjaan yang Anda lakukan terasa bermakna?", "code": "2", "sub": "Makna Kerja"},
        {"id": "T2_Q18", "text": "Apakah Anda merasa pekerjaan yang Anda lakukan itu penting?", "code": "2", "sub": "Makna Kerja"},
    ],
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": [
        {"id": "T3_Q1", "text": "Apakah Anda mendapat informasi lebih awal tentang keputusan penting, perubahan, atau rencana di tempat kerja?", "code": "2", "sub": "Prediktabilitas"},
        {"id": "T3_Q2", "text": "Apakah Anda memperoleh informasi yang dibutuhkan untuk menyelesaikan pekerjaan dengan baik?", "code": "2", "sub": "Prediktabilitas"},
        {"id": "T3_Q3", "text": "Apakah atasan atau manajemen mengakui dan menghargai hasil pekerjaan Anda?", "code": "2", "sub": "Pengakuan"},
        {"id": "T3_Q4", "text": "Apakah atasan atau manajemen menghormati Anda?", "code": "2", "sub": "Pengakuan"},
        {"id": "T3_Q5", "text": "Apakah Anda diperlakukan secara adil di tempat kerja?", "code": "2", "sub": "Pengakuan"},
        {"id": "T3_Q6", "text": "Apakah tujuan pekerjaan Anda jelas?", "code": "2", "sub": "Kejelasan Peran"},
        {"id": "T3_Q7", "text": "Apakah Anda mengetahui dengan jelas tugas dan tanggung jawab Anda?", "code": "2", "sub": "Kejelasan Peran"},
        {"id": "T3_Q8", "text": "Apakah Anda memahami dengan jelas apa yang diharapkan dari Anda dalam pekerjaan?", "code": "2", "sub": "Kejelasan Peran"},
        {"id": "T3_Q9", "text": "Apakah Anda menerima tuntutan pekerjaan yang saling bertentangan?", "code": "2", "sub": "Konflik Peran"},
        {"id": "T3_Q10", "text": "Apakah Anda terkadang harus melakukan pekerjaan dengan cara yang menurut Anda kurang tepat?", "code": "2", "sub": "Konflik Peran"},
        {"id": "T3_Q11", "text": "Apakah Anda terkadang harus mengerjakan sesuatu yang menurut Anda tidak diperlukan?", "code": "2", "sub": "Tugas Tidak Sah"},
        {"id": "T3_Q12", "text": "Apakah atasan langsung Anda memastikan bahwa Anda memiliki kesempatan untuk mengembangkan kemampuan?", "code": "2", "sub": "Kualitas Kepemimpinan", "sub_note": "Sejauh mana Anda menilai bahwa atasan langsung Anda:"},
        {"id": "T3_Q13", "text": "Apakah atasan langsung Anda mengutamakan kepuasan kerja staf?", "code": "2", "sub": "Kualitas Kepemimpinan"},
        {"id": "T3_Q14", "text": "Apakah atasan langsung Anda mampu merencanakan pekerjaan dengan baik?", "code": "2", "sub": "Kualitas Kepemimpinan"},
        {"id": "T3_Q15", "text": "Apakah atasan langsung Anda mampu menyelesaikan konflik dengan baik?", "code": "2", "sub": "Kualitas Kepemimpinan"},
        {"id": "T3_Q16", "text": "Seberapa sering atasan langsung Anda bersedia mendengarkan masalah pekerjaan Anda ketika Anda membutuhkan bantuan?", "code": "1", "sub": "Dukungan Sosial Atasan"},
        {"id": "T3_Q17", "text": "Seberapa sering Anda mendapat bantuan atau dukungan dari atasan langsung ketika membutuhkannya?", "code": "1", "sub": "Dukungan Sosial Atasan"},
        {"id": "T3_Q18", "text": "Seberapa sering atasan langsung Anda membahas dengan Anda bagaimana pekerjaan Anda dilakukan?", "code": "1", "sub": "Dukungan Sosial Atasan"},
        {"id": "T3_Q19", "text": "Seberapa sering Anda mendapat bantuan atau dukungan dari rekan kerja ketika membutuhkannya?", "code": "1", "sub": "Dukungan Sosial Rekan Kerja"},
        {"id": "T3_Q20", "text": "Seberapa sering rekan kerja bersedia mendengarkan masalah pekerjaan Anda ketika Anda membutuhkannya?", "code": "1", "sub": "Dukungan Sosial Rekan Kerja"},
        {"id": "T3_Q21", "text": "Seberapa sering rekan kerja membahas dengan Anda bagaimana pekerjaan Anda dilakukan?", "code": "1", "sub": "Dukungan Sosial Rekan Kerja"},
        {"id": "T3_Q22", "text": "Apakah Anda merasa nyaman dengan suasana kerja bersama rekan-rekan?", "code": "1", "sub": "Rasa Kebersamaan"},
        {"id": "T3_Q23", "text": "Apakah rekan-rekan di tempat kerja bekerja sama dengan baik?", "code": "1", "sub": "Rasa Kebersamaan"},
        {"id": "T3_Q24", "text": "Apakah Anda merasa menjadi bagian dari lingkungan kerja ini?", "code": "1", "sub": "Rasa Kebersamaan"},
    ],
    "KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI": [
        {"id": "T4_Q1", "text": "Apakah Anda senang bercerita kepada orang lain tentang tempat Anda bekerja?", "code": "2", "sub": "Komitmen terhadap Tempat Kerja"},
        {"id": "T4_Q2", "text": "Apakah tempat Anda bekerja memiliki arti penting bagi Anda?", "code": "2", "sub": "Komitmen terhadap Tempat Kerja"},
        {"id": "T4_Q3", "text": "Apakah Anda akan menyarankan orang lain untuk melamar pekerjaan di tempat Anda bekerja?", "code": "2", "sub": "Komitmen terhadap Tempat Kerja"},
        {"id": "T4_Q4", "text": "Seberapa sering Anda mempertimbangkan untuk mencari pekerjaan di tempat lain?", "code": "1R", "sub": "Komitmen terhadap Tempat Kerja"},
        {"id": "T4_Q5", "text": "Apakah Anda bangga menjadi bagian dari organisasi ini?", "code": "2", "sub": "Komitmen terhadap Tempat Kerja"},
        {"id": "T4_Q6", "text": "Saat bekerja, saya merasa berenergi.", "code": "3", "sub": "Keterikatan Kerja", "sub_note": "Seberapa sering Anda mengalami hal-hal berikut saat bekerja?"},
        {"id": "T4_Q7", "text": "Saya merasa antusias saat mengerjakan pekerjaan saya.", "code": "3", "sub": "Keterikatan Kerja"},
        {"id": "T4_Q8", "text": "Saya sangat larut atau fokus ketika mengerjakan pekerjaan saya.", "code": "3", "sub": "Keterikatan Kerja"},
        {"id": "T4_Q9", "text": "Apakah Anda khawatir akan kehilangan pekerjaan dan menjadi pengangguran?", "code": "2", "sub": "Job Insecurity"},
        {"id": "T4_Q10", "text": "Apakah Anda khawatir perkembangan teknologi dapat membuat pekerjaan Anda tidak lagi dibutuhkan?", "code": "2", "sub": "Job Insecurity"},
        {"id": "T4_Q11", "text": "Apakah Anda khawatir akan sulit mendapatkan pekerjaan lain jika kehilangan pekerjaan saat ini?", "code": "2", "sub": "Job Insecurity"},
        {"id": "T4_Q12", "text": "Apakah Anda khawatir dipindahkan ke pekerjaan lain tanpa keinginan Anda sendiri?", "code": "2", "sub": "Insecurity over Working Conditions"},
        {"id": "T4_Q13", "text": "Apakah Anda khawatir tugas pekerjaan Anda akan diubah tanpa persetujuan Anda?", "code": "2", "sub": "Insecurity over Working Conditions"},
        {"id": "T4_Q14", "text": "Apakah Anda khawatir jadwal kerja Anda—seperti giliran kerja, hari kerja, atau jam masuk dan pulang—diubah tanpa persetujuan Anda?", "code": "2", "sub": "Insecurity over Working Conditions"},
        {"id": "T4_Q15", "text": "Apakah Anda khawatir penghasilan atau gaji Anda akan dikurangi?", "code": "2", "sub": "Insecurity over Working Conditions"},
        {"id": "T4_Q16", "text": "Apakah menurut Anda pekerjaan Anda memiliki prospek atau peluang yang baik ke depannya?", "code": "2R", "sub": "Insecurity over Working Conditions"},
        {"id": "T4_Q17", "text": "Sejauh mana Anda merasa dapat menyelesaikan tugas dengan hasil yang memuaskan?", "code": "2", "sub": "Kualitas Kerja"},
        {"id": "T4_Q18", "text": "Apakah Anda puas dengan kualitas pekerjaan yang dihasilkan di tempat kerja Anda?", "code": "2", "sub": "Kualitas Kerja"},
        {"id": "T4_Q19", "text": "Seberapa puas Anda dengan peluang atau prospek pekerjaan Anda ke depannya?", "code": "6", "sub": "Kepuasan Kerja", "sub_note": "Secara umum, seberapa puas Anda dengan pekerjaan Anda?"},
        {"id": "T4_Q20", "text": "Seberapa puas Anda dengan kondisi fisik tempat kerja, seperti ruang, pencahayaan, dan fasilitas?", "code": "6", "sub": "Kepuasan Kerja"},
        {"id": "T4_Q21", "text": "Seberapa puas Anda dengan cara keterampilan dan kemampuan Anda digunakan dalam pekerjaan?", "code": "6", "sub": "Kepuasan Kerja"},
        {"id": "T4_Q22", "text": "Secara keseluruhan, seberapa puas Anda dengan pekerjaan Anda?", "code": "6", "sub": "Kepuasan Kerja"},
        {"id": "T4_Q23", "text": "Seberapa puas Anda dengan gaji yang Anda terima?", "code": "6", "sub": "Kepuasan Kerja"},
        {"id": "T4_Q24", "text": "Apakah Anda pernah merasa harus berada di tempat kerja dan di rumah pada waktu yang sama?", "code": "1", "sub": "Konflik Pekerjaan - Kehidupan Pribadi", "sub_note": "Pertanyaan berikut berkaitan dengan bagaimana pekerjaan Anda memengaruhi kehidupan pribadi Anda:"},
        {"id": "T4_Q25", "text": "Apakah pekerjaan menguras energi Anda hingga mengganggu kehidupan pribadi?", "code": "2", "sub": "Konflik Pekerjaan - Kehidupan Pribadi"},
        {"id": "T4_Q26", "text": "Apakah pekerjaan menyita banyak waktu hingga mengganggu kehidupan pribadi Anda?", "code": "2", "sub": "Konflik Pekerjaan - Kehidupan Pribadi"},
        {"id": "T4_Q27", "text": "Apakah tuntutan pekerjaan mengganggu kehidupan pribadi atau keluarga Anda?", "code": "2", "sub": "Konflik Pekerjaan - Kehidupan Pribadi"},
        {"id": "T4_Q28", "text": "Apakah urusan pekerjaan membuat Anda harus mengubah rencana kegiatan pribadi atau keluarga?", "code": "2", "sub": "Konflik Pekerjaan - Kehidupan Pribadi"},
    ],
    "MODAL SOSIAL": [
        {"id": "T5_Q1", "text": "Apakah pegawai saling menahan atau tidak membagikan informasi yang seharusnya diketahui bersama?", "code": "2R", "sub": "Kepercayaan Horizontal"},
        {"id": "T5_Q2", "text": "Apakah pegawai menahan informasi dari pihak manajemen?", "code": "2R", "sub": "Kepercayaan Horizontal"},
        {"id": "T5_Q3", "text": "Apakah pegawai di tempat kerja saling percaya?", "code": "2", "sub": "Kepercayaan Horizontal"},
        {"id": "T5_Q4", "text": "Apakah manajemen mempercayai pegawai untuk melakukan pekerjaan dengan baik?", "code": "2", "sub": "Kepercayaan Vertikal"},
        {"id": "T5_Q5", "text": "Apakah pegawai dapat mempercayai informasi yang disampaikan oleh manajemen?", "code": "2", "sub": "Kepercayaan Vertikal"},
        {"id": "T5_Q6", "text": "Apakah manajemen menahan informasi penting yang seharusnya diketahui pegawai?", "code": "2R", "sub": "Kepercayaan Vertikal"},
        {"id": "T5_Q7", "text": "Apakah pegawai dapat menyampaikan pendapat dan perasaan mereka secara terbuka?", "code": "2", "sub": "Kepercayaan Vertikal"},
        {"id": "T5_Q8", "text": "Apakah konflik di tempat kerja diselesaikan secara adil?", "code": "2", "sub": "Keadilan Organisasional"},
        {"id": "T5_Q9", "text": "Apakah pegawai mendapat penghargaan ketika melakukan pekerjaan dengan baik?", "code": "2", "sub": "Keadilan Organisasional"},
        {"id": "T5_Q10", "text": "Apakah manajemen menanggapi saran dari pegawai dengan serius?", "code": "2", "sub": "Keadilan Organisasional"},
        {"id": "T5_Q11", "text": "Apakah pembagian pekerjaan dilakukan secara adil?", "code": "2", "sub": "Keadilan Organisasional"},
    ],
    "KONFLIK DAN PERILAKU OFENSIF": [
        {"id": "T6_Q1", "text": "Dalam 12 bulan terakhir, apakah Anda menjadi sasaran gosip atau fitnah di tempat kerja?", "code": "4", "sub": "Gosip dan Fitnah"},
        {"id": "T6_Q2", "text": "Jika ya, siapa yang melakukannya? (Gosip/Fitnah)", "code": "5M", "sub": "Gosip dan Fitnah"},
        {"id": "T6_Q3", "text": "Dalam 12 bulan terakhir, apakah Anda terlibat pertengkaran atau konflik di tempat kerja?", "code": "4", "sub": "Pertengkaran dan Konflik"},
        {"id": "T6_Q4", "text": "Jika ya, siapa yang melakukannya? (Pertengkaran/Konflik)", "code": "5M", "sub": "Pertengkaran dan Konflik"},
        {"id": "T6_Q5", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami ejekan yang membuat Anda tidak nyaman di tempat kerja?", "code": "4", "sub": "Ejekan"},
        {"id": "T6_Q6", "text": "Jika ya, siapa yang melakukannya? (Ejekan)", "code": "5M", "sub": "Ejekan"},
        {"id": "T6_Q7", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami gangguan atau pelecehan terkait pekerjaan melalui media sosial, email, atau pesan teks?", "code": "4", "sub": "Perundungan Siber"},
        {"id": "T6_Q8", "text": "Jika ya, siapa yang melakukannya? (Pelecehan Media/Pesan)", "code": "5M", "sub": "Perundungan Siber"},
        {"id": "T6_Q9", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami perhatian atau perilaku bernuansa seksual yang tidak Anda inginkan di tempat kerja?", "code": "4", "sub": "Pelecehan Seksual"},
        {"id": "T6_Q10", "text": "Jika ya, siapa yang melakukannya? (Perilaku Seksual)", "code": "5M", "sub": "Pelecehan Seksual"},
        {"id": "T6_Q11", "text": "Dalam 12 bulan terakhir, apakah Anda menerima ancaman kekerasan di tempat kerja?", "code": "4", "sub": "Ancaman Kekerasan"},
        {"id": "T6_Q12", "text": "Jika ya, siapa yang melakukannya? (Ancaman Kekerasan)", "code": "5M", "sub": "Ancaman Kekerasan"},
        {"id": "T6_Q13", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami kekerasan fisik di tempat kerja?", "code": "4", "sub": "Kekerasan Fisik"},
        {"id": "T6_Q14", "text": "Jika ya, siapa yang melakukannya? (Kekerasan Fisik)", "code": "5M", "sub": "Kekerasan Fisik"},
        {"id": "T6_Q15", "text": "Perundungan adalah perlakuan tidak menyenangkan atau merendahkan yang terjadi berulang kali dan membuat seseorang sulit membela diri. Dalam 12 bulan terakhir, apakah Anda mengalami perundungan di tempat kerja?", "code": "4", "sub": "Perundungan"},
        {"id": "T6_Q16", "text": "Jika ya, siapa yang melakukannya? (Perundungan)", "code": "5M", "sub": "Perundungan"},
        {"id": "T6_Q17", "text": "Seberapa sering Anda merasa dikritik secara tidak adil, diintimidasi, atau dipermalukan di depan orang lain oleh rekan kerja atau atasan?", "code": "1", "sub": "Perundungan"}, 
    ],
    "HEALTH AND WELL-BEING": [
        {"id": "T7_Q1", "text": "Secara umum, bagaimana Anda menilai kondisi kesehatan Anda saat ini?", "code": "7", "sub": "Kesehatan yang Dinilai Diri Sendiri"},
        {"id": "T7_Q2", "text": "Jika kondisi kesehatan terbaik yang dapat Anda bayangkan diberi nilai 10 dan kondisi terburuk diberi nilai 0, berapa nilai yang Anda berikan untuk kondisi kesehatan Anda saat ini?", "code": "8", "sub": "Kesehatan yang Dinilai Diri Sendiri"},
        {"id": "T7_Q3", "text": "Seberapa sering tidur Anda terasa tidak nyenyak atau gelisah?", "code": "9", "sub": "Masalah Tidur", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q4", "text": "Seberapa sering Anda mengalami kesulitan untuk mulai tidur?", "code": "9", "sub": "Masalah Tidur"},
        {"id": "T7_Q5", "text": "Seberapa sering Anda terbangun terlalu pagi dan tidak bisa tidur kembali?", "code": "9", "sub": "Masalah Tidur"},
        {"id": "T7_Q6", "text": "Seberapa sering Anda terbangun beberapa kali pada malam hari dan sulit tidur kembali?", "code": "9", "sub": "Masalah Tidur"},
        {"id": "T7_Q7", "text": "Seberapa sering Anda merasa sangat terkuras atau kehabisan tenaga?", "code": "9", "sub": "Burnout", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q8", "text": "Seberapa sering Anda merasa kelelahan secara fisik?", "code": "9", "sub": "Burnout"},
        {"id": "T7_Q9", "text": "Seberapa sering Anda merasa kelelahan secara emosional?", "code": "9", "sub": "Burnout"},
        {"id": "T7_Q10", "text": "Seberapa sering Anda merasa lelah?", "code": "9", "sub": "Burnout"},
        {"id": "T7_Q11", "text": "Seberapa sering Anda merasa sulit untuk bersantai?", "code": "9", "sub": "Stress", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q12", "text": "Seberapa sering Anda merasa mudah tersinggung?", "code": "9", "sub": "Stress"},
        {"id": "T7_Q13", "text": "Seberapa sering Anda merasa tegang?", "code": "9", "sub": "Stress"},
        {"id": "T7_Q14", "text": "Seberapa sering Anda mengalami sakit perut?", "code": "9", "sub": "Somatic Stress", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q15", "text": "Seberapa sering Anda mengalami sakit kepala?", "code": "9", "sub": "Somatic Stress"},
        {"id": "T7_Q16", "text": "Seberapa sering jantung Anda terasa berdebar-debar?", "code": "9", "sub": "Somatic Stress"},
        {"id": "T7_Q17", "text": "Seberapa sering Anda merasakan ketegangan pada otot-otot tubuh?", "code": "9", "sub": "Somatic Stress"},
        {"id": "T7_Q18", "text": "Seberapa sering Anda mengalami kesulitan berkonsentrasi?", "code": "9", "sub": "Cognitive Stress", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q19", "text": "Seberapa sering Anda merasa sulit berpikir dengan jernih?", "code": "9", "sub": "Cognitive Stress"},
        {"id": "T7_Q20", "text": "Seberapa sering Anda mengalami kesulitan saat mengambil keputusan?", "code": "9", "sub": "Cognitive Stress"},
        {"id": "T7_Q21", "text": "Seberapa sering Anda mengalami kesulitan mengingat sesuatu?", "code": "9", "sub": "Cognitive Stress"},
        {"id": "T7_Q22", "text": "Seberapa sering Anda merasa sedih?", "code": "9", "sub": "Depressive Symptoms", "sub_note": "Pertanyaan berikut menanyakan keadaan Anda selama empat minggu terakhir:"},
        {"id": "T7_Q23", "text": "Seberapa sering Anda merasa kurang percaya diri?", "code": "9", "sub": "Depressive Symptoms"},
        {"id": "T7_Q24", "text": "Seberapa sering Anda merasa bersalah?", "code": "9", "sub": "Depressive Symptoms"},
        {"id": "T7_Q25", "text": "Seberapa sering Anda kehilangan minat terhadap kegiatan sehari-hari?", "code": "9", "sub": "Depressive Symptoms"},
    ],
    "PERSONALITY/KEPRIBADIAN": [
        {"id": "T8_Q1", "text": "Saya biasanya dapat menyelesaikan masalah sulit jika saya berusaha dengan sungguh-sungguh.", "code": "10", "sub": "Self Efficacy"},
        {"id": "T8_Q2", "text": "Jika orang lain menghambat saya, saya akan mencari cara untuk mencapai tujuan saya.", "code": "10", "sub": "Self Efficacy"},
        {"id": "T8_Q3", "text": "Saya mudah mengikuti rencana yang telah dibuat dan mencapai tujuan saya.", "code": "10", "sub": "Self Efficacy"},
        {"id": "T8_Q4", "text": "Saya yakin dapat menghadapi kejadian yang tidak terduga.", "code": "10", "sub": "Self Efficacy"},
        {"id": "T8_Q5", "text": "Saat menghadapi masalah, saya biasanya dapat menemukan beberapa cara untuk menyelesaikannya.", "code": "10", "sub": "Self Efficacy"},
        {"id": "T8_Q6", "text": "Apa pun yang terjadi, saya biasanya mampu mengatasinya.", "code": "10", "sub": "Self Efficacy"},
    ]
}

CATEGORY_METADATA = {
    "TUNTUTAN PEKERJAAN": {
        "label": "Tuntutan Pekerjaan",
        "short": "Tuntutan Kerja",
        "icon": "⏳",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan tuntutan yang Anda hadapi dalam pekerjaan, seperti beban kerja, kecepatan kerja, tuntutan kognitif, dan tuntutan emosional. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": {
        "label": "Pengorganisasian & Isi Kerja",
        "short": "Organisasi Kerja",
        "icon": "📋",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan pengaturan kerja dan karakteristik pekerjaan Anda, seperti kejelasan tugas, kesempatan mengembangkan keterampilan, serta pengaruh dan keleluasaan dalam pekerjaan. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": {
        "label": "Hubungan Antarpribadi & Kepemimpinan",
        "short": "Hubungan & Pemimpin",
        "icon": "🤝",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan hubungan Anda dengan rekan kerja dan atasan serta kepemimpinan di lingkungan kerja. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI": {
        "label": "Antarmuka Kerja Individu",
        "short": "Antarmuka Kerja",
        "icon": "💼",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan hubungan antara pekerjaan dan kehidupan pribadi Anda, termasuk bagaimana pekerjaan memengaruhi kehidupan di luar pekerjaan dan sebaliknya. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "MODAL SOSIAL": {
        "label": "Modal Sosial",
        "short": "Modal Sosial",
        "icon": "🏛️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan kepercayaan, kerja sama, dan hubungan sosial di lingkungan kerja, termasuk bagaimana pegawai saling mendukung dalam mencapai tujuan bersama. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "KONFLIK DAN PERILAKU OFENSIF": {
        "label": "Konflik & Perilaku Ofensif",
        "short": "Konflik & Ofensif",
        "icon": "⚠️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan konflik dan perilaku tidak menyenangkan yang mungkin Anda alami atau temui di lingkungan kerja, seperti perlakuan yang tidak pantas, pelecehan, atau tindakan lain yang membuat Anda merasa tidak nyaman. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada pengalaman Anda di lingkungan kerja selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "HEALTH AND WELL-BEING": {
        "label": "Kesehatan & Kesejahteraan (Health & Well-Being)",
        "short": "Kesehatan & Well-being",
        "icon": "❤️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan kondisi kesehatan dan kesejahteraan Anda, termasuk kondisi fisik, psikologis, dan perasaan yang berkaitan dengan pekerjaan. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda selama 12 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "PERSONALITY/KEPRIBADIAN": {
        "label": "Kepribadian & Efikasi Diri (Self-Efficacy)",
        "short": "Kepribadian & Efikasi",
        "icon": "🎯",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan karakteristik dan kecenderungan kepribadian Anda, termasuk bagaimana Anda biasanya berpikir, merasakan, dan berperilaku dalam berbagai situasi. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada gambaran diri Anda yang paling sesuai. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    }
}

DIMENSION_COLUMNS = {
    "TUNTUTAN PEKERJAAN": "Skor_Tuntutan_Kerja",
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": "Skor_Organisasi_Kerja",
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": "Skor_Hubungan_Kepemimpinan",
    "KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI": "Skor_Antarmuka_Kerja",
    "MODAL SOSIAL": "Skor_Modal_Sosial",
    "KONFLIK DAN PERILAKU OFENSIF": "Skor_Konflik_Ofensif",
    "HEALTH AND WELL-BEING": "Skor_Kesehatan_Wellbeing",
    "PERSONALITY/KEPRIBADIAN": "Skor_Kepribadian_Efikasi"
}

# DAFTAR SUB-DIMENSI PER KATEGORI (SEGMEN 1)
SUBDIMENSIONS_BY_CATEGORY = {
    "TUNTUTAN PEKERJAAN": [
        "Tuntutan Kuantitatif",
        "Laju Kerja",
        "Tuntutan Kognitif",
        "Tuntutan Emosional",
        "Tuntutan untuk Menyembunyikan Emosi"
    ],
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": [
        "Pengaruh di Tempat Kerja",
        "Kemungkinan Pengembangan",
        "Variasi Pekerjaan",
        "Kendali atas Waktu Kerja",
        "Makna Kerja"
    ],
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": [
        "Prediktabilitas",
        "Pengakuan",
        "Kejelasan Peran",
        "Konflik Peran",
        "Tugas Tidak Sah",
        "Kualitas Kepemimpinan",
        "Dukungan Sosial Atasan",
        "Dukungan Sosial Rekan Kerja",
        "Rasa Kebersamaan"
    ],
    "KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI": [
        "Komitmen terhadap Tempat Kerja",
        "Keterikatan Kerja",
        "Job Insecurity",
        "Insecurity over Working Conditions",
        "Kualitas Kerja",
        "Kepuasan Kerja",
        "Konflik Pekerjaan - Kehidupan Pribadi"
    ],
    "MODAL SOSIAL": [
        "Kepercayaan Horizontal",
        "Kepercayaan Vertikal",
        "Keadilan Organisasional"
    ],
    "KONFLIK DAN PERILAKU OFENSIF": [
        "Gosip dan Fitnah",
        "Pertengkaran dan Konflik",
        "Ejekan",
        "Perundungan Siber",
        "Pelecehan Seksual",
        "Ancaman Kekerasan",
        "Kekerasan Fisik",
        "Perundungan"
    ],
    "HEALTH AND WELL-BEING": [
        "Kesehatan yang Dinilai Diri Sendiri",
        "Masalah Tidur",
        "Burnout",
        "Stress",
        "Somatic Stress",
        "Cognitive Stress",
        "Depressive Symptoms"
    ],
    "PERSONALITY/KEPRIBADIAN": [
        "Self Efficacy"
    ]
}

# NAMA KOLOM UNTUK SKOR SETIAP SUB-DIMENSI
SUBDIMENSION_COLUMNS = {
    "Tuntutan Kuantitatif": "Sub_Tuntutan_Kuantitatif",
    "Laju Kerja": "Sub_Laju_Kerja",
    "Tuntutan Kognitif": "Sub_Tuntutan_Kognitif",
    "Tuntutan Emosional": "Sub_Tuntutan_Emosional",
    "Tuntutan untuk Menyembunyikan Emosi": "Sub_Tuntutan_Menyembunyikan_Emosi",
    "Pengaruh di Tempat Kerja": "Sub_Pengaruh_Tempat_Kerja",
    "Kemungkinan Pengembangan": "Sub_Kemungkinan_Pengembangan",
    "Variasi Pekerjaan": "Sub_Variasi_Pekerjaan",
    "Kendali atas Waktu Kerja": "Sub_Kendali_Waktu_Kerja",
    "Makna Kerja": "Sub_Makna_Kerja",
    "Prediktabilitas": "Sub_Prediktabilitas",
    "Pengakuan": "Sub_Pengakuan",
    "Kejelasan Peran": "Sub_Kejelasan_Peran",
    "Konflik Peran": "Sub_Konflik_Peran",
    "Tugas Tidak Sah": "Sub_Tugas_Tidak_Sah",
    "Kualitas Kepemimpinan": "Sub_Kualitas_Kepemimpinan",
    "Dukungan Sosial Atasan": "Sub_Dukungan_Sosial_Atasan",
    "Dukungan Sosial Rekan Kerja": "Sub_Dukungan_Sosial_Rekan_Kerja",
    "Rasa Kebersamaan": "Sub_Rasa_Kebersamaan",
    "Komitmen terhadap Tempat Kerja": "Sub_Komitmen_Tempat_Kerja",
    "Keterikatan Kerja": "Sub_Keterikatan_Kerja",
    "Job Insecurity": "Sub_Job_Insecurity",
    "Insecurity over Working Conditions": "Sub_Insecurity_Working_Conditions",
    "Kualitas Kerja": "Sub_Kualitas_Kerja",
    "Kepuasan Kerja": "Sub_Kepuasan_Kerja",
    "Konflik Pekerjaan - Kehidupan Pribadi": "Sub_Konflik_Pekerjaan_Kehidupan_Pribadi",
    "Kepercayaan Horizontal": "Sub_Kepercayaan_Horizontal",
    "Kepercayaan Vertikal": "Sub_Kepercayaan_Vertikal",
    "Keadilan Organisasional": "Sub_Keadilan_Organisasional",
    "Gosip dan Fitnah": "Sub_Gosip_Fitnah",
    "Pertengkaran dan Konflik": "Sub_Pertengkaran_Konflik",
    "Ejekan": "Sub_Ejekan",
    "Perundungan Siber": "Sub_Perundungan_Siber",
    "Pelecehan Seksual": "Sub_Pelecehan_Seksual",
    "Ancaman Kekerasan": "Sub_Ancaman_Kekerasan",
    "Kekerasan Fisik": "Sub_Kekerasan_Fisik",
    "Perundungan": "Sub_Perundungan",
    "Kesehatan yang Dinilai Diri Sendiri": "Sub_Kesehatan_Dinilai_Diri_Sendiri",
    "Masalah Tidur": "Sub_Masalah_Tidur",
    "Burnout": "Sub_Burnout",
    "Stress": "Sub_Stress",
    "Somatic Stress": "Sub_Somatic_Stress",
    "Cognitive Stress": "Sub_Cognitive_Stress",
    "Depressive Symptoms": "Sub_Depressive_Symptoms",
    "Self Efficacy": "Sub_Self_Efficacy"
}

# KLASIFIKASI POLARITAS SUB-DIMENSI: FAVORABLE VS UNFAVORABLE
# Ketentuan Kategori Skor (0-100):
# 0 - 33.33   -> Rendah
# 33.34 - 66.66 -> Sedang
# 66.67 - 100  -> Tinggi
SUBDIMENSION_POLARITY = {
    # TUNTUTAN PEKERJAAN (Unfavorable)
    "Tuntutan Kuantitatif": "Unfavorable",
    "Laju Kerja": "Unfavorable",
    "Tuntutan Kognitif": "Unfavorable",
    "Tuntutan Emosional": "Unfavorable",
    "Tuntutan untuk Menyembunyikan Emosi": "Unfavorable",

    # PENGORGANISASIAN KERJA DAN ISI PEKERJAAN (Favorable)
    "Pengaruh di Tempat Kerja": "Favorable",
    "Kemungkinan Pengembangan": "Favorable",
    "Variasi Pekerjaan": "Favorable",
    "Kendali atas Waktu Kerja": "Favorable",
    "Makna Kerja": "Favorable",

    # HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN
    "Prediktabilitas": "Favorable",
    "Pengakuan": "Favorable",
    "Kejelasan Peran": "Favorable",
    "Konflik Peran": "Favorable",
    "Tugas Tidak Sah": "Unfavorable",
    "Kualitas Kepemimpinan": "Unfavorable",
    "Dukungan Sosial Atasan": "Favorable",
    "Dukungan Sosial Rekan Kerja": "Favorable",
    "Rasa Kebersamaan": "Favorable",

    # KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI
    "Komitmen terhadap Tempat Kerja": "Favorable",
    "Keterikatan Kerja": "Favorable",
    "Job Insecurity": "Unfavorable",
    "Insecurity over Working Conditions": "Unfavorable",
    "Kualitas Kerja": "Favorable",
    "Kepuasan Kerja": "Favorable",
    "Konflik Pekerjaan - Kehidupan Pribadi": "Unfavorable",

    # MODAL SOSIAL (Favorable)
    "Kepercayaan Horizontal": "Favorable",
    "Kepercayaan Vertikal": "Favorable",
    "Keadilan Organisasional": "Favorable",

    # KONFLIK DAN PERILAKU OFENSIF (Unfavorable)
    "Gosip dan Fitnah": "Unfavorable",
    "Pertengkaran dan Konflik": "Unfavorable",
    "Ejekan": "Unfavorable",
    "Perundungan Siber": "Unfavorable",
    "Pelecehan Seksual": "Unfavorable",
    "Ancaman Kekerasan": "Unfavorable",
    "Kekerasan Fisik": "Unfavorable",
    "Perundungan": "Unfavorable",

    # HEALTH AND WELL-BEING
    "Kesehatan yang Dinilai Diri Sendiri": "Favorable",
    "Masalah Tidur": "Unfavorable",
    "Burnout": "Unfavorable",
    "Stress": "Unfavorable",
    "Somatic Stress": "Unfavorable",
    "Cognitive Stress": "Unfavorable",
    "Depressive Symptoms": "Unfavorable",

    # PERSONALITY/KEPRIBADIAN (Favorable)
    "Self Efficacy": "Favorable"
}

def get_score_level(score):
    """
    Kategori tingkat skor berdasarkan ketentuan:
    0 - 33.33   -> Rendah
    33.34 - 66.66 -> Sedang
    66.67 - 100  -> Tinggi
    """
    if score is None:
        return "-"
    try:
        val = float(score)
    except (ValueError, TypeError):
        return "-"
    if val <= 33.33:
        return "Rendah"
    elif val <= 66.66:
        return "Sedang"
    else:
        return "Tinggi"

def get_subdimension_status(sub_name, score):
    """
    Menentukan kategori (Rendah, Sedang, Tinggi), status interpretasi risiko,
    dan kode warna indikator berdasarkan polaritas Favorable / Unfavorable.
    """
    if score is None:
        return "-", "⚪ Belum Ada Data", "#94a3b8"
    
    level = get_score_level(score)
    polarity = SUBDIMENSION_POLARITY.get(sub_name, "Favorable")

    if polarity == "Favorable":
        if level == "Tinggi":
            status_text = "🟢 Baik (Risiko Rendah)"
            color = "#10b981"
        elif level == "Sedang":
            status_text = "🟡 Sedang (Risiko Sedang)"
            color = "#f59e0b"
        else:
            status_text = "🔴 Kurang (Risiko Tinggi)"
            color = "#ef4444"
    else:
        if level == "Rendah":
            status_text = "🟢 Baik (Risiko Rendah)"
            color = "#10b981"
        elif level == "Sedang":
            status_text = "🟡 Sedang (Risiko Sedang)"
            color = "#f59e0b"
        else:
            status_text = "🔴 Bahaya (Risiko Tinggi)"
            color = "#ef4444"

    return level, status_text, color

# LABEL DWIBAHASA (INGGRIS & INDONESIA) UNTUK SUB-DIMENSI
SUBDIMENSION_LABELS = {
    # TUNTUTAN PEKERJAAN
    "Tuntutan Kuantitatif": {"en": "Quantitative Demands", "id": "Jumlah Pekerjaan"},
    "Laju Kerja": {"en": "Work Pace", "id": "Kecepatan Kerja"},
    "Tuntutan Kognitif": {"en": "Cognitive Demands", "id": "Tuntutan Kognitif"},
    "Tuntutan Emosional": {"en": "Emotional Demands", "id": "Tuntutan Emosional"},
    "Tuntutan untuk Menyembunyikan Emosi": {"en": "Demands for Hiding Emotions", "id": "Mengendalikan Ekspresi Emosi"},

    # PENGORGANISASIAN KERJA DAN ISI PEKERJAAN
    "Pengaruh di Tempat Kerja": {"en": "Influence at Work", "id": "Pengaruh di Tempat Kerja"},
    "Kemungkinan Pengembangan": {"en": "Development Possibilities", "id": "Peluang Pengembangan Keterampilan"},
    "Variasi Pekerjaan": {"en": "Variation of Work", "id": "Variasi Pekerjaan"},
    "Kendali atas Waktu Kerja": {"en": "Control over Working Time", "id": "Kendali atas Waktu Kerja"},
    "Makna Kerja": {"en": "Meaning of Work", "id": "Makna Kerja"},

    # HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN
    "Prediktabilitas": {"en": "Predictability", "id": "Prediktabilitas Informasi"},
    "Pengakuan": {"en": "Recognition", "id": "Apresiasi & Pengakuan"},
    "Kejelasan Peran": {"en": "Role Clarity", "id": "Kejelasan Peran Kerja"},
    "Konflik Peran": {"en": "Role Conflicts", "id": "Konflik Peran Kerja"},
    "Tugas Tidak Sah": {"en": "Illegitimate Tasks", "id": "Tugas Tidak Sesuai"},
    "Kualitas Kepemimpinan": {"en": "Quality of Leadership", "id": "Kualitas Kepemimpinan"},
    "Dukungan Sosial Atasan": {"en": "Social Support from Supervisors", "id": "Dukungan Sosial Atasan"},
    "Dukungan Sosial Rekan Kerja": {"en": "Social Support from Colleagues", "id": "Dukungan Sosial Rekan Kerja"},
    "Rasa Kebersamaan": {"en": "Sense of Community", "id": "Rasa Kebersamaan Tim"},

    # KESEIMBANGAN KERJA DAN KEHIDUPAN PRIBADI
    "Komitmen terhadap Tempat Kerja": {"en": "Commitment to the Workplace", "id": "Komitmen Tempat Kerja"},
    "Keterikatan Kerja": {"en": "Work Engagement", "id": "Keterikatan Kerja"},
    "Job Insecurity": {"en": "Job Insecurity", "id": "Kekhawatiran Kehilangan Pekerjaan"},
    "Insecurity over Working Conditions": {"en": "Insecurity over Working Conditions", "id": "Ketidakpastian Kondisi Kerja"},
    "Kualitas Kerja": {"en": "Quality of Work", "id": "Kualitas Hasil Kerja"},
    "Kepuasan Kerja": {"en": "Job Satisfaction", "id": "Kepuasan Kerja"},
    "Konflik Pekerjaan - Kehidupan Pribadi": {"en": "Work-Life Conflict", "id": "Konflik Pekerjaan-Pribadi"},

    # MODAL SOSIAL
    "Kepercayaan Horizontal": {"en": "Horizontal Trust", "id": "Kepercayaan Antar Rekan"},
    "Kepercayaan Vertikal": {"en": "Vertical Trust", "id": "Kepercayaan thd Manajemen"},
    "Keadilan Organisasional": {"en": "Organizational Justice", "id": "Keadilan Organisasi"},

    # KONFLIK DAN PERILAKU OFENSIF
    "Gosip dan Fitnah": {"en": "Gossip and Slander", "id": "Gosip dan Fitnah"},
    "Pertengkaran dan Konflik": {"en": "Conflicts and Quarrels", "id": "Pertengkaran dan Konflik"},
    "Ejekan": {"en": "Teasing / Ridicule", "id": "Ejekan dan Hinaan"},
    "Perundungan Siber": {"en": "Cyberbullying", "id": "Pelecehan Media / Pesan Daring"},
    "Pelecehan Seksual": {"en": "Sexual Harassment", "id": "Pelecehan Seksual"},
    "Ancaman Kekerasan": {"en": "Threats of Violence", "id": "Ancaman Kekerasan"},
    "Kekerasan Fisik": {"en": "Physical Violence", "id": "Kekerasan Fisik"},
    "Perundungan": {"en": "Bullying", "id": "Perundungan di Tempat Kerja"},

    # HEALTH AND WELL-BEING
    "Kesehatan yang Dinilai Diri Sendiri": {"en": "Self-Rated Health", "id": "Kesehatan Dinilai Sendiri"},
    "Masalah Tidur": {"en": "Sleeping Troubles", "id": "Masalah Kualitas Tidur"},
    "Burnout": {"en": "Burnout", "id": "Kelelahan Fisik & Mental"},
    "Stress": {"en": "Stress", "id": "Tingkat Stres Kerja"},
    "Somatic Stress": {"en": "Somatic Stress", "id": "Stres Somatik / Fisik"},
    "Cognitive Stress": {"en": "Cognitive Stress", "id": "Stres Kognitif / Konsentrasi"},
    "Depressive Symptoms": {"en": "Depressive Symptoms", "id": "Gejala Depresif"},

    # PERSONALITY/KEPRIBADIAN
    "Self Efficacy": {"en": "Self Efficacy", "id": "Efikasi Diri / Keyakinan Diri"}
}

def get_subdimension_badge_style(level, polarity):
    """
    Mengembalikan style warna untuk pill badge kategori (Rendah, Sedang, Tinggi)
    dan batang progress bar sesuai referensi visual UI horizontal bar.
    """
    if polarity == "Favorable":
        if level == "Tinggi":
            return {"bg": "#ecfdf5", "text": "#059669", "border": "#a7f3d0", "bar": "#10b981"}
        elif level == "Sedang":
            return {"bg": "#fffbeb", "text": "#d97706", "border": "#fde68a", "bar": "#f59e0b"}
        else: # Rendah
            return {"bg": "#fef2f2", "text": "#dc2626", "border": "#fecaca", "bar": "#ef4444"}
    else: # Unfavorable
        if level == "Rendah":
            return {"bg": "#ecfdf5", "text": "#059669", "border": "#a7f3d0", "bar": "#10b981"}
        elif level == "Sedang":
            return {"bg": "#fffbeb", "text": "#d97706", "border": "#fde68a", "bar": "#f59e0b"}
        else: # Tinggi
            return {"bg": "#fef2f2", "text": "#dc2626", "border": "#fecaca", "bar": "#ef4444"}

def render_horizontal_subdimension_table(items, title, subtitle="Berikut adalah hasil penilaian pada setiap subdimensi dalam kategori ini."):
    """
    Menghasilkan HTML Card Table dengan Horizontal Barchart per sub-bidang
    sesuai dengan referensi desain visual yang diminta pengguna.
    """
    rows_html = ""
    for idx, item in enumerate(items, 1):
        s_name = item["sub_name"]
        score = float(item["score"])
        score_clamped = min(max(score, 0.0), 100.0)

        label_info = SUBDIMENSION_LABELS.get(s_name, {"en": s_name, "id": s_name})
        primary_title = label_info["en"]
        secondary_desc = f"({label_info['id']})"

        level = get_score_level(score)
        polarity = SUBDIMENSION_POLARITY.get(s_name, "Favorable")
        style = get_subdimension_badge_style(level, polarity)

        rows_html += f"""
        <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 13px 10px; text-align: center; color: #64748b; font-weight: 600; font-size: 13.5px;">{idx}</td>
            <td style="padding: 13px 16px; text-align: left;">
                <div style="font-weight: 700; color: #1e3a8a; font-size: 14.5px; line-height: 1.3;">{primary_title}</div>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px; font-weight: 500;">{secondary_desc}</div>
            </td>
            <td style="padding: 13px 16px; text-align: left;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="min-width: 42px; font-weight: 700; color: #0f172a; font-size: 15px; text-align: right; font-variant-numeric: tabular-nums;">{score:.1f}</div>
                    <div style="flex: 1; background: #f1f5f9; border-radius: 8px; height: 16px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.06); min-width: 140px;">
                        <div style="width: {score_clamped}%; background: {style['bar']}; height: 100%; border-radius: 8px; transition: width 0.4s ease;"></div>
                    </div>
                </div>
            </td>
            <td style="padding: 13px 16px; text-align: center;">
                <span style="display: inline-block; padding: 4px 18px; border-radius: 20px; font-weight: 700; font-size: 12px; background: {style['bg']}; color: {style['text']}; border: 1px solid {style['border']}; letter-spacing: 0.3px;">
                    {level}
                </span>
            </td>
        </tr>
        """

    html = f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 26px; box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05); margin-bottom: 22px;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1.5px solid #f1f5f9;">
            <div style="background: #fee2e2; border: 1px solid #fecaca; border-radius: 12px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 22px;">
                📊
            </div>
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">{title}</h3>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #64748b;">{subtitle}</p>
            </div>
        </div>

        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-family: inherit;">
                <thead>
                    <tr style="border-bottom: 1.5px solid #e2e8f0; color: #475569; font-size: 12.5px; font-weight: 700;">
                        <th style="padding: 10px 10px; text-align: center; width: 45px;">No.</th>
                        <th style="padding: 10px 16px; text-align: left;">Subdimensi</th>
                        <th style="padding: 10px 16px; text-align: left; width: 48%;">Skor</th>
                        <th style="padding: 10px 16px; text-align: center; width: 130px;">Kategori</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return html

def calculate_category_scores(answers):
    """
    Menghitung skor rata-rata (0-100) per kategori dan skor rata-rata total
    answers: dict {id_pertanyaan: jawaban_string}
    """
    category_scores = {}
    all_scores = []
    
    for category, questions in SURVEY_QUESTIONS.items():
        cat_scores = []
        for q in questions:
            qid = q["id"]
            code = q["code"]
            ans = answers.get(qid)
            # 5M adalah pertanyaan kualitatif pelaku (tidak dihitung sebagai skor numerik)
            if code == "5M":
                continue
            score = calculate_score(code, ans)
            if score is not None:
                cat_scores.append(score)
                all_scores.append(score)
        
        if cat_scores:
            avg_cat = sum(cat_scores) / len(cat_scores)
            category_scores[category] = round(avg_cat, 1)
        else:
            category_scores[category] = 0.0
            
    overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    return category_scores, overall_avg

def calculate_subdimension_scores(answers):
    """
    Menghitung skor rata-rata (0-100) per sub-dimensi.
    answers: dict {id_pertanyaan: jawaban_string}
    Returns: dict {sub_name: float_score}
    """
    sub_scores = {}
    for cat, questions in SURVEY_QUESTIONS.items():
        sub_map = {}
        for q in questions:
            sub = q.get("sub", cat)
            sub_map.setdefault(sub, []).append(q)
        
        for sub, qlist in sub_map.items():
            scores = []
            for q in qlist:
                qid = q["id"]
                code = q["code"]
                if code == "5M":
                    continue
                ans = answers.get(qid)
                score = calculate_score(code, ans)
                if score is not None:
                    scores.append(score)
            if scores:
                sub_scores[sub] = round(sum(scores) / len(scores), 1)
            else:
                sub_scores[sub] = 0.0
    return sub_scores

def compute_subdimensions_for_df(df):
    """
    Menghitung dan melengkapi kolom-kolom sub-dimensi jika belum ada pada dataframe.
    """
    if df is None or df.empty:
        return df
    
    missing_cols = [col for col in SUBDIMENSION_COLUMNS.values() if col not in df.columns]
    if not missing_cols:
        return df

    # Hitung untuk setiap baris
    new_cols_data = {col: [] for col in SUBDIMENSION_COLUMNS.values()}
    
    for _, row in df.iterrows():
        ans_dict = {c: row[c] for c in df.columns if pd.notna(row[c])}
        sub_scores = calculate_subdimension_scores(ans_dict)
        for sub_name, col_name in SUBDIMENSION_COLUMNS.items():
            new_cols_data[col_name].append(sub_scores.get(sub_name, 0.0))
            
    for col_name, data in new_cols_data.items():
        df[col_name] = data
        
    return df

# =====================================================================
# KONFIGURASI SEGMEN 2: KESEHATAN MENTAL (DASS-21)
# =====================================================================
SEGMEN2_OPTIONS = [
    "0 - Tidak sesuai dengan diri saya",
    "1 - Sesuai dengan diri pada tingkat tertentu",
    "2 - Sesuai dengan diri saya pada tingkat yang cukup besar",
    "3 - Sangat sesuai dengan diri saya"
]

SCORING_MAP_SEGMEN2 = {
    "0 - Tidak sesuai dengan diri saya": 0,
    "1 - Sesuai dengan diri pada tingkat tertentu": 1,
    "2 - Sesuai dengan diri saya pada tingkat yang cukup besar": 2,
    "3 - Sangat sesuai dengan diri saya": 3,
    "0 = Tidak sesuai dengan diri saya": 0,
    "1 = Sesuai dengan diri pada tingkat tertentu": 1,
    "2 = Sesuai dengan diri saya pada tingkat yang cukup besar": 2,
    "3 = Sangat sesuai dengan diri saya": 3,
    "Tidak sesuai dengan diri saya": 0,
    "Sesuai dengan diri pada tingkat tertentu": 1,
    "Sesuai dengan diri saya pada tingkat yang cukup besar": 2,
    "Sangat sesuai dengan diri saya": 3,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3
}

SURVEY_QUESTIONS_SEGMEN2 = {
    "Tingkat Energi dan Suasana Hati": [
        {"id": "D1", "text": "Saya sama sekali tidak dapat merasakan perasaan positif (contoh: merasa gembira, bangga, dsb)."},
        {"id": "D2", "text": "Saya merasa sulit berinisiatif melakukan sesuatu."},
        {"id": "D3", "text": "Saya merasa tidak ada lagi yang bisa saya harapkan."},
        {"id": "D4", "text": "Saya merasa sedih dan tertekan."},
        {"id": "D5", "text": "Saya tidak bisa merasa antusias terhadap hal apapun."},
        {"id": "D6", "text": "Saya merasa diri saya tidak berharga."},
        {"id": "D7", "text": "Saya merasa hidup ini tidak berarti."}
    ],
    "Respons Fisik dan  tingkat Kenyamanan Situasional": [
        {"id": "K1", "text": "Saya merasa rongga mulut saya kering."},
        {"id": "K2", "text": "Saya merasa kesulitan bernafas (misalnya seringkali terengah-engah atau tidak dapat bernapas padahal tidak melakukan aktivitas fisik sebelumnya)."},
        {"id": "K3", "text": "Saya merasa gemetar (misalnya pada tangan)."},
        {"id": "K4", "text": "Saya merasa khawatir dengan situasi dimana saya mungkin menjadi panik dan mempermalukan diri sendiri."},
        {"id": "K5", "text": "Saya merasa hampir panik."},
        {"id": "K6", "text": "Saya menyadari kondisi jantung saya (seperti meningkatnya atau melemahnya detak jantung) meskipun sedang tidak melakukan aktivitas fisik."},
        {"id": "K7", "text": "Saya merasa ketakutan tanpa alasan yang jelas."}
    ],
    "Pengelolaan Tekanan atau Ketegangan Kerja": [
        {"id": "S1", "text": "Saya merasa sulit untuk beristirahat."},
        {"id": "S2", "text": "Saya cenderung menunjukkan reaksi berlebihan terhadap suatu situasi."},
        {"id": "S3", "text": "Saya merasa energi saya terkuras karena terlalu cemas."},
        {"id": "S4", "text": "Saya merasa gelisah."},
        {"id": "S5", "text": "Saya merasa sulit untuk merasa tenang."},
        {"id": "S6", "text": "Saya sulit untuk bersabar dalam menghadapi gangguan yang terjadi ketika sedang melakukan sesuatu."},
        {"id": "S7", "text": "Perasaan saya mudah tergugah atau tersentuh."}
    ]
}

CATEGORY_METADATA_SEGMEN2 = {
    "Tingkat Energi dan Suasana Hati": {
        "label": "Tingkat Energi dan Suasana Hati (Depression)",
        "short": "Depresi",
        "icon": "🌧️",
        "desc": "Berikut ini terdapat sejumlah butir yang berkaitan dengan suasana hati dan perasaan sedih atau kehilangan minat. Nilailah seberapa sesuai dengan kondisi Anda."
    },
    "Respons Fisik dan  tingkat Kenyamanan Situasional": {
        "label": "Respons Fisik dan  tingkat Kenyamanan Situasional (Anxiety)",
        "short": "Kecemasan",
        "icon": "⚡",
        "desc": "Berikut ini terdapat sejumlah butir yang berkaitan dengan reaksi kecemasan, kegugupan, dan ketakutan fisik tubuh. Nilailah seberapa sesuai dengan kondisi Anda."
    },
    "Pengelolaan Tekanan atau Ketegangan Kerja": {
        "label": "Pengelolaan Tekanan atau Ketegangan Kerja (Stress)",
        "short": "Stress",
        "icon": "🔥",
        "desc": "Berikut ini terdapat sejumlah butir yang berkaitan dengan ketegangan fisik/emosional dan iritabilitas. Nilailah seberapa sesuai dengan kondisi Anda."
    }
}

DIMENSION_COLUMNS_SEGMEN2 = {
    "Tingkat Energi dan Suasana Hati": "Skor_Segmen2_Depresi",
    "Respons Fisik dan  tingkat Kenyamanan Situasional": "Skor_Segmen2_Kecemasan",
    "Pengelolaan Tekanan atau Ketegangan Kerja": "Skor_Segmen2_Stress"
}

def calculate_score_segmen2(answer):
    """Menghitung skor numerik (0-3) untuk butir pertanyaan Segmen 2"""
    if answer is None:
        return None
    ans_str = str(answer).strip()
    if ans_str in SCORING_MAP_SEGMEN2:
        return SCORING_MAP_SEGMEN2[ans_str]
    if len(ans_str) > 0 and ans_str[0] in ("0", "1", "2", "3"):
        return int(ans_str[0])
    return None

def get_dass_severity(dimension, score):
    """
    Menentukan tingkat keparahan DASS-21 berdasarkan skor total dimensi yang telah dikalikan 2 (skala 0-42):
    - Kecemasan: 0-7 Normal, 8-9 Ringan, 10-14 Sedang, 15-19 Berat, 20+ Sangat Berat
    - Stres: 0-14 Normal, 15-18 Ringan, 19-25 Sedang, 26-33 Berat, 34+ Sangat Berat
    - Depresi: 0-9 Normal, 10-13 Ringan, 14-20 Sedang, 21-27 Berat, 28+ Sangat Berat
    """
    if score is None:
        return "Normal"
    score = float(score)
    dim_str = str(dimension).strip()

    # Dimensi Depresi / Tingkat Energi dan Suasana Hati
    if any(k in dim_str for k in ["Depresi", "Depression", "Energi dan Suasana Hati"]):
        if score <= 9:
            return "Normal"
        elif score <= 13:
            return "Ringan"
        elif score <= 20:
            return "Sedang"
        elif score <= 27:
            return "Berat"
        else:
            return "Sangat Berat"

    # Dimensi Kecemasan / Respons Fisik dan Kenyamanan Situasional
    elif any(k in dim_str for k in ["Kecemasan", "Anxiety", "Respons Fisik"]):
        if score <= 7:
            return "Normal"
        elif score <= 9:
            return "Ringan"
        elif score <= 14:
            return "Sedang"
        elif score <= 19:
            return "Berat"
        else:
            return "Sangat Berat"

    # Dimensi Stress / Pengelolaan Tekanan atau Ketegangan Kerja
    elif any(k in dim_str for k in ["Stress", "Stres", "Pengelolaan Tekanan", "Ketegangan Kerja"]):
        if score <= 14:
            return "Normal"
        elif score <= 18:
            return "Ringan"
        elif score <= 25:
            return "Sedang"
        elif score <= 33:
            return "Berat"
        else:
            return "Sangat Berat"

    return "Normal"

def calculate_segmen2_scores(answers_segmen2):
    """
    Menghitung skor per dimensi untuk Segmen 2 (Total poin dikalikan 2 sehingga rentang 0-42 per dimensi),
    total skor Segmen 2 (rentang 0-126), dan tingkat keparahan DASS-21 (Normal, Ringan, Sedang, Berat, Sangat Berat).
    """
    dimension_scores = {}
    severity_levels = {}
    all_raw_scores = []

    for dim, questions in SURVEY_QUESTIONS_SEGMEN2.items():
        dim_scores = []
        for q in questions:
            qid = q["id"]
            ans = answers_segmen2.get(qid) if answers_segmen2 else None
            score = calculate_score_segmen2(ans)
            if score is not None:
                dim_scores.append(score)
                all_raw_scores.append(score)

        raw_total_dim = sum(dim_scores) if dim_scores else 0
        final_dim_score = raw_total_dim * 2  # Total skor dikalikan dua
        short_name = CATEGORY_METADATA_SEGMEN2.get(dim, {}).get("short", dim)

        # Simpan untuk kedua kunci: nama lengkap dimensi dan nama pendek (Depresi, Kecemasan, Stress)
        dimension_scores[dim] = final_dim_score
        dimension_scores[short_name] = final_dim_score

        sev = get_dass_severity(dim, final_dim_score)
        severity_levels[dim] = sev
        severity_levels[short_name] = sev

    # Total skor Segmen 2 (skor mentah dikalikan dua)
    total_segmen2 = sum(all_raw_scores) * 2 if all_raw_scores else 0
    return dimension_scores, total_segmen2, severity_levels

def compute_segmen2_for_df(df):
    """
    Memastikan kolom Segmen 2 (skor terkalibrasi x2 dan kategori keparahan DASS-21)
    terhitung dan tersedia di dataframe.
    """
    if df is None or df.empty:
        return df

    # Cek apakah ada butir pertanyaan Segmen 2 di DataFrame (D1..D7, K1..K7, S1..S7)
    seg2_q_ids = [q["id"] for qs in SURVEY_QUESTIONS_SEGMEN2.values() for q in qs]
    has_questions = any(qid in df.columns for qid in seg2_q_ids)

    if has_questions:
        dep_scores, anx_scores, str_scores = [], [], []
        tot_scores = []
        dep_levels, anx_levels, str_levels = [], [], []

        for _, row in df.iterrows():
            ans_seg2 = {c: row[c] for c in seg2_q_ids if c in df.columns and pd.notna(row[c])}
            scores, total, severities = calculate_segmen2_scores(ans_seg2)

            dep_scores.append(scores.get("Depresi", 0))
            anx_scores.append(scores.get("Kecemasan", 0))
            str_scores.append(scores.get("Stress", 0))
            tot_scores.append(total)

            dep_levels.append(severities.get("Depresi", "Normal"))
            anx_levels.append(severities.get("Kecemasan", "Normal"))
            str_levels.append(severities.get("Stress", "Normal"))

        df["Skor_Segmen2_Depresi"] = dep_scores
        df["Skor_Segmen2_Kecemasan"] = anx_scores
        df["Skor_Segmen2_Stress"] = str_scores
        df["Total_Skor_Segmen2"] = tot_scores
        df["Tingkat_Depresi"] = dep_levels
        df["Tingkat_Kecemasan"] = anx_levels
        df["Tingkat_Stress"] = str_levels
    else:
        for col_name, dim_key in [("Skor_Segmen2_Depresi", "Depresi"),
                                  ("Skor_Segmen2_Kecemasan", "Kecemasan"),
                                  ("Skor_Segmen2_Stress", "Stress")]:
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce").fillna(0)
                if df[col_name].max() <= 21 and (df[col_name] > 0).any():
                    df[col_name] = df[col_name] * 2
                df[f"Tingkat_{dim_key}"] = df[col_name].apply(lambda s: get_dass_severity(dim_key, s))

        if "Total_Skor_Segmen2" in df.columns:
            df["Total_Skor_Segmen2"] = (
                df.get("Skor_Segmen2_Depresi", 0) +
                df.get("Skor_Segmen2_Kecemasan", 0) +
                df.get("Skor_Segmen2_Stress", 0)
            )

    return df
