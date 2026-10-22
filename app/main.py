from fastapi import FastAPI, Depends , HTTPException
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models import OrderModel



app = FastAPI(title="Restaurant API")


class Order(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    food_name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

    @field_validator("customer_name", "food_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty or contain only spaces")

        return value

class OrderResponse(Order):
    id: int
    model_config = ConfigDict(from_attributes=True)



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
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException (
            status_code = 500,
            detail = "Database error while creating order"
        )

    return {
        "message": "Order created successfully",
        "order": db_order
    }

@app.get("/orders", response_model=list[OrderResponse] )
def get_orders(db:Session = Depends(get_db)):
    try:
        orders = db.query(OrderModel).all()
        return orders

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving orders"
        )




@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order:Order ,
    db: Session = Depends(get_db)
    ):
    try:
        db_order = db.query(OrderModel).filter(
            OrderModel.id == order_id).first()

        if db_order is None:
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
    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code = 500,
                            detail = "Database error while updating order")





@app.delete("/orders/{order_id}")
def delete_order(order_id: int,
                  db: Session = Depends(get_db)
                  ):
    try:
        db_order = db.query(OrderModel).filter(
            OrderModel.id == order_id
         ).first()

        if db_order is  None:
            raise HTTPException(status_code = 404 , detail = "order not found")


        db.delete(db_order)
        db.commit()
        return {"message": "Order deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code = 500,
            detail = "Database error while deleting order"
        )
