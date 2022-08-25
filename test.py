
from pymongo import MongoClient

client = MongoClient()

db = client.sreality

houses = db.houses

for house in houses.find():
    print(house)