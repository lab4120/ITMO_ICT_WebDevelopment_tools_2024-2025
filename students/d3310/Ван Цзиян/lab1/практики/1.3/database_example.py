from sqlmodel import SQLModel, create_engine, Session, select
from models import Skill, Warrior, SkillWarriorLink

# 创建数据库引擎
engine = create_engine("sqlite:///./test.db")

# 创建表（如果不存在）
SQLModel.metadata.create_all(engine)

def main():
    print("=== 数据库操作示例 ===")
    
    # 创建会话
    with Session(engine) as session:
        # 创建技能
        skill1 = Skill(name="剑术")
        skill2 = Skill(name="魔法")
        session.add(skill1)
        session.add(skill2)
        session.commit()
        
        # 创建战士
        warrior1 = Warrior(name="亚瑟")
        warrior2 = Warrior(name="梅林")
        session.add(warrior1)
        session.add(warrior2)
        session.commit()
        
        # 创建技能-战士关联
        link1 = SkillWarriorLink(skill_id=skill1.id, warrior_id=warrior1.id, level=5)
        link2 = SkillWarriorLink(skill_id=skill2.id, warrior_id=warrior2.id, level=8)
        session.add(link1)
        session.add(link2)
        session.commit()
        
        print("✅ 数据创建成功!")
        
        # 查询数据
        print("\n=== 查询结果 ===")
        
        # 查询所有技能
        skills = session.exec(select(Skill)).all()
        print("技能列表:")
        for skill in skills:
            print(f"  - {skill.name} (ID: {skill.id})")
        
        # 查询所有战士
        warriors = session.exec(select(Warrior)).all()
        print("\n战士列表:")
        for warrior in warriors:
            print(f"  - {warrior.name} (ID: {warrior.id})")
        
        # 查询技能-战士关联
        links = session.exec(select(SkillWarriorLink)).all()
        print("\n技能-战士关联:")
        for link in links:
            skill = session.get(Skill, link.skill_id)
            warrior = session.get(Warrior, link.warrior_id)
            print(f"  - {warrior.name} 掌握 {skill.name} (等级: {link.level})")

if __name__ == "__main__":
    main()
