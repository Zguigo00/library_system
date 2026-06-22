class BookPresenter:
    def __init__(self, db):
        self.db = db

    def get_all_books(self):
        return self.db.get_all_books()

    def get_copies_by_book(self, book_id):
        return self.db.get_copies_by_book(book_id)

    def add_book(self, data):
        self.db.add_book(data)

    def update_book(self, book_id, data):
        self.db.update_book(book_id, data)

    def delete_book(self, book_id):
        return self.db.delete_book(book_id)

    def add_copy(self, reg_no, book_id, library_room):
        self.db.add_copy(reg_no, book_id, library_room)

    def delete_copy(self, reg_no):
        return self.db.delete_copy(reg_no)
