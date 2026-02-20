import os
from openai import OpenAI
# 导入自定义模块（确保文件在同一目录）
from json_save import StorageModule
from skills import SkillModule

# ====================== 基础配置 ======================
# 加载环境变量（存放LLM API密钥，避免硬编码）
# LLM配置：直接硬编码，无需.env文件
LLM_API_KEY = "sk-b33606d1b2a34191ad5388d3fb91b531"  # 替换为你的真实密钥
LLM_MODEL = "deepseek-chat"  # 替换为你的模型
LLM_BASE_URL = "https://api.deepseek.com"  #替换为你模型的网址
# 提示词模板（核心：引导LLM只返回唯一口令，无多余内容）
PROMPT_TEMPLATE = """
你的唯一任务是根据用户的需求，返回对应的唯一程序口令，仅返回口令字符串，不要任何解释、标点或多余内容。

已知口令列表（必须从以下列表中选择，不存在则返回"unknown"）：
{command_list}

示例：
用户输入：帮我打开原神 → 返回：genshin
用户输入：启动微信 → 返回：wechat
用户输入：打开QQ → 返回：unknown

用户当前输入：{user_input}
"""

class MainAgent:
    def __init__(self):
        """初始化主程序：关联LLM、储存模块、技能模块"""
        # 初始化自定义模块
        self.storage = StorageModule()
        self.skill = SkillModule()
        # 初始化LLM客户端
        self.llm_client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL  # 新增：指定API网址
        )
        # 预加载所有口令列表（用于提示词，避免LLM返回未知口令）
        self.command_list = self._get_all_commands()

    def _get_all_commands(self) -> str:
        """获取储存模块中所有唯一口令，拼接成字符串供提示词使用"""
        all_programs = self.storage.get_all_programs()
        commands = list(all_programs.keys())
        return ", ".join(commands) if commands else "无"

    def _call_llm(self, user_input: str) -> str:
        """
        核心方法：调用LLM，解析用户输入并返回唯一口令
        :param user_input: 用户输入的自然语言需求
        :return: LLM返回的唯一口令（如genshin/unknown）
        """
        # 填充提示词模板（动态传入口令列表和用户输入）
        prompt = PROMPT_TEMPLATE.format(
            command_list=self.command_list,
            user_input=user_input.strip()
        )

        try:
            # 调用LLM API
            response = self.llm_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # 0温度保证输出稳定，只返回口令
                timeout=10  # 超时时间，避免卡壳
            )
            # 提取LLM返回的口令（去除空格）
            llm_command = response.choices[0].message.content.strip()
            return llm_command
        except Exception as e:
            # LLM调用失败时返回错误标识
            print(f"LLM调用失败：{str(e)}")
            return "error"

    def run(self):
        """主程序运行入口：持续交互，执行核心流程"""
        print("===== 小宅AI Agent Demo 启动 =====")
        print("核心功能：输入需求 → 启动指定exe程序")
        print("示例输入：帮我打开原神 | 输入“退出”终止程序")
        print("=================================\n")

        while True:
            # 步骤1：获取用户输入
            user_input = input("请输入你的需求：").strip()
            if user_input.lower() == "退出":
                print("小宅已退出，再见！")
                break
            if not user_input:
                print("输入不能为空，请重新输入！")
                continue

            # 步骤2：调用LLM，获取唯一口令
            print("正在解析你的需求...")
            llm_command = self._call_llm(user_input)
            
            # 处理LLM调用异常
            if llm_command == "error":
                print("小宅回复：解析需求失败，请稍后再试！\n")
                continue
            # 处理未知口令
            if llm_command == "unknown":
                print(f"小宅回复：未找到「{user_input}」对应的程序配置！\n")
                continue

            # 步骤3：调用技能模块，执行打开程序操作
            print("正在执行操作...")
            skill_result = self.skill.open_exe_program(llm_command)
            print(f"小宅回复：{skill_result}\n")

# ====================== 启动主程序 ======================
if __name__ == "__main__":
    # 初始化并运行主程序
    agent = MainAgent()
    agent.run()