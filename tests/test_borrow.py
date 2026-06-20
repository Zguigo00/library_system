"""借书业务规则测试"""
from database import Database


class TestBorrowCopyStatus:
    """借书时必须检查副本状态"""

    def test_borrow_available_copy_succeeds(self, db):
        """副本状态为「在馆」时，借书成功"""
        ok, msg = db.borrow_book("R0001", "C0001")
        assert ok is True
        assert "借书成功" in msg

    def test_borrow_borrowed_copy_fails(self, db):
        """副本状态为「借出」时，借书失败"""
        ok, msg = db.borrow_book("R0001", "C0002")
        assert ok is False
        assert "借出" in msg

    def test_borrow_lost_copy_fails(self, db):
        """副本状态为「丢失」时，借书失败"""
        db.conn.execute("UPDATE BookCopy SET status='丢失' WHERE reg_no='C0001'")
        db.conn.commit()
        ok, msg = db.borrow_book("R0001", "C0001")
        assert ok is False
        assert "丢失" in msg

    def test_borrow_updates_copy_status(self, db):
        """借书成功后，副本状态变为「借出」"""
        db.borrow_book("R0001", "C0001")
        copy = db.get_copy("C0001")
        assert copy["status"] == "借出"
