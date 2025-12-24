import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API anahtarını kontrol et
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "be/" in url:
        return url.split("be/")[1].split("?")[0]
    return None

@app.get("/")
def home():
    return {"status": "online", "api_key_set": bool(api_key)}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    if not api_key:
        return {"error": "API Anahtarı Vercel üzerinde tanımlanmamış!"}

    video_id = get_video_id(url)
    if not video_id:
        return {"error": "Geçersiz YouTube URL'si"}

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # Altyazı çekmeyi dene
        text = ""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_transcript(['tr', 'en'])
            except:
                transcript = next(iter(transcript_list))
            
            lines = transcript.fetch()
            text = " ".join([t['text'] for t in lines])
            prompt = f"Aşağıdaki altyazıları Türkçe olarak özetle:\n\n{text}"
        except Exception as e:
            # Altyazı yoksa tahmin moduna geç
            prompt = f"Bu YouTube videosunda ({url}) altyazı yok. Sadece linke ve başlığa bakarak videonun ne hakkında olduğunu tahmin et ve Türkçe açıkla."

        response = model.generate_content(prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": f"AI Analiz sırasında hata oluştu: {str(e)}"}
