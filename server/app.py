#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict_basic() for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict()), 200
    return jsonify({"error": "Restaurant not found"}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=["POST"])
def add_restaurant_pizzas():
    data = request.get_json()
    try:
        price = int(data.get("price"))
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        
        restaurant = Restaurant.query.get(data.get("restaurant_id"))
        pizza = Pizza.query.get(data.get("pizza_id"))
        if not restaurant or not pizza:
            return jsonify({"error": "Invalid restaurant or pizza ID"}), 400

        rp = RestaurantPizza(price=price, restaurant_id=restaurant.id, pizza_id=pizza.id)
        db.session.add(rp)
        db.session.commit()

        return jsonify({
            "id": rp.id,
            "price": rp.price,
            "pizza_id": rp.pizza_id,
            "restaurant_id": rp.restaurant_id,
            "pizza": rp.pizza.to_dict(),
            "restaurant": rp.restaurant.to_dict_basic()
        }), 201


    except (KeyError, ValueError):
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == "__main__":
    app.run(port=5551, debug=True)
