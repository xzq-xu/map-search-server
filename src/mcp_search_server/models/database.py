#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库模型
定义项目相关的数据库表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 项目-分类关联表
project_category = Table(
    'project_category',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# 项目-标签关联表
project_tag = Table(
    'project_tag',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Project(Base):
    """项目表"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    repo_url = Column(String(200), unique=True, nullable=False)
    readme_content = Column(String(10000))
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    language = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    last_crawled_at = Column(DateTime)
    search_score = Column(Float, default=0.0)  # 用于搜索排序
    
    # 关系
    categories = relationship("Category", secondary=project_category, back_populates="projects")
    tags = relationship("Tag", secondary=project_tag, back_populates="projects")

class Category(Base):
    """分类表"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    projects = relationship("Project", secondary=project_category, back_populates="categories")

class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    projects = relationship("Project", secondary=project_tag, back_populates="tags")

def init_db(database_url: str = None):
    """
    初始化数据库
    
    Args:
        database_url: 数据库URL，如果不提供则使用默认的SQLite数据库
        
    Returns:
        SQLAlchemy engine实例
    """
    import os
    from pathlib import Path
    
    if database_url is None:
        # 确保data目录存在
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 使用默认的SQLite数据库
        database_url = "sqlite:///data/mcp_search.db"
    
    # 检查数据库类型
    db_type = database_url.split(":")[0].lower()
    
    # 根据数据库类型设置不同的engine参数
    engine_kwargs = {
        "echo": False  # 默认不输出SQL语句
    }
    
    if db_type == "sqlite":
        # SQLite特定配置
        engine_kwargs.update({
            "connect_args": {"check_same_thread": False},  # 允许多线程访问
        })
    
    engine = create_engine(database_url, **engine_kwargs)
    Base.metadata.create_all(engine)
    return engine 