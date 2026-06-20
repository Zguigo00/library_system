"""删除约束业务规则测试"""
import pytest


class TestDeleteReader:
    """删除读者时的约束检查"""

    def test_delete_reader_with_unreturned_book_fails(self, db):
        """有未还的书，禁止删除读者"""
        db.borrow_book("R0001", "C0001")
        ok, msg = db.delete_reader("R0001")
        assert ok is False
        assert "未归还" in msg

    def test_delete_reader_after_return_succeeds(self, db):
        """书已还清，可以删除读者"""
        db.borrow_book("R0001", "C0001")
        record = db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        db.return_book(record["borrow_id"])
        ok, msg = db.delete_reader("R0001")
        assert ok is True

    def test_delete_reader_preserves_history(self, db):
        """删除读者后，历史借阅记录保留（reader_id 置空）"""
        db.borrow_book("R0001", "C0001")
        record = db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        borrow_id = record["borrow_id"]
        db.return_book(borrow_id)
        db.delete_reader("R0001")
        # 读者和用户已删除
        assert db.get_reader("R0001") is None
        # 借阅记录还在，但 reader_id 被置为 NULL
        history = db.conn.execute(
            "SELECT * FROM BorrowRecord WHERE borrow_id=?", (borrow_id,)
        ).fetchall()
        assert len(history) == 1
        assert history[0]["reader_id"] is None
