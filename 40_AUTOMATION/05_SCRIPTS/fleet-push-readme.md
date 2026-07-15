# PAIOS Fleet Manifest Exchange

## 架构

依据 ADR-0015/0017，Fleet 不属于 Developer Repository，**不进入 Git**。
实例间状态同步通过 **FleetExchange** 目录在独立通道上完成。

```
FleetExchange/              <-- 共享交换区（Quark/Tailscale/LAN）
  Case-01/
    manifest.yaml           <-- Case-01 写入，Case-02/03 读取
  Case-02/
    manifest.yaml           <-- Case-02 写入，Case-01/03 读取
  Case-03/
    manifest.yaml           <-- Case-03 写入，Case-01/02 读取
```

## Case-02 每日推送

### 脚本

```
40_AUTOMATION\05_SCRIPTS\fleet-push-case-02.bat
```

### 执行效果

| 输出目标 | 路径 | 策略 |
|---------|------|------|
| 共享交换区 | `E:\FleetExchange\Case-02\manifest.yaml` | 始终覆盖 |
| 本地归档 | `PAIOS\Fleet\cases\case-02-YYYYMMDD.yaml` | 每日副本 |
| 本地最新 | `PAIOS\Fleet\cases\case-02.yaml` | 始终覆盖 |

### Windows Task Scheduler 配置

1. 打开 `taskschd.msc`
2. 创建任务：
   - **名称：** `PAIOS Case-02 Daily Fleet Push`
   - **触发器：** 每天，时间自定（如 21:00）
   - **操作：** 启动 `C:\Windows\System32\cmd.exe`
   - **参数：** `/c "E:\PAIOS\40_AUTOMATION\05_SCRIPTS\fleet-push-case-02.bat"`
   - **起始于：** `E:\PAIOS`
3. 确定

### 跨实例同步

FleetExchange 目录需要放在 Case-01 和 Case-02 都能访问的共享通道上：

| 通道 | 说明 |
|------|------|
| **夸克云盘** | 将 `E:\FleetExchange\` 设为夸克同步目录 |
| **Tailscale** | 两机内网互通后，直接文件共享 |
| **局域网共享** | SMB 共享文件夹 |
| **USB 离线交换** | 离线环境下手动复制 |

### 运行日志

```
PAIOS\Fleet\logs\fleet-push-YYYYMMDD.log
```

## 输出示例

```yaml
instance:
  id: case-02
  role: personal

platform:
  version: v1.0.1

status:
  last_sync: "2026-07-12"
  health: healthy

evidence:
  - object: PILOT-ROLE-VALIDATION
    level: Validated
    note: "Case-02 Developer role: synchronized to baseline v1.1.0-pilot-baseline"
```

## 相关 ADR

| ADR | 状态 | 内容 |
|-----|------|------|
| ADR-0013 | Implemented | Federated Instance Manifest 作为 Fleet 通信层 |
| ADR-0015 | Enforced | Fleet 不属于 Developer Repository |
| ADR-0017 | Enforced | 平台仓库纯净化，运行时状态与代码分离 |
