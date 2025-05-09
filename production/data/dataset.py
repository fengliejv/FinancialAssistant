from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, JSON, ForeignKey, func
)
Base = declarative_base()

class PreferenceConfig(Base):
    __tablename__ = 'weekly_report_preference_config'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增ID')
    user_id = Column(String(50), nullable=False, comment='用户ID')
    config_name = Column(String(255), nullable=False, comment='配置名称')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    extra = Column(JSON, nullable=True, comment='扩展字段')

class PreferenceConfigDetail(Base):
    __tablename__ = 'weekly_report_preference_config_detail'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增ID')
    user_id = Column(String(50), nullable=False, comment='用户ID')
    config_id = Column(Integer, nullable=False, comment='配置ID')
    content = Column(Text, nullable=False, comment='内容')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    extra = Column(JSON, nullable=True, comment='扩展字段')

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WeeklyReport(Base):
    __tablename__ = 'weekly_report'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增ID')
    user_id = Column(String(50), nullable=False, comment='用户ID')
    user_name = Column(String(10), comment='用戶名')
    department = Column(String(100), comment='部门')
    item = Column(String(255), comment='事项')
    year = Column(Integer, nullable=False, comment='年')
    month = Column(Integer, nullable=False, comment='月')
    term = Column(Integer, nullable=False, comment='月内第几期')
    type = Column(Integer, nullable=False, comment='周报类型：1为个人，2为部门')
    work_this_week = Column(Text, comment='本周工作内容')
    plan_next_week = Column(Text, comment='下周工作计划')
    version = Column(Integer, comment='版本')
    status = Column(Integer, comment='0为未提交，1为已提交')
    raw_content = Column(Text, comment='原始内容')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    is_deleted = Column(Integer, default=0, comment='删除标记（0-未删除，1-已删除）')


from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'weekly_report_user'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增ID')
    username = Column(String(255), nullable=False, comment='用户名')
    department_id = Column(Integer, nullable=False, comment='部门ID')
    password = Column(String(255), nullable=False, comment='密码')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')
    is_deleted = Column(Integer, default=0, comment='删除标记（0-未删除，1-已删除）')
    extra = Column(JSON, nullable=True, comment='扩展字段')


class WeeklyReportTemplate(Base):
    __tablename__ = 'weekly_report_template'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增ID')
    username = Column(String(255), nullable=False, comment='用户名')
    department_id = Column(Integer, nullable=False, comment='部门ID')
    content = Column(Text, nullable=False, comment='内容')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')
    is_deleted = Column(Integer, default=0, comment='删除标记（0-未删除，1-已删除）')
    extra = Column(JSON, nullable=True, comment='扩展字段')

DATABASE_URL = (
    "mysql+pymysql://fusion-ai:lxR8uudwRX6C@106.63.7.106:11001/ai"
    "?charset=utf8mb4"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# db = 
def get_db():   
    return SessionLocal()