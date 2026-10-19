from sqlalchemy import String, Integer, Float  
from sqlalchemy.orm import Mapped, mapped_column 
from app.database import Base 


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    food_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)
    price : Mapped[float] = mapped_column(Float)

    

