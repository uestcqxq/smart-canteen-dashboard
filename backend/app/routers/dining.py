from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, time
from ..models.database import get_db
from ..models.canteen import DiningRecord
from ..utils.dining_simulator import DiningSimulator
import random
import json

router = APIRouter()

# 创建模拟器实例
simulator = DiningSimulator()

@router.get("/dining/trend")
async def get_dining_trend(db: Session = Depends(get_db)):
    """获取就餐实时趋势数据"""
    try:
        # 获取当前时间和2小时前的时间
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        
        # 获取最近2小时的就餐记录
        records = db.query(DiningRecord).filter(
            DiningRecord.payment_time >= two_hours_ago,
            DiningRecord.payment_time <= now
        ).order_by(DiningRecord.payment_time).all()
        
        # 生成时间点（每5分钟一个点）
        time_points = []
        current_time = two_hours_ago
        while current_time <= now:
            time_points.append(current_time)
            current_time += timedelta(minutes=5)
        
        # 计算每个时间点的在餐人数
        dining_counts = []
        for point in time_points:
            # 计算在这个时间点还在就餐的人数（假设每人就餐时间为20分钟）
            count = sum(
                1 for record in records
                if record.payment_time <= point and 
                record.payment_time + timedelta(minutes=20) >= point
            )
            dining_counts.append(count)
        
        # 格式化时间点（只显示时:分）
        formatted_times = [t.strftime('%H:%M') for t in time_points]
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "times": formatted_times,
                "counts": dining_counts,
                "current": dining_counts[-1] if dining_counts else 0
            }
        }
    except Exception as e:
        print(f"获取就餐趋势数据出错: {str(e)}")
        return {
            "code": 500,
            "message": str(e)
        }

@router.get("/dining/revenue")
async def get_revenue_trend(db: Session = Depends(get_db)):
    """获取营业额趋势数据"""
    try:
        # 获取当前时间和2小时前的时间
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        
        # 获取最近2小时的就餐记录
        records = db.query(DiningRecord).filter(
            DiningRecord.payment_time >= two_hours_ago,
            DiningRecord.payment_time <= now
        ).order_by(DiningRecord.payment_time).all()
        
        # 生成时间点（每5分钟一个点）
        time_points = []
        current_time = two_hours_ago
        while current_time <= now:
            time_points.append(current_time)
            current_time += timedelta(minutes=5)
        
        # 计算每个时间点的营业额
        revenue_data = []
        for point in time_points:
            # 计算5分钟时间段内的营业额
            point_end = point + timedelta(minutes=5)
            revenue = sum(
                float(record.payment_amount)
                for record in records
                if point <= record.payment_time < point_end
            )
            revenue_data.append(round(revenue, 2))
        
        # 格式化时间点
        formatted_times = [t.strftime('%H:%M') for t in time_points]
        
        # 计算当前总营业额
        total_revenue = sum(float(record.payment_amount) for record in records)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "times": formatted_times,
                "revenues": revenue_data,
                "total_revenue": round(total_revenue, 2)
            }
        }
    except Exception as e:
        print(f"获取营业额趋势数据出错: {str(e)}")
        return {
            "code": 500,
            "message": str(e)
        }

@router.get("/dining/realtime")
async def get_dining_records(db: Session = Depends(get_db)):
    """获取实时就餐记录和今日就餐总人数"""
    try:
        # 随机生成新记录（30%的概率）
        if random.random() < 0.3:
            simulator.add_random_records(db, random.randint(1, 3))
        
        # 获取今天的开始时间和结束时间
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # 查询今日就餐总人数
        total_dining = db.query(func.count(DiningRecord.id)).filter(
            DiningRecord.payment_time.between(today_start, today_end)
        ).scalar()
        
        # 获取最近10条就餐记录
        records = db.query(DiningRecord).order_by(
            DiningRecord.payment_time.desc()
        ).limit(10).all()
        
        # 转换记录为字典格式
        records_data = []
        for record in records:
            try:
                dishes = json.loads(record.dishes) if isinstance(record.dishes, str) else record.dishes
                records_data.append({
                    "id": record.id,
                    "employee_id": record.employee_id,
                    "employee_name": record.employee_name,
                    "payment_time": record.payment_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "payment_amount": float(record.payment_amount),
                    "dishes": dishes
                })
            except Exception as e:
                print(f"处理记录时出错: {e}")
                continue
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "total_dining": int(total_dining or 0),
                "records": records_data
            }
        }
    except Exception as e:
        print(f"获取就餐记录时出错: {str(e)}")
        return {
            "code": 500,
            "message": f"Error: {str(e)}",
            "data": {
                "total_dining": 0,
                "records": []
            }
        }
  