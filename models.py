from pydantic import BaseModel
from typing import Optional, List

class Product(BaseModel):
    productId: int
    productName: str
    amountAvailable: int
    cost: int
    sellerId: str

class User(BaseModel):
    username: str
    password: str
    deposit: int
    role: str

class Deposit(BaseModel):
    amount: int

class Purchase(BaseModel):
    productId: int
    amount: int

class SwitchUser(BaseModel):
    username: str
    password: str
