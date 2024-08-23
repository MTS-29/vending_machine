from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from utils import read_data, write_data
from models import Product, User, Deposit, Purchase, SwitchUser

app = FastAPI()

# Get the current working user
def get_current_user(username: str, password: str) -> User:
    data = read_data()
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return User(**user)
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Create a new user
@app.post("/users", response_model=User)
def create_user(user: User):
    data = read_data()
    if any(u["username"] == user.username for u in data["users"]):
        raise HTTPException(status_code=400, detail="User already exists")
    data["users"].append(user.dict())
    write_data(data)
    return user

# Get all products
@app.get("/products", response_model=List[Product])
def get_products():
    data = read_data()
    return [Product(**p) for p in data["products"]]

# Create new product
@app.post("/products", response_model=Product)
def create_product(product: Product, current_user: User = Depends(get_current_user)):
    if current_user.role != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can add products")
    if any(p["productId"] == product.productId for p in read_data()["products"]):
        raise HTTPException(status_code=400, detail="Product already exists")
    data = read_data()
    data["products"].append(product.dict())
    write_data(data)
    return product

# Update existing product - Seller only
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: Product, current_user: User = Depends(get_current_user)):
    if current_user.role != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can update products")
    data = read_data()
    products = [p for p in data["products"] if p["productId"] != product_id]
    if len(products) == len(data["products"]):
        raise HTTPException(status_code=404, detail="Product not found")
    products.append(product.dict())
    data["products"] = products
    write_data(data)
    return product

# Delete an existing product - Seller only
@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can delete products")
    data = read_data()
    products = [p for p in data["products"] if p["productId"] != product_id]
    if len(products) == len(data["products"]):
        raise HTTPException(status_code=404, detail="Product not found")
    write_data({"products": products, "users": data["users"]})
    return {"productId": product_id, "status": "deleted"}

# Deposit money - Buyer only
@app.post("/deposit")
def deposit_money(deposit: Deposit, current_user: User = Depends(get_current_user)):
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can deposit money")
    if deposit.amount not in [5, 10, 20, 50, 100]:
        raise HTTPException(status_code=400, detail="Invalid coin value")
    data = read_data()
    for user in data["users"]:
        if user["username"] == current_user.username:
            user["deposit"] += deposit.amount
            break
    write_data(data)
    return {"deposit": deposit.amount, "total": user["deposit"]}

# Buy existing product - Buyer only
@app.post("/buy")
def buy_product(purchase: Purchase, current_user: User = Depends(get_current_user)):
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can buy products")
    data = read_data()
    product = next((p for p in data["products"] if p["productId"] == purchase.productId), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["amountAvailable"] < purchase.amount:
        raise HTTPException(status_code=400, detail="Not enough product available")
    if product["cost"] * purchase.amount > current_user.deposit:
        raise HTTPException(status_code=400, detail="Not enough deposit")
    product["amountAvailable"] -= purchase.amount
    current_user.deposit -= product["cost"] * purchase.amount
    write_data(data)
    change = current_user.deposit
    change_coins = {5: 0, 10: 0, 20: 0, 50: 0, 100: 0}
    for coin in sorted(change_coins.keys(), reverse=True):
        while change >= coin:
            change_coins[coin] += 1
            change -= coin
    return {"total_spent": product["cost"] * purchase.amount, "products_purchased": purchase.amount, "change": change_coins}

# Reset any buyer's money to default value
@app.post("/reset")
def reset_deposit(current_user: User = Depends(get_current_user)):
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can reset deposit")
    data = read_data()
    for user in data["users"]:
        if user["username"] == current_user.username:
            user["deposit"] = 0
            break
    write_data(data)
    return {"message": "Deposit reset successful"}

# Switch user from buyer to seller or vice versa
@app.post("/switch_user")
def switch_user(switch: SwitchUser):
    data = read_data()
    for user in data["users"]:
        if user["username"] == switch.username and user["password"] == switch.password:
            return {"message": f"Switched to user {switch.username}"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
