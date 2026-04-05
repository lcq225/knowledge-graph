#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ontology CLI - 本体操作命令行工具

用法：
    python ontology_cli.py create --type Person --props '{"name":"Alice"}'
    python ontology_cli.py query --type Task --where '{"status":"open"}'
    python ontology_cli.py relate --from proj_001 --rel has_task --to task_001
    python ontology_cli.py validate
    python ontology_cli.py validate --file data.json

版本：v2.0
日期：2026-03-29
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加技能目录到路径
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

try:
    from core.validator import OntologyValidator, ValidationResult
    from core.security import OntologySecurity, SecurityResult
except ImportError as e:
    print(f"❌ 导入失败：{e}")
    print("请确保在 knowledge-graph 目录下运行此脚本")
    sys.exit(1)

# Schema 路径
SCHEMA_PATH = SKILL_DIR / 'schema' / 'ontology_schema.yaml'


def cmd_create(args):
    """创建实体"""
    print("=" * 60)
    print("创建实体")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    # 解析属性
    try:
        props = json.loads(args.props)
    except json.JSONDecodeError as e:
        print(f"❌ 属性 JSON 格式错误：{e}")
        sys.exit(1)
    
    # 验证
    print(f"\n📋 验证实体：{args.type}")
    print(f"   属性：{json.dumps(props, ensure_ascii=False, indent=2)}")
    
    result = validator.validate_entity(args.type, props)
    print(result)
    
    if not result.valid:
        print("\n❌ 验证失败，无法创建实体")
        sys.exit(1)
    
    # 输出创建命令（实际创建需要集成到 graph_engine）
    print("\n✅ 验证通过，实体可以创建")
    print("   提示：实际创建需要集成到 KnowledgeGraphEngine")
    print(f"   示例：kg.create_entity('{args.type}', {props})")


def cmd_query(args):
    """查询实体"""
    print("=" * 60)
    print("查询实体")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    # 验证类型
    if args.type not in validator.schema['types']:
        print(f"❌ 未知实体类型：{args.type}")
        print(f"   可用类型：{', '.join(validator.schema['types'].keys())}")
        sys.exit(1)
    
    # 解析过滤条件
    where = {}
    if args.where:
        try:
            where = json.loads(args.where)
        except json.JSONDecodeError as e:
            print(f"❌ 过滤条件 JSON 格式错误：{e}")
            sys.exit(1)
    
    print(f"\n📊 查询条件:")
    print(f"   类型：{args.type}")
    print(f"   过滤：{json.dumps(where, ensure_ascii=False, indent=2) if where else '无'}")
    
    # 输出查询命令（实际查询需要集成到 graph_engine）
    print("\nℹ️ 提示：实际查询需要集成到 KnowledgeGraphEngine")
    print(f"   示例：kg.query_entities('{args.type}', {where})")


def cmd_relate(args):
    """创建关系"""
    print("=" * 60)
    print("创建关系")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    print(f"\n📋 验证关系:")
    print(f"   源：{args.from_id} (类型：{args.from_type})")
    print(f"   关系：{args.rel}")
    print(f"   目标：{args.to_id} (类型：{args.to_type})")
    
    # 验证关系
    result = validator.validate_relation(
        args.from_type,
        args.rel,
        args.to_type,
        args.from_id,
        args.to_id
    )
    print(result)
    
    if not result.valid:
        print("\n❌ 关系验证失败，无法创建")
        sys.exit(1)
    
    # 输出创建命令
    print("\n✅ 验证通过，关系可以创建")
    print("   提示：实际创建需要集成到 KnowledgeGraphEngine")
    print(f"   示例：kg.create_relation('{args.from_id}', '{args.rel}', '{args.to_id}')")


def cmd_validate(args):
    """验证数据"""
    print("=" * 60)
    print("验证数据")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    # 获取 Schema 信息
    info = validator.get_schema_info()
    print(f"\n📊 Schema 信息:")
    print(f"   版本：{info['version']}")
    print(f"   更新时间：{info['updated']}")
    print(f"   实体类型：{info['entity_types']}")
    print(f"   关系类型：{info['relation_types']}")
    print(f"   禁止属性：{info['forbidden_properties']}")
    print(f"   推理规则：{info['inference_rules']}")
    
    # 如果指定了文件，验证文件中的数据
    if args.file:
        print(f"\n📋 验证文件：{args.file}")
        
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ 文件不存在：{args.file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式错误：{e}")
            sys.exit(1)
        
        entities = data.get('entities', [])
        relations = data.get('relations', [])
        
        print(f"   实体数：{len(entities)}")
        print(f"   关系数：{len(relations)}")
        
        # 批量验证
        result = validator.validate_batch(entities, relations)
        print(result)
        
        if not result.valid:
            print("\n❌ 数据验证失败")
            sys.exit(1)
        else:
            print("\n✅ 数据验证通过")
    else:
        # 验证 Schema 本身
        print("\n✅ Schema 验证通过")
    
    # 安全检查
    print("\n" + "=" * 60)
    print("安全检查")
    print("=" * 60)
    
    security = OntologySecurity()
    report = security.get_security_report()
    print(f"允许用户：{report['allowed_users']}")
    print(f"允许渠道：{report['allowed_channels']}")
    print(f"禁止属性数：{report['forbidden_properties_count']}")


def cmd_info(args):
    """显示信息"""
    print("=" * 60)
    print("Ontology 信息")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    # 显示实体类型
    if args.type:
        if args.type not in validator.schema['types']:
            print(f"❌ 未知实体类型：{args.type}")
            sys.exit(1)
        
        type_def = validator.schema['types'][args.type]
        print(f"\n📋 实体类型：{args.type}")
        print(f"   描述：{type_def.get('description', '无')}")
        print(f"   分类：{type_def.get('category', '无')}")
        print(f"   必填字段：{type_def.get('required', [])}")
        print(f"   可选字段：{type_def.get('optional', [])}")
        
        if 'enums' in type_def:
            print(f"   枚举值:")
            for field, values in type_def['enums'].items():
                print(f"     {field}: {values}")
        
        if 'validations' in type_def:
            print(f"   验证规则:")
            for rule in type_def['validations']:
                print(f"     - {rule}")
    else:
        # 显示所有类型
        info = validator.get_schema_info()
        print(f"\n📊 Schema 概览:")
        print(f"   版本：{info['version']}")
        print(f"   实体类型：{info['entity_types']}")
        print(f"   关系类型：{info['relation_types']}")
        
        print(f"\n📋 实体类型列表:")
        for type_name in sorted(validator.schema['types'].keys()):
            type_def = validator.schema['types'][type_name]
            description = type_def.get('description', '无')
            print(f"   - {type_name}: {description}")
        
        print(f"\n📋 关系类型列表:")
        for rel_name in sorted(validator.schema['relations'].keys()):
            rel_def = validator.schema['relations'][rel_name]
            description = rel_def.get('description', '无')
            print(f"   - {rel_name}: {description}")


def cmd_validate_file(args):
    """验证 JSON 文件"""
    print("=" * 60)
    print("验证 JSON 文件")
    print("=" * 60)
    
    # 加载验证器
    try:
        validator = OntologyValidator(str(SCHEMA_PATH))
    except Exception as e:
        print(f"❌ 加载 Schema 失败：{e}")
        sys.exit(1)
    
    # 检查文件
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        sys.exit(1)
    
    print(f"\n📋 验证文件：{file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误：{e}")
        sys.exit(1)
    
    entities = data.get('entities', [])
    relations = data.get('relations', [])
    
    print(f"   实体数：{len(entities)}")
    print(f"   关系数：{len(relations)}")
    
    # 批量验证
    result = validator.validate_batch(entities, relations)
    print(result)
    
    if not result.valid:
        print("\n❌ 数据验证失败")
        sys.exit(1)
    else:
        print("\n✅ 数据验证通过")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Ontology CLI - 本体操作命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s create --type Person --props '{"name":"Alice"}'
  %(prog)s query --type Task --where '{"status":"open"}'
  %(prog)s relate --from proj_001 --rel has_task --to task_001 --from-type Project --to-type Task
  %(prog)s validate
  %(prog)s validate --file data.json
  %(prog)s info
  %(prog)s info --type Task
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建实体（验证模式）')
    create_parser.add_argument('--type', required=True, help='实体类型')
    create_parser.add_argument('--props', required=True, help='属性（JSON 格式）')
    create_parser.set_defaults(func=cmd_create)
    
    # query 命令
    query_parser = subparsers.add_parser('query', help='查询实体')
    query_parser.add_argument('--type', required=True, help='实体类型')
    query_parser.add_argument('--where', help='过滤条件（JSON 格式）')
    query_parser.set_defaults(func=cmd_query)
    
    # relate 命令
    relate_parser = subparsers.add_parser('relate', help='创建关系')
    relate_parser.add_argument('--from', dest='from_id', required=True, help='源实体 ID')
    relate_parser.add_argument('--rel', required=True, help='关系类型')
    relate_parser.add_argument('--to', dest='to_id', required=True, help='目标实体 ID')
    relate_parser.add_argument('--from-type', dest='from_type', required=True, help='源实体类型')
    relate_parser.add_argument('--to-type', dest='to_type', required=True, help='目标实体类型')
    relate_parser.set_defaults(func=cmd_relate)
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证数据')
    validate_parser.add_argument('--file', help='JSON 数据文件')
    validate_parser.set_defaults(func=cmd_validate)
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='显示信息')
    info_parser.add_argument('--type', help='实体类型（可选）')
    info_parser.set_defaults(func=cmd_info)
    
    # validate-file 命令（validate 的别名）
    validate_file_parser = subparsers.add_parser('validate-file', help='验证 JSON 文件')
    validate_file_parser.add_argument('--file', required=True, help='JSON 文件路径')
    validate_file_parser.set_defaults(func=cmd_validate_file)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
