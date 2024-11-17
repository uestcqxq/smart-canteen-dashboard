from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.canteen import DiningRecord, DishSales
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter()

# 生成200名模拟员工数据
MOCK_EMPLOYEES = []
for i in range(1, 201):
    gender = "men" if i % 2 == 0 else "women"
    avatar_id = (i % 50) + 1  # 循环使用1-50的头像
    MOCK_EMPLOYEES.append({
        "id": f"EMP{i:03d}",  # 格式化为3位数，如 EMP001
        "name": f"员工{i:03d}",
        "avatar": f"https://randomuser.me/api/portraits/{gender}/{avatar_id}.jpg"
    })

MOCK_DISHES = [
    {"name": "红烧肉", "price": 15.0},
    {"name": "清炒时蔬", "price": 8.0},
    {"name": "鱼香肉丝", "price": 12.0},
    {"name": "番茄炒蛋", "price": 10.0},
    {"name": "宫保鸡丁", "price": 13.0},
    {"name": "米饭", "price": 2.0},
    {"name": "青椒肉丝", "price": 12.0},
    {"name": "麻婆豆腐", "price": 10.0},
    {"name": "炸鸡排", "price": 15.0},
    {"name": "水煮鱼", "price": 22.0},
]

class DiningRecordResponse(BaseModel):
    employee_id: str
    employee_name: str
    avatar_url: str
    payment_time: datetime
    payment_amount: float
    dishes: List[dict]

    class Config:
        from_attributes = True

class DiningRealtimeResponse(BaseModel):
    code: int
    data: Dict[str, Any]
    message: str

async def generate_mock_data(db: Session):
    """生成模拟数据"""
    try:
        # 获取最近5分钟内已经就餐的员工ID
        recent_time = datetime.now() - timedelta(minutes=5)
        recent_records = db.query(DiningRecord.employee_id).filter(
            DiningRecord.payment_time >= recent_time
        ).all()
        recent_employee_ids = {record[0] for record in recent_records}
        
        # 过滤出未就餐的员工
        available_employees = [emp for emp in MOCK_EMPLOYEES if emp["id"] not in recent_employee_ids]
        
        if not available_employees:
            print("所有员工在最近5分钟内都已就餐")
            return
        
        # 随机选择一个未就餐的员工
        employee = random.choice(available_employees)
        
        # 随机选择2-4个菜品，确保有米饭
        other_dishes = [dish for dish in MOCK_DISHES if dish["name"] != "米饭"]
        selected_dishes = random.sample(other_dishes, random.randint(1, 3))
        # 添加米饭
        selected_dishes.append(next(dish for dish in MOCK_DISHES if dish["name"] == "米饭"))
        
        total_amount = sum(dish["price"] for dish in selected_dishes)
        
        # 创建就餐记录
        record = DiningRecord(
            employee_id=employee["id"],
            employee_name=employee["name"],
            avatar_url=employee["avatar"],
            payment_time=datetime.now(),
            payment_amount=total_amount,
            dishes=selected_dishes
        )
        
        db.add(record)
        
        # 更新菜品销售记录
        current_time = datetime.now()
        for dish in selected_dishes:
            # 查找是否存在当天的销售记录
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            existing_record = db.query(DishSales).filter(
                DishSales.dish_name == dish["name"],
                DishSales.sales_time.between(today_start, today_end)
            ).first()
            
            if existing_record:
                # 更新现有记录
                existing_record.sales_count += 1
            else:
                # 创建新记录
                new_sales = DishSales(
                    dish_name=dish["name"],
                    price=dish["price"],
                    sales_count=1,
                    sales_time=current_time
                )
                db.add(new_sales)
        
        db.commit()
        print(f"生成模拟数据: {employee['name']} 消费 {total_amount} 元")
        
    except Exception as e:
        print(f"生成模拟数据失败: {str(e)}")
        db.rollback()

@router.get("/dining/realtime", response_model=DiningRealtimeResponse)
async def get_realtime_dining(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    """获取实时就餐数据"""
    try:
        # 生成一些模拟数据
        background_tasks.add_task(generate_mock_data, db)
        
        # 获取最近5分钟的就餐记录，限制20条
        recent_time = datetime.now() - timedelta(minutes=5)
        records = db.query(DiningRecord).filter(
            DiningRecord.payment_time >= recent_time
        ).order_by(DiningRecord.payment_time.desc()).limit(20).all()
        
        # 获取今日就餐总人数
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        total_diners = db.query(DiningRecord).filter(
            DiningRecord.payment_time >= today_start
        ).count()
        
        # 如果没有记录，生成一条
        if not records:
            await generate_mock_data(db)
            records = db.query(DiningRecord).filter(
                DiningRecord.payment_time >= recent_time
            ).order_by(DiningRecord.payment_time.desc()).limit(20).all()
        
        # 转换记录为字典格式
        records_data = []
        for record in records:
            records_data.append({
                "employee_id": record.employee_id,
                "employee_name": record.employee_name,
                "avatar_url": record.avatar_url,
                "payment_time": record.payment_time,
                "payment_amount": float(record.payment_amount),
                "dishes": record.dishes
            })
        
        return {
            "code": 200,
            "data": {
                "records": records_data,
                "total_diners": total_diners
            },
            "message": "success"
        }
        
    except Exception as e:
        print(f"获取实时就餐数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dining/simulate")
async def simulate_dining(db: Session = Depends(get_db)):
    """手动触发生成模拟数据"""
    try:
        await generate_mock_data(db)
        return {"code": 200, "message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 