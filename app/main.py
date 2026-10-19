from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import OrderModel



app = FastAPI(title="Restaurant API")


class Order(BaseModel):
    customer_name: str
    food_name: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class OrderResponse(Order):
    id: int
    class Config:
        from_attributes = True



class OrderCreatedResponse(BaseModel):
    message: str
    order: OrderResponse



@app.get("/")
def home():
    return {"message": "restaurant api is running"}




@app.post("/orders", response_model=OrderCreatedResponse, status_code=201)
def create_order(order: Order, db: Session = Depends(get_db)):
    db_order = OrderModel(
        customer_name=order.customer_name,
        food_name=order.food_name,
        quantity=order.quantity,
        price=order.price
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return {
        "message": "Order created successfully",
        "order": db_order
    }

@app.get("/orders", response_model=list[OrderResponse] )
def get_orders(db:Session = Depends(get_db)):
    orders = db.query(OrderModel).all()
    return orders    

                  