from fastapi import FastAPI, Depends , HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
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


@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order:Order ,
    db: Session = Depends(get_db)
    ):
    db_order = db.query(OrderModel).filter(
        OrderModel.id == order_id).first()

    if db_order == None:
        raise HTTPException(status_code = 404 ,
                             detail = "Order not found"
                             )
    
    db_order.customer_name = order.customer_name
    db_order.food_name = order.food_name
    db_order.quantity = order.quantity
    db_order.price = order.price

    db.commit()
    db.refresh(db_order)

    return db_order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, 
                  db: Session = Depends(get_db)
                  ):
    db_order = db.query(OrderModel).filter(
        OrderModel.id == order_id
    ).first()

    if db_order == None:
        raise HTTPException(status_code = 404 , detail = "order not found")    

    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}

    