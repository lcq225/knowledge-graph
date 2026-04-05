# -*- coding: utf-8 -*-
"""
Knowledge Graph - 知识图谱技能

从 MemoryCoreClaw 记忆系统中提取实体和关系，构建可视化的知识图谱

融合 Ontology 本体论：
- 类层次结构
- 属性继承  
- 关系推理
- 本体查询

主要功能：
- 实体识别和提取
- 关系提取和构建
- 本体推理增强
- 知识图谱查询
- Mermaid 可视化
- 文本描述输出

使用示例：
    from knowledge_graph import create_graph_engine
    
    kg = create_graph_engine()
    result = kg.semantic_query("老K 使用什么技术？")
    print(kg.to_mermaid())
"""
from .core.graph_engine import (
    KnowledgeGraphEngine,
    KnowledgeGraph,
    Entity,
    Relation,
    create_graph_engine
)
from .core.security import (
    get_security_manager,
    check_channel_permission,
    sanitize_output,
    PermissionError,
    SecurityManager
)
from .core.ontology import (
    OntologyManager,
    OntologyClass,
    OntologyProperty,
    get_ontology_manager,
    create_ontology_manager
)

__all__ = [
    # 图谱引擎
    'KnowledgeGraphEngine',
    'KnowledgeGraph',
    'Entity',
    'Relation',
    'create_graph_engine',
    
    # 安全模块
    'get_security_manager',
    'check_channel_permission',
    'sanitize_output',
    'PermissionError',
    'SecurityManager',
    
    # 本体模块
    'OntologyManager',
    'OntologyClass',
    'OntologyProperty',
    'get_ontology_manager',
    'create_ontology_manager',
]

# 版本
__version__ = '1.1.0'  # 升级到 1.1.0（本体论增强）