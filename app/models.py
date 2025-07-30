from sqlalchemy import Column, Integer, String, Float
from database import Base
import uuid

class Transaction(Base):
    __tablename__ = "transaction"
    uuid = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float)
    src_bal = Column(Float)
    dst_bal = Column(Float)
    transac_type = Column(String)
    is_fraud = Column(Integer)