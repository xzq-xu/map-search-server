#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Search Server
核心服务器实现
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import sessionmaker
from ..models.database import init_db
from ..services.project_service import ProjectService
from ..utils.github_crawler import GitHubCrawler
import asyncio
from datetime import datetime

class MCPSearchServer:
    """
    MCP搜索服务器
    实现MCP项目的搜索、管理和推荐功能
    """
    
    def __init__(self, server_name: str = "mcp-search-server", config: Dict = None):
        """
        初始化MCP搜索服务器
        
        Args:
            server_name: 服务器名称
            config: 配置信息，如果不提供则使用默认配置
        """
        self.server_name = server_name
        self.config = config or {}
        self.mcp = FastMCP(server_name)
        self.logger = logging.getLogger(server_name)
        
        # 初始化数据库
        database_config = self.config.get("database", {})
        database_url = database_config.get("url")
        self.engine = init_db(database_url)  # 如果url为None，将使用默认SQLite
        self.Session = sessionmaker(bind=self.engine)
        
        # 初始化GitHub爬虫
        self.github_token = self.config.get("github", {}).get("token")
        if not self.github_token:
            self.logger.warning("GitHub token not provided, some features may be limited")
            
        self._setup_tools()
        self._setup_resources()
        
    def _setup_tools(self):
        """
        设置MCP工具
        包括搜索、安装等功能
        """
        self._setup_search_tools()
        self._setup_install_tools()
        self._setup_recommendation_tools()
        
    def _setup_search_tools(self):
        """设置搜索相关工具"""
        
        @self.mcp.tool()
        async def search_projects(query: str, page: int = 1, size: int = 10, category: str = None) -> Dict:
            """
            搜索MCP项目
            
            Args:
                query: 搜索关键词
                page: 页码
                size: 每页大小
                category: 分类
                
            Returns:
                Dict: 搜索结果
            """
            session = self.Session()
            try:
                project_service = ProjectService(session)
                results = project_service.search_projects(
                    query=query,
                    page=page,
                    size=size,
                    category=category
                )
                return results
            finally:
                session.close()
            
        @self.mcp.tool()
        async def list_awesome_projects(page: int = 1, size: int = 10) -> Dict:
            """
            获取Awesome MCP项目列表
            
            Args:
                page: 页码
                size: 每页大小
                
            Returns:
                Dict: 项目列表
            """
            session = self.Session()
            try:
                project_service = ProjectService(session)
                results = project_service.search_projects(
                    query="",
                    page=page,
                    size=size,
                    category="awesome-mcp"
                )
                return results
            finally:
                session.close()
                
        @self.mcp.tool()
        async def refresh_projects(force: bool = False) -> Dict:
            """
            刷新项目数据
            
            Args:
                force: 是否强制刷新所有项目
                
            Returns:
                Dict: 刷新结果
            """
            try:
                async with GitHubCrawler(self.github_token) as crawler:
                    # 搜索MCP相关项目
                    search_results = await crawler.search_repos("topic:mcp-project")
                    
                    session = self.Session()
                    try:
                        project_service = ProjectService(session)
                        updated = 0
                        new = 0
                        
                        for item in search_results.get("items", []):
                            owner, repo = item["full_name"].split("/")
                            
                            # 获取项目详细信息
                            readme = await crawler.get_readme(owner, repo)
                            stats = await crawler.get_repo_stats(owner, repo)
                            
                            # 解析README
                            project_info = crawler.parse_readme_content(readme)
                            
                            # 准备项目数据
                            project_data = {
                                "name": item["name"],
                                "description": item["description"] or project_info["description"],
                                "repo_url": item["html_url"],
                                "readme_content": readme,
                                "stars": stats["stars"],
                                "forks": stats["forks"],
                                "language": stats["language"],
                                "categories": project_info["categories"],
                                "tags": project_info["tags"]
                            }
                            
                            # 创建或更新项目
                            project = project_service.create_project(project_data)
                            if project:
                                new += 1
                            else:
                                updated += 1
                                
                        return {
                            "status": "success",
                            "new_projects": new,
                            "updated_projects": updated,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    finally:
                        session.close()
            except Exception as e:
                self.logger.error(f"Failed to refresh projects: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        # 设置refresh_projects工具
        # self.refresh_projects = refresh_projects;

            
    def _setup_install_tools(self):
        """设置安装相关工具"""
        
        @self.mcp.tool()
        def install_project(project_url: str) -> Dict:
            """
            安装MCP项目
            
            Args:
                project_url: 项目地址
                
            Returns:
                Dict: 安装结果
            """
            # TODO: 实现项目安装逻辑
            return {
                "status": "pending",
                "message": "Installation started"
            }
            
    def _setup_recommendation_tools(self):
        """设置推荐相关工具"""
        
        @self.mcp.tool()
        def get_daily_recommendations() -> List[Dict]:
            """
            获取每日推荐项目
            
            Returns:
                List[Dict]: 推荐项目列表
            """
            session = self.Session()
            try:
                project_service = ProjectService(session)
                results = project_service.search_projects(
                    query="",
                    page=1,
                    size=5,
                    category=None
                )
                return results["items"]
            finally:
                session.close()
            
    def _setup_resources(self):
        """
        设置MCP资源
        包括每日推荐、统计信息等
        """
        
        @self.mcp.resource("daily://recommendations")
        def get_daily_recommendations_resource() -> str:
            """
            获取每日推荐项目资源
            """
            session = self.Session()
            try:
                project_service = ProjectService(session)
                results = project_service.search_projects(
                    query="",
                    page=1,
                    size=5,
                    category=None
                )
                
                # 生成Markdown格式的推荐列表
                markdown = "# 今日推荐MCP项目\n\n"
                for project in results["items"]:
                    markdown += f"## {project['name']}\n"
                    markdown += f"{project['description']}\n\n"
                    markdown += f"- Stars: {project['stars']}\n"
                    markdown += f"- Language: {project['language']}\n"
                    markdown += f"- URL: {project['repo_url']}\n\n"
                
                return markdown
            finally:
                session.close()
            
        @self.mcp.resource("stats://overview")
        def get_stats_overview() -> str:
            """
            获取MCP项目统计信息
            """
            session = self.Session()
            try:
                project_service = ProjectService(session)
                results = project_service.search_projects(query="", page=1, size=1)
                
                return f"""
                # MCP项目统计
                
                - 总项目数: {results['total']}
                - 今日新增: {0}  # TODO: 实现新增统计
                - 本周热门: {results['items'][0]['name'] if results['items'] else '暂无'}
                """
            finally:
                session.close()
            
    def start(self):
        """
        启动MCP服务器
        
        Args:
            host: 服务器地址
            port: 服务器端口
        """
        self.logger.info(f"Starting MCP Search Server")
        
        # 启动时刷新项目数据
        # asyncio.create_task( self.refresh_projects())
        
        self.mcp.run()
        
    def stop(self):
        """
        停止MCP服务器
        """
        self.logger.info("Stopping MCP Search Server")
        # 关闭数据库连接
        self.engine.dispose() 