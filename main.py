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

# API anahtarını yükle
api_key = os.getenv("GEMINI_API_KEY")

@app.get("/")
def home():
    return {"status": "online", "api_key_loaded": bool(api_key)}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    if not api_key:
        return {"error": "API anahtarı bulunamadı. Vercel redeploy edilmelidir."}

    genai.configure(api_key=api_key)
    
    try:
        # Video ID ayıklama
        video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        try:
            # Altyazıları çek
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
            text = " ".join([t['text'] for t in transcript])
            prompt = f"Aşağıdaki altyazıları Türkçe özetle:\n\n{text}"
        except:
            # Altyazı yoksa tahmin et
            prompt = f"Bu videoda ({url}) altyazı yok. Başlığa ve linke bakarak ne hakkında olduğunu Türkçe tahmin et."

        response = model.generate_content(prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": f"Sistem hatası: {str(e)}"}
