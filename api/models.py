from django.db import models
from db_connect import db

users_collection = db['users']
admin_collection = db['admin']
product_collection = db['product']
orders_collection = db['orders']
cart_collection = db['cart']

