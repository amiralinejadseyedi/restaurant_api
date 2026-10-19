from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import OrderModel



app = FastAPI(title="Restaurant API")


class Order(BaseModel):
    customer_name: str
    food_name: str
    quantity: int
    price: float


@app.get("/")
def home():
    return {"message": "restaurant api is running"}


orders = []

@app.post("/orders")
def create_order(order: Order):
    orders.append(order)

    return{
        "message":"Order created succesfully",
        "order": order
    }




@app.get("/orders")
def get_orders():
    return orders

                  