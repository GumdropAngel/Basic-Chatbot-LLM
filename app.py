import streamlit as st
from google import genai
from google.genai import types
import time
import json
import os
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

#memuat environment variables dari file .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

#jika file .env lupa dibuat atau API Key kosong
if not api_key:
    st.error("Hmm... API Key tidak ditemukan. Pastikan sudah diset di file .env!")
    st.stop()

#inisialisasi client google gen AI versi terbaru. 
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Kamu adalah seorang villager dari Minecraft.
Kamu apa adanya, ekspresi datar, dan sering mengatakan 'hmm'.
Tugas kamu adalah memberi pengguna opsi-opsi apa saja yang tersedia untuk melakukan trading dengan pengguna dan mau menerima negosiasi.
Gunakan bahasa indonesia yang santai, netral, dan terkadang terdengar bosan kecuali saat pengguna sudah melakukan trade.
Jangan pernah keluar dari karaktermu."""

st.set_page_config(page_title="Chat dengan seorang villager!", page_icon="🥸", layout="wide")
st.title("🤔 Chatbot karakter fiksi/roleplay")
st.caption("Ketik **/save** untuk menyimpan, **/clear** untuk reset, atau **/exit** untuk keluar.")

# ==========================================
# FITUR 3: KONTROL PARAMETER (Sidebar)
# ==========================================
with st.sidebar:
    st.header("Pengaturan")
    st.write("Atur pola pikir Villager ini:")
    
    # Slider untuk temperature dan batas output
    temp_setting = st.slider("Tingkat Kreativitas (Temperature)", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    max_tokens_setting = st.slider("Maksimal Panjang Jawaban", min_value=100, max_value=1000, value=500, step=50)
    
    st.divider()
    
    # ==========================================
    # FITUR 1: MEMUAT RIWAYAT PERCAKAPAN (JSON)
    # ==========================================
    st.header("📂 Muat Riwayat Trade")
    uploaded_file = st.file_uploader("Upload file .json yang pernah di-save", type=["json"])
    
    if uploaded_file is not None:
        if st.button("Muat Percakapan Ini"):
            try:
                loaded_data = json.load(uploaded_file)
                st.session_state.messages = loaded_data
                
                # Membangun ulang riwayat agar sesuai dengan format yang dibaca oleh google-genai
                history_content = []
                for msg in loaded_data:
                    role = "user" if msg["role"] == "user" else "model"
                    history_content.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
                
                st.session_state.chat_session = st.session_state.client.chats.create(
                    model="gemini-3.6-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=temp_setting,
                        max_output_tokens=max_tokens_setting
                    ),
                    history=history_content
                )
                st.success("Hmm... Ingatanku sudah kembali.")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memuat file: {e}")

# Inisialisasi Awal
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=temp_setting,
            max_output_tokens=max_tokens_setting
        )
    )

if "is_exited" not in st.session_state:
    st.session_state.is_exited = False

def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=temp_setting,
            max_output_tokens=max_tokens_setting
        )
    )
    st.session_state.is_exited = False

#statistik percakapan
if len(st.session_state.messages) > 0:
    with st.expander("📊 Statistik Trade (Buka untuk melihat detail)"):
        total_msg = len(st.session_state.messages)
        user_msg = sum(1 for m in st.session_state.messages if m["role"] == "user")
        
        #logika sederhana mencari topik berdasarkan kata yang sering diketik user
        user_text = " ".join([m["content"].lower() for m in st.session_state.messages if m["role"] == "user"])
        #Mengabaikan perintah bergaris miring (/) dan kata pendek di bawah 5 huruf
        words = [w for w in user_text.split() if len(w) > 4 and not w.startswith('/')] 
        common_words = [word for word, count in Counter(words).most_common(3)]
        topik_str = ", ".join(common_words) if common_words else "Belum ada"

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Percakapan", total_msg)
        col2.metric("Pesan Pengguna", user_msg)
        col3.metric("Topik Utama", topik_str.title())

#render history pesan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#alur Chatbot
if st.session_state.is_exited:
    st.info("Sesi telah diakhiri. Refresh halaman atau tekan tombol di bawah untuk memulai ulang.")
    if st.button("Mulai Ulang Percakapan"):
        reset_chat()
        st.rerun()
else:
    if prompt := st.chat_input("Tanya sesuatu ke villager random ini"):
        
        if prompt.strip().lower() == "/clear":
            reset_chat()
            st.rerun()
            
        elif prompt.strip().lower() == "/save":
            if len(st.session_state.messages) == 0:
                st.toast("Hmm. Belum ada obrolan untuk disimpan.", icon="⚠️")
            else:
                filename = f"riwayat_trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                save_msg = f"Hmm... Riwayat obrolan sudah disimpan di file `{filename}`. Sekarang, mau trade atau tidak?"
                st.session_state.messages.append({"role": "model", "content": save_msg})
                with st.chat_message("model"):
                    st.markdown(save_msg)
                
                st.toast(f"Tersimpan sebagai {filename}", icon="💾")
            
        elif prompt.strip().lower() == "/exit":
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            goodbye_msg = "Sampai jumpa, hmm. Aku tidak akan merindukan mu."
            st.session_state.messages.append({"role": "model", "content": goodbye_msg})
            with st.chat_message("model"):
                st.markdown(goodbye_msg)
            
            st.session_state.is_exited = True
            st.rerun()

        else:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("model"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    #mengirimkan pesan dengan memberlakukan konfigurasi parameter terbaru dari slider
                    response = st.session_state.chat_session.send_message_stream(
                        prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=temp_setting,
                            max_output_tokens=max_tokens_setting
                        )
                    )
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            time.sleep(0.01) 
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"⚠️ Hmm... ada masalah dengan desa ini. Error: {str(e)}"
                    message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "model", "content": full_response})