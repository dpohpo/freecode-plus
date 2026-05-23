---
name: backend-dev
description: 后端开发专家系统。当用户需要开发后端 API、数据库设计、服务器架构、微服务、或者处理后端相关任务时使用。支持：Node.js/Python/Go/Rust 等主流后端技术栈，RESTful API 设计，数据库建模，认证授权，性能优化，测试部署等全栈后端开发。
user-invocable: "true"
---

# 后端开发专家系统

专业的后端开发助手，覆盖从 API 设计到部署的全流程。

## 技术栈支持

| 语言 | 框架 | 适用场景 |
|------|------|----------|
| **Node.js** | Express, Fastify, NestJS | 高并发 API、实时应用 |
| **Python** | FastAPI, Django, Flask | 数据处理、AI 服务、快速开发 |
| **Go** | Gin, Echo, gRPC | 高性能服务、微服务 |
| **Rust** | Actix, Rocket | 系统级性能要求 |

## 开发流程

### 1. API 设计

遵循 RESTful 最佳实践：

```
GET    /api/v1/resources       # 列表
GET    /api/v1/resources/:id   # 详情
POST   /api/v1/resources       # 创建
PUT    /api/v1/resources/:id   # 全量更新
PATCH  /api/v1/resources/:id   # 部分更新
DELETE /api/v1/resources/:id   # 删除
```

**API 设计原则**：
- 使用名词复数形式 (`/users` 不是 `/user`)
- 使用标准 HTTP 方法
- 版本控制通过 URL (`/api/v1/`)
- 统一响应格式
- 合理使用状态码

### 2. 数据库设计

#### 数据建模步骤

1. **识别实体**：确定核心业务实体
2. **定义关系**：一对一、一对多、多对多
3. **规范化**：消除冗余，保证数据一致性
4. **索引优化**：为查询字段添加索引
5. **约束设计**：主键、外键、唯一约束

#### 命名规范

```sql
-- 表名：snake_case 复数
CREATE TABLE user_profiles (...);

-- 字段名：snake_case
user_id, created_at, is_active

-- 索引名：idx_表名_字段名
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
```

### 3. 认证授权

#### JWT 认证流程

```
1. 用户登录 → 验证凭证
2. 生成 JWT Token (包含用户信息)
3. 返回 Token 给客户端
4. 客户端每次请求携带 Token
5. 服务器验证 Token 有效性
```

**JWT Token 结构**：
```json
{
  "user_id": "123",
  "role": "admin",
  "exp": 1234567890
}
```

#### RBAC 权限模型

```
用户 → 角色 → 权限

权限定义格式：
  resource:action:scope

示例：
  user:read:all        # 读取所有用户
  user:write:own       # 写入自己的数据
  article:delete:all   # 删除所有文章
```

### 4. 错误处理

#### 统一错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "request_id": "req_abc123"
}
```

#### HTTP 状态码使用

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 验证失败 |
| 429 | Too Many Requests | 限流 |
| 500 | Internal Server Error | 服务器错误 |

### 5. 性能优化

#### 数据库优化

```sql
-- 使用索引
CREATE INDEX idx_users_email ON users(email);

-- 避免 SELECT *
SELECT id, name, email FROM users;

-- 使用分页
SELECT * FROM posts LIMIT 20 OFFSET 0;

-- 使用连接池
-- 配置：pool_size = max_connections * 1.5
```

#### 缓存策略

```
缓存层级：
1. 客户端缓存 (ETag/Last-Modified)
2. CDN 缓存 (静态资源)
3. 应用缓存 (Redis/Memcached)
4. 数据库缓存 (查询缓存)

缓存失效策略：
- TTL：自动过期
- LRU：最近最少使用
- 主动失效：数据更新时清除
```

### 6. 测试

#### 测试金字塔

```
       /\
      /E2E\        少量端到端测试
     /------\
    /集成测试 \     适量 API 集成测试
   /----------\
  /  单元测试   \    大量单元测试
 /--------------\
```

#### 测试示例 (Node.js + Jest)

```javascript
// 单元测试
describe('User.validate', () => {
  it('should reject invalid email', () => {
    expect(() => User.validate({ email: 'invalid' }))
      .toThrow('Invalid email');
  });
});

// 集成测试
describe('POST /api/users', () => {
  it('should create a new user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', password: 'secure123' });

    expect(response.status).toBe(201);
    expect(response.body.data.email).toBe('test@example.com');
  });
});
```

### 7. 部署

#### Docker 化

```dockerfile
# Node.js 示例
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

#### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

## 代码模板

### Express.js API 模板

```javascript
import express from 'express';
import { authMiddleware } from './middleware/auth.js';
import { validate } from './middleware/validate.js';
import { errorHandler } from './middleware/errorHandler.js';

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: Date.now() });
});

// API 路由
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/users', authMiddleware, userRoutes);
app.use('/api/v1/posts', authMiddleware, postRoutes);

// 错误处理
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### FastAPI 模板

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

app = FastAPI(title="My API", version="1.0.0")

# 数据模型
class UserCreate(BaseModel):
    email: str
    name: str

class User(BaseModel):
    id: int
    email: str
    name: str

# 路由
@app.get("/users", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100):
    return await get_users(skip=skip, limit=limit)

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    return await create_user_in_db(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 安全最佳实践

1. **输入验证**：始终验证和清理用户输入
2. **SQL 注入防护**：使用参数化查询
3. **XSS 防护**：转义输出内容
4. **CSRF 防护**：使用 CSRF Token
5. **HTTPS**：生产环境强制 HTTPS
6. **密钥管理**：使用环境变量，不硬编码密钥
7. **限流**：防止 DDoS 攻击
8. **日志脱敏**：不记录敏感信息

## 监控和日志

### 结构化日志

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "message": "User login",
  "user_id": "123",
  "ip": "192.168.1.1",
  "request_id": "req_abc123"
}
```

### 关键指标监控

- 请求响应时间 (p50, p95, p99)
- 错误率
- 请求吞吐量 (QPS)
- 数据库连接数
- 内存使用率
- CPU 使用率

---

现在开始后端开发。请告诉我：
1. 技术栈选择 (Node.js/Python/Go/Rust)
2. 项目类型 (API/微服务/定时任务等)
3. 具体需求
