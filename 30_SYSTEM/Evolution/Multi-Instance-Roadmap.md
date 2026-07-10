# PAIOS 多实例演进路线图

> 配套 ADR-0016（架构基线冻结）。本文档把"从一个人系统到多实例平台"的演进拆成可执行的阶段与优先级。
> 核心纪律：**不让架构领先数据**（Need-Driven / Necessity-Gated）。

---

## 一、这次工作的真正成果

讨论主题经历了三次升级：

| 阶段 | 主题 | 实质 |
|------|------|------|
| 1 | Growth OS 是否作为 PAIOS 分支？ | 应用边界 |
| 2 | PAIOS Core + Applications 如何演进？ | 平台结构 |
| 3 | PAIOS 从"一个人的系统"走向"多个实例的平台" | **阶段转换** |

真正的成果不是 FIM，而是**第一次建立了 PAIOS 的多实例架构**。

---

## 二、4 层架构模型（已冻结，见 ADR-0016）

```
L1  Platform (PAIOS Core)       平台代码，开发者维护
        │
        ▼
L2  Instance (每个用户一个 PAIOS)   部署单元，独立运行
        │
        ▼
L3  Manifest (实例状态)           FIM 协议，主动声明
        │
        ▼
L4  Fleet (聚合观察)              只读汇总，非侵入
```

---

## 三、已冻结（不再反复讨论）

1. **PAIOS 不再只是个人系统** —— 平台已出现（Core → Case-01/02/03）。
2. **Core 与 Workspace 分离** —— 比 FIM 更基础，以后所有升级围绕它。
3. **Instance 独立** —— 知识/照片/项目全留本地。
4. **FIM = Instance State** —— 原则 Snapshot / Pull / Observe / Zero Intrusion 已成熟。

---

## 四、路线图（Stage0 → Stage4）

### Stage0 · 单实例
- ✅ 已完成（v1.0.0 个人系统）

### Stage1 · 三个实例（★ 当前）
```
Core
  ├── Workspace（每实例独立）
  ├── Upgrade（v1.0.1 统一基线）
  └── Manifest（collect_manifest.py 产出）
```
- 目标：三个真实实例都跑到同一 Core 版本（1.0.1），各自生成 Manifest。
- 出口标准：Case-01/02/03 均有 `profile.yaml` + `manifest.yaml`，core_version 一致。

### Stage2 · Fleet MVP
```
aggregate.py
    ↓
fleet.md（Markdown 周报）
    ↓
版本统计 / Profile 统计
```
- 先**人工**汇总三个 Manifest 成 fleet.md（验证需求）。
- 当人工开始重复 → 用 aggregate.py 自动化生成 Markdown。
- 不做 Dashboard。

### Stage3 · Fleet Dashboard
```
HTML 仪表盘
    ↓
趋势 / Health / Adoption
```
- 触发：至少 5+ 真实实例。
- 单实例/少量实例时 HTML 价值极低，推迟。

### Stage4 · PAIOS Platform
```
Photo OS / Growth OS / Study OS ...
    ↓
统一 Manifest
    ↓
Fleet
```
- 触发：应用真正成熟（Photo/Growth/Study 真实出现），再统一接入 FIM。
- 现在不做。

---

## 五、优先级表（P0 → P3）

| 优先级 | 事项 | 是否立即 | 原因 |
|--------|------|----------|------|
| **P0** | 冻结 Core / Workspace / FIM 三层架构 | ✅ | 后续基础，不宜反复调整 |
| **P0** | 三个实例升级到同一 Core 版本（1.0.1） | ✅ | 建立统一版本基线 |
| **P0** | 补齐 profile.yaml（Case-01 work / Case-02 personal / Case-03 study） | ✅ | 场景信息无法自动推导，聚合关键 |
| **P0** | 三个真实实例运行 collect_manifest.py 生成 Manifest | ✅ | 首次跨实例验证 FIM 是否成立 |
| **P0** | 人工汇总三个 Manifest → fleet.md 周报 | ✅ | 用真实数据验证聚合需求，避免过早开发 Dashboard |
| **P1** | Manifest Validator | ⏳ | 保证 Schema/版本一致性，降维护成本 |
| **P1** | aggregate.py 自动生成 Markdown/HTML 周报 | ⏳ | 人工汇总开始重复时再自动化 |
| **P1** | Release / Migration 机制完善 | ⏳ | 版本迭代频率增加时再完善 |
| **P2** | Fleet Dashboard / 趋势 / Capability Adoption | ⏳ | 至少 5–10 真实实例后 |
| **P3** | 统一应用生态（Photo/Growth/Study OS） | ⏳ | 应用成熟后再统一接入 FIM |

---

## 六、当前立即行动清单（P0 落地路径）

> 真实用户只有三个，且目前仅 Case-01 在本机跑通过。P0 的多数项依赖"另外两个实例真正执行"。

1. **发送统一升级通知**（已备：`RELEASES/upgrade-notice-1.0.1.md`）给 Case-01/02/03。
2. 三用户各自：
   - 升级到 Core 1.0.1（非强制，自愿）；
   - 填写 `PAIOS-Usage/profile.yaml`（work / personal / study）；
   - 运行 `collect_manifest.py` 生成 `manifest.yaml`。
3. Evan（开发者）**人工**收集三份 manifest → 产出 `fleet.md` 周报，验证：
   - FIM 设计在跨实例下是否成立；
   - 聚合需求是否真实（决定 Stage2 是否启动 aggregate.py）。
4. 据真实数据决定下一步，**不提前开发 Dashboard / Validator / Capability**。

---

## 七、一句话总结

> 这次的目标已不是设计新功能，而是为 PAIOS 建立"多实例持续演进机制"：**实例自治 · 平台统一 · 升级可控 · 观察轻量 · 聚合非侵入**。

就此收敛设计，先把三个真实实例跑通完整闭环（升级 → Manifest → 人工聚合 → 周报），再根据真实使用数据决定下一步。

---

**Related**: `ADR-0016-Multi-Instance-Architecture-Baseline.md` | `ADR-0013-Federated-Instance-Manifest.md` | `ADR-0014-Upgrade-Mechanism.md` | `ADR-0015-Federated-Aggregation-Viewing.md` | `RELEASES/upgrade-notice-1.0.1.md`
