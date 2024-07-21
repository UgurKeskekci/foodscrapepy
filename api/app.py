from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv('MONGO_URI'))
db = client['food_database']
collection = db['foods']

@app.route('/foods', methods=['GET'])
def get_foods():
    foods = list(collection.find())
    for food in foods:
        food['_id'] = str(food['_id'])
    return jsonify(foods)

@app.route('/food/<id>', methods=['GET'])
def get_food(id):
    food = collection.find_one({"_id": ObjectId(id)})
    if food:
        food['_id'] = str(food['_id'])
        return jsonify(food)
    else:
        return jsonify({"error": "Food not found"}), 404

@app.route('/food', methods=['POST'])
def add_food():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@app.route('/food/<id>', methods=['PUT'])
def update_food(id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Food updated"}), 200
    else:
        return jsonify({"error": "Food not found"}), 404

@app.route('/food/<id>', methods=['DELETE'])
def delete_food(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Food deleted"}), 200
    else:
        return jsonify({"error": "Food not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
