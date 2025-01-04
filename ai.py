from db_utils import DatabaseUtils
import re

def extract_intent(user_input):
    """
    根据用户输入识别意图，并尝试提取具体关键字段
    """
    intents = {
        "查看信息": ["查看", "查询"],
        "更新信息": ["更新", "设置", "记住"],
        "删除信息": ["删除", "移除"],
        "计算": ["计算", "求值"],
        "问答": ["今天", "喜欢", "几", "什么"],
        "问候": ["你好", "您好", "嗨", "Hello"]
    }

    # 遍历意图，尝试匹配关键词
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                # 提取意图及具体的关键字段
                remaining_text = user_input.replace(keyword, "").strip()
                return intent, remaining_text
    return "未知", ""

def record_unknown_question(user_question):
    conn = DatabaseUtils.get_database_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO unknown_questions (question)
        VALUES (?)
    """, (user_question,))
    conn.commit()
    conn.close()

# 主程序
if __name__ == "__main__":
    DatabaseUtils.initialize_knowledge_base()  # 初始化知识库
    print("你好，我是你的学习小助手！告诉我你的信息，我会记住哦！")

    while True:
        user_input = input("你想对我说什么？（输入'退出'结束对话）: ")
        if user_input == "退出":
            print("再见，小凡！期待下次和你聊天！👋")
            break

        # 使用改进的意图解析
        intent, key = extract_intent(user_input)

        if intent == "查看信息":
            if key:  # 处理具体字段
                value = DatabaseUtils.get_user_data(key)
                if value:
                    print(f"你的{key}是：{value}")
                else:
                    print(f"我没有找到关于{key}的信息。")
            else:
                print("请输入要查看的具体内容，例如：查看名字")
        elif intent == "更新信息":
            try:
                key, value = user_input.split("是")[0][2:].strip(), user_input.split("是")[1].strip()
                DatabaseUtils.update_user_data(key, value)
            except IndexError:
                print("更新信息格式错误，请输入类似‘更新爱好是绘画’的命令！")
        elif intent == "删除信息":
            if key:
                DatabaseUtils.delete_user_data(key)
            else:
                print("请输入要删除的具体内容，例如：删除名字")
        elif intent == "计算":
            expression = key
            try:
                result = eval(expression)
                print(f"计算结果是：{result}")
            except Exception as e:
                print(f"无法计算表达式。错误：{e}")
        elif intent == "问答":
            answer = DatabaseUtils.get_best_match_with_options(user_input)
            if answer == "抱歉，我不太明白你的意思。":
                record_unknown_question(user_input)
                print("抱歉，我还不知道这个问题的答案，但我已经记录下来了。")
            else:
                print(answer)
        elif intent == "问候":
            print("你好呀！很高兴见到你！")
        else:
            print("抱歉，我不太明白你的意思呢。")



