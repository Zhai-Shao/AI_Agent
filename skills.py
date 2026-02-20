import subprocess
import psutil
import os
from typing import Optional
# 导入之前定义的储存模块（确保两个文件在同一目录）
from json_save import StorageModule

class SkillModule:
    def __init__(self):
        """初始化技能模块，关联储存模块"""
        self.storage = StorageModule()  # 关联储存模块，用于口令匹配
        self._win_no_console_flag = subprocess.CREATE_NO_WINDOW  # Win11无控制台启动标识

    def _is_program_running(self, exe_path: str) -> bool:
        """
        辅助方法：检查程序是否已运行（避免重复启动）
        :param exe_path: exe绝对路径
        :return: 是否运行
        """
        if not exe_path:
            return False
        # 提取程序名称（如YuanShen.exe）
        exe_name = os.path.basename(exe_path)
        # 遍历进程检查是否已运行
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] == exe_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # 忽略无权限访问的进程
                continue
        return False

    def open_exe_program(self, ai_command: str) -> str:
        """
        核心技能：根据AI返回的口令打开exe程序（严格遵循「口令→匹配→路径→启动」流程）
        :param ai_command: AI返回的唯一口令（如genshin）
        :return: 执行结果提示（用于返回给用户）
        """
        # 步骤1：获取AI返回的口令（入参直接传入）
        if not ai_command or not ai_command.strip():
            return "错误：未获取到有效的指令口令！"
        
        # 步骤2：匹配口令，获取程序路径
        exe_path = self.storage.get_exe_path_by_command(ai_command.strip())
        if not exe_path:
            return f"错误：未找到口令「{ai_command}」对应的程序配置！"
        
        # 步骤3：前置校验（路径有效性+是否已运行）
        if not os.path.exists(exe_path):
            return f"错误：程序路径「{exe_path}」不存在，请检查配置！"
        if self._is_program_running(exe_path):
            exe_name = os.path.basename(exe_path)
            return f"提示：「{exe_name}」已经在运行中，无需重复启动！"
        
        # 步骤4：启动程序
        try:
            # Win11下无控制台启动exe（避免弹出cmd窗口）
            subprocess.Popen(
                exe_path,
                creationflags=self._win_no_console_flag
            )
            exe_name = os.path.basename(exe_path)
            return f"成功：已启动「{exe_name}」！"
        except PermissionError:
            return "错误：启动失败，无权限运行该程序，请以管理员身份运行！"
        except Exception as e:
            # 捕获所有未知异常，保证demo不崩溃
            return f"错误：启动失败，原因：{str(e)}"

# ====================== 测试用例（快速验证demo） ======================
if __name__ == "__main__":
    # 初始化技能模块
    skill = SkillModule()

    # 1. 模拟AI返回的口令，执行打开程序技能（demo核心流程）
    ai_returned_command = "endfiled_launcher"  # 模拟LLM返回的口令
    result = skill.open_exe_program(ai_returned_command)
    print(result)

    # 2. 测试无效口令场景
    result_invalid = skill.open_exe_program("invalid_command")
    print(result_invalid)