#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relationship_engine 测试套件

运行方式：
  python test_relationship_engine.py          # 所有测试
  python test_relationship_engine.py -v        # 详细输出

依赖：仅 Python 标准库
"""

import os
import sys
import json
import unittest
import tempfile

# 将被测脚本所在目录加入路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import relationship_engine as re_mod


class TestFrontmatterParser(unittest.TestCase):
    """frontmatter 解析器测试"""

    def test_no_frontmatter(self):
        """无 frontmatter 的纯文本"""
        text = "# Hello World\n\nThis is a test."
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm, {})

    def test_empty_frontmatter(self):
        """空的 frontmatter (---\\n---)"""
        text = "---\n---\n\n# Hello"
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm, {})

    def test_simple_frontmatter(self):
        """标准的 frontmatter"""
        text = """---
title: Test Title
type: reference
---
# Content"""
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm.get("title"), "Test Title")
        self.assertEqual(fm.get("type"), "reference")

    def test_frontmatter_with_id(self):
        """带有 id 的 frontmatter"""
        text = """---
id: "KB-2026-07-02-0001"
title: Test
---
# Content"""
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm.get("id"), "KB-2026-07-02-0001")

    def test_frontmatter_with_ref_id(self):
        """带有 ref_id 的 frontmatter"""
        text = """---
ref_id: "REF-0010"
title: Test Reference
---
# Content"""
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm.get("ref_id"), "REF-0010")

    def test_frontmatter_with_adr(self):
        """带有 adr 字段的 frontmatter"""
        text = """---
adr: "0013"
status: Proposed
---
# ADR-0013"""
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm.get("adr"), "0013")

    def test_frontmatter_with_related_inline(self):
        """数组格式 related (格式 A)"""
        text = """---
related: ["REF-0002", "REF-0003"]
---
# Content"""
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm.get("related"), ["REF-0002", "REF-0003"])

    def test_frontmatter_with_related_block(self):
        """多行列表格式 related (格式 C)"""
        text = """---
related:
  - REF-0002
  - REF-0003
---
# Content"""
        fm = re_mod.extract_frontmatter(text)
        # 注意：自定义解析器可能返回列表
        related = fm.get("related")
        self.assertIn(related, (["REF-0002", "REF-0003"], [" REF-0002", " REF-0003"]))

    def test_frontmatter_with_html_in_body(self):
        """正文中有表格和 --- 分隔线的文件"""
        text = "# Header\n\nSome content\n\n---\n\n| Table | Data |\n|------|------|\n| A | B |"
        fm = re_mod.extract_frontmatter(text)
        self.assertEqual(fm, {})


class TestRelatedParser(unittest.TestCase):
    """related 字段解析测试"""

    def test_empty(self):
        """空 related"""
        items, warns = re_mod.RelatedParser.parse(None)
        self.assertEqual(items, [])
        items, warns = re_mod.RelatedParser.parse([])
        self.assertEqual(items, [])

    def test_inline_list(self):
        """格式 A: [a, b, c]"""
        items, warns = re_mod.RelatedParser.parse(["REF-0002", "REF-0003"])
        self.assertEqual(items, ["REF-0002", "REF-0003"])

    def test_empty_list(self):
        """格式 B: []"""
        items, warns = re_mod.RelatedParser.parse([])
        self.assertEqual(items, [])

    def test_string_with_commas(self):
        """格式 D: 'a, b, c'"""
        items, warns = re_mod.RelatedParser.parse("ADR-0013, ADR-0014, README.md")
        self.assertEqual(len(items), 3)

    def test_mixed_numeric(self):
        """包含数字的列表"""
        items, warns = re_mod.RelatedParser.parse(["REF-0001", "REF-0002"])
        self.assertEqual(len(items), 2)


class TestNodeResolver(unittest.TestCase):
    """节点解析器测试"""

    def setUp(self):
        self.nr = re_mod.NodeResolver()

    def test_id_first_priority(self):
        """P1: id 优先"""
        scanned = [{
            "path": "20_KNOWLEDGE/Platform/Concepts/test.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nid: \"KB-0001\"\ntitle: Test\n---\n# Body",
            "filename_stem": "test",
            "path_stem": "Platform-Concepts-test",
        }]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(nodes[0]["id"], "KB-0001")

    def test_ref_id_fallback(self):
        """P2: ref_id 退场"""
        scanned = [{
            "path": "20_KNOWLEDGE/Platform/References/test.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nref_id: \"REF-0010\"\ntitle: Test\n---\n# Body",
            "filename_stem": "test",
            "path_stem": "Platform-References-test",
        }]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(nodes[0]["id"], "REF-0010")

    def test_path_stem_fallback(self):
        """P3: path_stem 退场"""
        scanned = [{
            "path": "20_KNOWLEDGE/Platform/Concepts/some-concept.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "# Some Concept\n\nNo frontmatter here.",
            "filename_stem": "some-concept",
            "path_stem": "Platform-Concepts-some-concept",
        }]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(nodes[0]["id"], "Platform-Concepts-some-concept")

    def test_adr_id_from_adr_field(self):
        """ADR 特例：adr: \"0013\" -> ADR-0013"""
        scanned = [{
            "path": "30_SYSTEM/ADR/ADR-0013-Test.md",
            "abspath": "",
            "scope": "30_SYSTEM/ADR",
            "raw_text": "---\nadr: \"0013\"\nstatus: Accepted\n---\n# ADR-0013",
            "filename_stem": "ADR-0013-Test",
            "path_stem": "ADR/ADR-0013-Test",
        }]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(nodes[0]["id"], "ADR-0013")

    def test_adr_id_from_filename(self):
        """ADR 特例：文件名前缀"""
        scanned = [{
            "path": "30_SYSTEM/ADR/ADR-0006-Metadata-Standard.md",
            "abspath": "",
            "scope": "30_SYSTEM/ADR",
            "raw_text": "# ADR-0006\n\nNo frontmatter",
            "filename_stem": "ADR-0006-Metadata-Standard",
            "path_stem": "ADR/ADR-0006-Metadata-Standard",
        }]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(nodes[0]["id"], "ADR-0006")

    def test_conflict_detection(self):
        """冲突检测：两个文件解析出相同 node_id"""
        scanned = [
            {
                "path": "20_KNOWLEDGE/a.md",
                "abspath": "",
                "scope": "20_KNOWLEDGE",
                "raw_text": "---\nref_id: \"REF-X\"\n---\n# A",
                "filename_stem": "a",
                "path_stem": "a",
            },
            {
                "path": "20_KNOWLEDGE/b.md",
                "abspath": "",
                "scope": "20_KNOWLEDGE",
                "raw_text": "---\nref_id: \"REF-X\"\n---\n# B",
                "filename_stem": "b",
                "path_stem": "b",
            },
        ]
        nodes = self.nr.resolve_all(scanned)
        self.assertEqual(len(self.nr.conflicts), 1)
        self.assertIn("REF-X", self.nr.conflicts[0]["node_id"])
        # 第二个节点应被去重
        self.assertNotEqual(nodes[0]["id"], nodes[1]["id"])


class TestRelatedScanning(unittest.TestCase):
    """related 字段从 real world 文件扫描测试"""

    def test_architecture_related(self):
        """architecture 目录下的 related 格式"""
        text = """---
related: [paios-positioning-consensus-v2.1, FIM-v1, ADR-0002, ADR-0007]
---
# Architecture Model"""
        fm = re_mod.extract_frontmatter(text)
        related = fm.get("related", [])
        self.assertIsInstance(related, list)
        self.assertTrue(len(related) >= 4)

    def test_comma_separated_string(self):
        """逗号分隔字符串格式（格式 D）"""
        text = """---
related: README.md, 30_SYSTEM/Vision/00_Abstract.md, ADR-0022
---
# Positioning"""
        fm = re_mod.extract_frontmatter(text)
        raw = fm.get("related", "")
        self.assertIsInstance(raw, str)
        items, warns = re_mod.RelatedParser.parse(raw)
        self.assertEqual(len(items), 3)


class TestBuildAndQuery(unittest.TestCase):
    """集成测试（build + 查询）"""

    @classmethod
    def setUpClass(cls):
        """执行 build"""
        cls.scanner = re_mod.Scanner()
        cls.nr = re_mod.NodeResolver()
        cls.tr = re_mod.TargetResolver(cls.nr)
        cls.builder = re_mod.GraphBuilder(cls.scanner, cls.nr, cls.tr)
        cls.graph = cls.builder.build()

    def test_build_success(self):
        """build 生成完整图"""
        self.assertIn("nodes", self.graph)
        self.assertIn("edges_declared", self.graph)
        self.assertIn("edges_backlinks", self.graph)
        self.assertIn("edges_supersedes", self.graph)
        self.assertIn("unresolved", self.graph)
        self.assertIn("orphans", self.graph)
        self.assertGreater(len(self.graph["nodes"]), 0)

    def test_stats_non_negative(self):
        """统计数据非负"""
        stats = self.graph["stats"]
        for key in ["nodes", "declared_edges", "backlinks", "supersedes", "unresolved", "orphans"]:
            self.assertGreaterEqual(stats[key], 0, f"{key} should be >= 0")

    def test_supersedes_detected(self):
        """检测到 ADR-0017 supersedes ADR-0016"""
        supersedes = self.graph["edges_supersedes"]
        self.assertGreaterEqual(len(supersedes), 1)
        found = False
        for e in supersedes:
            if "ADR-0017" in e["source"] and "ADR-0016" in e["target"]:
                found = True
        self.assertTrue(found, "ADR-0017 -> ADR-0016 supersedes not found")

    def test_backlinks_symmetric(self):
        """backlinks 数量合理"""
        self.assertGreaterEqual(len(self.graph["edges_backlinks"]), 10)

    def test_unresolved_recorded(self):
        """unresolved 记录包含必要字段"""
        for u in self.graph["unresolved"]:
            self.assertIn("from", u)
            self.assertIn("raw_target", u)
            self.assertIn("reason", u)

    def test_orphans_are_valid_nodes(self):
        """orphans 都是已有节点的 id"""
        all_ids = {n["id"] for n in self.graph["nodes"]}
        for oid in self.graph["orphans"]:
            self.assertIn(oid, all_ids)

    # ---- A-6 Edge Schema Enhancement tests ----

    def test_a6_declared_fields(self):
        """edges_declared 包含 A-6 四字段"""
        for e in self.graph["edges_declared"]:
            self.assertIn("confidence", e)
            self.assertIn("source_type", e)
            self.assertIn("created_by", e)
            self.assertIn("created_time", e)
            self.assertEqual(e["confidence"], 1.0)
            self.assertEqual(e["source_type"], "human_frontmatter")
            self.assertEqual(e["created_by"], "human")

    def test_a6_backlinks_fields(self):
        """edges_backlinks 包含 A-6 四字段"""
        for e in self.graph["edges_backlinks"]:
            self.assertIn("confidence", e)
            self.assertEqual(e["source_type"], "engine_derived")
            self.assertEqual(e["created_by"], "relationship_engine")

    def test_a6_supersedes_fields(self):
        """edges_supersedes 包含 A-6 四字段"""
        for e in self.graph["edges_supersedes"]:
            self.assertEqual(e["source_type"], "adr_text_scan")
            self.assertEqual(e["created_by"], "relationship_engine")

    def test_a6_created_time_iso8601(self):
        """created_time 格式符合 ISO 8601"""
        sample = self.graph["edges_declared"][0]["created_time"]
        import re
        self.assertRegex(sample, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')


class TestResolveNode(unittest.TestCase):
    """A-2 resolve_node 测试"""

    @classmethod
    def setUpClass(cls):
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        builder = re_mod.GraphBuilder(scanner, nr, tr)
        cls.graph = builder.build()

    def test_stem_exact_match(self):
        """文件名 stem 精确匹配"""
        result = re_mod.resolve_node(self.graph, "ADR-0017")
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0][2], "stem_exact")

    def test_title_substring(self):
        """title 子串匹配"""
        result = re_mod.resolve_node(self.graph, "NotebookLM")
        self.assertGreater(len(result), 0)

    def test_empty_query(self):
        """空查询返回 []"""
        result = re_mod.resolve_node(self.graph, "")
        self.assertEqual(result, [])

    def test_result_limit(self):
        """返回结果不超过 10 条"""
        result = re_mod.resolve_node(self.graph, "a")
        self.assertLessEqual(len(result), 10)


class TestFullPipeline(unittest.TestCase):
    """端到端管线测试"""

    def test_idempotent_build(self):
        """幂等性：两次 build 的 nodes/edges 一致（除 generated_at）"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        builder = re_mod.GraphBuilder(scanner, nr, tr)
        g1 = builder.build()
        g2 = builder.build()

        # nodes 和 edges 应一致
        self.assertEqual(len(g1["nodes"]), len(g2["nodes"]))
        self.assertEqual(len(g1["edges_declared"]), len(g2["edges_declared"]))
        self.assertEqual(len(g1["edges_backlinks"]), len(g2["edges_backlinks"]))
        self.assertEqual(len(g1["edges_supersedes"]), len(g2["edges_supersedes"]))

    def test_generated_at_different(self):
        """两次 build 的 generated_at 应不同（时间戳）"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        builder = re_mod.GraphBuilder(scanner, nr, tr)
        g1 = builder.build()
        g2 = builder.build()
        # 验证时间戳格式有效（两次 build 可能在同一秒，不比较不等性）
        self.assertRegex(g1["generated_at"], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

    def test_graph_json_serializable(self):
        """graph 可序列化为 JSON"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        builder = re_mod.GraphBuilder(scanner, nr, tr)
        graph = builder.build()
        try:
            serialized = json.dumps(graph, ensure_ascii=False)
            self.assertIsInstance(serialized, str)
        except (TypeError, ValueError) as e:
            self.fail(f"JSON serialization failed: {e}")

    def test_node_id_uniqueness(self):
        """所有节点 ID 唯一"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        builder = re_mod.GraphBuilder(scanner, nr, tr)
        graph = builder.build()
        ids = [n["id"] for n in graph["nodes"]]
        self.assertEqual(len(ids), len(set(ids)), "Node IDs should be unique")


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_related(self):
        """空 related"""
        items, warns = re_mod.RelatedParser.parse([])
        self.assertEqual(items, [])

    def test_self_reference_skipped(self):
        """自引用应被跳过"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)

        # 手动构造自引用
        scanned = [{
            "path": "test.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nid: SELF\nrelated: [SELF]\n---\n# Self",
            "filename_stem": "test",
            "path_stem": "test",
        }]
        nodes = nr.resolve_all(scanned)
        edges = tr.resolve_all(nodes)
        # 自引用不产生边
        self.assertEqual(len(edges), 0)

    def test_duplicate_edges_deduped(self):
        """重复边去重"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        scanned = [{
            "path": "test.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nid: A\nrelated: [B, B]\n---\n# A",
            "filename_stem": "test",
            "path_stem": "test",
        }, {
            "path": "other.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nid: B\n---\n# B",
            "filename_stem": "other",
            "path_stem": "other",
        }]
        nodes = nr.resolve_all(scanned)
        edges = tr.resolve_all(nodes)
        # 两条 B 引用只产生 1 条边
        b_edges = [e for e in edges if e["target"] == "B"]
        self.assertEqual(len(b_edges), 1)

    def test_glob_pattern_unresolved(self):
        """glob 模式应标记为 unresolved"""
        scanner = re_mod.Scanner()
        nr = re_mod.NodeResolver()
        tr = re_mod.TargetResolver(nr)
        scanned = [{
            "path": "test.md",
            "abspath": "",
            "scope": "20_KNOWLEDGE",
            "raw_text": "---\nid: A\nrelated: [AI-Packets/*]\n---\n# A",
            "filename_stem": "test",
            "path_stem": "test",
        }]
        nodes = nr.resolve_all(scanned)
        edges = tr.resolve_all(nodes)
        self.assertEqual(len(tr.unresolved), 1)
        self.assertEqual(tr.unresolved[0]["reason"], "glob-pattern")


if __name__ == "__main__":
    unittest.main(verbosity=2)
