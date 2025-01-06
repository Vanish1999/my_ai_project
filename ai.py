from db_utils import DatabaseUtils
import re

class ContextManager:
    """
    管理对话的上下文，用于多轮对话
    """
    def __init__(self):
        self.intent = None  # 记录用户的意图
        self.key = None  # 记录关键字或上下文内容

    def update_context(self, intent, key):
        """
        更新上下文
        """
        self.intent = intent
        self.key = key

    def clear_context(self):
        """
        清除上下文
        """
        self.intent = None
        self.key = None

    def get_context(self):
        """
        获取当前的上下文
        """
        return self.intent, self.key


def extract_intent(user_input):
    """
    根据用户输入识别意图，并尝试提取具体关键字段
    """
    intents = {
    
    "查看信息": ["查看", "查询", "查找", "搜索", "获取", "找"],
    "更新信息": ["更新", "设置", "记住", "修改", "保存", "变更"],
    "删除信息": ["删除", "移除", "清除", "去掉", "丢弃"],
    "计算": ["计算", "求值", "算一下", "求解", "多少"],
    "问答": ["今天", "喜欢", "几", "什么", "为何", "为什么", "怎么", "如何", "意义", "定义","哪","谁","啥","原因"],
    "问候": ["你好", "您好", "嗨", "Hello", "哈喽", "早上好", "晚上好", "下午好", "在吗"],
    "未知问题": ["未知问题"],
    "帮助": ["帮助", "功能", "指南",  "使用说明"]


    }

    # 遍历意图，尝试匹配关键词
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                # 提取意图及具体的关键字段
                remaining_text = user_input.replace(keyword, "").strip()
                return intent, remaining_text
    return "未知", ""

def handle_view_information(key):
    """
    处理查看信息的逻辑
    """
    if key == "未知问题":
        questions = DatabaseUtils.get_all_unknown_questions()
        if questions:
            print("以下是所有未知问题：")
            for question in questions:
                print(f"ID: {question[0]}, 问题: {question[1]}, 创建时间: {question[2]}")
        else:
            print("当前没有未知问题。")
    elif key:
        value = DatabaseUtils.get_user_data(key)
        if value:
            print(f"你的{key}是：{value}")
        else:
            print(f"我没有找到关于{key}的信息。")
    else:
        print("请输入要查看的具体内容，例如：查看名字")

def handle_unknown_question(intent, key, context_manager):
    """
    处理未知问题的删除和更新
    """
    if intent == "删除信息":
        if "未知问题" in key:
            try:
                # 提取未知问题的ID
                question_id = int(key.split()[1])
                DatabaseUtils.delete_unknown_question_by_id(question_id)
                context_manager.clear_context()
            except (IndexError, ValueError):
                print("请输入有效的未知问题 ID，例如：删除未知问题 1")
                context_manager.update_context(intent, "未知问题")
        else:
            print("你想删除哪个未知问题呢？请输入 '删除未知问题 ID' 的格式")
            context_manager.update_context(intent, "未知问题")

    elif intent == "更新信息":
        if "未知问题" in key:
            try:
                # 提取未知问题的ID
                question_id = int(key.split()[1])
                answer = input(f"请输入未知问题 ID {question_id} 的答案：")
                DatabaseUtils.move_unknown_question_to_knowledge_base(question_id, answer)
                context_manager.clear_context()
            except (IndexError, ValueError):
                print("请输入有效的未知问题 ID，例如：更新未知问题 1")
                context_manager.update_context(intent, "未知问题")
        else:
            print("你想更新哪个未知问题呢？请输入 '更新未知问题 ID' 的格式")
            context_manager.update_context(intent, "未知问题")


# 主程序
if __name__ == "__main__":
    DatabaseUtils.initialize_knowledge_base()  # 初始化知识库
    print("你好，我是你的学习小助手！告诉我你的信息，我会记住哦！")

    # 初始化上下文管理器
    context_manager = ContextManager()

    while True:
        user_input = input("你想对我说什么？（输入'退出'结束对话）: ")
        if user_input == "退出":
            print("再见，小凡！期待下次和你聊天！👋")
            break

        # 使用改进的意图解析
        intent, key = extract_intent(user_input)

        # 如果意图为空，尝试从上下文补全
        if intent == "未知" and key == "":
            intent, key = context_manager.get_context()

        # 更新或清除上下文
        if intent and key:
            context_manager.update_context(intent, key)
        else:
            context_manager.clear_context()

        print(f"调试信息 - 意图: {intent}, 关键字: {key}")  # 调试信息

        # 处理不同的意图
        if intent == "查看信息":
            if key:
                handle_view_information(key)
                context_manager.clear_context()  # 清除上下文
            else:
                print("请输入要查看的具体内容，例如：查看名字")
                context_manager.update_context(intent, key)

        elif key and key.startswith("未知问题"):
            handle_unknown_question(intent, key, context_manager)

        elif intent == "更新信息":
            if key:
                if "是" in user_input:
                    try:
                        key, value = user_input.split("是")[0][2:].strip(), user_input.split("是")[1].strip()
                        DatabaseUtils.update_user_data(key, value)
                        context_manager.clear_context()  # 更新成功后清除上下文
                    except IndexError:
                        print("更新信息格式错误，请输入类似‘更新爱好是绘画’的命令！")
                else:
                    print("更新信息时请使用‘是’来分隔关键字和值，例如：更新名字是小凡")
                    context_manager.update_context(intent, key)
            else:
                print("你想更新什么信息呢？例如：更新名字是小凡")
                context_manager.update_context(intent, key)

        elif intent == "删除信息":
            if key:
                DatabaseUtils.delete_user_data(key)
                context_manager.clear_context()  # 删除成功后清除上下文
            else:
                print("你想删除什么信息呢？例如：删除名字")
                context_manager.update_context(intent, key)


        elif intent == "计算":
            expression = key
            try:
                result = eval(expression)
                if len(expression) > 10:
                    print(f"哇！这么复杂的表达式，我动脑子算了下，答案是：{result}")
                else:
                    print(f"答案是：{result}")
            except Exception as e:
                print(f"哎呀，这个表达式我算不出来呢！错误信息：{e}")


        elif intent == "问答":
            answer = DatabaseUtils.get_best_match_with_options(user_input)
            if answer == "抱歉，我无法理解你的问题。":
                print("我暂时无法回答这个问题，但我已经记录下来啦！")
                DatabaseUtils.record_unknown_question(user_input)
            else:
                print(answer)
                context_manager.clear_context()  # 问答完成后清除上下文

        elif intent == "问候":
            print("你好呀！很高兴见到你！")
            context_manager.clear_context()

        elif intent == "帮助":
            print("这是我目前支持的功能列表：")
            print("1. 查看信息：输入类似 '查看名字' 或 '查看未知问题'。")
            print("2. 更新信息：输入类似 '记住名字是小凡' 或 '更新地址是纽约'。")
            print("3. 删除信息：输入类似 '删除名字' 或 '删除未知问题 1'。")
            print("4. 计算功能：输入类似 '计算 2 + 2'。")
            print("5. 提问问题：输入问题，我会尝试回答！如果我不知道答案，我会记录下来。")
            print("6. 帮助：输入 '帮助' 查看这个提示列表。")
            print("7. 导入知识：输入 '导入知识 文件名.csv' 导入外部知识库。")
            print("8. 导出知识：输入 '导出知识 文件名.csv' 导出为外部知识库。")
            context_manager.clear_context()

        else:
            print("抱歉，我不太明白你的意思呢。")

