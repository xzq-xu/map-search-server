## 一个MCP Server


### 主要功能

- 查询关于MCP的awesome项目 支持翻页
    - 通过爬虫获取github上的awesome项目
    -（有没有不需要使用数据库的方案）
    - 【这一步获取可以在初始化的时候执行】下载awesome项目的README.md 到本地，解析到一个临时数据库（sqlite）
    - 通过sqlite查询项目
- 根据关键词查询MCP项目 支持翻页
    - 通过sqlite查询项目

- 提供安装MCP项目的服务  
    - 根据项目README.md 提供安装服务（具体为命令执行能力）
        - 支持命令执行 or 提供安装命令
- 提供MCP项目功能查询服务
    - 根据项目README.md 提供文档服务

- 今日MCP项目推荐

    
#### 

修改实现

维护一个专用的git仓库 （该仓库负责收集和分类各个mcpServer，记录mcpServer的项目地址、简介、分类，记录形式为分类markdown文档），通过简介和分类进行检索

在上述仓库的基础上提供搜索服务，具体实现待定（可能为爬取仓库文件，解析并获取简介、地址）

提供一个安装mcpServer的prompt，交由cursor等mcphost自己去  拉取项目、阅读项目readme、安装依赖、编写mcp.json配置 完成安装





