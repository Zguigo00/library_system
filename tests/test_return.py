"""还书业务规则测试"""
from datetime import datetime, timedelta
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


class TestReturnLostBook:
    """允许归还已遗失的书"""

    def test_return_lost_book_restores_copy(self, db):
        """归还已遗失的书，副本状态恢复为「在馆」"""
        db.borrow_book("R0001", "C0001")
        record = db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        # 先标记为遗失
        db.return_book(record["borrow_id"], is_lost=True)
        copy = db.get_copy("C0001")
        assert copy["status"] == "丢失"
        # 读者找到书，归还
        ok, msg = db.return_book(record["borrow_id"], is_lost=False)
        assert ok is True
        copy = db.get_copy("C0001")
        assert copy["status"] == "在馆"

    def test_lost_book_fine_stays(self, db):
        """归还已遗失的书，遗失罚款保留"""
        db.borrow_book("R0001", "C0001")
        borrow = db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        borrow_id = borrow["borrow_id"]
        # 标记遗失，罚款100
        db.return_book(borrow_id, is_lost=True)
        record = db.conn.execute(
            "SELECT fine, is_lost FROM BorrowRecord WHERE borrow_id=?",
            (borrow_id,)
        ).fetchone()
        assert record["fine"] == 100.0
        assert record["is_lost"] == 1
        # 归还，罚款应清除（因为书回来了）
        db.return_book(borrow_id, is_lost=False)
        record = db.conn.execute(
            "SELECT fine, is_lost, return_date FROM BorrowRecord WHERE borrow_id=?",
            (borrow_id,)
        ).fetchone()
        assert record["is_lost"] == 0
        assert record["return_date"] is not None
