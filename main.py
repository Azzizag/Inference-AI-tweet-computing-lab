import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, constr
from transformers import pipeline
from sqlalchemy.orm import Session
from database import SessionLocal, TweetLog
from typing import List, Dict, Any
from sqlalchemy import func

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tweet Classification API",
    description="API untuk mengklasifikasikan topik dari dataset Twitter.",
    version="1.0.0"
)

# 1. Load Model Inference [cite: 1]
# Menggunakan model dari repo HuggingFace ML Engineer kalian
MODEL_NAME = "aderohmatmaulana98/tweet-classification"
logger.info(f"Loading model {MODEL_NAME}...")
try:
    classifier = pipeline("text-classification", model=MODEL_NAME, return_all_scores=True)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    classifier = None

# Dependency untuk Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Skema Request & Response (Validasi Pydantic)
class PredictRequest(BaseModel):
    # Validasi: Tidak boleh kosong, max 10.000 karakter, harus string
    tweet: str = Field(..., min_length=1, max_length=10000, description="Teks tweet murni")

class PredictResponse(BaseModel):
    label: str
    confidence: float
    probabilities: dict

class LogEntry(BaseModel):
    id: int
    tweet_text: str
    predicted_label: str
    confidence: float
    timestamp: str

class StatisticsResponse(BaseModel):
    total_tweets: int
    label_distribution: Dict[str, int]
    trend_data: Dict[str, int]
    recent_logs: List[LogEntry]

# 3. Endpoint POST /predict [cite: 1]
@app.post("/predict", response_model=PredictResponse)
async def predict_tweet(request: PredictRequest, db: Session = Depends(get_db)):
    if classifier is None:
        raise HTTPException(status_code=500, detail="Prediction failed: Model is not loaded.")
    
    try:
        # Melakukan prediksi
        predictions = classifier(request.tweet)[0] # Hasil list of dicts
        
        # Ekstrak probabilitas
        probabilities = {pred['label']: pred['score'] for pred in predictions}
        
        # Ambil label dengan probabilitas tertinggi
        best_prediction = max(predictions, key=lambda x: x['score'])
        top_label = best_prediction['label']
        top_confidence = best_prediction['score']

        # Simpan ke Database
        db_log = TweetLog(
            tweet_text=request.tweet,
            predicted_label=top_label,
            confidence=top_confidence
        )
        db.add(db_log)
        db.commit()

        logger.info(f"Successfully classified tweet as {top_label}")

        # Format Response sesuai API specs [cite: 1]
        return PredictResponse(
            label=top_label,
            confidence=top_confidence,
            probabilities=probabilities
        )

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        # Error handling gracefully
        raise HTTPException(status_code=500, detail={"error": "Prediction failed"})
    

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    try:
        # 1. Total Tweets
        total_tweets = db.query(TweetLog).count()

        # 2. Distribusi Label (Untuk Pie Chart)
        label_dist_query = db.query(
            TweetLog.predicted_label, 
            func.count(TweetLog.id)
        ).group_by(TweetLog.predicted_label).all()
        
        label_distribution = {label: count for label, count in label_dist_query}

        # 3. Tren Jumlah Tweet Harian (Untuk Grafik Tren)
        # Menggunakan func.date() yang didukung oleh SQLite untuk mengelompokkan berdasarkan hari
        trend_query = db.query(
            func.date(TweetLog.timestamp).label("date"), 
            func.count(TweetLog.id)
        ).group_by(func.date(TweetLog.timestamp)).all()
        
        trend_data = {str(date): count for date, count in trend_query}

        # 4. Tabel Log Tweet Terbaru (Limit 10 data terakhir)
        recent_logs_query = db.query(TweetLog).order_by(TweetLog.timestamp.desc()).limit(10).all()
        recent_logs = [
            LogEntry(
                id=log.id,
                tweet_text=log.tweet_text,
                predicted_label=log.predicted_label,
                confidence=log.confidence,
                # Konversi datetime ke string ISO format agar mudah di-parse Frontend
                timestamp=log.timestamp.isoformat() 
            ) for log in recent_logs_query
        ]

        return StatisticsResponse(
            total_tweets=total_tweets,
            label_distribution=label_distribution,
            trend_data=trend_data,
            recent_logs=recent_logs
        )

    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics data")