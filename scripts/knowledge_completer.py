# -*- coding: utf-8 -*-
"""
知识图谱自动补全器 - 简化版
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import sqlite3
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime

MEMORY_DB = "~/.knowledge-graph/data/memory.db"


class KnowledgeCompleter:
    """知识图谱自动补全器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_relations(self) -> List[Tuple[str, str, str]]:
        """获取所有关系 (from, relation, to)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        relations = []
        cursor.execute('SELECT from_entity, relation_type, to_entity FROM relations')
        
        for row in cursor.fetchall():
            relations.append((row['from_entity'], row['relation_type'], row['to_entity']))
        
        conn.close()
        return relations
    
    def get_entity_outgoing(self, entity: str) -> Dict[str, List[str]]:
        """获取实体的出向关系"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        result = defaultdict(list)
        cursor.execute('''
            SELECT relation_type, to_entity 
            FROM relations 
            WHERE from_entity = ?
        ''', (entity,))
        
        for row in cursor.fetchall():
            result[row['relation_type']].append(row['to_entity'])
        
        conn.close()
        return dict(result)
    
    def infer(self) -> List[Dict]:
        """执行推理"""
        all_rels = self.get_all_relations()
        
        # 构建实体关系索引
        entity_rels = defaultdict(lambda: defaultdict(list))
        for from_e, rel, to_e in all_rels:
            entity_rels[from_e][rel].append(to_e)
        
        results = []
        
        # 规则：works_at -> colleague_of
        # 如果 A works_at X, B works_at X，则 A 和 B 是同事
        works_at_groups = defaultdict(list)
        for from_e, rel, to_e in all_rels:
            if rel == "works_at":
                works_at_groups[to_e].append(from_e)
        
        for org, members in works_at_groups.items():
            for i, a in enumerate(members):
                for b in members[i+1:]:
                    # 检查是否已存在同事关系
                    existing = [(r[1], r[2]) for r in all_rels if r[0] == a]
                    if not any(rel == "colleague_of" and target == b for rel, target in existing):
                        results.append({
                            "from": a,
                            "relation": "colleague_of",
                            "to": b,
                            "confidence": 0.8,
                            "reason": f"同在 {org} 工作"
                        })
        
        # 规则：related_to 传递
        # 如果 A related_to B, B related_to C，则 A related_to C (置信度降低)
        for from_a, rel_ab, to_b in all_rels:
            if rel_ab == "related_to":
                # 找 B 的关系
                if to_b in entity_rels:
                    for rel_bc, to_c in entity_rels[to_b].items():
                        if rel_bc == "related_to":
                            for c in to_c:
                                # 检查是否已存在
                                existing = [(r[1], r[2]) for r in all_rels if r[0] == from_a]
                                if not any(rel == "related_to" and target == c for rel, target in existing):
                                    if from_a != c:  # 排除自己
                                        results.append({
                                            "from": from_a,
                                            "relation": "related_to",
                                            "to": c,
                                            "confidence": 0.5,
                                            "reason": f"传递关联: {from_a}->{to_b}->{c}"
                                        })
        
        # 规则：leads -> works_at
        # 如果 A leads X，则 A works_at X
        for from_e, rel, to_e in all_rels:
            if rel == "leads":
                existing = [(r[1], r[2]) for r in all_rels if r[0] == from_e]
                if not any(rel == "works_at" and target == to_e for rel, target in existing):
                    results.append({
                        "from": from_e,
                        "relation": "works_at",
                        "to": to_e,
                        "confidence": 0.9,
                        "reason": f"领导 {to_e}"
                    })
        
        # 去重
        seen = set()
        unique = []
        for r in results:
            key = (r['from'], r['relation'], r['to'])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        
        return unique
    
    def detect_conflicts(self) -> List[Dict]:
        """检测冲突"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        conflicts = []
        
        cursor.execute('''
            SELECT from_entity, to_entity, GROUP_CONCAT(relation_type) as rels
            FROM relations
            GROUP BY from_entity, to_entity
            HAVING COUNT(*) > 1
        ''')
        
        for row in cursor.fetchall():
            rels = row['rels'].split(',')
            if any('not' in r.lower() for r in rels) and any('not' not in r.lower() for r in rels):
                conflicts.append({
                    "from": row['from_entity'],
                    "to": row['to_entity'],
                    "relations": rels
                })
        
        conn.close()
        return conflicts
    
    def complete(self) -> Dict:
        """完整补全"""
        inferences = self.infer()
        conflicts = self.detect_conflicts()
        
        return {
            "completed_at": datetime.now().isoformat(),
            "inferences": inferences,
            "conflicts": conflicts,
            "total_inferences": len(inferences),
            "total_conflicts": len(conflicts)
        }
    
    def print_report(self):
        """打印报告"""
        results = self.complete()
        
        print("\n" + "=" * 60)
        print("🔮 知识图谱补全报告")
        print("=" * 60)
        
        print(f"\n📊 统计:")
        print(f"  推理关系数: {results['total_inferences']}")
        print(f"  冲突检测数: {results['total_conflicts']}")
        
        if results['inferences']:
            print(f"\n🔍 推理结果:")
            for i, inf in enumerate(results['inferences'][:15], 1):
                print(f"  {i}. {inf['from']} --[{inf['relation']}]--> {inf['to']}")
                print(f"     置信度: {inf['confidence']:.0%} | {inf['reason']}")
        
        if results['conflicts']:
            print(f"\n⚠️ 冲突:")
            for c in results['conflicts']:
                print(f"  {c['from']} vs {c['to']}: {c['relations']}")
        
        print("\n" + "=" * 60)
        return results


if __name__ == "__main__":
    completer = KnowledgeCompleter()
    completer.print_report()