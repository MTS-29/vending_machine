import json

def read_data():
    with open('data.json', 'r') as file:
        return json.load(file)

def write_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)
