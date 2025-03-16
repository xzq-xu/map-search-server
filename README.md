# MCP Search Server

!!!! 正在大幅修改中

一个强大的MCP（Model Context Protocol）项目搜索和管理服务器，帮助开发者更好地发现和使用MCP生态系统中的优秀项目。

## 功能特点

- 🔍 **智能搜索**
  - 支持关键词搜索MCP项目
  - 实现分页和排序功能
  - 提供高效的搜索性能

- 📚 **Awesome项目管理**
  - 自动收集GitHub上的Awesome MCP项目
  - 解析并管理项目信息
  - 提供项目分类浏览

- 🛠️ **安装服务**
  - 智能解析项目安装要求
  - 提供一键安装功能
  - 支持安装状态追踪

- 📖 **文档服务**
  - 自动生成项目API文档
  - 提供功能查询接口
  - 支持文档搜索

- 🎯 **智能推荐**
  - 每日优质项目推荐
  - 基于用户偏好的个性化推荐
  - 定期更新推荐内容

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/mcp-search.git
cd mcp-search

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制配置文件模板：
```bash
cp config.example.yaml config.yaml
```

2. 修改配置文件：
```yaml
github:
  token: "your_github_token"  # GitHub API Token
server:
  host: "127.0.0.1"
  port: 8000
```

### 运行

```bash
python main.py
```

访问 http://localhost:8000/docs 查看API文档。

## API接口

### 项目搜索
```http
GET /api/v1/search?q=关键词&page=1&size=10
```

### Awesome项目列表
```http
GET /api/v1/awesome?page=1&size=10
```

### 项目安装
```http
POST /api/v1/install
{
    "project_url": "https://github.com/username/project"
}
```

### 今日推荐
```http
GET /api/v1/recommendations
```

## 项目结构

```
mcp-search/
├── src/
│   ├── core/           # 核心功能模块
│   ├── api/            # API接口
│   ├── services/       # 业务服务
│   ├── models/         # 数据模型
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── docs/               # 文档
├── config/             # 配置文件
└── scripts/            # 脚本工具
```

## 开发计划

详见 [development_plan.md](development_plan.md)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系我们

- 项目问题请提交 [Issue](https://github.com/yourusername/mcp-search/issues)
- 其他问题请发送邮件至：your.email@example.com
