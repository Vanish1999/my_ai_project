import sqlite3
from fuzzywuzzy import process
import csv

# 数据库工具模块
class DatabaseUtils:

    @staticmethod
    def get_database_connection():
        # 连接到 SQLite 数据库
        conn = sqlite3.connect("ai_assistant.db")
        return conn

    @staticmethod
    def get_user_data(key):
        # 查询用户
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
        matches = process.extract(user_question, question_texts, limit=5)  # 获取三个最接近的问题

        if matches[0][1] > 80:  # 高可信度直接返回答案
            for question, answer in questions:
                if question == matches[0][0]:
                    return answer

        elif matches[0][1] > 50:  # 中等可信度返回选项
            print("以下是可能的问题，请选择：")
            for idx, (match, score) in enumerate(matches):
                print(f"{idx + 1}. {match} (匹配度：{score}%)")
            print(f"{len(matches) + 1}. 不在以上选项中，标记为未知问题")  # 增加“未知问题”选项

            while True:
                choice = input("请输入对应的序号（输入 0 退出）：")
                if choice.isdigit():
                    choice = int(choice)
                    if choice == 0:
                        return "好的，取消选择。"
                    elif 1 <= choice <= len(matches):
                        selected_question = matches[choice - 1][0]
                        for question, answer in questions:
                            if question == selected_question:
                                return answer
                    elif choice == len(matches) + 1:
                    # 标记为未知问题并存储
                        DatabaseUtils.record_unknown_question(user_question)
                        return "问题已存储为未知问题，感谢您的反馈！"
                print("输入无效，请输入有效的序号。")
        else:
            return "抱歉，我无法理解你的问题。"


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
            
    @staticmethod
    def record_unknown_question(user_question):
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO unknown_questions (question)
            VALUES (?)
        """, (user_question,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_unknown_questions():
        # 获取所有未知问题
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, created_at FROM unknown_questions")
        questions = cursor.fetchall()
        conn.close()
        return questions

    @staticmethod
    def delete_unknown_question_by_id(question_id):
        # 根据 ID 删除未知问题
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM unknown_questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
        print(f"未知问题 ID 为 {question_id} 的记录已删除！")
        
    @staticmethod
    def move_unknown_question_to_knowledge_base(question_id, answer):
        # 将未知问题移到知识库
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        # 查询问题
        cursor.execute("SELECT question FROM unknown_questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()
        if question:
            # 添加到知识库
            cursor.execute("""
                INSERT INTO knowledge_base (question, answer)
                VALUES (?, ?)
            """, (question[0], answer))
            # 删除未知问题
            cursor.execute("DELETE FROM unknown_questions WHERE id = ?", (question_id,))
            conn.commit()
            print(f"问题 '{question[0]}' 已添加答案，并移至知识库！")
        else:
            print(f"未知问题 ID 为 {question_id} 的记录不存在。")
        conn.close()

    @staticmethod
    def import_knowledge_from_csv(file_path):
        """
        从 CSV 文件批量导入知识库
        """
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = row['question']
                answer = row['answer']
                cursor.execute("""
                    INSERT INTO knowledge_base (question, answer)
                    VALUES (?, ?)
                    ON CONFLICT(question) DO NOTHING
                """, (question, answer))
        conn.commit()
        conn.close()
        print(f"知识库已从 {file_path} 导入！")
        
    @staticmethod
    def export_knowledge_to_csv(file_path):
        """
        将知识库导出到 CSV 文件
        """
        conn = DatabaseUtils.get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM knowledge_base")
        rows = cursor.fetchall()
        conn.close()

        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['question', 'answer'])  # 写入表头
            writer.writerows(rows)
        print(f"知识库已导出到 {file_path}！")
