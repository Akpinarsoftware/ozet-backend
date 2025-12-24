import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "BriefingTube v3.6"}

@app.get("/ozetle")
async def summarize(url: str = Query(...)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API anahtari sunucuda tanimli degil."}

    try:
        # Video ID ayikla
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        text = ""
        try:
            # Altyazilari dene
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
            text = " ".join([t['text'] for t in transcript])
            final_prompt = f"Asagidaki metni Turkce ozetle:\n\n{text}"
        except:
            # Altyazi yoksa link uzerinden tahmin et
            final_prompt = f"Bu YouTube videosu ({url}) hakkinda sadece basliga bakarak Turkce bir yorum yap."

        response = model.generate_content(final_prompt)
        return {"ozet": response.text}

    except Exception as e:
        return {"error": f"Islem hatasi: {str(e)}"}
