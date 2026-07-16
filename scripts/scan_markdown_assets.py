#!/usr/bin/env python3
"""
scan_markdown_assets.py — PAIOS Phase-4 Markdown Asset Scanner

Tool:   scan_markdown_assets
Phase:  Phase-4 STABILIZE
Mode:   readonly
Status: experimental

Purpose:
  Scan 5 root directories for .md files, extract metadata,
  classify by priority (P0-P4), identify ADR candidates,
  and output three inventory files.

Usage:
  python3 scripts/scan_markdown_assets.py

Output:
  90_ARCHIVE/Asset-Inventory/
    ├── markdown_inventory.yaml
    ├── adr_candidates.yaml
    └── ADR_REGISTRY.md
"""

import os
import sys
import time
import re
import hashlib
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "90_ARCHIVE" / "Asset-Inventory"

SCAN_ROOTS = [
    {"path": r"D:\PAIOS-PORTABLE\Core",      "mode": "full_content", "instance": "PAIOS-PORTABLE-001"},
    {"path": r"F:\PAIOS",                      "mode": "full_content", "instance": "PAIOS-F-001"},
    {"path": r"G:\2in1\PAIOS",                 "mode": "full_content", "instance": "PAIOS-G-2IN1-001"},
    {"path": r"G:\workspace",                  "mode": "metadata_only", "instance": "G-WORKSPACE-001"},
    {"path": r"H:\workspace",                  "mode": "metadata_only", "instance": "H-WORKSPACE-001"},
]

EXCLUDE_DIRS = {".git", ".reasonix", ".workbuddy", "node_modules", "__pycache__",
                ".pytest_cache", ".autoresearch", "backup", "archive_old", "Legacy"}

EXCLUDE_FILES_CONTAINING = {"tutorial", "example", "template", "README"}

EXCLUDE_FILES_EXACT = {"README.md", "_template.md", "_index.md"}

# ── Classification priority order (highest first) ─────────────────────────

CLASSIFICATION_ORDER = [
    "ADR",          # P0 — Architecture Decision Records
    "Governance",   # P0 — Governance rules & policies
    "Architecture", # P0-P1 — Architecture docs
    "Methodology",  # P1 — Methods & workflows
    "Project",      # P2 — Project notes & cases
    "Log",          # P3 — Daily logs & journals
    "Temporary",    # P4 — Drafts & temporary
]

CLASSIFICATION_RULES = [
    # (category, priority, path_keywords, content_keywords)
    ("ADR",         0, ["ADR-", "/ADR/", "decision-record"], ["ADR", "Architecture Decision", "Decision Record", "Status:", "Accepted"]),
    ("Governance",  0, ["Governance/", "architectural-invariants", "Decision-Traceability",
                        "Change-Control", "Operating-Model", "policy", "protocol",
                        "invariant", "rule", "Rule"], []),
    ("Architecture", 1, ["Architecture", "Design_Notes", "architecture", "Specifications",
                         "Vision/", "Evolution/", "架构", "设计"], []),
    ("Methodology", 1, ["Method/", "Workflow", "SOP/", "SOP-", "method", "流程"], []),
    ("Project",     2, ["Case-", "CASE-", "Project/", "Projects/", "10_WORK/",
                        "案例", "项目"], []),
    ("Log",         3, ["JOURNAL/", "Journal/", "日志", "Daily", "Log", "日记",
                        "80_HISTORY/"], []),
    ("Temporary",   4, ["Inbox", "_candidates", "tmp", "TMP", "notes",
                        "70_TMP", "00_CAPTURE"], []),
]

# ── ADR content detection patterns ────────────────────────────────────────

ADR_FILENAME_PATTERN = "ADR-"

ADR_CONTENT_SIGNALS = [
    "Architecture Decision Record",
    "ADR",
    "Decision Record",
    "## Decision",
    "## Status",
    "Status: Accepted",
    "Status: Proposed",
    "Status: Deprecated",
    "Status: Superseded",
    "Status: Rejected",
]

# Files that explain ADR concept but are not themselves ADRs
ADR_EXCLUDE_SIGNALS = [
    "what is an architecture decision",
    "how to write an adr",
    "adr template",
    "adr tutorial",
    "adr example",
    "adr lifecycle",
    "adr index",
    "adr governance",
]


# ── Helpers ────────────────────────────────────────────────────────────────

def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from scanning."""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def calculate_hash(filepath: Path) -> str:
    """SHA256 hash of file contents (only for .md files)."""
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return ""


def classify_file(rel_path: str, content_preview: str = "") -> tuple:
    """Classify a file by priority category.
    
    Returns (category, priority, match_reason).
    Classification priority order: ADR → Governance → Architecture → ...
    """
    path_lower = rel_path.lower().replace("\\", "/")

    for cat, pri, path_kw, content_kw in CLASSIFICATION_RULES:
        # Check path keywords first
        for kw in path_kw:
            if kw.lower() in path_lower:
                return cat, pri, f"path_match:{kw}"

        # Check content keywords (only if content is available)
        if content_kw and content_preview:
            content_lower = content_preview.lower()
            for kw in content_kw:
                if kw.lower() in content_lower:
                    return cat, pri, f"content_match:{kw}"

    return "Unclassified", 5, "no_match"


def detect_adr(filepath: Path, rel_path: str, content_preview: str = "") -> dict:
    """Detect if a file is an ADR candidate.
    
    Returns dict with confidence, reason, source, or None.
    """
    filename = filepath.name
    content_lower = content_preview.lower()

    # ── Exclude non-ADR files ──
    for signal in ADR_EXCLUDE_SIGNALS:
        if signal in content_lower:
            return None

    # ── High confidence: filename match ──
    if filename.startswith(ADR_FILENAME_PATTERN) and filename.endswith(".md"):
        # Extract ADR ID from filename
        adr_id = filename.replace(".md", "")
        # Try to extract title
        title = ""
        parts = filename.replace(".md", "").split("-", 2)
        if len(parts) >= 3:
            title = parts[2].replace("-", " ")

        return {
            "confidence": "high",
            "reason": "filename_match",
            "source": "filename",
            "adr_id": adr_id,
            "title": title,
        }

    # ── Medium confidence: content signals ──
    if content_preview:
        signal_count = 0
        matched_signals = []
        for signal in ADR_CONTENT_SIGNALS:
            if signal.lower() in content_lower:
                signal_count += 1
                matched_signals.append(signal)

        signal_count_exclude = 0
        for signal in ADR_EXCLUDE_SIGNALS:
            if signal in content_lower:
                signal_count_exclude += 1

        if signal_count_exclude > 0:
            return None

        if signal_count >= 2:
            return {
                "confidence": "medium",
                "reason": f"content_signals:{','.join(matched_signals[:3])}",
                "source": "content",
                "adr_id": "",
                "title": "",
            }
        elif signal_count == 1:
            return {
                "confidence": "low",
                "reason": f"content_signal:{matched_signals[0]}",
                "source": "content",
                "adr_id": "",
                "title": "",
            }

    return None


# ── Phase-4.5 ADR classification helpers ────────────────────────────────

def classify_adr_candidate_type(filepath: Path, rel_path: str, content_preview: str, confidence: str) -> str:
    """Determine adr_candidate_type based on ChatGPT-approved rules.
    
    Returns: confirmed_candidate / possible_candidate / false_positive_candidate
    """
    filename = filepath.name
    path_lower = rel_path.lower().replace("\\", "/")
    content_lower = content_preview.lower()

    # Rule 1: filename matches ADR-NNNN-*.md
    if filename.startswith("ADR-") and filename.endswith(".md"):
        if re.match(r'ADR-\d+', filename):
            return "confirmed_candidate"

    # Rule 2: path contains /ADR/ or /adr/
    if "/adr/" in path_lower:
        return "confirmed_candidate"

    # Rule 3: content has standard ADR template structure
    if content_preview:
        has_status_section = "## Status" in content_preview or "##Decision" in content_preview
        has_context_or_decision = "## Context" in content_preview or "## Decision" in content_preview
        if has_status_section and has_context_or_decision:
            return "confirmed_candidate"

        # Rule 4: contains "Architecture Decision Record" or "ADR-NNNN" + "Status:"
        has_adr_record = "architecture decision record" in content_lower
        has_adr_id = bool(re.search(r'ADR-\d{4}', content_preview))
        has_status_field = "Status:" in content_preview
        if has_adr_record or (has_adr_id and has_status_field):
            return "confirmed_candidate"

    # High/medium confidence but no structural match
    if confidence in ("high", "medium"):
        return "possible_candidate"

    # Low confidence with no structural evidence
    return "false_positive_candidate"


def classify_adr_scope(filepath: Path, rel_path: str, source_instance: str, candidate_type: str) -> str:
    """Determine adr_scope: system / knowledge / external / unknown."""
    if candidate_type == "false_positive_candidate":
        return "unknown"

    path_lower = rel_path.lower().replace("\\", "/")
    filename = filepath.name

    # System: PAIOS platform ADRs
    if "30_system/adr" in path_lower or "30_system/governance" in path_lower:
        return "system"
    if filename.startswith("ADR-") and re.match(r'ADR-\d{4}', filename):
        if source_instance in ("PAIOS-PORTABLE-001", "PAIOS-F-001", "PAIOS-G-2IN1-001"):
            return "system"

    # External: installer / tool projects
    if "installer" in path_lower or "external" in path_lower or "legacy" in path_lower:
        return "external"
    if source_instance in ("H-WORKSPACE-001", "G-WORKSPACE-001"):
        return "external"

    # Knowledge: decision records that are not architecture-level
    if "knowledge" in path_lower or "dec-" in path_lower or "decision" in path_lower:
        return "knowledge"

    return "unknown"


def derive_review_type(adr_scope: str) -> str:
    """Derive review_type from adr_scope."""
    mapping = {
        "system": "system_promotion",
        "knowledge": "knowledge_reference",
        "external": "external_archive",
        "unknown": "reject_candidate",
    }
    return mapping.get(adr_scope, "reject_candidate")


def read_content_preview(filepath: Path, max_bytes: int = 4096) -> str:
    """Read first bytes of a file for content analysis (full_content mode only)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)
    except (OSError, PermissionError):
        return ""


# ── Main scanning logic ────────────────────────────────────────────────────

def scan_roots():
    """Scan all roots and return structured data."""
    all_files = []           # For markdown_inventory.yaml
    adr_candidates = []      # For adr_candidates.yaml
    per_path_stats = defaultdict(lambda: {"file_count": 0, "md_count": 0})

    for root_cfg in SCAN_ROOTS:
        root = Path(root_cfg["path"])
        mode = root_cfg["mode"]
        instance = root_cfg["instance"]

        if not root.exists():
            print(f"  [SKIP] Root does not exist: {root}")
            continue

        print(f"  Scanning: {root}  (mode={mode})")

        for filepath in root.rglob("*.md"):
            if should_exclude(filepath):
                continue

            rel_path = str(filepath.relative_to(root))
            per_path_stats[root_cfg["path"]]["file_count"] += 1

            try:
                stat = filepath.stat()
            except OSError:
                continue

            per_path_stats[root_cfg["path"]]["md_count"] += 1

            # ── Metadata (always collected) ──
            entry = {
                "path": str(filepath),
                "rel_path": rel_path,
                "source_root": root_cfg["path"],
                "source_instance": instance,
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "ctime": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "mode": mode,
            }

            # ── Content analysis (full_content only) ──
            content_preview = ""
            if mode == "full_content":
                content_preview = read_content_preview(filepath)

                # Optional SHA256 for .md files
                if filepath.suffix.lower() == ".md":
                    entry["sha256"] = calculate_hash(filepath)

            # ── Classification ──
            cat, pri, match_reason = classify_file(rel_path, content_preview)
            entry["category"] = cat
            entry["priority"] = pri
            entry["classification_reason"] = match_reason

            all_files.append(entry)

            # ── ADR detection ──
            adr = detect_adr(filepath, rel_path, content_preview)
            if adr:
                confidence = adr["confidence"]
                candidate_type = classify_adr_candidate_type(filepath, rel_path, content_preview, confidence)
                adr_scope = classify_adr_scope(filepath, rel_path, instance, candidate_type)
                review_type = derive_review_type(adr_scope)
                adr_entry = {
                    "file": str(filepath),
                    "rel_path": rel_path,
                    "source_instance": instance,
                    "confidence": confidence,
                    "reason": adr["reason"],
                    "source": adr["source"],
                    "adr_id": adr["adr_id"],
                    "title": adr["title"],
                    "category": cat,
                    "priority": pri,
                    "adr_candidate_type": candidate_type,
                    "adr_scope": adr_scope,
                    "review_type": review_type,
                }
                adr_candidates.append(adr_entry)

        print(f"    → {per_path_stats[root_cfg['path']]['md_count']} .md files found")

    return all_files, adr_candidates, per_path_stats


# ── Duplicate detection ────────────────────────────────────────────────────

def mark_duplicates(adr_candidates):
    """Mark duplicate ADR candidates across instances."""
    # Group by filename
    by_filename = defaultdict(list)
    for adr in adr_candidates:
        fname = Path(adr["file"]).name
        by_filename[fname].append(adr)

    for fname, items in by_filename.items():
        if len(items) > 1:
            for item in items:
                item["duplicate_candidate"] = True
        else:
            items[0]["duplicate_candidate"] = False


# ── Output writers ─────────────────────────────────────────────────────────

def write_markdown_inventory(all_files, stats):
    """Write markdown_inventory.yaml."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "generator": "scan_markdown_assets.py",
        "phase": "Phase-4 STABILIZE",
        "total_files": len(all_files),
        "per_root": {},
        "files": all_files,
    }

    for root_path, s in stats.items():
        output["per_root"][root_path] = {
            "file_count": s["file_count"],
            "md_count": s["md_count"],
        }

    path = OUTPUT_DIR / "markdown_inventory.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] Wrote {path}")
    return output["total_files"]


def write_adr_candidates(adr_candidates):
    """Write adr_candidates.yaml."""
    # Sort by confidence (high first), then by source_instance
    adr_candidates.sort(key=lambda x: (
        {"high": 0, "medium": 1, "low": 2}.get(x["confidence"], 3),
        x["source_instance"],
        x["rel_path"],
    ))

    output = {
        "generated_at": datetime.now().isoformat(),
        "generator": "scan_markdown_assets.py",
        "phase": "Phase-4 STABILIZE",
        "total_candidates": len(adr_candidates),
        "adr_candidates": adr_candidates,
    }

    path = OUTPUT_DIR / "adr_candidates.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] Wrote {path}")
    return output["total_candidates"]


def write_adr_registry(adr_candidates):
    """Write ADR_REGISTRY.md with cross-reference to ADR-INDEX.md."""
    # Filter to high/medium confidence only for the registry
    registry_entries = [a for a in adr_candidates
                        if a["confidence"] in ("high", "medium")]

    # Read existing ADR-INDEX.md from Core for cross-reference
    core_adr_index = Path(r"D:\PAIOS-PORTABLE\Core\30_SYSTEM\ADR\ADR-INDEX.md")
    registered_adrs = set()
    if core_adr_index.exists():
        content = core_adr_index.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("| ADR-"):
                parts = line.split("|")
                if len(parts) >= 2:
                    adr_id = parts[1].strip()
                    if adr_id.startswith("ADR-"):
                        registered_adrs.add(adr_id)

    # Build markdown
    lines = []
    lines.append("# PAIOS Architecture Decision Record Registry")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")
    lines.append(f"*Phase: Phase-4 STABILIZE*")
    lines.append(f"*Total candidates (high+medium confidence): {len(registry_entries)}*")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append("| ADR ID | Title | Status | Confidence | Source Instance | Location | Duplicate | In ADR-INDEX.md | Lifecycle Status | Canonical Source |")
    lines.append("|--------|-------|--------|------------|-----------------|----------|-----------|-----------------|-----------------|-----------------|")

    # Group by adr_id for display
    registry_entries.sort(key=lambda x: (
        {"high": 0, "medium": 1}.get(x["confidence"], 2),
        x.get("adr_id", ""),
    ))

    seen_ids = set()
    for entry in registry_entries:
        raw_adr_id = entry.get("adr_id", "") or Path(entry["file"]).stem
        # Extract just ADR-NNNN prefix for INDEX comparison
        adr_id = raw_adr_id
        m = re.match(r'(ADR-\d+)', adr_id)
        if m:
            adr_id = m.group(1)
        title = entry.get("title", "") or raw_adr_id
        confidence = entry["confidence"]
        instance = entry["source_instance"]
        location = entry["rel_path"]
        dup = "[DUP]" if entry.get("duplicate_candidate") else ""
        in_index = "[INDEXED]" if adr_id in registered_adrs else "[NEW]"

        # Status: try to infer from path or mark
        status = "Unknown"
        if "Accepted" in entry.get("reason", ""):
            status = "Accepted"
        elif "Proposed" in entry.get("reason", ""):
            status = "Proposed"
        elif confidence == "high":
            status = "Registered" if adr_id in registered_adrs else "Candidate"

        lifecycle_status = "discovered"
        canonical_source = "pending_review"
        lines.append(f"| {adr_id} | {title} | {status} | {confidence} | {instance} | `{location}` | {dup} | {in_index} | {lifecycle_status} | {canonical_source} |")
        seen_ids.add(adr_id)

    # Add ADRs from INDEX that were NOT found in scan
    unfound = registered_adrs - seen_ids
    if unfound:
        lines.append("")
        lines.append("## ADRs in INDEX but Not Found in Scan")
        lines.append("")
        lines.append("| ADR ID | Note |")
        lines.append("|--------|------|")
        for adr_id in sorted(unfound):
            lines.append(f"| {adr_id} | Referenced in ADR-INDEX.md but not found in any scan root |")

    # Summary
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total ADR candidates (high/medium confidence): {len(registry_entries)}")
    lines.append(f"- Registered in ADR-INDEX.md: {len(registered_adrs & seen_ids)}")
    lines.append(f"- New candidates not in ADR-INDEX.md: {len(seen_ids - registered_adrs)}")
    lines.append(f"- Unreferenced INDEX entries: {len(unfound)}")
    lines.append(f"- Duplicate candidates: {sum(1 for e in registry_entries if e.get('duplicate_candidate'))}")
    lines.append(f"- All lifecycle_status default: discovered")
    lines.append(f"- All canonical_source default: pending_review (until Phase-5)")
    lines.append("")

    path = OUTPUT_DIR / "ADR_REGISTRY.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [OK] Wrote {path}")
    return len(registry_entries)


# ── Phase-4.5: ADR Master Registry ──────────────────────────────────────

def build_duplicate_groups(adr_candidates):
    """Group ADR candidates by ADR prefix for duplicate tracking."""
    groups = defaultdict(list)
    for entry in adr_candidates:
        raw_id = entry.get("adr_id", "") or Path(entry["file"]).stem
        m = re.match(r'(ADR-\d+)', raw_id)
        if m:
            group_key = m.group(1)
        else:
            group_key = raw_id
        groups[group_key].append(entry)
    return groups


def write_adr_master_registry(adr_candidates):
    """Write ADR_MASTER_REGISTRY.md — the governance-level registry.
    
    Only includes confirmed_candidate + possible_candidate (excludes false_positive).
    """
    # Filter out false positives
    filtered = [a for a in adr_candidates
                if a.get("adr_candidate_type") in ("confirmed_candidate", "possible_candidate")]

    # Read existing ADR-INDEX.md for cross-reference
    core_adr_index = Path(r"D:\PAIOS-PORTABLE\Core\30_SYSTEM\ADR\ADR-INDEX.md")
    registered_adrs = set()
    if core_adr_index.exists():
        content = core_adr_index.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("| ADR-"):
                parts = line.split("|")
                if len(parts) >= 2:
                    adr_id = parts[1].strip()
                    if adr_id.startswith("ADR-"):
                        registered_adrs.add(adr_id)

    # Build duplicate groups
    groups = build_duplicate_groups(filtered)

    # Build markdown
    lines = []
    lines.append("# PAIOS Architecture Decision Record — Master Registry")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")
    lines.append(f"*Phase: Phase-4.5 ADR Candidate Review*")
    lines.append(f"*Total entries: {len(filtered)} (confirmed + possible candidates)*")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append("| ADR ID | Title | Type | Scope | Confidence | Source Instance | Source Paths | Review Type | In INDEX | Duplicate Group |")
    lines.append("|--------|-------|------|-------|------------|-----------------|--------------|-------------|----------|----------------|")

    filtered.sort(key=lambda x: (
        {"confirmed_candidate": 0, "possible_candidate": 1}.get(x.get("adr_candidate_type", ""), 2),
        {"high": 0, "medium": 1, "low": 2}.get(x.get("confidence", ""), 3),
        x.get("adr_id", ""),
    ))

    for entry in filtered:
        raw_adr_id = entry.get("adr_id", "") or Path(entry["file"]).stem
        m = re.match(r'(ADR-\d+)', raw_adr_id)
        adr_id_short = m.group(1) if m else raw_adr_id
        title = entry.get("title", "") or raw_adr_id
        ctype = entry.get("adr_candidate_type", "unknown")
        scope = entry.get("adr_scope", "unknown")
        confidence = entry.get("confidence", "")
        instance = entry.get("source_instance", "")
        location = entry.get("rel_path", "")
        review_type = entry.get("review_type", "")
        in_index = "[INDEXED]" if adr_id_short in registered_adrs else "[NEW]"
        dup_group = adr_id_short if m else ""

        lines.append(f"| {adr_id_short} | {title} | {ctype} | {scope} | {confidence} | {instance} | `{location}` | {review_type} | {in_index} | {dup_group} |")

    # Group summary
    lines.append("")
    lines.append("## Duplicate Groups Summary")
    lines.append("")
    lines.append("| ADR ID | Instance Count | Instances | Canonical Source |")
    lines.append("|--------|---------------|-----------|-----------------|")

    for group_id, members in sorted(groups.items()):
        if len(members) > 1:
            instances = ", ".join(sorted(set(m.get("source_instance", "") for m in members)))
            source_paths = ", ".join(sorted(set(m.get("rel_path", "") for m in members)))
            lines.append(f"| {group_id} | {len(members)} | {instances} | `{source_paths}` |")

    if not any(len(m) > 1 for m in groups.values()):
        lines.append("| (no duplicates) | | | |")

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total master registry entries: {len(filtered)}")
    lines.append(f"- Confirmed candidates: {sum(1 for e in filtered if e.get('adr_candidate_type') == 'confirmed_candidate')}")
    lines.append(f"- Possible candidates: {sum(1 for e in filtered if e.get('adr_candidate_type') == 'possible_candidate')}")
    lines.append(f"- System scope: {sum(1 for e in filtered if e.get('adr_scope') == 'system')}")
    lines.append(f"- Knowledge scope: {sum(1 for e in filtered if e.get('adr_scope') == 'knowledge')}")
    lines.append(f"- External scope: {sum(1 for e in filtered if e.get('adr_scope') == 'external')}")
    lines.append(f"- Unknown scope: {sum(1 for e in filtered if e.get('adr_scope') == 'unknown')}")
    lines.append(f"- Duplicate groups: {sum(1 for g in groups.values() if len(g) > 1)}")
    lines.append(f"- Already in ADR-INDEX.md: {len(registered_adrs)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Note: `canonical_source` and `migration_target` are null until Phase-5.*")
    lines.append("*`lifecycle_status` defaults to `discovered` until human review.*")
    lines.append("")

    path = OUTPUT_DIR / "ADR_MASTER_REGISTRY.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [OK] Wrote {path}")
    return len(filtered)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PAIOS Phase-4 — Markdown Asset Scanner")
    print("=" * 60)
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Phase-4 constraint check
    print("[CONSTRAINTS]")
    print("  [OK] Readonly scan - no files will be modified")
    print("  [OK] No migration - inventory only")
    print("  [OK] No deletion - nothing removed")
    print("  [OK] No RAG import - YAML/MD output only")
    print("  [OK] No Core structure change - output in 90_ARCHIVE/Asset-Inventory/")
    print()

    # Scan
    print("[SCAN]")
    start = time.time()
    all_files, adr_candidates, stats = scan_roots()
    elapsed = time.time() - start
    print()
    print(f"  Scan completed in {elapsed:.1f}s")
    print(f"  Total .md files scanned: {len(all_files)}")
    print()

    # Mark duplicates
    mark_duplicates(adr_candidates)

    # Write outputs
    print("[OUTPUTS]")
    total_inventory = write_markdown_inventory(all_files, stats)
    total_adr = write_adr_candidates(adr_candidates)
    total_registry = write_adr_registry(adr_candidates)
    total_master = write_adr_master_registry(adr_candidates)
    print()

    # Summary
    print("[SUMMARY]")
    print(f"  markdown_inventory.yaml:  {total_inventory} files")
    print(f"  adr_candidates.yaml:      {total_adr} candidates")
    print(f"  ADR_REGISTRY.md:          {total_registry} registry entries")
    print(f"  ADR_MASTER_REGISTRY.md:   {total_master} master entries")
    print()

    # Category distribution
    from collections import Counter
    cat_counter = Counter(f["category"] for f in all_files)
    print("[CATEGORY DISTRIBUTION]")
    for cat in CLASSIFICATION_ORDER:
        count = cat_counter.get(cat, 0)
        print(f"  {cat:15s}  {count:4d}")
    print(f"  {'Unclassified':15s}  {cat_counter.get('Unclassified', 0):4d}")
    print()
    print("Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
