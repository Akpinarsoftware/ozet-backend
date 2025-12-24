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
    return {"message": "BriefingTube Backend Aktif"}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    video_id = get_video_id(url)
    if not video_id:
        return {"error": "Geçersiz URL"}

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # Önce altyazı ara
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['tr', 'en'])
            text = " ".join([t['text'] for t in transcript.fetch()])
            prompt = f"Bu altyazıları özetle: {text}"
        except:
            # Altyazı yoksa tahmin moduna geç
            prompt = f"Bu YouTube videosunda ({url}) altyazı yok. Başlığa bakarak videonun içeriğini tahmin et ve Türkçe açıkla."

        response = model.generate_content(prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": str(e)}
