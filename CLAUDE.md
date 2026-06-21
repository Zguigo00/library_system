# CLAUDE.md - 高校图书管理系统

## 项目概述
基于 Python tkinter + SQLite 的桌面端高校图书管理系统。个人学习项目，目标是掌握软件工程实践。

## 技术栈
- 语言：Python 3.11
- GUI：tkinter + ttk
- 数据库：SQLite3（文件：library.db）
- 测试：pytest
- 架构：MVP（Model-View-Presenter）

## 项目结构
```
main.py                          — 入口，组装 MVP，导航，登录/登出/改密
models/
  database.py                    — 数据库操作 + 业务规则（Database 类）
  init_data.py                   — 示例数据初始化
views/
  ui_login.py                    — 登录界面
  ui_reader.py                   — 读者管理（管理员）
  ui_book.py                     — 图书管理（管理员）
  ui_search.py                   — 图书检索
  ui_borrow.py                   — 借还书
presenters/
  presenter_borrow.py            — 借还书业务协调（BorrowPresenter）
tests/
  conftest.py                    — 公共 fixture（内存数据库）
  test_borrow.py                 — 借书规则测试
  test_return.py                 — 还书规则测试
  test_delete.py                 — 删除约束测试
```

## 架构（MVP）
- **Model**（models/）：数据访问 + 业务规则验证
- **View**（views/）：纯 UI 渲染和用户输入捕获，不直接访问数据库
- **Presenter**（presenters/）：协调 View 和 Model，处理业务流程
- main.py 负责组装：创建 Model → 创建 Presenter → 注入 View

## 数据库表
- Reader — 读者
- Book — 图书
- BookCopy — 图书副本
- BorrowRecord — 借阅记录（外键 ON DELETE SET NULL）
- SysUser — 系统用户

## 开发约定
- 改代码前先写测试（TDD）
- 测试用内存数据库 `sqlite3.connect(":memory:")`
- Database 类通过 `db_path` 参数支持依赖注入
- 测试文件放 `tests/` 目录，公共 fixture 放 `conftest.py`
- 新增功能：先加 Presenter，再改 View，最后更新 main.py 组装

## 业务规则
- 借书：副本状态必须为"在馆"，读者借阅数不超过最大可借数
- 还书：验证借阅记录属于当前读者；允许归还已遗失的书
- 删除读者：有未还的书则禁止；历史借阅记录保留（reader_id 置空）
- 删除图书：有副本则禁止
- 删除副本：已借出则禁止；历史借阅记录保留（reg_no 置空）

## 运行
```bash
python main.py
```
首次运行自动创建数据库并初始化示例数据。

## 默认账号
- 管理员：admin / admin123
- 读者：R20210001 / 123456
