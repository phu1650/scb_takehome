from pydantic import BaseModel

class TransactionScheman(BaseModel):
    amount: float
    src_bal: float
    dst_bal: float
    transac_type: str