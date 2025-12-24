import os
from fastapi import FastAPI, Query
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Firefox eklentisinin sunucuya bağlanabilmesi için gerekli izin (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel Settings -> Environment Variables kısmına ekleyeceğin anahtarı okur
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@app.get("/ozetle")
def ozet_yap(url: str = Query(..., description="YouTube video URL'si")):
    try:
        # 1. URL'den Video ID'sini ayıkla
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "be/" in url:
            video_id = url.split("be/")[1].split("?")[0]
        else:
            return {"error": "Geçersiz YouTube URL'si."}

        # 2. Altyazıları çek (Önce Türkçe, yoksa İngilizce dene)
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
            text = " ".join([t['text'] for t in transcript_list])
        except Exception:
            return {"error": "Bu videonun altyazılarına ulaşılamadı."}

        # 3. Gemini ile özetle
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Aşağıdaki video metnini anlamlı ve akıcı bir şekilde, tek bir paragraf olarak özetle:\n\n{text}"
        response = model.generate_content(prompt)
        
        return {"ozet": response.text}

    except Exception as e:
        return {"error": f"Sunucu hatası: {str(e)}"}