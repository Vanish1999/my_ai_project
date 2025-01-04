import sqlite3
from fuzzywuzzy import process

# 数据库工具模块
class DatabaseUtils:

    @staticmethod
    def get_database_connection():
        # 连接到 SQLite 数据库
        conn = sqlite3.connect("ai_assistant.db")
        return conn

    @staticmethod
    def get_user_data(key):
        # 查询用户数据
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM user_data WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def update_user_data(key, value):
        # 更新或插入用户数据
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_data (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()
        conn.close()
        print(f"我记住了，你的{key}是：{value}")

    @staticmethod
    def delete_user_data(key):
        # 删除用户数据
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_data WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        print(f"我已经删除了你的{key}！")

    @staticmethod
    def get_best_match_with_options(user_question):
        # 从数据库中模糊匹配问题，返回最佳答案或备选项
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM knowledge_base")
        questions = cursor.fetchall()
        conn.close()

        # 提取所有问题文本
        question_texts = [q[0] for q in questions]
        matches = process.extract(user_question, question_texts, limit=3)  # 获取三个最接近的问题

        if matches[0][1] > 80:  # 高可信度直接返回答案
            for question, answer in questions:
                if question == matches[0][0]:
                    return answer
        elif matches[0][1] > 50:  # 中等可信度返回选项
            print("以下是可能的问题，请选择：")
            for idx, (match, score) in enumerate(matches):
                print(f"{idx + 1}. {match} (可信度：{score}%)")
            choice = input("请输入对应的序号：")
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                selected_question = matches[int(choice) - 1][0]
                for question, answer in questions:
                    if question == selected_question:
                        return answer
            else:
                return "抱歉，我无法理解你的选择。"
        else:
            return "抱歉，我不太明白你的意思。"

    @staticmethod
    def insert_into_knowledge_base(question, answer):
        # 插入预定义问题和答案
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_base (question, answer)
            VALUES (?, ?)
            ON CONFLICT(question) DO NOTHING
        """, (question, answer))
        conn.commit()
        conn.close()

    @staticmethod
    def initialize_knowledge_base():
        # 初始化知识库
        predefined_questions = {
            "今天星期几？": "虽然不知道星期几但今天是美好的一天，不是吗？🌞",
            "2加2等于几？": "2加2当然等于4啦！🧠",
            "你喜欢做什么？": "我喜欢陪小凡学习和进步！💖"
        }
        for question, answer in predefined_questions.items():
            DatabaseUtils.insert_into_knowledge_base(question, answer)
