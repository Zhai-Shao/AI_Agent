import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

# 配置文件路径（可抽离到配置文件，新手直接写死更易理解）
CONFIG_FILE = "program_commands.json"

class StorageModule:
    def __init__(self):
        """初始化储存模块，确保配置文件存在"""
        self._ensure_config_file()

    def _ensure_config_file(self):
        """确保配置文件存在，不存在则创建空JSON"""
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"配置文件 {CONFIG_FILE} 已创建")

    def _load_config(self) -> Dict[str, Any]:
        """加载JSON配置文件，返回字典"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 配置文件损坏时重置为空字典
            print("配置文件格式错误，已重置为空")
            self._reset_config()
            return {}

    def _reset_config(self):
        """重置配置文件为空"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    def add_program(self, command: str, name: str, exe_path: str) -> bool:
        """
        添加程序配置（核心：校验口令唯一、路径有效）
        :param command: 唯一口令（如genshin）
        :param name: 程序名称（如原神）
        :param exe_path: exe绝对路径
        :return: 是否添加成功
        """
        # 1. 校验口令非空且唯一
        if not command or not command.strip():
            print("错误：口令不能为空！")
            return False
        
        config = self._load_config()
        if command in config:
            print(f"错误：口令「{command}」已存在，无法重复添加！")
            return False
        
        # 2. 校验exe路径有效性
        exe_path = Path(exe_path).resolve()  # 解析绝对路径（处理相对路径）
        if not exe_path.exists() or not exe_path.suffix == ".exe":
            print(f"错误：路径「{exe_path}」不是有效的exe文件！")
            return False
        
        # 3. 写入配置
        config[command] = {
            "name": name,
            "exe_path": str(exe_path),  # 转字符串存储，避免JSON序列化问题
            "command": command
        }
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"成功添加程序：{name}（口令：{command}）")
        return True

    def get_exe_path_by_command(self, command: str) -> Optional[str]:
        """
        根据唯一口令匹配并返回exe绝对路径（核心方法）
        :param command: LLM返回的唯一口令（如genshin）
        :return: 对应路径，无匹配则返回None
        """
        if not command:
            return None
        
        config = self._load_config()
        program_info = config.get(command.strip())
        if program_info:
            return program_info["exe_path"]
        return None

    def get_all_programs(self) -> Dict[str, Any]:
        """获取所有程序配置（用于调试/管理）"""
        return self._load_config()

# ====================== 测试用例（新手可直接运行验证） ======================
if __name__ == "__main__":
    # 初始化储存模块
    storage = StorageModule()

    # 1. 添加终末地配置（替换为你的实际路径）
    storage.add_program(
        command="endfiled",
        name="终末地",
        exe_path=r"D:\Endfield\Hypergryph Launcher\games\Endfield Game\Endfield.exe"
    )

    # 2. 尝试添加重复口令（验证唯一性）
    storage.add_program(
        command="endfiled",
        name="终末地",
        exe_path=r"D:\Endfield\Hypergryph Launcher\games\Endfield Game\Endfield.exe"
    )

    # 3. 加入启动器
    storage.add_program(
        command="wechat",
        name="微信",
        exe_path=r"D:\Weixin\Weixin.exe"
    )


    # 3. 根据口令匹配路径（模拟LLM返回后的逻辑）
    command_from_llm = "genshin"
    exe_path = storage.get_exe_path_by_command(command_from_llm)
    print(f"\n口令「{command_from_llm}」匹配到路径：{exe_path}")

    command_from_llm = "endfiled"
    exe_path = storage.get_exe_path_by_command(command_from_llm)
    print(f"\n口令「{command_from_llm}」匹配到路径：{exe_path}")

    # 4. 查看所有配置
    print("\n所有程序配置：")
    for cmd, info in storage.get_all_programs().items():
        print(f"- 口令：{cmd} | 名称：{info['name']} | 路径：{info['exe_path']}")