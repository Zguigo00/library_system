"""还书业务规则测试"""
import pytest


class TestReturnBookOwnership:
    """还书时必须验证借阅记录属于当前读者"""

    @pytest.fixture(autouse=True)
    def setup_borrow(self, db):
        """为每个测试创建一条借阅记录"""
        db.borrow_book("R0001", "C0001")
        self.db = db

    def test_return_by_owner_succeeds(self):
        """借书本人还书，成功"""
        record = self.db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        ok, msg = self.db.return_book(record["borrow_id"], reader_id="R0001")
        assert ok is True
        assert "归还成功" in msg

    def test_return_by_wrong_reader_fails(self):
        """非本人还书，失败"""
        # 插入第二个读者
        self.db.conn.execute(
            "INSERT INTO Reader (reader_id, reader_name, reader_sex, dept, max_borrow, borrow_period) "
            "VALUES ('R0002', '李四', '女', '数学学院', 5, 30)"
        )
        self.db.conn.commit()
        record = self.db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        ok, msg = self.db.return_book(record["borrow_id"], reader_id="R0002")
        assert ok is False
        assert "不属于" in msg or "无权" in msg
