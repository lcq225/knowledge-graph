#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化 - 简单版本

从记忆数据库构建知识图谱并生成 Mermaid 图表
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
from pathlib import Path
from datetime import datetime

# 配置
MEMORY_DB = "~/.knowledge-graph/data/memory.db"
OUTPUT_DIR = Path("./output")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🕸️ 知识图谱可视化")
    print("=" * 60)
    print(f"数据库：{MEMORY_DB}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 连接数据库
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    # 读取记忆（按重要性排序）
    cursor.execute("""
        SELECT id, content, tags, importance, category 
        FROM facts 
        ORDER BY importance DESC 
        LIMIT 30
    """)
    
    memories = []
    for row in cursor.fetchall():
        memories.append({
            'id': f"f_{row[0]}",
            'content': row[1],
            'tags': row[2] or '',
            'importance': row[3],
            'category': row[4] or 'general'
        })
    
    conn.close()
    
    print(f"\n📊 读取到 {len(memories)} 条记忆")
    
    # 生成 Mermaid 图表
    print("\n🎨 生成 Mermaid 图表...")
    
    mermaid_lines = ["graph LR"]
    
    # 添加中心节点
    mermaid_lines.append('    root[("🧠 记忆数据库")]')
    
    # 按类别分组
    category_nodes = {}
    for mem in memories:
        category = mem['category']
        if category not in category_nodes:
            category_nodes[category] = []
        category_nodes[category].append(mem)
    
    # 添加类别节点
    for category, mems in category_nodes.items():
        safe_cat = category.replace(' ', '_').replace('-', '_')
        emoji = {
            'identity': '👤',
            'preference': '⭐',
            'workflow': '📋',
            'milestone': '🎯',
            'lesson': '💡',
            'config': '⚙️',
            'rule': '📜',
            'mechanism': '🔧',
            'tools': '🛠️'
        }.get(category, '📌')
        
        mermaid_lines.append(f'    cat_{safe_cat}[{emoji} {category} ({len(mems)})]')
        mermaid_lines.append(f'    root --> cat_{safe_cat}')
        
        # 添加记忆节点（每个类别最多 3 个）
        for i, mem in enumerate(mems[:3]):
            safe_id = mem['id'].replace('-', '_')
            content_short = mem['content'][:30] + "..." if len(mem['content']) > 30 else mem['content']
            content_short = content_short.replace('"', "'").replace('\n', ' ')
            
            mermaid_lines.append(f'    {safe_id}["📝 {content_short}"]')
            mermaid_lines.append(f'    cat_{safe_cat} --> {safe_id}')
    
    mermaid_code = '\n'.join(mermaid_lines)
    
    print(f"✅ Mermaid 图表生成完成")
    print(f"   节点数：{len(mermaid_lines) - 1}")
    
    # 生成 HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱 - {datetime.now().strftime('%Y-%m-%d')}</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🕸️ 知识图谱可视化</h1>
        <p class="subtitle">记忆数据库 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(memories)}</div>
                <div class="stat-label">记忆总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(category_nodes)}</div>
                <div class="stat-label">类别数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(mermaid_lines) - 1}</div>
                <div class="stat-label">节点数</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="changeDirection('LR')">← 左到右 →</button>
            <button onclick="changeDirection('TD')">↑ 上到下 ↓</button>
            <button onclick="zoomIn()">🔍 放大</button>
            <button onclick="zoomOut()">🔎 缩小</button>
        </div>
        
        <div class="mermaid" id="graph">
{mermaid_code}
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
        
        let currentDirection = 'LR';
        let currentZoom = 1;
        
        function changeDirection(direction) {{
            const graphDiv = document.getElementById('graph');
            const mermaidCode = `{mermaid_code.replace('"', '&quot;')}`;
            const escapedCode = mermaidCode.replace(/\\n/g, '\\\\n');
            const newCode = escapedCode.replace(/graph (LR|TD|RL)/, `graph ${{direction}}`);
            graphDiv.innerHTML = newCode;
            currentDirection = direction;
            
            // 重新渲染
            mermaid.init(undefined, graphDiv);
        }}
        
        function zoomIn() {{
            currentZoom += 0.1;
            document.getElementById('graph').style.transform = `scale(${{currentZoom}})`;
        }}
        
        function zoomOut() {{
            currentZoom = Math.max(0.5, currentZoom - 0.1);
            document.getElementById('graph').style.transform = `scale(${{currentZoom}})`;
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
    
    print(f"\n✅ 已保存到：{output_file}")
    
    # 显示 Mermaid 代码
    print("\n" + "=" * 60)
    print("📝 Mermaid 代码（可直接用于文档）")
    print("=" * 60)
    print(mermaid_code)
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"\n🌐 在浏览器中打开查看可交互图表：")
    print(f"   {output_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
