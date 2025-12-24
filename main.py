import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

app = FastAPI()

# --- CORS Ayarları ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API Yapılandırması
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "be/" in url:
        return url.split("be/")[1].split("?")[0]
    return None

@app.get("/")
def home():
    return {"status": "online", "message": "BriefingTube API Hazır"}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Geçersiz YouTube URL'si")

    try:
        # Altyazıları getir (Türkçe öncelikli, sonra İngilizce)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        text = " ".join([t['text'] for t in transcript])

        # Video çok kısaysa Gemini'ye özel talimat ver
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Aşağıdaki YouTube videosu metnini analiz et. Eğer video kısaysa ana fikri net yaz, uzunsa bölümlere ayırarak Türkçe özetle:\n\n{text}"
        
        response = model.generate_content(prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": f"Altyazı alınamadı veya video özetlenemedi: {str(e)}"}
