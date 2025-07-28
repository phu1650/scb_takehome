from fastapi import FastAPI, Depends, HTTPException
from models import Base, Transaction
from schemas import TransactionScheman
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import pandas as pd
import joblib

Base.metadata.create_all(bind=engine)


model = {}
OPTIMAL_THRESH = 0.4004254

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    model["fraud"] = joblib.load("model/xgb_pipeline.pkl")
    yield
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
def predict(request:TransactionScheman, db: Session = Depends(get_db)):
    input_df = pd.DataFrame({"amount": [request.amount], 
                             "src_bal": [request.src_bal], 
                             "dst_bal": [request.dst_bal], 
                             "transac_type": [request.transac_type]})
    probability = model["fraud"].predict_proba(input_df)[:, 1]
    prediction = (probability >= OPTIMAL_THRESH)[0]
    transaction = Transaction(amount=request.amount, 
                              src_bal=request.src_bal, 
                              dst_bal=request.dst_bal, 
                              transac_type=request.transac_type,
                              is_fraud=int(prediction))
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/frauds")
def get_fraud_transaction(db: Session = Depends(get_db)):
    fruad_transactions = db.query(Transaction).filter(Transaction.is_fraud == 1).all()
    return fruad_transactions