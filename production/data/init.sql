-- 配置表
CREATE TABLE weekly_report_preference_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    user_id VARCHAR(50) COMMENT '用户ID',
    config_name VARCHAR(255) NOT NULL COMMENT '配置名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    extra JSON NULL COMMENT '扩展字段',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置表';


-- 配置详情表
CREATE TABLE weekly_report_preference_config_detail (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    user_id VARCHAR(50) COMMENT '用户ID',
    config_id INT NOT NULL COMMENT '配置ID',
    content TEXT NOT NULL COMMENT '内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    extra JSON NULL COMMENT '扩展字段',
    INDEX idx_user_id (user_id),
    INDEX idx_config_id (config_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配置详情表';




CREATE TABLE weekly_report (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    user_id VARCHAR(50) COMMENT '用户ID',
    user_name VARCHAR(10) COMMENT '用户名',
    department VARCHAR(100) NOT NULL COMMENT '部门',
    item VARCHAR(255) NOT NULL COMMENT '事项',
    year INT NOT NULL COMMENT '年',
    month INT NOT NULL COMMENT '月',
    term INT NOT NULL COMMENT '月内第几期',
    work_this_week TEXT COMMENT '本周工作内容',
    plan_next_week TEXT COMMENT '下周工作计划',
    version INT COMMENT '版本',
    status INT COMMENT '状态，默认为0，1为已提交',
    type INT COMMENT '周报类型，1为个人周报，2为部门',
    raw_content TEXT COMMENT '原始内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    extra JSON NULL COMMENT '扩展字段',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '删除标记（0-未删除，1-已删除）',
    INDEX idx_user_id (user_id),
    INDEX idx_department (department),
    INDEX idx_year_month_term (year, month, term)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='周报表';


CREATE TABLE weekly_report_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    username VARCHAR(255) NOT NULL COMMENT '用户名',
    department_id INT NOT NULL COMMENT '部门ID',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '删除标记（0-未删除，1-已删除）',
    extra JSON NULL COMMENT '扩展字段',
    INDEX idx_username (username),
    INDEX idx_department_id (department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


CREATE TABLE weekly_report_template (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    username VARCHAR(255) NOT NULL COMMENT '用户名',
    department_id INT NOT NULL COMMENT '部门ID',
    type INT COMMENT '模板类型。1为部门关键事项模板，2为部门工作事项模板',
    content TEXT NOT NULL COMMENT '内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '删除标记（0-未删除，1-已删除）',
    extra JSON NULL COMMENT '扩展字段',
    INDEX idx_username (username),
    INDEX idx_department_id (department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='周报模板表';





