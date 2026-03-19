# LongCat API 配置指南

## 概述

myPAW 现已支持 LongCat API 开放平台，兼容 OpenAI API 格式。本指南将帮助您正确配置和使用 LongCat API。

## API 端点

LongCat API 开放平台提供两种格式的 API 端点：

### OpenAI 格式 (推荐)
- **端点**: `https://api.longcat.chat/openai`
- **兼容性**: 完全兼容 OpenAI API 规范
- **接口**: `/v1/chat/completions`

### Anthropic 格式
- **端点**: `https://api.longcat.chat/anthropic`
- **兼容性**: 兼容 Anthropic Claude API 规范
- **接口**: `/v1/messages`

## 支持的模型

| 模型名称 | API格式 | 描述 | 推荐用途 |
|---------|---------|------|----------|
| LongCat-Flash-Chat | OpenAI/Anthropic | 高性能通用对话模型 | 一般对话、问答 |
| LongCat-Flash-Thinking | OpenAI/Anthropic | 深度思考模型 | 复杂推理、分析 |
| LongCat-Flash-Thinking-2601 | OpenAI/Anthropic | 升级版深度思考模型 | **推荐** - 最佳性能 |
| LongCat-Flash-Lite | OpenAI/Anthropic | 高效轻量化MoE模型 | 快速响应、简单任务 |

## 配置步骤

### 1. 获取 API 密钥
1. 访问 [LongCat API 开放平台](https://api.longcat.chat)
2. 注册账号并获取 API 密钥
3. 确保账户有足够的额度

### 2. 配置环境变量
创建或编辑 `.env` 文件：

```bash
# LongCat API 密钥
LLM_API_KEY=your_longcat_api_key_here

# API 端点 (使用 OpenAI 格式)
LLM_API_BASE=https://api.longcat.chat/openai

# 使用的模型 (推荐 LongCat-Flash-Thinking-2601)
LLM_MODEL=LongCat-Flash-Thinking-2601
```

### 3. 验证配置
运行桌面端程序，如果配置正确，您将看到：
- 状态栏显示 "系统就绪 | 已连接 LongCat-Flash-Thinking-2601"
- 可以正常发送消息并获得回复

## API 调用示例

### OpenAI 格式请求
```http
POST https://api.longcat.chat/openai/v1/chat/completions
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "model": "LongCat-Flash-Thinking-2601",
  "messages": [
    {"role": "system", "content": "你是一个AI助手"},
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### Anthropic 格式请求
```http
POST https://api.longcat.chat/anthropic/v1/messages
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "model": "LongCat-Flash-Thinking-2601",
  "max_tokens": 1024,
  "temperature": 0.7,
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
```

## 常见问题

### Q: API 调用失败，返回 401 错误
A: 检查 `LLM_API_KEY` 是否正确配置，确保没有多余的空格或特殊字符。

### Q: API 调用失败，返回 404 错误
A: 检查 `LLM_API_BASE` 是否正确，确保使用完整的 URL。

### Q: 模型名称无效
A: 确保使用的模型名称在支持列表中，推荐使用 `LongCat-Flash-Thinking-2601`。

### Q: 响应速度慢
A: 尝试使用 `LongCat-Flash-Lite` 模型，或者检查网络连接。

## 性能优化建议

1. **选择合适的模型**: 
   - 复杂任务使用 `LongCat-Flash-Thinking-2601`
   - 简单任务使用 `LongCat-Flash-Lite`

2. **调整参数**:
   - `temperature`: 控制创造性，0.7 为推荐值
   - `max_tokens`: 控制响应长度，1024 为推荐值

3. **网络优化**:
   - 确保稳定的网络连接
   - 考虑使用有线连接以获得更好的稳定性

## 故障排除

### 日志查看
桌面端会显示详细的错误信息，包括：
- API 调用状态
- 错误代码和消息
- 网络连接状态

### 测试 API 连接
可以使用 curl 命令测试 API 连接：

```bash
curl -X POST "https://api.longcat.chat/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "model": "LongCat-Flash-Thinking-2601",
    "messages": [{"role": "user", "content": "测试"}],
    "max_tokens": 10
  }'
```

## 技术支持

如果遇到问题，请检查：
1. API 密钥是否有效
2. 网络连接是否正常
3. 模型名称是否正确
4. API 配额是否充足

更多技术支持请访问 [LongCat API 开放平台文档](https://api.longcat.chat/docs)。