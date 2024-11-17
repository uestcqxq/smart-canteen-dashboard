import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

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
                        INDEX idx_employee_id (employee_id),
                        INDEX idx_payment_time (payment_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                'satisfaction': """
                    CREATE TABLE satisfaction (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                        comment VARCHAR(500),
                        timestamp DATETIME NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'dish_sales': """
                    CREATE TABLE dish_sales (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        dish_name VARCHAR(100) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        sales_count INT NOT NULL,
                        sales_time DATETIME NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
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
        start_date = datetime.now() - timedelta(days=30)
        current_date = start_date
        end_date = datetime.now()

        print("开始生成模拟数据...")
        record_count = 0

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
                
                timestamp = current_date.replace(hour=hour, minute=0, second=0)
                customer_count = base_customers
                avg_consumption = random.uniform(15, 25)
                total_revenue = customer_count * avg_consumption
                peak_hour = 1 if customer_count > 300 else 0

                # 插入就餐记录
                cursor.execute("""
                    INSERT INTO dining_records (timestamp, customer_count, total_revenue, peak_hour)
                    VALUES (%s, %s, %s, %s)
                """, (timestamp, customer_count, total_revenue, peak_hour))
                record_count += 1

                # 生成满意度评价
                num_ratings = int(customer_count * 0.1)
                for _ in range(num_ratings):
                    rating = random.choices([5,4,3,2,1], weights=[0.4,0.3,0.2,0.07,0.03])[0]
                    comment = None
                    if rating <= 3:
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
                    base_sales = random.randint(20, 50)
                    if hour == 12:
                        base_sales *= 1.5
                    if is_weekend:
                        base_sales *= 0.7
                    
                    sales_count = int(base_sales)
                    print(f"插入菜品销售记录: {dish_name}, 价格: {price}, 销量: {sales_count}, 时间: {timestamp}")
                    cursor.execute("""
                        INSERT INTO dish_sales (dish_name, price, sales_count, sales_time)
                        VALUES (%s, %s, %s, %s)
                    """, (dish_name, price, sales_count, timestamp))

            current_date += timedelta(days=1)
            
        print(f"成功生成 {record_count} 条就餐记录")
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