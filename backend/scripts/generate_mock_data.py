import random
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def connect_to_database():
    try:
        # 从环境变量获取数据库配置
        DB_HOST = os.getenv("DB_HOST")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")

        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"连接数据库时出错: {e}")
        return None

def generate_dining_records(connection, start_date):
    """生成就餐记录数据"""
    cursor = connection.cursor()
    
    # 常见菜品列表
    dishes = [
        ("红烧肉", 15.00),
        ("清炒时蔬", 8.00),
        ("鱼香肉丝", 12.00),
        ("番茄炒蛋", 10.00),
        ("宫保鸡丁", 13.00),
        ("米饭", 2.00),
        ("馒头", 1.00),
        ("水饺", 12.00),
        ("炒面", 10.00),
        ("汤面", 8.00)
    ]

    # 生成一个月的数据
    current_date = start_date
    end_date = start_date + timedelta(days=30)

    while current_date < end_date:
        # 每天三个就餐时段
        for hour in [7, 12, 18]:  # 早餐、午餐、晚餐
            # 基础就餐人数
            base_customers = {
                7: random.randint(100, 200),   # 早餐
                12: random.randint(300, 500),  # 午餐
                18: random.randint(200, 400)   # 晚餐
            }[hour]
            
            # 考虑工作日和周末的差异
            is_weekend = current_date.weekday() >= 5
            if is_weekend:
                base_customers = int(base_customers * 0.7)
            
            # 生成就餐记录
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            customer_count = base_customers
            avg_consumption = random.uniform(15, 25)  # 平均消费
            total_revenue = customer_count * avg_consumption
            peak_hour = 1 if customer_count > 300 else 0

            # 插入就餐记录
            cursor.execute("""
                INSERT INTO dining_records (timestamp, customer_count, total_revenue, peak_hour)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, customer_count, total_revenue, peak_hour))

            # 生成满意度评价
            num_ratings = int(customer_count * 0.1)  # 假设10%的客户会评价
            for _ in range(num_ratings):
                rating = random.choices([5,4,3,2,1], weights=[0.4,0.3,0.2,0.07,0.03])[0]
                comment = None
                if rating <= 3:  # 低分时可能会有评价
                    comments = [
                        "菜品不够新鲜", "服务态度需要改善", "等待时间太长",
                        "价格偏高", "口味一般", "环境需要改善"
                    ]
                    comment = random.choice(comments)

                cursor.execute("""
                    INSERT INTO satisfaction (rating, comment, timestamp)
                    VALUES (%s, %s, %s)
                """, (rating, comment, timestamp))

            # 生成菜品销售记录
            for dish_name, price in dishes:
                # 每个菜品的基础销量
                base_sales = random.randint(20, 50)
                # 考虑时段和周末因素
                if hour == 12:  # 午餐时段销量最高
                    base_sales *= 1.5
                if is_weekend:
                    base_sales *= 0.7
                
                sales_count = int(base_sales)
                cursor.execute("""
                    INSERT INTO dish_sales (dish_name, price, sales_count, sales_time)
                    VALUES (%s, %s, %s, %s)
                """, (dish_name, price, sales_count, timestamp))

        current_date += timedelta(days=1)

    connection.commit()
    cursor.close()

def main():
    connection = connect_to_database()
    if connection:
        try:
            # 生成过去一个月的数据
            start_date = datetime.now() - timedelta(days=30)
            generate_dining_records(connection, start_date)
            print("模拟数据生成完成！")
        except Error as e:
            print(f"生成数据时出错: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    main() 