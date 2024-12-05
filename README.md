# CMDB 资产管理系统

一个现代化的 IT 资产管理系统，基于 Django 开发，用于管理数据中心的各类设备资源。

## 功能特点

### 数据中心管理
- 数据中心基本信息管理（名称、位置、联系人等）
- 数据中心资源统计（面积、电力容量、制冷能力）
- 直观的设备统计展示
- 设备关联管理

### 设备管理
- 服务器管理
  - 硬件信息（CPU、内存、硬盘等）
  - 系统信息（操作系统、业务系统）
  - 网络信息（IP地址、MAC地址）

- 网络设备管理
  - 设备类型
  - 端口信息
  - 网络配置

- 存储设备管理
  - 存储类型
  - 容量管理
  - RAID配置

- 安全设备管理
  - 设备类型
  - 规则版本
  - 安全配置

### 通用功能
- 批量导入/导出（Excel格式）
- 批量删除
- 历史记录追踪
- 权限管理
- 搜索和过滤
- 分页显示

## 技术栈

### 后端
- Python 3.8+
- Django 5.1.3
- Django REST framework
- MySQL 数据库

### 前端
- Bootstrap 5
- Font Awesome 图标
- JavaScript/jQuery
- AJAX 异步请求

### 第三方库
- django-filter：用于实现过滤功能
- django-import-export：用于Excel导入导出
- django-simple-history：用于记录数据变更历史
- mysqlclient：MySQL数据库驱动
- python-dotenv：环境变量管理

## 安装部署

### 环境要求
- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- 操作系统：支持 Linux、Windows、macOS

### 安装步骤

1. 克隆项目
```bash
git clone [https://github.com/sjxixi/AAA.git]
cd cmdb
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
```bash
# 创建 .env 文件并配置数据库连接信息
DB_NAME=cmdb
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

5. 初始化数据库
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. 运行开发服务器
```bash
python manage.py runserver
```

## 使用说明

### 基本操作流程

1. 数据中心管理
   - 创建数据中心
   - 设置基本信息
   - 查看设备统计

2. 设备管理
   - 添加各类设备
   - 设置设备参数
   - 关联到数据中心

3. 批量操作
   - 使用Excel模板批量导入
   - 选择设备批量导出
   - 批量删除设备

### 权限说明

- 超级管理员：具有所有操作权限
- 普通用户：
  - 查看权限：可以查看所有资源
  - 编辑权限：可以编辑设备信息
  - 删除权限：可以删除设备
  - 导入导出权限：可以进行批量操作

## 开发说明

### 项目结构
```
cmdb/
├── assets/                 # 资产管理应用
│   ├── models/            # 数据模型
│   ├── views/             # 视图函数
│   ├── forms/             # 表单类
│   ├── resources/         # 导入导出资源
│   └── templates/         # 模板文件
├── static/                # 静态文件
├── templates/             # 公共模板
└── cmdb/                  # 项目配置
```

### 开发规范

1. 代码风格
   - 遵循 PEP 8 规范
   - 使用 4 空格缩进
   - 类名使用驼峰命名
   - 函数和变量使用下划线命名

2. Git 提交规范
   - feat: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式调整
   - refactor: 代码重构

### 测试
```bash
python manage.py test
```

## 维护说明

### 日常维护
- 定期备份数据库
- 检查日志文件
- 更新系统依赖
- 监控系统性能

### 故障处理
- 检查日志文件
- 验证数据库连接
- 确认权限设置
- 检查网络状况

## 版本历史

- v1.0.0 (2024-01)
  - 初始版本发布
  - 基本功能实现
  - 数据中心管理
  - 设备管理功能

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 作者：sjxixi
- 邮箱：sjcache@gmail.com
- 项目地址：[https://github.com/sjxixi/AAA.git]