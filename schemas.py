from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class ProductCreate(BaseModel):
    productName: str
    amountAvailable: int
    cost: int

class Deposit(BaseModel):
    amount: int

class BuyRequest(BaseModel):
    productId: str
    amount: int
