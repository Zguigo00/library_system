class ReaderPresenter:
    def __init__(self, db):
        self.db = db

    def get_all_readers(self):
        return self.db.get_all_readers()

    def search_readers(self, keyword):
        return self.db.search_readers(keyword)

    def add_reader(self, data):
        self.db.add_reader(data)

    def add_user(self, user_id, user_name, password, role):
        self.db.add_user(user_id, user_name, password, role)

    def update_reader(self, reader_id, data):
        self.db.update_reader(reader_id, data)

    def delete_reader(self, reader_id):
        return self.db.delete_reader(reader_id)
