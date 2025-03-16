#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目服务
处理项目相关的数据库操作
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.database import Project, Category, Tag

class ProjectService:
    """项目服务类"""
    
    def __init__(self, session: Session):
        """
        初始化项目服务
        
        Args:
            session: 数据库会话
        """
        self.session = session
        
    def create_project(self, project_data: Dict) -> Project:
        """
        创建新项目
        
        Args:
            project_data: 项目数据
            
        Returns:
            Project: 创建的项目
        """
        project = Project(
            name=project_data["name"],
            description=project_data["description"],
            repo_url=project_data["repo_url"],
            readme_content=project_data.get("readme_content", ""),
            stars=project_data.get("stars", 0),
            forks=project_data.get("forks", 0),
            language=project_data.get("language", ""),
            last_crawled_at=datetime.utcnow()
        )
        
        # 处理分类
        for category_name in project_data.get("categories", []):
            category = self.session.query(Category).filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                self.session.add(category)
            project.categories.append(category)
            
        # 处理标签
        for tag_name in project_data.get("tags", []):
            tag = self.session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
            project.tags.append(tag)
            
        self.session.add(project)
        self.session.commit()
        return project
        
    def update_project(self, project_id: int, project_data: Dict) -> Optional[Project]:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            project_data: 更新的数据
            
        Returns:
            Optional[Project]: 更新后的项目
        """
        project = self.session.query(Project).get(project_id)
        if not project:
            return None
            
        # 更新基本信息
        for key, value in project_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
                
        project.updated_at = datetime.utcnow()
        self.session.commit()
        return project
        
    def search_projects(
        self,
        query: str,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        搜索项目
        
        Args:
            query: 搜索关键词
            page: 页码
            size: 每页大小
            category: 分类
            tags: 标签列表
            
        Returns:
            Dict: 搜索结果
        """
        # 基础查询
        base_query = self.session.query(Project)
        
        # 关键词搜索
        if query:
            base_query = base_query.filter(
                or_(
                    Project.name.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                    Project.readme_content.ilike(f"%{query}%")
                )
            )
            
        # 分类过滤
        if category:
            base_query = base_query.join(Project.categories).filter(Category.name == category)
            
        # 标签过滤
        if tags:
            for tag in tags:
                base_query = base_query.join(Project.tags).filter(Tag.name == tag)
                
        # 计算总数
        total = base_query.count()
        
        # 分页
        projects = base_query.order_by(Project.stars.desc())\
            .offset((page - 1) * size)\
            .limit(size)\
            .all()
            
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [self._project_to_dict(p) for p in projects]
        }
        
    def _project_to_dict(self, project: Project) -> Dict:
        """
        将项目对象转换为字典
        
        Args:
            project: 项目对象
            
        Returns:
            Dict: 项目信息字典
        """
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "repo_url": project.repo_url,
            "stars": project.stars,
            "forks": project.forks,
            "language": project.language,
            "categories": [c.name for c in project.categories],
            "tags": [t.name for t in project.tags],
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        } 