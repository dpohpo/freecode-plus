# 火山引擎豆包语音 API 凭证配置指南

## 概述
本 skill 记录获取火山引擎豆包语音实时通话所需全部凭证的完整流程。

## 所需凭证清单

| 凭证名 | 用途 | 来源 |
|--------|------|------|
| ASR_APP_ID | 语音识别应用ID | 语音技术产品控制台 |
| ASR_ACCESS_TOKEN | 语音识别访问令牌 | 语音技术产品控制台 |
| TTS_APP_ID | 语音合成应用ID | 语音技术产品控制台（与ASR共用） |
| TTS_ACCESS_TOKEN | 语音合成访问令牌 | 语音技术产品控制台（与ASR共用） |
| ARK_API_KEY | 方舟API密钥 | 火山方舟控制台 |
| LLM_ENDPOINT_ID | 大模型接入点ID | 火山方舟在线推理 |

---

## 第一部分：语音 API 凭证（ASR/TTS）

### 前置条件
1. 完成企业认证：https://console.volcengine.com/user/authentication/detail/
2. 开通语音技术产品：https://console.volcengine.com/speech/app

### 步骤

#### 1. 创建应用
1. 访问：https://console.volcengine.com/speech/app
2. 点击「创建应用」
3. **关键**：同时勾选以下两个服务：
   - ✅ 大模型语音合成
   - ✅ 流式语音识别大模型
4. 填写应用名称（如：`nano`）

#### 2. 开通语音合成大模型
1. 创建应用后，进入应用详情
2. 找到「语音合成大模型」
3. 点击「开通」
4. **注意**：开通后需要等待 5-10 分钟才能使用

#### 3. 获取 APP ID 和 Access Token
1. 在应用列表页面：https://console.volcengine.com/speech/app
2. 找到创建的应用
3. 复制 **APP ID** → 这就是 `ASR_APP_ID` 和 `TTS_APP_ID`
4. 点击 **Access Token** 旁边的眼睛图标显示明文
5. 复制 **Access Token** → 这就是 `ASR_ACCESS_TOKEN` 和 `TTS_ACCESS_TOKEN`

### 已踩过的坑

#### 坑1：Access Token 和 Secret Key 是两个不同的东西
- Access Token：用于 API 调用认证（我们需要这个）
- Secret Key：用于签名认证（不是我们需要的）
- **教训**：不要混淆这两个字段

#### 坑2：点击眼睛图标会互相隐藏
- 点击 Access Token 的眼睛会显示 Access Token
- 再点击 Secret Key 的眼睛会隐藏 Access Token
- **解决方案**：每次只点击一个眼睛，复制完再点击另一个

#### 坑3：ASR 和 TTS 共用同一套凭证
- 不需要分别创建两个应用
- 一个应用同时勾选两个服务即可
- APP ID 和 Access Token 完全相同

---

## 第二部分：方舟 API 凭证（ARK_API_KEY）

### 步骤

#### 1. 获取 API Key
1. 访问：https://console.volcengine.com/ark/region:ark+cn-beijing/api-key
2. 点击「创建 API Key」
3. **重要**：API Key 只显示一次，立即复制保存
4. 格式示例：`ark-xxxxxxxxxxxxxxxx`

#### 2. 配置环境变量
```bash
export ARK_API_KEY="你的API Key"
```

或写入 `~/.zshrc` 永久生效：
```bash
echo 'export ARK_API_KEY="你的API Key"' >> ~/.zshrc
source ~/.zshrc
```

---

## 第三部分：LLM Endpoint ID

### 步骤

#### 1. 创建接入点
1. 访问：https://console.volcengine.com/ark/region:ark+cn-beijing/inference-online
2. 点击「创建推理接入点」
3. 选择模型：**Doubao-pro-32k**
4. 完成创建

#### 2. 获取 Endpoint ID
1. 在接入点列表中找到创建的接入点
2. 复制 **Endpoint ID**
3. 格式示例：`ep-xxxxxxxxxxxxxxxx`

---

## 第四部分：配置项目

### handler.py 配置
文件位置：`~/projects/ai-app-lab/demohouse/live_voice_call/backend/handler.py`

```python
# replace with your asr API access
ASR_ACCESS_TOKEN = "你的Access Token"
ASR_APP_ID = "你的APP ID"
# replace with your tts API access
TTS_ACCESS_TOKEN = "你的Access Token"  # 与ASR相同
TTS_APP_ID = "你的APP ID"  # 与ASR相同
# replace with your ark endpoint
LLM_ENDPOINT_ID = "你的Endpoint ID"
```

### 环境变量配置
```bash
export ARK_API_KEY="你的API Key"
```

---

## 当前已配置凭证

| 凭证 | 值 |
|------|-----|
| ASR_APP_ID | 8814415262 |
| ASR_ACCESS_TOKEN | QO7nYwtWrNLprElGLhsX80-w7EIxkXr_ |
| TTS_APP_ID | 8814415262 |
| TTS_ACCESS_TOKEN | QO7nYwtWrNLprElGLhsX80-w7EIxkXr_ |
| ARK_API_KEY | ⏳ 待用户输入 |
| LLM_ENDPOINT_ID | ⏳ 待用户输入 |

---

## 快速命令

### 启动后端服务
```bash
cd ~/projects/ai-app-lab/demohouse/live_voice_call/backend
source .venv/bin/activate 2>/dev/null || python -m venv .venv && source .venv/bin/activate
pip install poetry==1.6.1 -q
poetry install
poetry run python -m handler
```

### 启动前端服务
```bash
cd ~/projects/ai-app-lab/demohouse/live_voice_call/frontend
pnpm install
pnpm run dev
```

### 访问应用
打开 http://localhost:8080

---

## 相关链接汇总

| 页面 | URL |
|------|-----|
| 语音技术控制台 | https://console.volcengine.com/speech/app |
| API Key 管理 | https://console.volcengine.com/ark/region:ark+cn-beijing/api-key |
| 在线推理（Endpoint） | https://console.volcengine.com/ark/region:ark+cn-beijing/inference-online |
| 企业认证 | https://console.volcengine.com/user/authentication/detail/ |
| API Key 签名文档 | https://www.volcengine.com/docs/82379/1298459 |
| 创建 Endpoint 文档 | https://www.volcengine.com/docs/82379/1099522 |
