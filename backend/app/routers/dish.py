import sys
import os
from decimal import Decimal
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..models.database import get_db
from ..models.canteen import DiningRecord
import json

router = APIRouter()

@router.get("/dish/analysis")
async def get_dish_analysis(db: Session = Depends(get_db)):
    """获取实时菜品销售分析"""
    try:
        print("开始获取菜品分析数据...")
        
        # 获取今天的开始时间
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # 获取所有今日就餐记录
        records = db.query(DiningRecord).filter(
            DiningRecord.payment_time >= today_start
        ).all()
        
        print(f"查询到 {len(records)} 条就餐记录")
        
        # 统计菜品销量
        dish_stats = {}
        total_sales = 0
        
        for record in records:
            if record.dishes:
                try:
                    dishes = json.loads(record.dishes) if isinstance(record.dishes, str) else record.dishes
                    print(f"处理就餐记录: {dishes}")
                    for dish in dishes:
                        dish_name = dish.get('name', '')
                        if dish_name:
                            if dish_name not in dish_stats:
                                dish_stats[dish_name] = {
                                    'name': dish_name,
                                    'sales': 0,
                                    'revenue': 0.0
                                }
                            dish_stats[dish_name]['sales'] += 1
                            dish_stats[dish_name]['revenue'] += float(dish.get('price', 0))
                            total_sales += 1
                except Exception as e:
                    print(f"处理菜品数据出错: {e}")
                    continue
        
        print(f"统计得到 {len(dish_stats)} 种菜品")
        
        # 转换为列表并排序
        dish_list = list(dish_stats.values())
        dish_list.sort(key=lambda x: x['sales'], reverse=True)
        
        # 计算排名和趋势
        for i, dish in enumerate(dish_list):
            dish['rank'] = 'hot' if i < len(dish_list) * 0.3 else ('cold' if i >= len(dish_list) * 0.7 else 'normal')
            dish['percentage'] = round(dish['sales'] * 100 / total_sales, 2) if total_sales > 0 else 0
        
        response_data = {
            "code": 200,
            "message": "success",
            "data": {
                "dishes": dish_list,
                "stats": {
                    "total_dishes": len(dish_list),
                    "total_sales": total_sales,
                    "total_revenue": sum(dish['revenue'] for dish in dish_list),
                    "hot_dishes_count": len([d for d in dish_list if d['rank'] == 'hot']),
                    "cold_dishes_count": len([d for d in dish_list if d['rank'] == 'cold'])
                },
                "update_time": datetime.now().strftime("%H:%M:%S")
            }
        }
        
        print("返回数据:", response_data)
        return response_data
        
    except Exception as e:
        print(f"获取菜品分析数据出错: {str(e)}")
        return {
            "code": 500,
            "message": str(e)
        }