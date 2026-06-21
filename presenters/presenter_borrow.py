class BorrowPresenter:
    def __init__(self, db, user_info):
        self.db = db
        self.user_info = user_info
        self.is_admin = user_info['role'] == '管理员'

    def _reader_id_for_query(self):
        """管理员查全部返回 None，普通读者返回自己的 ID"""
        return None if self.is_admin else self.user_info['user_id']

    def borrow_book(self, reader_id, reg_no):
        return self.db.borrow_book(reader_id, reg_no)

    def return_book(self, borrow_id):
        reader_id = self._reader_id_for_query()
        return self.db.return_book(borrow_id, is_lost=False, reader_id=reader_id)

    def mark_lost(self, borrow_id):
        reader_id = self._reader_id_for_query()
        return self.db.return_book(borrow_id, is_lost=True, reader_id=reader_id)

    def get_active_borrows(self):
        return self.db.get_active_borrows(self._reader_id_for_query())

    def get_borrow_history(self):
        return self.db.get_all_borrows(self._reader_id_for_query())
