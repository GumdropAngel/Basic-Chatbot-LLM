Chatbot LLM : Seorang villager di minecraft

Tema dan konsep dari chat bot ini adalah karakter fiksi / roleplay Villager dari game Minecraft.
Dibangun menggunakan Gemini API (model `gemini-3.6-flash`) dan UI Streamlit.
LLM di-setting menggunakan system prompt untuk melakukan peran yang memiliki kepribadian datar, netral, sering mengatakan "hmm", dan
terkadang terdengar bosan agar interaksi dengan pengguna seperti aslinya

Chatbot ini mencakup beberapa fitur di antaranya :
- Parameter dinamis : Mengatur reson chatbot dari temperature dan maksimal panjang jawaban
- Manajemen state dan memori : Mempertahankan riwayat percakapan selama sesi berlangsung
- Penyimpanan lokal : Menyimpan percakapan secara lokal dalam bentuk file JSON yang dapat di-load kedepannya
- Statistik percakapan : Menghitung hal-hal seperti berapa total percakapan, berapa pesan pengguna, dan apa topik utama
- Error handling : Menjaga input / chatbot stabil walaupun jika terdapat error yang menghambat

Cara menjalankan program :
1. Memastikan python sudah terinstall
2. Membuka terminal dan mengarahkannya ke folder
3. Menginstall dependensi yang dibutuhkan dengan menjalankan perintah 'pip install streamlit google-genai'

Contoh screenshot :

Penjelasan kode :
1. Inisialisasi client dan state. Mendefinisikan API Key dan memasukkannya ke dalam genai.Client(). Objek client, riwayat chat, dan sesi API (chat_session) disimpan ke dalam session_state agar koneksi tidak putus dan percakapan tidak hilang saat streamlit di-refresh
2. UI sidebar dan parameter. st.sidebar digunakan untuk menampung slider konfigurasi LLM (temperature dan maksimal panjang jawaban). Nilai dari slider ini dimasukkan secara dinamis ke dalam argumen types.GenerateContentConfig saat pesan dikirim
3. Fitur file I/O. Saat pengguna mendownload file JSON, program memetakan ulang teks tersebut menjadi format types.Content agar API gemini mengetahui riwayat chat tersebut. Saat mengetik perintah khusus /save, program mengambil isi session_state.messages
4. Dashboard statistik. Menggunakan collections.Counter untuk mengurai seluruh teks input dari pengguna, menyaring kata-kata penting, dan menampilkannya di dalam st.expander beserta total percakapan
5. Routing chat dan error handling. Input dari pengguna akan ditangkap oleh st.chat_input. Program mengecek apakah input tersebut adalah perintah sistem (seperti /clear, /save, atau /exit) atau percakapan biasa. Jika percakapan biasa, input akan dikirim ke API gemini menggunakan fungsi send_message_stream() yang dibungkus dalam blok try except