#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
usage_tracker 测试套件（PKT-EXE-20260719-002 验收）

运行方式：
  python test_usage_tracker.py
  python test_usage_tracker.py -v
"""

import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import usage_tracker as ut


class TestRecordUsage(unittest.TestCase):
    """record_usage() API 测试"""

    def setUp(self):
        # 重定向到临时目录
        self.tmpdir = tempfile.mkdtemp(prefix="paios_usage_test_")
        ut.USAGE_DIR = os.path.join(self.tmpdir, "usage")
        self.CST = timezone(timedelta(hours=8))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_basic_record(self):
        """基本的 record_usage 调用"""
        trace_id = ut.record_usage(
            session_id="SESSION-001",
            task="考研复习规划",
            actor="Buddy",
            action="retrieve",
            assets=[("ADR-0017", "adr"), ("定位共识v2.1", "knowledge")],
        )
        self.assertRegex(trace_id, r"^UT-\d{8}-\d{4}$")
        # 验证文件存在
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        self.assertTrue(os.path.isfile(path), f"File not found: {path}")

    def test_record_with_outcome_true(self):
        """outcome=True 的记录"""
        trace_id = ut.record_usage(
            session_id="SESSION-002",
            task="代码审查",
            actor="Reasonix",
            action="validate",
            assets=[("ADR-0009", "adr")],
            outcome=True,
        )
        self.assertIsNotNone(trace_id)
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("success: true", content)

    def test_record_with_outcome_false(self):
        """outcome=False 的记录"""
        trace_id = ut.record_usage(
            session_id="SESSION-003",
            task="查询架构",
            actor="ChatGPT",
            action="query",
            assets=[("ADR-0012", "adr")],
            outcome=False,
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("success: false", content)

    def test_record_outcome_default_null(self):
        """outcome 不传时默认为 null"""
        trace_id = ut.record_usage(
            session_id="SESSION-004",
            task="默认任务",
            actor="Buddy",
            action="generate",
            assets=[("KB-0001", "knowledge")],
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("success: null", content)

    def test_record_with_relationship(self):
        """带 relationship_query + related_nodes 的记录"""
        trace_id = ut.record_usage(
            session_id="SESSION-005",
            task="关系追溯",
            actor="Reasonix",
            action="reference",
            assets=[("ADR-0017", "adr")],
            relationship_query="backlinks",
            related_nodes=["ADR-0016", "ADR-0019"],
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("query_type: backlinks", content)
        self.assertIn("ADR-0016", content)
        self.assertIn("ADR-0019", content)

    def test_missing_session_id(self):
        """缺少 session_id 抛异常"""
        with self.assertRaises(ValueError):
            ut.record_usage(
                session_id="",
                task="x",
                actor="x",
                action="retrieve",
                assets=[("a", "adr")],
            )

    def test_missing_task(self):
        """缺少 task 抛异常"""
        with self.assertRaises(ValueError):
            ut.record_usage(
                session_id="S1",
                task="",
                actor="x",
                action="retrieve",
                assets=[("a", "adr")],
            )

    def test_missing_actor(self):
        """缺少 actor 抛异常"""
        with self.assertRaises(ValueError):
            ut.record_usage(
                session_id="S1",
                task="x",
                actor="",
                action="retrieve",
                assets=[("a", "adr")],
            )

    def test_invalid_action(self):
        """无效 action 抛异常"""
        with self.assertRaises(ValueError):
            ut.record_usage(
                session_id="S1",
                task="x",
                actor="x",
                action="invalid_action",
                assets=[("a", "adr")],
            )

    def test_missing_assets(self):
        """缺少 assets 抛异常"""
        with self.assertRaises(ValueError):
            ut.record_usage(
                session_id="S1",
                task="x",
                actor="x",
                action="query",
                assets=[],
            )

    def test_trace_id_increments(self):
        """trace_id 顺序号递增"""
        ids = []
        for i in range(3):
            tid = ut.record_usage(
                session_id=f"SESSION-INCR-{i}",
                task="递增测试",
                actor="Buddy",
                action="query",
                assets=[("ADR-0001", "adr")],
            )
            ids.append(tid)

        # 提取顺序号
        seqs = [int(t.split("-")[-1]) for t in ids]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(seqs[-1] - seqs[0], len(seqs) - 1)


class TestListTraces(unittest.TestCase):
    """list_traces() 测试"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="paios_usage_test_")
        ut.USAGE_DIR = os.path.join(self.tmpdir, "usage")
        self.CST = timezone(timedelta(hours=8))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_list_empty(self):
        """无 trace 的日期返回空"""
        traces = ut.list_traces("2099-01-01")
        self.assertEqual(traces, [])

    def test_list_with_traces(self):
        """有 trace 的日期正确返回"""
        # 先录制几条
        ut.record_usage(
            session_id="S-LIST-1", task="t1", actor="Buddy",
            action="retrieve", assets=[("a", "adr")],
        )
        ut.record_usage(
            session_id="S-LIST-2", task="t2", actor="Reasonix",
            action="validate", assets=[("b", "knowledge")],
        )

        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        traces = ut.list_traces(today)
        self.assertEqual(len(traces), 2)
        # 每个 trace 是 (trace_id, created_time, session_id, action_type)
        self.assertEqual(len(traces[0]), 4)

    def test_list_default_today(self):
        """不传 date 默认今天"""
        ut.record_usage(
            session_id="S-DEFAULT", task="t", actor="Buddy",
            action="generate", assets=[("c", "tool")],
        )
        traces = ut.list_traces()  # 默认今天
        self.assertGreaterEqual(len(traces), 1)


class TestYamlSchema(unittest.TestCase):
    """YAML 输出 schema 验证"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="paios_usage_test_")
        ut.USAGE_DIR = os.path.join(self.tmpdir, "usage")
        self.CST = timezone(timedelta(hours=8))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_yaml_has_required_fields(self):
        """YAML 包含所有必需字段"""
        trace_id = ut.record_usage(
            session_id="SESSION-YAML",
            task="YAML Schema Test",
            actor="Buddy",
            action="retrieve",
            assets=[("ADR-0017", "adr")],
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        required = [
            "trace_id:",
            "created_time:",
            "session:",
            "actor:",
            "action:",
            "assets:",
            "outcome:",
        ]
        for field in required:
            self.assertIn(field, content, f"Missing field: {field}")

    def test_yaml_no_reuse_value(self):
        """YAML 不含 reuse_value 字段（红线 7）"""
        trace_id = ut.record_usage(
            session_id="SESSION-NOREUSE",
            task="No Reuse",
            actor="Buddy",
            action="generate",
            assets=[("a", "knowledge")],
            outcome=True,
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("reuse_value", content)
        self.assertNotIn("failure_reason", content)

    def test_yaml_created_time_iso8601(self):
        """created_time 为 ISO 8601 格式"""
        trace_id = ut.record_usage(
            session_id="SESSION-ISO",
            task="ISO Test",
            actor="Buddy",
            action="validate",
            assets=[("a", "adr")],
        )
        today = datetime.now(self.CST).strftime("%Y-%m-%d")
        path = os.path.join(ut.USAGE_DIR, today, f"{trace_id}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("created_time: "):
                    ts = line.split(": ", 1)[1].strip()
                    self.assertRegex(ts, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}')
                    break


class TestRedLines(unittest.TestCase):
    """7 条红线验证"""

    def test_no_relationship_engine_import(self):
        """不 import relationship_engine"""
        with open(os.path.join(SCRIPT_DIR, "usage_tracker.py"), "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                self.assertNotIn("relationship_engine", stripped,
                    f"'relationship_engine' referenced in import: {stripped}")

    def test_no_database_import(self):
        """不依赖任何数据库模块"""
        with open(os.path.join(SCRIPT_DIR, "usage_tracker.py"), "r", encoding="utf-8") as f:
            content = f.read()
        banned = ["sqlite3", "mysql", "postgresql", "pymongo", "redis"]
        for b in banned:
            self.assertNotIn(b, content.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
