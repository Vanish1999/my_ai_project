import sqlite3
from db_utils import DatabaseUtils

# 创建或连接数据库
def create_database():
    try:
        conn = sqlite3.connect("ai_assistant.db")  # 数据库文件
        cursor = conn.cursor()

        # 创建用户数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT
            )
        """)

        # 创建知识库表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT
            )
        """)

        conn.commit()
        print("数据库和表已创建！")
    except Exception as e:
        print(f"创建数据库或表时出错：{e}")
    finally:
        conn.close()

def create_unknown_questions_table():
    try:
        conn = DatabaseUtils.get_database_connection()  # 使用 DatabaseUtils 提供的静态方法
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unknown_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("未知问题表已创建！")
    except Exception as e:
        print(f"创建未知问题表时出错：{e}")
    finally:
        conn.close()

# 运行初始化
create_database()
create_unknown_questions_table()
