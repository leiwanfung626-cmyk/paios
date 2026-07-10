# Reasonix 多模态传图规则

> 2026-07-09 定稿
> 背景：Reasonix 引擎会将多模态 content（含 image_url）直接发给所有模型，**不做内容裁剪**。
> 纯文本模型端点收到 `[{type:"text",...}, {type:"image_url",...}]` 会返回 HTTP 400。

## 模型能力对照表

| 模型 | 视觉能力 | 能否在 Reasonix 中传图 | 备注 |
|------|---------|----------------------|------|
| DeepSeek (v4-flash, v4-pro) | ❌ 纯文本 | **不能** | API 只接受 `type:"text"` |
| GLM-4V-plus | ✅ 视觉 | **能** | 已在 toml 标注 vision_models |
| glm5.2 | ✅ 视觉 | **能** | 已在 toml 标注 vision_models |

## 工作流规则

### 规则 1：纯文本模型（DeepSeek）不传图

DeepSeek 的 API 端点只接受 `content` 为字符串，不接受数组。
即使 toml 中 `vision_models = []`，Reasonix 引擎**也不会自动剥离 image_url**。

**做法**：
- 如果任务涉及图片分析，**不要使用 deepseek 模型**
- 在 skill 或 task 中显式指定视觉模型：`model = "glm/glm-4v-plus"`

### 规则 2：带图任务显式路由到视觉模型

Reasonix 支持在 task/skill 层面指定模型。带图时使用 `glm` provider：

```toml
# skill/task 配置示例
[model]
default = "glm/glm-4v-plus"   # 用 provider/model 格式
```

或模型透传名：`glm-4v-plus` / `glm5.2`

### 规则 3：视觉模型的正确后缀

| toml provider 名 | 可用模型名 |
|-----------------|-----------|
| `glm` | `glm/glm-4v-plus`, `glm/glm5.2` |

## 兜底出口

当 Reasonix 内部无法处理带图任务时，使用独立的视觉脚本：

```
python F:\PAIOS\40_AUTOMATION\05_SCRIPTS\vision_query.py ^
    --image <url或本地路径> ^
    --prompt "请描述这张图" ^
    --model glm-4v-plus
```

环境变量 `GLM_API_KEY`、`GLM_BASE_URL`、`GLM_VISION_MODEL` 控制连接参数。

## 如果又遇到 400 错误

1. 确认所用模型在 toml 中有 provider 定义
2. 检查该 provider 的 `vision_models` 是否包含了你的模型名
3. DeepSeek 系列必然 400 —— 纯文本模型，表传图
4. 如果确认模型支持视觉但仍 400 → Reasonix 引擎 bug，走兜底脚本
