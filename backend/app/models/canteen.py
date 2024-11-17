from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, DECIMAL
from .database import Base
import datetime

class DiningRecord(Base):
    """就餐记录模型"""
    __tablename__ = "dining_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50))
    employee_name = Column(String(50))
    avatar_url = Column(String(200))
    payment_time = Column(DateTime, default=datetime.datetime.utcnow)
    payment_amount = Column(DECIMAL(10, 2))
    dishes = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    class Config:
        orm_mode = True

class Satisfaction(Base):
    """满意度评价模型"""
    __tablename__ = "satisfaction"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)          # 评分（1-5）
    comment = Column(String(500))     # 评价内容
    created_at = Column(DateTime, default=datetime.datetime.now)

class DishSales(Base):
    """菜品销售记录模型"""
    __tablename__ = "dish_sales"

    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    sales_count = Column(Integer, nullable=False)
    sales_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)