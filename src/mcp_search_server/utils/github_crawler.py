#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub爬虫模块
用于爬取GitHub上的MCP项目信息
"""

import aiohttp
import asyncio
import logging
import base64
from typing import Dict, List, Optional, Union
from datetime import datetime
import re
from bs4 import BeautifulSoup

class GitHubCrawler:
    """
    GitHub爬虫类
    负责从GitHub获取项目信息
    """
    
    def __init__(self, token: str, api_base_url: str = "https://api.github.com"):
        """
        初始化GitHub爬虫
        
        Args:
            token: GitHub API Token
            api_base_url: GitHub API基础URL
        """
        self.token = token
        self.api_base_url = api_base_url
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.logger = logging.getLogger("github_crawler")
        self.session = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            
    async def get_repo_info(self, owner: str, repo: str) -> Dict:
        """
        获取仓库基本信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            Dict: 仓库信息
        """
        url = f"{self.api_base_url}/repos/{owner}/{repo}"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                self.logger.error(f"Failed to get repo info: {response.status}")
                return {}
                
    async def get_readme(self, owner: str, repo: str) -> str:
        """
        获取仓库的README内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            str: README内容
        """
        url = f"{self.api_base_url}/repos/{owner}/{repo}/readme"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                content = data.get("content", "")
                if content:
                    return base64.b64decode(content).decode('utf-8')
            self.logger.error(f"Failed to get readme: {response.status}")
            return ""
            
    async def search_repos(self, query: str, page: int = 1, per_page: int = 30) -> Dict:
        """
        搜索GitHub仓库
        
        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            Dict: 搜索结果
        """
        url = f"{self.api_base_url}/search/repositories"
        params = {
            "q": query,
            "page": page,
            "per_page": per_page,
            "sort": "stars",
            "order": "desc"
        }
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                self.logger.error(f"Failed to search repos: {response.status}")
                return {"total_count": 0, "items": []}
                
    def parse_readme_content(self, content: str) -> Dict:
        """
        解析README内容，提取项目信息
        
        Args:
            content: README内容
            
        Returns:
            Dict: 解析后的项目信息
        """
        soup = BeautifulSoup(content, 'html.parser')
        
        # 提取标题
        title = soup.find('h1')
        title = title.text.strip() if title else ""
        
        # 提取描述
        description = ""
        for p in soup.find_all('p'):
            if len(p.text.strip()) > 30:  # 假设较长的段落是描述
                description = p.text.strip()
                break
                
        # 提取分类和标签
        categories = []
        tags = []
        for h2 in soup.find_all('h2'):
            categories.append(h2.text.strip())
            
        # 提取链接
        links = []
        for a in soup.find_all('a', href=True):
            if 'github.com' in a['href']:
                links.append(a['href'])
                
        return {
            "title": title,
            "description": description,
            "categories": categories,
            "tags": tags,
            "related_links": links
        }
        
    async def get_repo_stats(self, owner: str, repo: str) -> Dict:
        """
        获取仓库统计信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            Dict: 统计信息
        """
        info = await self.get_repo_info(owner, repo)
        return {
            "stars": info.get("stargazers_count", 0),
            "forks": info.get("forks_count", 0),
            "updated_at": info.get("updated_at", ""),
            "created_at": info.get("created_at", ""),
            "language": info.get("language", "")
        } 