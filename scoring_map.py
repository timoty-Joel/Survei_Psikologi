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

PILIHAN_5M = ["Teman Kerja", "Atasan/Pimpinan", "Masyarakat/Pengguna", "Layanan Pihak Luar", "Tidak ada"]

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
        {"id": "T1_Q1", "text": "Apakah pekerjaan Anda sering menumpuk karena pembagian beban kerja tidak merata?", "code": "1"},
        {"id": "T1_Q2", "text": "Seberapa sering Anda tidak memiliki cukup waktu untuk menyelesaikan semua tugas pekerjaan?", "code": "1"},
        {"id": "T1_Q3", "text": "Seberapa sering pekerjaan Anda tertunda atau belum selesai sesuai rencana?", "code": "1"},
        {"id": "T1_Q4", "text": "Apakah waktu yang tersedia cukup untuk menyelesaikan tugas pekerjaan Anda?", "code": "1R"},
        {"id": "T1_Q5", "text": "Apakah Anda dituntut untuk bekerja dengan sangat cepat?", "code": "1"},
        {"id": "T1_Q6", "text": "Apakah Anda harus bekerja dengan cepat hampir sepanjang hari?", "code": "2"},
        {"id": "T1_Q7", "text": "Apakah Anda harus terus bekerja dengan cepat?", "code": "2"},
        {"id": "T1_Q8", "text": "Apakah saat bekerja Anda harus memperhatikan banyak hal sekaligus?", "code": "1"},
        {"id": "T1_Q9", "text": "Apakah pekerjaan Anda mengharuskan Anda mengingat banyak informasi atau hal?", "code": "1"},
        {"id": "T1_Q10", "text": "Apakah pekerjaan Anda menuntut Anda untuk menghasilkan ide-ide baru?", "code": "1"},
        {"id": "T1_Q11", "text": "Apakah pekerjaan Anda mengharuskan Anda mengambil keputusan yang sulit?", "code": "1"},
        {"id": "T1_Q12", "text": "Apakah pekerjaan Anda membuat Anda menghadapi situasi yang mengganggu perasaan?", "code": "1"},
        {"id": "T1_Q13", "text": "Apakah dalam pekerjaan Anda, Anda perlu menangani masalah pribadi orang lain?", "code": "1"},
        {"id": "T1_Q14", "text": "Apakah pekerjaan Anda menuntut banyak tenaga atau keterlibatan emosional?", "code": "2"},
        {"id": "T1_Q15", "text": "Apakah Anda harus memperlakukan semua orang dengan setara, meskipun perasaan Anda sedang tidak mendukung?", "code": "1"},
        {"id": "T1_Q16", "text": "Apakah Anda harus menyembunyikan perasaan saat bekerja?", "code": "2"},
        {"id": "T1_Q17", "text": "Apakah Anda harus tetap bersikap ramah dan terbuka kepada semua orang, apa pun sikap mereka kepada Anda?", "code": "2"},
        {"id": "T1_Q18", "text": "Apakah Anda harus menahan diri untuk tidak menyampaikan pendapat saat bekerja?", "code": "1"},
    ],
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": [
        {"id": "T2_Q1", "text": "Apakah Anda memiliki kesempatan untuk ikut memengaruhi keputusan yang berkaitan dengan pekerjaan Anda?", "code": "1"},
        {"id": "T2_Q2", "text": "Apakah Anda dapat ikut menentukan dengan siapa Anda bekerja?", "code": "1"},
        {"id": "T2_Q3", "text": "Apakah Anda dapat memengaruhi banyaknya pekerjaan yang diberikan kepada Anda?", "code": "1"},
        {"id": "T2_Q4", "text": "Apakah Anda dapat memengaruhi jenis atau kegiatan pekerjaan yang Anda lakukan?", "code": "1"},
        {"id": "T2_Q5", "text": "Apakah Anda dapat memengaruhi kecepatan dalam menyelesaikan pekerjaan?", "code": "1"},
        {"id": "T2_Q6", "text": "Apakah Anda dapat menentukan cara untuk menyelesaikan pekerjaan Anda?", "code": "1"},
        {"id": "T2_Q7", "text": "Apakah pekerjaan Anda memberi kesempatan untuk mempelajari hal-hal baru?", "code": "2"},
        {"id": "T2_Q8", "text": "Apakah Anda dapat menggunakan keterampilan atau keahlian yang Anda miliki dalam pekerjaan?", "code": "2"},
        {"id": "T2_Q9", "text": "Apakah pekerjaan Anda memberi kesempatan untuk meningkatkan keterampilan?", "code": "2"},
        {"id": "T2_Q10", "text": "Apakah tugas-tugas yang Anda kerjakan cukup beragam?", "code": "1"},
        {"id": "T2_Q11", "text": "Apakah Anda harus melakukan tugas yang sama berulang kali?", "code": "1R"},
        {"id": "T2_Q12", "text": "Apakah Anda dapat menentukan sendiri kapan akan beristirahat?", "code": "1"},
        {"id": "T2_Q13", "text": "Apakah Anda dapat mengambil cuti pada waktu yang Anda inginkan?", "code": "1"},
        {"id": "T2_Q14", "text": "Apakah Anda dapat meninggalkan pekerjaan sebentar untuk berbincang dengan rekan kerja?", "code": "1"},
        {"id": "T2_Q15", "text": "Jika ada urusan pribadi, apakah Anda dapat meninggalkan tempat kerja selama sekitar 30 menit tanpa harus meminta izin khusus?", "code": "1"},
        {"id": "T2_Q16", "text": "Apakah Anda perlu bekerja melebihi jam kerja yang ditetapkan (lembur)?", "code": "1R"},
        {"id": "T2_Q17", "text": "Apakah pekerjaan yang Anda lakukan terasa bermakna?", "code": "2"},
        {"id": "T2_Q18", "text": "Apakah Anda merasa pekerjaan yang Anda lakukan itu penting?", "code": "2"},
    ],
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": [
        {"id": "T3_Q1", "text": "Apakah Anda mendapat informasi lebih awal tentang keputusan penting, perubahan, atau rencana di tempat kerja?", "code": "2"},
        {"id": "T3_Q2", "text": "Apakah Anda memperoleh informasi yang dibutuhkan untuk menyelesaikan pekerjaan dengan baik?", "code": "2"},
        {"id": "T3_Q3", "text": "Apakah atasan atau manajemen mengakui dan menghargai hasil pekerjaan Anda?", "code": "2"},
        {"id": "T3_Q4", "text": "Apakah atasan atau manajemen menghormati Anda?", "code": "2"},
        {"id": "T3_Q5", "text": "Apakah Anda diperlakukan secara adil di tempat kerja?", "code": "2"},
        {"id": "T3_Q6", "text": "Apakah tujuan pekerjaan Anda jelas?", "code": "2"},
        {"id": "T3_Q7", "text": "Apakah Anda mengetahui dengan jelas tugas dan tanggung jawab Anda?", "code": "2"},
        {"id": "T3_Q8", "text": "Apakah Anda memahami dengan jelas apa yang diharapkan dari Anda dalam pekerjaan?", "code": "2"},
        {"id": "T3_Q9", "text": "Apakah Anda menerima tuntutan pekerjaan yang saling bertentangan?", "code": "2"},
        {"id": "T3_Q10", "text": "Apakah Anda terkadang harus melakukan pekerjaan dengan cara yang menurut Anda kurang tepat?", "code": "2"},
        {"id": "T3_Q11", "text": "Apakah Anda terkadang harus mengerjakan sesuatu yang menurut Anda tidak diperlukan?", "code": "2"},
        {"id": "T3_Q12", "text": "Apakah atasan langsung Anda memastikan bahwa Anda memiliki kesempatan untuk mengembangkan kemampuan?", "code": "2"},
        {"id": "T3_Q13", "text": "Apakah atasan langsung Anda mengutamakan kepuasan kerja staf?", "code": "2"},
        {"id": "T3_Q14", "text": "Apakah atasan langsung Anda mampu merencanakan pekerjaan dengan baik?", "code": "2"},
        {"id": "T3_Q15", "text": "Apakah atasan langsung Anda mampu menyelesaikan konflik dengan baik?", "code": "2"},
        {"id": "T3_Q16", "text": "Seberapa sering atasan langsung Anda bersedia mendengarkan masalah pekerjaan Anda ketika Anda membutuhkan bantuan?", "code": "1"},
        {"id": "T3_Q17", "text": "Seberapa sering Anda mendapat bantuan atau dukungan dari atasan langsung ketika membutuhkannya?", "code": "1"},
        {"id": "T3_Q18", "text": "Seberapa sering atasan langsung Anda membahas dengan Anda bagaimana pekerjaan Anda dilakukan?", "code": "1"},
        {"id": "T3_Q19", "text": "Seberapa sering Anda mendapat bantuan atau dukungan dari rekan kerja ketika membutuhkannya?", "code": "1"},
        {"id": "T3_Q20", "text": "Seberapa sering rekan kerja bersedia mendengarkan masalah pekerjaan Anda ketika Anda membutuhkannya?", "code": "1"},
        {"id": "T3_Q21", "text": "Seberapa sering rekan kerja membahas dengan Anda bagaimana pekerjaan Anda dilakukan?", "code": "1"},
        {"id": "T3_Q22", "text": "Apakah Anda merasa nyaman dengan suasana kerja bersama rekan-rekan?", "code": "1"},
        {"id": "T3_Q23", "text": "Apakah rekan-rekan di tempat kerja bekerja sama dengan baik?", "code": "1"},
        {"id": "T3_Q24", "text": "Apakah Anda merasa menjadi bagian dari lingkungan kerja ini?", "code": "1"},
    ],
    "ANTARMUKA KERJA INDIVIDU": [
        {"id": "T4_Q1", "text": "Apakah Anda senang bercerita kepada orang lain tentang tempat Anda bekerja?", "code": "2"},
        {"id": "T4_Q2", "text": "Apakah tempat Anda bekerja memiliki arti penting bagi Anda?", "code": "2"},
        {"id": "T4_Q3", "text": "Apakah Anda akan menyarankan orang lain untuk melamar pekerjaan di tempat Anda bekerja?", "code": "2"},
        {"id": "T4_Q4", "text": "Seberapa sering Anda mempertimbangkan untuk mencari pekerjaan di tempat lain?", "code": "1R"},
        {"id": "T4_Q5", "text": "Apakah Anda bangga menjadi bagian dari organisasi ini?", "code": "2"},
        {"id": "T4_Q6", "text": "Saat bekerja, saya merasa berenergi.", "code": "3"},
        {"id": "T4_Q7", "text": "Saya merasa antusias saat mengerjakan pekerjaan saya.", "code": "3"},
        {"id": "T4_Q8", "text": "Saya sangat larut atau fokus ketika mengerjakan pekerjaan saya.", "code": "3"},
        {"id": "T4_Q9", "text": "Apakah Anda khawatir akan kehilangan pekerjaan dan menjadi pengangguran?", "code": "2"},
        {"id": "T4_Q10", "text": "Apakah Anda khawatir perkembangan teknologi dapat membuat pekerjaan Anda tidak lagi dibutuhkan?", "code": "2"},
        {"id": "T4_Q11", "text": "Apakah Anda khawatir akan sulit mendapatkan pekerjaan lain jika kehilangan pekerjaan saat ini?", "code": "2"},
        {"id": "T4_Q12", "text": "Apakah Anda khawatir dipindahkan ke pekerjaan lain tanpa keinginan Anda sendiri?", "code": "2"},
        {"id": "T4_Q13", "text": "Apakah Anda khawatir tugas pekerjaan Anda akan diubah tanpa persetujuan Anda?", "code": "2"},
        {"id": "T4_Q14", "text": "Apakah Anda khawatir jadwal kerja Anda—seperti giliran kerja, hari kerja, atau jam masuk dan pulang—diubah tanpa persetujuan Anda?", "code": "2"},
        {"id": "T4_Q15", "text": "Apakah Anda khawatir penghasilan atau gaji Anda akan dikurangi?", "code": "2"},
        {"id": "T4_Q16", "text": "Apakah menurut Anda pekerjaan Anda memiliki prospek atau peluang yang baik ke depannya?", "code": "2R"},
        {"id": "T4_Q17", "text": "Sejauh mana Anda merasa dapat menyelesaikan tugas dengan hasil yang memuaskan?", "code": "2"},
        {"id": "T4_Q18", "text": "Apakah Anda puas dengan kualitas pekerjaan yang dihasilkan di tempat kerja Anda?", "code": "2"},
        {"id": "T4_Q19", "text": "Seberapa puas Anda dengan peluang atau prospek pekerjaan Anda ke depannya?", "code": "6"},
        {"id": "T4_Q20", "text": "Seberapa puas Anda dengan kondisi fisik tempat kerja, seperti ruang, pencahayaan, dan fasilitas?", "code": "6"},
        {"id": "T4_Q21", "text": "Seberapa puas Anda dengan cara keterampilan dan kemampuan Anda digunakan dalam pekerjaan?", "code": "6"},
        {"id": "T4_Q22", "text": "Secara keseluruhan, seberapa puas Anda dengan pekerjaan Anda?", "code": "6"},
        {"id": "T4_Q23", "text": "Seberapa puas Anda dengan gaji yang Anda terima?", "code": "6"},
        {"id": "T4_Q24", "text": "Apakah Anda pernah merasa harus berada di tempat kerja dan di rumah pada waktu yang sama?", "code": "1"},
        {"id": "T4_Q25", "text": "Apakah pekerjaan menguras energi Anda hingga mengganggu kehidupan pribadi?", "code": "2"},
        {"id": "T4_Q26", "text": "Apakah pekerjaan menyita banyak waktu hingga mengganggu kehidupan pribadi Anda?", "code": "2"},
        {"id": "T4_Q27", "text": "Apakah tuntutan pekerjaan mengganggu kehidupan pribadi atau keluarga Anda?", "code": "2"},
        {"id": "T4_Q28", "text": "Apakah urusan pekerjaan membuat Anda harus mengubah rencana kegiatan pribadi atau keluarga?", "code": "2"},
    ],
    "MODAL SOSIAL": [
        {"id": "T5_Q1", "text": "Apakah pegawai saling menahan atau tidak membagikan informasi yang seharusnya diketahui bersama?", "code": "2R"},
        {"id": "T5_Q2", "text": "Apakah pegawai menahan informasi dari pihak manajemen?", "code": "2R"},
        {"id": "T5_Q3", "text": "Apakah pegawai di tempat kerja saling percaya?", "code": "2"},
        {"id": "T5_Q4", "text": "Apakah manajemen mempercayai pegawai untuk melakukan pekerjaan dengan baik?", "code": "2"},
        {"id": "T5_Q5", "text": "Apakah pegawai dapat mempercayai informasi yang disampaikan oleh manajemen?", "code": "2"},
        {"id": "T5_Q6", "text": "Apakah manajemen menahan informasi penting yang seharusnya diketahui pegawai?", "code": "2R"},
        {"id": "T5_Q7", "text": "Apakah pegawai dapat menyampaikan pendapat dan perasaan mereka secara terbuka?", "code": "2"},
        {"id": "T5_Q8", "text": "Apakah konflik di tempat kerja diselesaikan secara adil?", "code": "2"},
        {"id": "T5_Q9", "text": "Apakah pegawai mendapat penghargaan ketika melakukan pekerjaan dengan baik?", "code": "2"},
        {"id": "T5_Q10", "text": "Apakah manajemen menanggapi saran dari pegawai dengan serius?", "code": "2"},
        {"id": "T5_Q11", "text": "Apakah pembagian pekerjaan dilakukan secara adil?", "code": "2"},
    ],
    "KONFLIK DAN PERILAKU OFENSIF": [
        {"id": "T6_Q1", "text": "Dalam 12 bulan terakhir, apakah Anda menjadi sasaran gosip atau fitnah di tempat kerja?", "code": "4"},
        {"id": "T6_Q2", "text": "Jika ya, siapa yang melakukannya? (Gosip/Fitnah)", "code": "5M"},
        {"id": "T6_Q3", "text": "Dalam 12 bulan terakhir, apakah Anda terlibat pertengkaran atau konflik di tempat kerja?", "code": "4"},
        {"id": "T6_Q4", "text": "Jika ya, siapa yang melakukannya? (Pertengkaran/Konflik)", "code": "5M"},
        {"id": "T6_Q5", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami ejekan yang membuat Anda tidak nyaman di tempat kerja?", "code": "4"},
        {"id": "T6_Q6", "text": "Jika ya, siapa yang melakukannya? (Ejekan)", "code": "5M"},
        {"id": "T6_Q7", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami gangguan atau pelecehan terkait pekerjaan melalui media sosial, email, atau pesan teks?", "code": "4"},
        {"id": "T6_Q8", "text": "Jika ya, siapa yang melakukannya? (Pelecehan Media/Pesan)", "code": "5M"},
        {"id": "T6_Q9", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami perhatian atau perilaku bernuansa seksual yang tidak Anda inginkan di tempat kerja?", "code": "4"},
        {"id": "T6_Q10", "text": "Jika ya, siapa yang melakukannya? (Perilaku Seksual)", "code": "5M"},
        {"id": "T6_Q11", "text": "Dalam 12 bulan terakhir, apakah Anda menerima ancaman kekerasan di tempat kerja?", "code": "4"},
        {"id": "T6_Q12", "text": "Jika ya, siapa yang melakukannya? (Ancaman Kekerasan)", "code": "5M"},
        {"id": "T6_Q13", "text": "Dalam 12 bulan terakhir, apakah Anda mengalami kekerasan fisik di tempat kerja?", "code": "4"},
        {"id": "T6_Q14", "text": "Jika ya, siapa yang melakukannya? (Kekerasan Fisik)", "code": "5M"},
        {"id": "T6_Q15", "text": "Perundungan adalah perlakuan tidak menyenangkan atau merendahkan yang terjadi berulang kali dan membuat seseorang sulit membela diri. Dalam 12 bulan terakhir, apakah Anda mengalami perundungan di tempat kerja?", "code": "4"},
        {"id": "T6_Q16", "text": "Jika ya, siapa yang melakukannya? (Perundungan)", "code": "5M"},
        {"id": "T6_Q17", "text": "Seberapa sering Anda merasa dikritik secara tidak adil, diintimidasi, atau dipermalukan di depan orang lain oleh rekan kerja atau atasan?", "code": "1"}, 
    ],
    "HEALTH AND WELL-BEING": [
        {"id": "T7_Q1", "text": "Secara umum, bagaimana Anda menilai kondisi kesehatan Anda saat ini?", "code": "7"},
        {"id": "T7_Q2", "text": "Jika kondisi kesehatan terbaik yang dapat Anda bayangkan diberi nilai 10 dan kondisi terburuk diberi nilai 0, berapa nilai yang Anda berikan untuk kondisi kesehatan Anda saat ini?", "code": "8"},
        {"id": "T7_Q3", "text": "Seberapa sering tidur Anda terasa tidak nyenyak atau gelisah?", "code": "9"},
        {"id": "T7_Q4", "text": "Seberapa sering Anda mengalami kesulitan untuk mulai tidur?", "code": "9"},
        {"id": "T7_Q5", "text": "Seberapa sering Anda terbangun terlalu pagi dan tidak bisa tidur kembali?", "code": "9"},
        {"id": "T7_Q6", "text": "Seberapa sering Anda terbangun beberapa kali pada malam hari dan sulit tidur kembali?", "code": "9"},
        {"id": "T7_Q7", "text": "Seberapa sering Anda merasa sangat terkuras atau kehabisan tenaga?", "code": "9"},
        {"id": "T7_Q8", "text": "Seberapa sering Anda merasa kelelahan secara fisik?", "code": "9"},
        {"id": "T7_Q9", "text": "Seberapa sering Anda merasa kelelahan secara emosional?", "code": "9"},
        {"id": "T7_Q10", "text": "Seberapa sering Anda merasa lelah?", "code": "9"},
        {"id": "T7_Q11", "text": "Seberapa sering Anda merasa sulit untuk bersantai?", "code": "9"},
        {"id": "T7_Q12", "text": "Seberapa sering Anda merasa mudah tersinggung?", "code": "9"},
        {"id": "T7_Q13", "text": "Seberapa sering Anda merasa tegang?", "code": "9"},
        {"id": "T7_Q14", "text": "Seberapa sering Anda mengalami sakit perut?", "code": "9"},
        {"id": "T7_Q15", "text": "Seberapa sering Anda mengalami sakit kepala?", "code": "9"},
        {"id": "T7_Q16", "text": "Seberapa sering jantung Anda terasa berdebar-debar?", "code": "9"},
        {"id": "T7_Q17", "text": "Seberapa sering Anda merasakan ketegangan pada otot-otot tubuh?", "code": "9"},
        {"id": "T7_Q18", "text": "Seberapa sering Anda mengalami kesulitan berkonsentrasi?", "code": "9"},
        {"id": "T7_Q19", "text": "Seberapa sering Anda merasa sulit berpikir dengan jernih?", "code": "9"},
        {"id": "T7_Q20", "text": "Seberapa sering Anda mengalami kesulitan saat mengambil keputusan?", "code": "9"},
        {"id": "T7_Q21", "text": "Seberapa sering Anda mengalami kesulitan mengingat sesuatu?", "code": "9"},
        {"id": "T7_Q22", "text": "Seberapa sering Anda merasa sedih?", "code": "9"},
        {"id": "T7_Q23", "text": "Seberapa sering Anda merasa kurang percaya diri?", "code": "9"},
        {"id": "T7_Q24", "text": "Seberapa sering Anda merasa bersalah?", "code": "9"},
        {"id": "T7_Q25", "text": "Seberapa sering Anda kehilangan minat terhadap kegiatan sehari-hari?", "code": "9"},
    ],
    "PERSONALITY/KEPRIBADIAN": [
        {"id": "T8_Q1", "text": "Saya biasanya dapat menyelesaikan masalah sulit jika saya berusaha dengan sungguh-sungguh.", "code": "10"},
        {"id": "T8_Q2", "text": "Jika orang lain menghambat saya, saya akan mencari cara untuk mencapai tujuan saya.", "code": "10"},
        {"id": "T8_Q3", "text": "Saya mudah mengikuti rencana yang telah dibuat dan mencapai tujuan saya.", "code": "10"},
        {"id": "T8_Q4", "text": "Saya yakin dapat menghadapi kejadian yang tidak terduga.", "code": "10"},
        {"id": "T8_Q5", "text": "Saat menghadapi masalah, saya biasanya dapat menemukan beberapa cara untuk menyelesaikannya.", "code": "10"},
        {"id": "T8_Q6", "text": "Apa pun yang terjadi, saya biasanya mampu mengatasinya.", "code": "10"},
    ]
}

CATEGORY_METADATA = {
    "TUNTUTAN PEKERJAAN": {
        "label": "Tuntutan Pekerjaan",
        "short": "Tuntutan Kerja",
        "icon": "⏳",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan tuntutan yang Anda hadapi dalam pekerjaan, seperti beban kerja, kecepatan kerja, tuntutan kognitif, dan tuntutan emosional. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "PENGORGANISASIAN KERJA DAN ISI PEKERJAAN": {
        "label": "Pengorganisasian & Isi Kerja",
        "short": "Organisasi Kerja",
        "icon": "📋",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan pengaturan kerja dan karakteristik pekerjaan Anda, seperti kejelasan tugas, kesempatan mengembangkan keterampilan, serta pengaruh dan keleluasaan dalam pekerjaan. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "HUBUNGAN ANTARPRIBADI DAN KEPEMIMPINAN": {
        "label": "Hubungan Antarpribadi & Kepemimpinan",
        "short": "Hubungan & Pemimpin",
        "icon": "🤝",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan hubungan Anda dengan rekan kerja dan atasan serta kepemimpinan di lingkungan kerja. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "ANTARMUKA KERJA INDIVIDU": {
        "label": "Antarmuka Kerja Individu",
        "short": "Antarmuka Kerja",
        "icon": "💼",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan hubungan antara pekerjaan dan kehidupan pribadi Anda, termasuk bagaimana pekerjaan memengaruhi kehidupan di luar pekerjaan dan sebaliknya. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "MODAL SOSIAL": {
        "label": "Modal Sosial",
        "short": "Modal Sosial",
        "icon": "🏛️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan kepercayaan, kerja sama, dan hubungan sosial di lingkungan kerja, termasuk bagaimana pegawai saling mendukung dalam mencapai tujuan bersama. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda dalam pekerjaan selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "KONFLIK DAN PERILAKU OFENSIF": {
        "label": "Konflik & Perilaku Ofensif",
        "short": "Konflik & Ofensif",
        "icon": "⚠️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan konflik dan perilaku tidak menyenangkan yang mungkin Anda alami atau temui di lingkungan kerja, seperti perlakuan yang tidak pantas, pelecehan, atau tindakan lain yang membuat Anda merasa tidak nyaman. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada pengalaman Anda di lingkungan kerja selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
    },
    "HEALTH AND WELL-BEING": {
        "label": "Kesehatan & Kesejahteraan (Health & Well-Being)",
        "short": "Kesehatan & Well-being",
        "icon": "❤️",
        "desc": "Berikut ini terdapat sejumlah pernyataan yang berkaitan dengan kondisi kesehatan dan kesejahteraan Anda, termasuk kondisi fisik, psikologis, dan perasaan yang berkaitan dengan pekerjaan. Bacalah setiap pernyataan dengan saksama. Dalam memberikan jawaban, harap merujuk pada kondisi dan pengalaman Anda selama 3 bulan terakhir. Ketentuan keterangan jawaban yaitu sebagai berikut:"
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
    "ANTARMUKA KERJA INDIVIDU": "Skor_Antarmuka_Kerja",
    "MODAL SOSIAL": "Skor_Modal_Sosial",
    "KONFLIK DAN PERILAKU OFENSIF": "Skor_Konflik_Ofensif",
    "HEALTH AND WELL-BEING": "Skor_Kesehatan_Wellbeing",
    "PERSONALITY/KEPRIBADIAN": "Skor_Kepribadian_Efikasi"
}

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
