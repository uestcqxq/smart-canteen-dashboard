import sys
import os
from decimal import Decimal
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..models.database import get_db
from ..models.canteen import DishSales
from typing import List
from pydantic import BaseModel
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

router = APIRouter()

class DishAnalysisResponse(BaseModel):
    name: str
    sales: int
    rank: str
    avg_daily_sales: float
    total_revenue: float
    trend: str  # 'up', 'down', 'stable'

def calculate_trend(dish_name: str, db: Session, start_date: datetime, end_date: datetime) -> str:
    """计算菜品销售趋势"""
    mid_date = start_date + (end_date - start_date) / 2
    
    # 计算前半期销量
    first_half = db.query(func.sum(DishSales.sales_count)).filter(
        DishSales.dish_name == dish_name,
        DishSales.sales_time.between(start_date, mid_date)
    ).scalar() or Decimal('0')
    
    # 计算后半期销量
    second_half = db.query(func.sum(DishSales.sales_count)).filter(
        DishSales.dish_name == dish_name,
        DishSales.sales_time.between(mid_date, end_date)
    ).scalar() or Decimal('0')
    
    # 计算趋势
    if float(second_half) > float(first_half) * 1.1:
        return "up"
    elif float(second_half) < float(first_half) * 0.9:
        return "down"
    else:
        return "stable"

@router.get("/dish/analysis")
@cache(expire=300)  # 缓存5分钟
async def get_dish_analysis(days: int = 30, db: Session = Depends(get_db)):
    """获取菜品销售分析数据"""
    try:
        print(f"开始获取菜品分析数据，时间范围：{days}天")
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        print(f"查询时间范围：{start_date} 至 {end_date}")
        
        # 构建SQL查询
        query = db.query(
            DishSales.dish_name,
            func.sum(DishSales.sales_count).label('total_sales'),
            func.sum(DishSales.sales_count * DishSales.price).label('total_revenue'),
            func.avg(DishSales.sales_count).label('avg_daily_sales')
        ).filter(
            DishSales.sales_time.between(start_date, end_date)
        ).group_by(
            DishSales.dish_name
        ).order_by(
            desc('total_sales')
        )
        
        # 打印实际执行的SQL查询
        print("执行的SQL查询:", str(query.statement.compile(compile_kwargs={"literal_binds": True})))
        
        results = query.all()
        print(f"查询到 {len(results)} 条菜品记录")
        print("原始查询结果:", results)  # 添加原始结果的打印
        
        # 处理数据
        total_dishes = len(results)
        analysis_data = []
        
        for i, result in enumerate(results):
            # 计算排名等级
            if i < total_dishes * 0.3:
                rank = "hot"
            elif i >= total_dishes * 0.7:
                rank = "cold"
            else:
                rank = "normal"
                
            trend = calculate_trend(result.dish_name, db, start_date, end_date)
            
            # 确保所有数值都转换为适当的类型
            item_data = {
                "name": result.dish_name,
                "sales": int(float(result.total_sales)),
                "rank": rank,
                "avg_daily_sales": round(float(result.avg_daily_sales), 2),  # 保留两位小数
                "total_revenue": round(float(result.total_revenue), 2),  # 保留两位小数
                "trend": trend
            }
            analysis_data.append(item_data)
            print(f"处理后的菜品数据: {item_data}")  # 添加处理后数据的打印
            
        # 添加统计信息
        stats = {
            "total_dishes": total_dishes,
            "total_sales": sum(d["sales"] for d in analysis_data),
            "total_revenue": round(sum(d["total_revenue"] for d in analysis_data), 2),
            "hot_dishes_count": len([d for d in analysis_data if d["rank"] == "hot"]),
            "cold_dishes_count": len([d for d in analysis_data if d["rank"] == "cold"])
        }
        
        response_data = {
            "code": 200,  # 添加状态码
            "data": analysis_data,
            "stats": stats,
            "message": "success"  # 添加状态消息
        }
        
        print("完整返回数据:", response_data)  # 打印完整返回数据
        
        return response_data
        
    except Exception as e:
        print(f"处理数据时出错: {e}")
        print(f"错误详情: ", str(e.__traceback__))  # 添加更详细的错误信息
        raise HTTPException(status_code=500, detail=str(e))