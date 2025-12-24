import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

app = FastAPI()

# Reklam engelleyicilerin engellememesi için CORS ayarlarını en geniş haline getirdik
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "BriefingTube Sunucusu Aktif"}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API anahtari eksik!"}
    
    genai.configure(api_key=api_key)
    # URL'den Video ID'yi güvenli bir şekilde ayıkla
    try:
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1].split("?")[0]
    except:
        return {"error": "Video ID ayiklanamadi."}

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        try:
            # Altyazı çekmeyi dene
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
            text = " ".join([t['text'] for t in transcript])
            prompt = f"Lütfen bu YouTube videosu metnini Türkçe özetle: {text}"
        except:
            # Altyazı yoksa Multimodal tahmin yap
            prompt = f"Bu YouTube videosu ({url}) altyazısızdır. Sadece başlığına ve linkine bakarak ne hakkında olduğunu Türkçe açıkla."

        response = model.generate_content(prompt)
        return {"ozet": response.text}
    except Exception as e:
        return {"error": f"Yapay zeka hatası: {str(e)}"}
