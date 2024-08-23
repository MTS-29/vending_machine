import json
from models import User, Product

users = []
products = []

# Load data from JSON files
def load_data_from_file():
    global users, products
    try:
        with open('data/users.json', 'r') as f:
            users = [User(**data) for data in json.load(f)]
    except FileNotFoundError:
        users = []

    try:
        with open('data/products.json', 'r') as f:
            products = [Product(**data) for data in json.load(f)]
    except FileNotFoundError:
        products = []

# Save data to JSON files
def save_data_to_file():
    with open('data/users.json', 'w') as f:
        json.dump([user.dict() for user in users], f, indent=4)

    with open('data/products.json', 'w') as f:
        json.dump([product.dict() for product in products], f, indent=4)

# Initial load of data
load_data_from_file()
