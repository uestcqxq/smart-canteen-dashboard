from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import get_db
from ..models.canteen import Satisfaction
from typing import List
from pydantic import BaseModel

router = APIRouter()

class SatisfactionStats(BaseModel):
    rating: int
    count: int
    percentage: float

@router.get("/satisfaction/stats")
async def get_satisfaction_stats(db: Session = Depends(get_db)):
    """获取满意度评价统计"""
    try:
        # 查询各评分的数量
        results = db.query(
            Satisfaction.rating,
            func.count(Satisfaction.id).label('count')
        ).group_by(
            Satisfaction.rating
        ).all()
        
        # 计算总评价数
        total = sum(r.count for r in results)
        
        # 计算各评分占比
        stats = [
            {
                "rating": r.rating,
                "count": r.count,
                "percentage": round(r.count * 100 / total if total > 0 else 0, 2)
            }
            for r in results
        ]
        
        return {
            "code": 200,
            "data": {
                "total": total,
                "stats": stats
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取满意度统计失败: {str(e)}"
        } 