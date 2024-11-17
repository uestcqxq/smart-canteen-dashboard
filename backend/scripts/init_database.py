import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

def get_db_config():
    """获取数据库配置"""
    return {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_NAME")
    }

def init_database():
    """初始化数据库和表"""
    config = get_db_config()
    try:
        # 连接MySQL服务器
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute(f"DROP DATABASE IF EXISTS {config['database']}")
            cursor.execute(f"CREATE DATABASE {config['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {config['database']} 创建成功")
            
            # 切换到新创建的数据库
            cursor.execute(f"USE {config['database']}")
            
            # 创建表
            tables = {
                'dining_records': """
                    CREATE TABLE dining_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee_id VARCHAR(50),
                        employee_name VARCHAR(50),
                        avatar_url VARCHAR(200),
                        payment_time DATETIME,
                        payment_amount DECIMAL(10, 2),
                        dishes JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_payment_time (payment_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                'satisfaction': """
                    CREATE TABLE satisfaction (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                        comment VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            }
            
            for table_name, create_statement in tables.items():
                cursor.execute(create_statement)
                print(f"表 {table_name} 创建成功")
            
            return connection, cursor
            
    except Error as e:
        print(f"数据库初始化错误: {e}")
        return None, None

def generate_mock_data(cursor):
    """生成模拟数据"""
    try:
        # 常见菜品列表
        dishes = [
            {"name": "红烧肉", "price": 15.00},
            {"name": "清炒时蔬", "price": 8.00},
            {"name": "鱼香肉丝", "price": 12.00},
            {"name": "番茄炒蛋", "price": 10.00},
            {"name": "宫保鸡丁", "price": 13.00},
            {"name": "米饭", "price": 2.00},
            {"name": "馒头", "price": 1.00},
            {"name": "水饺", "price": 12.00},
            {"name": "炒面", "price": 10.00},
            {"name": "汤面", "price": 8.00}
        ]

        # 生成今天不同时段的就餐记录
        current_date = datetime.now().date()
        
        # 生成不同时段的就餐记录
        for hour in range(7, 20):  # 从早上7点到晚上8点
            # 每个小时生成多条记录
            records_count = random.randint(5, 15)
            for _ in range(records_count):
                # 生成随机时间（在当前小时内）
                minutes = random.randint(0, 59)
                current_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minutes))
                
                # 生成员工信息
                employee_id = f"EMP{random.randint(1000, 9999)}"
                employee_name = f"员工{random.randint(1, 200)}"
                
                # 生成随机菜品（1-4个菜）
                meal_dishes = []
                dish_count = random.randint(1, 4)
                selected_dishes = random.sample(dishes, dish_count)
                for dish in selected_dishes:
                    meal_dishes.append(dish)
                
                # 计算总金额
                total_amount = sum(dish["price"] for dish in meal_dishes)
                
                # 插入就餐记录
                cursor.execute("""
                    INSERT INTO dining_records 
                    (employee_id, employee_name, payment_time, payment_amount, dishes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    employee_id,
                    employee_name,
                    current_time,
                    total_amount,
                    json.dumps(meal_dishes)
                ))
                
                print(f"生成就餐记录: {employee_name} 在 {current_time} 消费 {total_amount}")
        
        print("成功生成就餐记录")
        
        # 生成满意度评价数据
        print("开始生成满意度评价数据...")
        
        # 生成今天的满意度评价
        current_date = datetime.now()
        
        # 生成100条满意度评价
        for _ in range(100):
            # 生成随机评分（1-5分，倾向于好评）
            rating = random.choices(
                [5, 4, 3, 2, 1],
                weights=[0.4, 0.3, 0.15, 0.1, 0.05]  # 权重分配，好评占比更高
            )[0]
            
            # 生成评价时间（今天内的随机时间）
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            rating_time = current_date.replace(hour=hours, minute=minutes, second=seconds)
            
            # 生成评价内容
            comment = None
            if rating <= 3:  # 低分时生成评价内容
                comments = [
                    "菜品不够新鲜",
                    "服务态度需要改善",
                    "等待时间太长",
                    "价格偏高",
                    "口味一般",
                    "环境需要改善",
                    "分量太少",
                    "种类不够丰富",
                    "餐具不够干净",
                    "出餐速度慢"
                ]
                comment = random.choice(comments)
            
            # 插入满意度评价
            cursor.execute("""
                INSERT INTO satisfaction (rating, comment, created_at)
                VALUES (%s, %s, %s)
            """, (rating, comment, rating_time))
        
        print("成功生成满意度评价数据")
        return True

    except Error as e:
        print(f"生成数据时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始初始化数据库...")
    connection, cursor = init_database()
    
    if connection and cursor:
        try:
            if generate_mock_data(cursor):
                connection.commit()
                print("数据库初始化和数据生成完成！")
            else:
                print("数据生成失败！")
        except Error as e:
            print(f"执行出错: {e}")
        finally:
            cursor.close()
            connection.close()
            print("数据库连接已关闭")
    else:
        print("数据库初始化失败！")

if __name__ == "__main__":
    main() 