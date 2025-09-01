#!/usr/bin/env python3
"""
项目运行脚本
演示如何使用这个数据库迁移和环境配置项目
"""

import os
import sys

def check_dependencies():
    """检查依赖包是否已安装"""
    print("=== 检查依赖包 ===")
    
    required_packages = ['alembic', 'sqlmodel', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - 已安装")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装\n")
    return True

def run_environment_example():
    """运行环境变量示例"""
    print("=== 环境变量配置示例 ===")
    try:
        import config_example
        print("✅ 环境变量配置测试完成\n")
    except Exception as e:
        print(f"❌ 环境变量配置测试失败: {e}\n")

def run_database_example():
    """运行数据库操作示例"""
    print("=== 数据库操作示例 ===")
    try:
        import database_example
        print("✅ 数据库操作测试完成\n")
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}\n")

def show_migration_commands():
    """显示迁移命令"""
    print("=== 数据库迁移命令 ===")
    print("以下是一些常用的 Alembic 命令:")
    print("  alembic current          # 查看当前迁移状态")
    print("  alembic history          # 查看迁移历史")
    print("  alembic upgrade head     # 应用所有迁移")
    print("  alembic downgrade -1     # 回滚一个迁移")
    print("  alembic revision --autogenerate -m \"描述\"  # 创建新迁移")
    print()

def main():
    """主函数"""
    print("🚀 项目运行脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 运行环境变量示例
    run_environment_example()
    
    # 运行数据库示例
    run_database_example()
    
    # 显示迁移命令
    show_migration_commands()
    
    print("🎉 项目运行完成!")
    print("\n📝 提示:")
    print("- 查看 SUMMARY.md 了解项目详情")
    print("- 使用 alembic 命令管理数据库迁移")
    print("- 修改 .env 文件配置环境变量")

if __name__ == "__main__":
    main()
