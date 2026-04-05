#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化 - 从记忆数据库构建并生成可视化图表

功能：
1. 从 memory.db 读取实体和关系
2. 生成 Mermaid 图表
3. 保存为 HTML 文件（可交互查看）
4. 支持多种可视化模式

版本：v1.0
日期：2026-03-31
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knowledge_graph.core.graph_engine import KnowledgeGraph

# 配置
WORKSPACE_DIR = Path("./workspace")
MEMORY_DB = "~/.knowledge-graph/data/memory.db"
OUTPUT_DIR = Path("./output")


def build_knowledge_graph():
    """从记忆数据库构建知识图谱"""
    print("\n" + "=" * 60)
    print("🕸️ 构建知识图谱")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(WORKSPACE_DIR / "knowledge-graph" / "knowledge-graph"))
        from core.graph_engine import KnowledgeGraphBuilder, Entity, Relation, KnowledgeGraph
        
        # 创建图谱构建器
        builder = KnowledgeGraphBuilder(MEMORY_DB)
        
        # 构建图谱
        print("\n📊 从记忆数据库提取实体和关系...")
        graph = builder.build_graph(limit=50)  # 限制 50 个实体
        
        print(f"✅ 提取到 {len(graph.entities)} 个实体")
        print(f"✅ 提取到 {len(graph.relations)} 个关系")
        
        return graph
    
    except Exception as e:
        print(f"❌ 构建失败：{e}")
        print("📝 尝试简化模式...")
        
        # 简化模式：直接从数据库读取
        import sqlite3
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        
        # 读取实体（记忆）
        cursor.execute("""
            SELECT id, content, tags, importance, category 
            FROM facts 
            ORDER BY importance DESC 
            LIMIT 30
        """)
        
        entities = []
        for row in cursor.fetchall():
            entities.append({
                'id': f"f_{row[0]}",
                'name': row[1][:50] + "..." if len(row[1]) > 50 else row[1],
                'type': row[4] or 'general',
                'importance': row[3]
            })
        
        # 从标签创建关系
        relations = []
        tag_to_entities = {}
        
        for entity in entities:
            if entity['name']:
                tags = entity.get('tags', '').split(',') if entity.get('tags') else []
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        if tag not in tag_to_entities:
                            tag_to_entities[tag] = []
                        tag_to_entities[tag].append(entity['id'])
        
        # 创建标签节点和关系
        tag_entities = []
        for tag, entity_ids in tag_to_entities.items():
            if len(entity_ids) > 1:  # 只连接有多个实体的标签
                tag_id = f"tag_{tag}"
                tag_entities.append({
                    'id': tag_id,
                    'name': f"🏷️ {tag}",
                    'type': 'tag'
                })
                
                for entity_id in entity_ids:
                    relations.append({
                        'from': entity_id,
                        'to': tag_id,
                        'type': 'tagged_with'
                    })
        
        conn.close()
        
        # 创建图谱对象
        from core.graph_engine import Entity, Relation, KnowledgeGraph
        
        graph = KnowledgeGraph(
            entities=[
                Entity(
                    id=e['id'],
                    name=e['name'],
                    entity_type=e['type'],
                    importance=e.get('importance', 0.5)
                ) for e in entities + tag_entities
            ],
            relations=[
                Relation(
                    id=i,
                    from_entity=r['from'],
                    relation_type=r['type'],
                    to_entity=r['to']
                ) for i, r in enumerate(relations)
            ],
            query="memory_db_visualization"
        )
        
        print(f"✅ 简化模式：{len(graph.entities)} 个实体，{len(graph.relations)} 个关系")
        return graph


def generate_mermaid_html(graph, output_path: Path):
    """生成可交互的 Mermaid HTML"""
    print("\n" + "=" * 60)
    print("🎨 生成可视化图表")
    print("=" * 60)
    
    # 生成 Mermaid 代码
    mermaid_code = graph.to_mermaid(direction="LR")
    
    # 创建 HTML 模板
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱可视化 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .mermaid {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            overflow: auto;
            max-height: 70vh;
        }}
        .controls {{
            text-align: center;
            margin: 20px 0;
        }}
        button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #5568d3;
        }}
        .code-section {{
            margin-top: 30px;
        }}
        textarea {{
            width: 100%;
            height: 200px;
            font-family: 'Courier New', monospace;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            resize: vertical;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🕸️ 知识图谱可视化</h1>
        <p class="subtitle">从记忆数据库构建 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(graph.entities)}</div>
                <div class="stat-label">实体数量</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(graph.relations)}</div>
                <div class="stat-label">关系数量</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{datetime.now().strftime('%H:%M')}</div>
                <div class="stat-label">生成时间</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="changeDirection('LR')">← 左到右 →</button>
            <button onclick="changeDirection('TD')">↑ 上到下 ↓</button>
            <button onclick="changeDirection('RL')">→ 右到左 ←</button>
            <button onclick="toggleCode()">显示/隐藏 Mermaid 代码</button>
        </div>
        
        <div class="mermaid" id="graph">
{mermaid_code}
        </div>
        
        <div class="code-section" id="codeSection" style="display: none;">
            <h3>📝 Mermaid 代码</h3>
            <textarea id="mermaidCode">{mermaid_code.replace('"', '&quot;')}</textarea>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
        
        function changeDirection(direction) {{
            const graphDiv = document.getElementById('graph');
            const code = document.getElementById('mermaidCode').value;
            const newCode = code.replace(/graph (LR|TD|RL)/, `graph ${{direction}}`);
            graphDiv.innerHTML = newCode;
            document.getElementById('mermaidCode').value = newCode;
            
            // 重新渲染
            mermaid.init(undefined, graphDiv);
        }}
        
        function toggleCode() {{
            const codeSection = document.getElementById('codeSection');
            codeSection.style.display = codeSection.style.display === 'none' ? 'block' : 'none';
        }}
    </script>
</body>
</html>
"""
    
    # 保存 HTML
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 已保存到：{output_file}")
    print(f"\n🌐 在浏览器中打开查看可交互图表")
    
    return output_file


def print_graph_summary(graph):
    """打印图谱摘要"""
    print("\n" + "=" * 60)
    print("📊 知识图谱摘要")
    print("=" * 60)
    
    # 按类型统计实体
    type_count = {}
    for entity in graph.entities:
        entity_type = entity.entity_type
        type_count[entity_type] = type_count.get(entity_type, 0) + 1
    
    print("\n实体类型分布:")
    for type_name, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {type_name}: {count} 个")
    
    # 按类型统计关系
    relation_count = {}
    for relation in graph.relations:
        rel_type = relation.relation_type
        relation_count[rel_type] = relation_count.get(rel_type, 0) + 1
    
    print("\n关系类型分布:")
    for rel_type, count in sorted(relation_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {rel_type}: {count} 个")
    
    # 显示前 5 个重要实体
    print("\nTop 5 重要实体:")
    sorted_entities = sorted(graph.entities, key=lambda x: x.importance, reverse=True)[:5]
    for i, entity in enumerate(sorted_entities, 1):
        print(f"  {i}. [{entity.importance:.2f}] {entity.name}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🕸️ 知识图谱可视化系统")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库：{MEMORY_DB}")
    print("=" * 60)
    
    # 1. 构建图谱
    graph = build_knowledge_graph()
    
    # 2. 打印摘要
    print_graph_summary(graph)
    
    # 3. 生成可视化
    output_file = generate_mermaid_html(graph, OUTPUT_DIR)
    
    # 4. 完成
    print("\n" + "=" * 60)
    print("✅ 可视化完成！")
    print("=" * 60)
    print(f"\n📁 文件位置：{output_file}")
    print(f"\n🎯 下一步：")
    print(f"  1. 在浏览器中打开 HTML 文件")
    print(f"  2. 查看可交互的知识图谱")
    print(f"  3. 切换不同方向查看")
    print(f"  4. 复制 Mermaid 代码用于文档")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
