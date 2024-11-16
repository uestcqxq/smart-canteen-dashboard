from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, DECIMAL
from .database import Base
import datetime

class DiningRecord(Base):
    """就餐记录模型"""
    __tablename__ = "dining_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    customer_count = Column(Integer)  # 就餐人数
    total_revenue = Column(Float)     # 营业额
    peak_hour = Column(Boolean)       # 是否高峰时段

class Satisfaction(Base):
    """满意度评价模型"""
    __tablename__ = "satisfaction"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)          # 评分（1-5）
    comment = Column(String(500))     # 评价内容
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DishSales(Base):
    """菜品销售记录模型"""
    __tablename__ = "dish_sales"

    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    sales_count = Column(Integer, nullable=False)
    sales_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)