# -*- coding: utf-8 -*-
"""
Knowledge Graph Core - 知识图谱核心模块
"""
from .graph_engine import (
    KnowledgeGraphEngine,
    KnowledgeGraph,
    Entity,
    Relation,
    create_graph_engine
)
from .security import (
    get_security_manager,
    check_channel_permission,
    sanitize_output,
    PermissionError
)
from .ontology import (
    OntologyManager,
    OntologyClass,
    OntologyProperty,
    get_ontology_manager,
    create_ontology_manager,
    RelationType
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
    
    # 本体模块
    'OntologyManager',
    'OntologyClass',
    'OntologyProperty',
    'get_ontology_manager',
    'create_ontology_manager',
    'RelationType',
]

# 版本信息
__version__ = '1.1.0'