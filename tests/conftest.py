import pytest
from database import Database


@pytest.fixture
def db():
    """创建内存数据库，每个测试用例独立的干净数据库"""
    database = Database(":memory:")
    # 插入测试用的基础数据
    database.conn.execute(
        "INSERT INTO Reader (reader_id, reader_name, reader_sex, dept, max_borrow, borrow_period, borrow_range) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("R0001", "张三", "男", "计算机学院", 5, 30, "")
    )
    database.conn.execute(
        "INSERT INTO Book (book_id, book_name, author, publisher) VALUES (?, ?, ?, ?)",
        ("B0001", "数据结构", "严蔚敏", "清华大学出版社")
    )
    database.conn.execute(
        "INSERT INTO BookCopy (reg_no, book_id, library_room, status) VALUES (?, ?, ?, ?)",
        ("C0001", "B0001", "综合书库", "在馆")
    )
    database.conn.execute(
        "INSERT INTO BookCopy (reg_no, book_id, library_room, status) VALUES (?, ?, ?, ?)",
        ("C0002", "B0001", "综合书库", "借出")
    )
    database.conn.execute(
        "INSERT INTO SysUser (user_id, user_name, password, role) VALUES (?, ?, ?, ?)",
        ("R0001", "张三", "123456", "读者")
    )
    database.conn.commit()
    return database
