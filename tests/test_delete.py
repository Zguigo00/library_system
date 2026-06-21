"""删除约束业务规则测试"""
import pytest
from models.database import Database


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


class TestDeleteBook:
    """删除图书时的约束检查"""

    def test_delete_book_with_copies_fails(self, db):
        """有副本存在，禁止删除图书"""
        ok, msg = db.delete_book("B0001")
        assert ok is False
        assert "副本" in msg

    def test_delete_book_without_copies_succeeds(self, db):
        """无副本，可以删除图书"""
        # 先删掉所有副本
        db.conn.execute("DELETE FROM BookCopy WHERE book_id='B0001'")
        db.conn.commit()
        ok, msg = db.delete_book("B0001")
        assert ok is True


class TestDeleteCopy:
    """删除副本时的约束检查"""

    def test_delete_borrowed_copy_fails(self, db):
        """已借出的副本，禁止删除"""
        db.borrow_book("R0001", "C0001")
        ok, msg = db.delete_copy("C0001")
        assert ok is False
        assert "借出" in msg

    def test_delete_available_copy_succeeds(self, db):
        """在馆副本，可以删除"""
        ok, msg = db.delete_copy("C0001")
        assert ok is True

    def test_delete_copy_preserves_history(self, db):
        """删除副本后，历史借阅记录保留"""
        db.borrow_book("R0001", "C0001")
        record = db.conn.execute(
            "SELECT borrow_id FROM BorrowRecord WHERE reader_id='R0001'"
        ).fetchone()
        borrow_id = record["borrow_id"]
        db.return_book(borrow_id)
        db.delete_copy("C0001")
        # 借阅记录还在，但 reg_no 被置为 NULL
        history = db.conn.execute(
            "SELECT * FROM BorrowRecord WHERE borrow_id=?", (borrow_id,)
        ).fetchall()
        assert len(history) == 1
        assert history[0]["reg_no"] is None
