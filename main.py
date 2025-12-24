import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

app = FastAPI()

# CORS Ayarları
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
    return {"status": "online", "message": "BriefingTube AI Aktif"}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Geçersiz URL")

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # 1. Adım: Altyazı var mı bak
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['tr', 'en'])
            text = " ".join([t['text'] for t in transcript.fetch()])
            prompt = f"Aşağıdaki altyazılara sahip videoyu Türkçe özetle:\n\n{text}"
        except:
            # 2. Adım: Altyazı yoksa Gemini'a videoyu "yorumlat"
            prompt = f"Bu YouTube videosunda ({url}) altyazı yok. Sadece linke ve video başlığına bakarak bu videonun ne hakkında olduğunu (oyun, müzik, eğitim vb.) Türkçe tahmin et ve açıkla."

        response = model.generate_content(prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": str(e)}
