#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化 v2 - 力导向图展示

使用 ECharts 实现交互式力导向网络图
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
from pathlib import Path
from datetime import datetime
import json

# 配置
MEMORY_DB = "~/.knowledge-graph/data/memory.db"
OUTPUT_DIR = Path("./output")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🕸️ 知识图谱可视化 - 力导向图")
    print("=" * 60)
    
    # 连接数据库
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    # 读取记忆
    cursor.execute("""
        SELECT id, content, category, importance 
        FROM facts 
        WHERE importance >= 0.7
        ORDER BY importance DESC
        LIMIT 50
    """)
    
    memories = []
    for row in cursor.fetchall():
        memories.append({
            'id': row[0],
            'content': row[1],
            'category': row[2] or 'general',
            'importance': row[3]
        })
    
    conn.close()
    
    print(f"📊 读取到 {len(memories)} 条高价值记忆")
    
    # 按类别分组
    categories = {}
    for mem in memories:
        cat = mem['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(mem)
    
    print(f"📁 分为 {len(categories)} 个类别")
    
    # 生成节点和边
    nodes = []
    links = []
    
    # 中心节点
    nodes.append({
        'id': 'center',
        'name': '🧠 记忆核心',
        'symbolSize': 100,
        'category': -1,
        'value': '核心'
    })
    
    # 类别节点
    category_colors = [
        '#006064', '#00838F', '#0097A7', '#00ACC1', '#26C6DA',
        '#4DD0E1', '#80DEEA', '#B2EBF2', '#004D40', '#00695C'
    ]
    
    for i, (cat, mems) in enumerate(categories.items()):
        cat_id = f'cat_{i}'
        nodes.append({
            'id': cat_id,
            'name': f'{cat} ({len(mems)})',
            'symbolSize': 60,
            'category': i,
            'value': '类别'
        })
        
        # 连接到中心
        links.append({
            'source': 'center',
            'target': cat_id,
            'value': '包含'
        })
        
        # 记忆节点（每个类别最多 5 个）
        for j, mem in enumerate(mems[:5]):
            mem_id = f'mem_{mem["id"]}'
            content_short = mem['content'][:30] + '...' if len(mem['content']) > 30 else mem['content']
            
            nodes.append({
                'id': mem_id,
                'name': content_short,
                'symbolSize': 30 + mem['importance'] * 20,
                'category': i,
                'value': f'重要性：{mem["importance"]:.2f}'
            })
            
            # 连接到类别
            links.append({
                'source': cat_id,
                'target': mem_id,
                'value': '属于'
            })
    
    print(f"🎯 生成 {len(nodes)} 个节点，{len(links)} 条边")
    
    # 生成 HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱 - 力导向图</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #006064 0%, #00838F 50%, #0097A7 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #006064;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #E0F7FA, #B2EBF2);
            border-radius: 15px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #00838F;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        #chart {{
            width: 100%;
            height: 700px;
            border-radius: 15px;
            background: linear-gradient(135deg, #FAFAFA, #F5F5F5);
        }}
        .controls {{
            text-align: center;
            margin: 20px 0;
        }}
        button {{
            background: linear-gradient(135deg, #00838F, #0097A7);
            color: white;
            border: none;
            padding: 12px 25px;
            margin: 5px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,131,143,0.4);
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 20px;
            gap: 15px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            padding: 8px 15px;
            background: #F5F5F5;
            border-radius: 20px;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕸️ 知识图谱 - 力导向网络图</h1>
            <p style="color: #666;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(nodes)}</div>
                <div class="stat-label">节点数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(links)}</div>
                <div class="stat-label">连接数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(categories)}</div>
                <div class="stat-label">类别数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(memories)}</div>
                <div class="stat-label">记忆总数</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="setLayout('force')">力导向布局</button>
            <button onclick="setLayout('circular')">环形布局</button>
            <button onclick="setLayout('none')">自由布局</button>
            <button onclick="toggleLabels()">切换标签</button>
            <button onclick="resetZoom()">重置视图</button>
        </div>
        
        <div id="chart"></div>
        
        <div class="legend" id="legend"></div>
    </div>
    
    <script>
        var chart = echarts.init(document.getElementById('chart'));
        
        var data = {{
            nodes: {json.dumps(nodes, ensure_ascii=False)},
            links: {json.dumps(links, ensure_ascii=False)}
        }};
        
        var categories = [
            {{'name': '{list(categories.keys())[i] if i < len(categories) else ''}'}} for i in range({len(categories)})
        ];
        
        var option = {{
            tooltip: {{
                show: true,
                formatter: function(params) {{
                    if (params.dataType === 'node') {{
                        return `<b>${{params.data.name}}</b><br/>大小：${{params.data.symbolSize}}<br/>${{params.data.value || ''}}`;
                    }}
                    return `${{params.data.source}} → ${{params.data.target}}`;
                }}
            }},
            legend: [{{
                data: categories.map(c => c.name),
                bottom: 10
            }}],
            series: [{{
                type: 'graph',
                layout: 'force',
                data: data.nodes,
                links: data.links,
                categories: categories,
                roam: true,
                label: {{
                    show: true,
                    position: 'right',
                    formatter: '{{b}}',
                    fontSize: 11
                }},
                force: {{
                    repulsion: 300,
                    edgeLength: [50, 150],
                    gravity: 0.1
                }},
                lineStyle: {{
                    color: 'source',
                    curveness: 0.3,
                    width: 2
                }},
                emphasis: {{
                    focus: 'adjacency',
                    lineStyle: {{
                        width: 5
                    }}
                }}
            }}]
        }};
        
        chart.setOption(option);
        
        // 生成图例
        var legendHtml = '';
        var colors = {json.dumps(category_colors)};
        var categoryNames = {json.dumps(list(categories.keys()))};
        categoryNames.forEach((name, i) => {{
            legendHtml += `<div class="legend-item">
                <div class="legend-color" style="background: ${{colors[i % colors.length]}}"></div>
                <span>${{name}}</span>
            </div>`;
        }});
        document.getElementById('legend').innerHTML = legendHtml;
        
        // 控制函数
        function setLayout(layout) {{
            option.series[0].layout = layout;
            chart.setOption(option);
        }}
        
        function toggleLabels() {{
            option.series[0].label.show = !option.series[0].label.show;
            chart.setOption(option);
        }}
        
        function resetZoom() {{
            chart.dispatchAction({{
                type: 'restore'
            }});
        }}
        
        // 窗口大小变化时重新调整
        window.addEventListener('resize', function() {{
            chart.resize();
        }});
    </script>
</body>
</html>
"""
    
    # 保存
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"knowledge_graph_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 已保存到：{output_file}")
    print(f"\n🌐 在浏览器中打开查看交互式力导向图")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
