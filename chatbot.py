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
        return None

def chatbot_response(user_input, chat_history=[]):
    global language_status

    if language_status is None:
        detected_lang = detect_language(user_input)
        language_status = detected_lang if detected_lang else "id"

    # Tambahkan input user ke chat_history sebagai dictionary
    chat_history.append({"role": "user", "content": user_input})

    # Buat konteks prompt
    context = ""
    for turn in chat_history[-5:]:  # Hanya ambil 5 pesan terakhir
        if turn["role"] == "user":
            context += f"Kamu: {turn['content']}\n" if language_status == "id" else f"You: {turn['content']}\n"
        else:
            context += f"{chatbot_name}: {turn['content']}\n"

    # Tentukan prompt dan stop sequence berdasarkan bahasa
    if language_status == "id":
        prompt = (
            f"Kamu adalah chatbot bernama {chatbot_name}, hanya berbicara dalam bahasa Indonesia.\n"
            f"Berikut percakapan sejauh ini:\n{context}{chatbot_name}:"
        )
        stop_seq = ["Kamu:", f"{chatbot_name}:"]
    else:
        prompt = (
            f"You are a chatbot named {chatbot_name}, speaking in English only.\n"
            f"Here is the conversation so far:\n{context}{chatbot_name}:"
        )
        stop_seq = ["You:", f"{chatbot_name}:"]

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 200,
            "stop": stop_seq
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        try:
            result = response.json()[0]['generated_text']

            # Hapus bagian prompt awal
            if result.startswith(prompt):
                result = result[len(prompt):].strip()

            # Potong jika ada stop token muncul di respons
            for stop_token in stop_seq:
                if stop_token in result:
                    result = result.split(stop_token)[0].strip()

            # Filter respons aneh
            if not result or any(char in result for char in ["\ud83d", "왜", "卒딜", "1."]):
                return "Maaf, aku belum paham pertanyaannya. Bisa diulang?" if language_status == "id" else "Sorry, I didn't get that. Can you repeat?"

            chat_history.append({"role": "bot", "content": result})
            return result
        except Exception:
            return "Oops! Ada yang salah nih, coba lagi ya!" if language_status == "id" else "Oops! Something went wrong!"
    else:
        return f"Error {response.status_code}: {response.text}"

