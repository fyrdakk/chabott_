import requests
import os
from dotenv import load_dotenv
from langdetect import detect

# Load API Key dari file .env
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# API Model
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Nama chatbot dan status bahasa
chatbot_name = "JayHyung, dibuat oleh Firda"
language_status = None  # Menyimpan bahasa yang digunakan

def detect_language(user_input):
    try:
        detected_lang = detect(user_input)
        return detected_lang if detected_lang in ["id", "en"] else None
    except Exception:
        return None  # Jika gagal deteksi, default ke bahasa pertama yang dipilih

def chatbot_response(user_input, chat_history=[]):
    global language_status
    
    # Tentukan bahasa berdasarkan input pertama
    if language_status is None:
        detected_lang = detect_language(user_input)
        language_status = detected_lang if detected_lang else "id"  # Default ke bahasa Indonesia
    
    # Gabungkan chat history untuk konteks lebih nyambung
    chat_history.append(f"Kamu: {user_input}")
    chat_context = "\n".join(chat_history[-5:])  # Ambil 5 percakapan terakhir biar ga kepanjangan

    # Prompt dengan gaya santai
    if language_status == "id":
        prompt = f"Kamu adalah chatbot bernama {chatbot_name}, berbicara dalam bahasa Indonesia. Jangan gunakan bahasa lain.\nKamu: {chat_context}\n{chatbot_name}:"
    else:
        prompt = f"You are a chatbot named {chatbot_name}, speaking in English only. Do not use other languages.\nYou: {chat_context}\n{chatbot_name}:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 200,
            "stop": ["\n"]
        }
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        try:
            result = response.json()[0]['generated_text']
            
            # **Perbaikan**: Menghapus bagian prompt dari hasil chatbot
            if result.startswith(prompt):
                result = result[len(prompt):].strip()

            # Filter respons aneh
            if not result or any(char in result for char in ["\ud83d", "1.", "100%", "왜", "卒딜"]):
                return "Maaf, aku belum paham pertanyaannya. Bisa diulang?" if language_status == "id" else "Sorry, I didn't get that. Can you repeat?"

            return result
        except Exception:
            return "Oops! Ada yang salah nih, coba lagi ya! 😅" if language_status == "id" else "Oops! Something went wrong, try again! 😅"
    else:
        return f"Error {response.status_code}: {response.text}"
