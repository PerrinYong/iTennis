"""
NTRP 网球等级评估系统主程序

基于分层架构的网球等级评估系统。
采用 MVC 设计模式，代码结构清晰，便于维护和扩展。
"""

import sys
import pathlib

# 添加当前目录到路径，确保可以导入模块
current_dir = pathlib.Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app_controller import AppController


def main():
    """主程序入口"""
    try:
        # 确定配置文件目录
        config_dir = pathlib.Path(__file__).parent.parent / "config"
        
        # 初始化并运行应用控制器
        controller = AppController(config_dir)
        controller.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()