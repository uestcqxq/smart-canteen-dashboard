import random
from datetime import datetime
import json
from sqlalchemy.orm import Session
from ..models.canteen import DiningRecord

class DiningSimulator:
    def __init__(self):
        self.dishes = [
            {"name": "红烧肉", "price": 15.00},
            {"name": "清炒时蔬", "price": 8.00},
            {"name": "鱼香肉丝", "price": 12.00},
            {"name": "番茄炒蛋", "price": 10.00},
            {"name": "宫保鸡丁", "price": 13.00},
            {"name": "米饭", "price": 2.00},
            {"name": "馒头", "price": 1.00},
            {"name": "水饺", "price": 12.00},
            {"name": "炒面", "price": 10.00},
            {"name": "汤面", "price": 8.00},
            {"name": "麻婆豆腐", "price": 11.00},
            {"name": "青椒肉丝", "price": 12.00},
            {"name": "糖醋里脊", "price": 14.00},
            {"name": "鱼香茄子", "price": 9.00},
            {"name": "炒青菜", "price": 7.00}
        ]

    def generate_record(self) -> dict:
        """生成一条就餐记录"""
        # 生成员工信息
        employee_id = f"EMP{random.randint(1000, 9999)}"
        employee_name = f"员工{random.randint(1, 200)}"
        
        # 随机选择1-4个菜品
        selected_dishes = random.sample(self.dishes, random.randint(1, 4))
        
        # 计算总金额
        total_amount = sum(dish["price"] for dish in selected_dishes)
        
        return {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "payment_time": datetime.now(),
            "payment_amount": total_amount,
            "dishes": selected_dishes
        }

    def add_random_records(self, db: Session, count: int = 1) -> list:
        """添加随机就餐记录到数据库"""
        new_records = []
        try:
            for _ in range(count):
                record_data = self.generate_record()
                record = DiningRecord(
                    employee_id=record_data["employee_id"],
                    employee_name=record_data["employee_name"],
                    payment_time=record_data["payment_time"],
                    payment_amount=record_data["payment_amount"],
                    dishes=json.dumps(record_data["dishes"])
                )
                db.add(record)
                new_records.append(record)
            
            db.commit()
            print(f"成功添加 {len(new_records)} 条新就餐记录")
            return new_records
        except Exception as e:
            db.rollback()
            print(f"添加就餐记录失败: {e}")
            return [] 