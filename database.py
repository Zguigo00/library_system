import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library.db')


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DB_PATH
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS Reader (
            reader_id      TEXT(10) PRIMARY KEY,
            reader_name    TEXT(20) NOT NULL,
            reader_sex     TEXT(2) CHECK(reader_sex IN ('男','女')),
            birth_date     TEXT,
            id_card        TEXT(18) UNIQUE,
            dept           TEXT(50),
            address        TEXT(100),
            zip_code       TEXT(6),
            phone          TEXT(15),
            reg_date       TEXT DEFAULT (date('now')),
            borrow_range   TEXT(50),
            max_borrow     INTEGER DEFAULT 10,
            borrow_period  INTEGER DEFAULT 30,
            photo          BLOB,
            occupation     TEXT(20)
        );

        CREATE TABLE IF NOT EXISTS Book (
            book_id       TEXT(10) PRIMARY KEY,
            book_name     TEXT(100) NOT NULL,
            author        TEXT(50),
            publisher     TEXT(50),
            pub_date      TEXT,
            edition       INTEGER DEFAULT 1,
            price         REAL,
            summary       TEXT,
            class_no      TEXT(20),
            call_no       TEXT(20),
            total_copies  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS BookCopy (
            reg_no        TEXT(15) PRIMARY KEY,
            book_id       TEXT(10) NOT NULL,
            library_room  TEXT(30),
            in_date       TEXT DEFAULT (date('now')),
            status        TEXT(4) DEFAULT '在馆' CHECK(status IN ('在馆','借出','丢失')),
            FOREIGN KEY (book_id) REFERENCES Book(book_id)
        );

        CREATE TABLE IF NOT EXISTS BorrowRecord (
            borrow_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id    TEXT(10) NOT NULL,
            reg_no       TEXT(15) NOT NULL,
            borrow_date  TEXT NOT NULL DEFAULT (date('now')),
            due_date     TEXT NOT NULL,
            return_date  TEXT,
            fine         REAL DEFAULT 0,
            is_lost      INTEGER DEFAULT 0,
            FOREIGN KEY (reader_id) REFERENCES Reader(reader_id),
            FOREIGN KEY (reg_no) REFERENCES BookCopy(reg_no)
        );

        CREATE TABLE IF NOT EXISTS SysUser (
            user_id    TEXT(10) PRIMARY KEY,
            user_name  TEXT(20) NOT NULL,
            password   TEXT(64) NOT NULL,
            role       TEXT(10) CHECK(role IN ('管理员','读者'))
        );
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ─── 身份验证 ───
    def authenticate(self, user_id, password):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM SysUser WHERE user_id=? AND password=?",
                    (user_id, hash_password(password)))
        return cur.fetchone()

    def change_password(self, user_id, old_pw, new_pw):
        user = self.authenticate(user_id, old_pw)
        if not user:
            return False
        self.conn.execute("UPDATE SysUser SET password=? WHERE user_id=?",
                          (hash_password(new_pw), user_id))
        self.conn.commit()
        return True

    # ─── 用户管理 ───
    def add_user(self, user_id, user_name, password, role):
        self.conn.execute(
            "INSERT INTO SysUser VALUES (?,?,?,?)",
            (user_id, user_name, hash_password(password), role))
        self.conn.commit()

    def get_all_users(self):
        return self.conn.execute("SELECT user_id, user_name, role FROM SysUser").fetchall()

    def delete_user(self, user_id):
        self.conn.execute("DELETE FROM SysUser WHERE user_id=?", (user_id,))
        self.conn.commit()

    # ─── 读者管理 ───
    def add_reader(self, data):
        sql = """INSERT INTO Reader
            (reader_id, reader_name, reader_sex, birth_date, id_card,
             dept, address, zip_code, phone, reg_date, borrow_range,
             max_borrow, borrow_period, occupation)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        self.conn.execute(sql, data)
        self.conn.commit()

    def update_reader(self, reader_id, data):
        sql = """UPDATE Reader SET
            reader_name=?, reader_sex=?, birth_date=?, id_card=?,
            dept=?, address=?, zip_code=?, phone=?, borrow_range=?,
            max_borrow=?, borrow_period=?, occupation=?
            WHERE reader_id=?"""
        self.conn.execute(sql, (*data, reader_id))
        self.conn.commit()

    def delete_reader(self, reader_id):
        active = self.conn.execute(
            "SELECT COUNT(*) FROM BorrowRecord WHERE reader_id=? AND return_date IS NULL",
            (reader_id,)).fetchone()[0]
        if active > 0:
            return False, "该读者有未归还的图书，无法删除"
        self.conn.execute("DELETE FROM BorrowRecord WHERE reader_id=?", (reader_id,))
        self.conn.execute("DELETE FROM SysUser WHERE user_id=?", (reader_id,))
        self.conn.execute("DELETE FROM Reader WHERE reader_id=?", (reader_id,))
        self.conn.commit()
        return True, "删除成功"

    def get_reader(self, reader_id):
        return self.conn.execute("SELECT * FROM Reader WHERE reader_id=?",
                                 (reader_id,)).fetchone()

    def get_all_readers(self):
        return self.conn.execute("SELECT * FROM Reader ORDER BY reader_id").fetchall()

    def search_readers(self, keyword):
        like = f"%{keyword}%"
        return self.conn.execute(
            "SELECT * FROM Reader WHERE reader_id LIKE ? OR reader_name LIKE ? OR dept LIKE ?",
            (like, like, like)).fetchall()

    def get_reader_borrow_count(self, reader_id):
        row = self.conn.execute(
            "SELECT COUNT(*) FROM BorrowRecord WHERE reader_id=? AND return_date IS NULL",
            (reader_id,)).fetchone()
        return row[0]

    # ─── 图书管理 ───
    def add_book(self, data):
        sql = """INSERT INTO Book
            (book_id, book_name, author, publisher, pub_date,
             edition, price, summary, class_no, call_no, total_copies)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
        self.conn.execute(sql, data)
        self.conn.commit()

    def update_book(self, book_id, data):
        sql = """UPDATE Book SET
            book_name=?, author=?, publisher=?, pub_date=?,
            edition=?, price=?, summary=?, class_no=?, call_no=?, total_copies=?
            WHERE book_id=?"""
        self.conn.execute(sql, (*data, book_id))
        self.conn.commit()

    def delete_book(self, book_id):
        borrowed = self.conn.execute("""
            SELECT COUNT(*) FROM BorrowRecord br
            JOIN BookCopy bc ON br.reg_no = bc.reg_no
            WHERE bc.book_id=? AND br.return_date IS NULL
        """, (book_id,)).fetchone()[0]
        if borrowed > 0:
            return False, "该书有未归还的副本，无法删除"
        self.conn.execute("""
            DELETE FROM BorrowRecord WHERE reg_no IN
            (SELECT reg_no FROM BookCopy WHERE book_id=?)
        """, (book_id,))
        self.conn.execute("DELETE FROM BookCopy WHERE book_id=?", (book_id,))
        self.conn.execute("DELETE FROM Book WHERE book_id=?", (book_id,))
        self.conn.commit()
        return True, "删除成功"

    def get_book(self, book_id):
        return self.conn.execute("SELECT * FROM Book WHERE book_id=?",
                                 (book_id,)).fetchone()

    def get_all_books(self):
        return self.conn.execute("SELECT * FROM Book ORDER BY book_id").fetchall()

    # ─── 图书副本管理 ───
    def add_copy(self, reg_no, book_id, library_room):
        self.conn.execute(
            "INSERT INTO BookCopy (reg_no, book_id, library_room) VALUES (?,?,?)",
            (reg_no, book_id, library_room))
        self.conn.execute(
            "UPDATE Book SET total_copies = total_copies + 1 WHERE book_id=?",
            (book_id,))
        self.conn.commit()

    def delete_copy(self, reg_no):
        copy = self.conn.execute("SELECT * FROM BookCopy WHERE reg_no=?",
                                 (reg_no,)).fetchone()
        if not copy:
            return False, "副本不存在"
        if copy['status'] == '借出':
            return False, "该副本已借出，无法删除"
        self.conn.execute(
            "UPDATE Book SET total_copies = total_copies - 1 WHERE book_id=?",
            (copy['book_id'],))
        self.conn.execute("DELETE FROM BorrowRecord WHERE reg_no=?", (reg_no,))
        self.conn.execute("DELETE FROM BookCopy WHERE reg_no=?", (reg_no,))
        self.conn.commit()
        return True, "删除成功"

    def get_copies_by_book(self, book_id):
        return self.conn.execute(
            "SELECT * FROM BookCopy WHERE book_id=? ORDER BY reg_no",
            (book_id,)).fetchall()

    def get_copy(self, reg_no):
        return self.conn.execute("SELECT * FROM BookCopy WHERE reg_no=?",
                                 (reg_no,)).fetchone()

    def get_available_copies(self, book_id):
        return self.conn.execute(
            "SELECT * FROM BookCopy WHERE book_id=? AND status='在馆'",
            (book_id,)).fetchall()

    # ─── 检索 ───
    def search_books(self, field, keyword):
        like = f"%{keyword}%"
        valid = {
            '书号': 'book_id', '书名': 'book_name', '作者': 'author',
            '出版单位': 'publisher', '内容提要': 'summary',
            '分类号': 'class_no', '索书号': 'call_no'
        }
        col = valid.get(field, 'book_name')
        return self.conn.execute(
            f"SELECT * FROM Book WHERE {col} LIKE ? ORDER BY book_id",
            (like,)).fetchall()

    def search_by_reg_no(self, reg_no):
        like = f"%{reg_no}%"
        return self.conn.execute("""
            SELECT b.*, bc.reg_no, bc.library_room, bc.status
            FROM Book b JOIN BookCopy bc ON b.book_id = bc.book_id
            WHERE bc.reg_no LIKE ?
        """, (like,)).fetchall()

    # ─── 借书 ───
    def borrow_book(self, reader_id, reg_no):
        reader = self.get_reader(reader_id)
        if not reader:
            return False, "读者不存在"
        copy = self.get_copy(reg_no)
        if not copy:
            return False, "副本不存在"
        if copy['status'] != '在馆':
            return False, f"该副本状态为「{copy['status']}」，不可借出"
        if reader['borrow_range'] and copy['library_room'] and reader['borrow_range'] != copy['library_room']:
            return False, f"该读者借阅范围为「{reader['borrow_range']}」，无法从「{copy['library_room']}」借书"
        current = self.get_reader_borrow_count(reader_id)
        if current >= reader['max_borrow']:
            return False, f"已达最大借书数量（{reader['max_borrow']}册）"
        today = datetime.now().strftime('%Y-%m-%d')
        due = (datetime.now() + timedelta(days=reader['borrow_period'])).strftime('%Y-%m-%d')
        self.conn.execute(
            "INSERT INTO BorrowRecord (reader_id, reg_no, borrow_date, due_date) VALUES (?,?,?,?)",
            (reader_id, reg_no, today, due))
        self.conn.execute("UPDATE BookCopy SET status='借出' WHERE reg_no=?", (reg_no,))
        self.conn.commit()
        return True, f"借书成功！应还日期：{due}"

    # ─── 还书 ───
    def return_book(self, borrow_id, is_lost=False, reader_id=None):
        record = self.conn.execute("SELECT * FROM BorrowRecord WHERE borrow_id=?",
                                   (borrow_id,)).fetchone()
        if not record:
            return False, "借阅记录不存在"
        if reader_id and record['reader_id'] != reader_id:
            return False, "该借阅记录不属于当前读者，无权归还"
        if record['return_date']:
            return False, "该书已归还"
        today = datetime.now().strftime('%Y-%m-%d')
        fine = 0.0
        if is_lost:
            fine = 100.0  # 丢失罚款
            self.conn.execute("UPDATE BookCopy SET status='丢失' WHERE reg_no=?",
                              (record['reg_no'],))
        else:
            if record['due_date'] < today:
                days = (datetime.strptime(today, '%Y-%m-%d') -
                        datetime.strptime(record['due_date'], '%Y-%m-%d')).days
                fine = days * 0.5  # 每天0.5元
            self.conn.execute("UPDATE BookCopy SET status='在馆' WHERE reg_no=?",
                              (record['reg_no'],))
        self.conn.execute(
            "UPDATE BorrowRecord SET return_date=?, fine=?, is_lost=? WHERE borrow_id=?",
            (today, fine, 1 if is_lost else 0, borrow_id))
        self.conn.commit()
        msg = f"归还成功！罚款：{fine}元" if fine > 0 else "归还成功！"
        return True, msg

    def get_active_borrows(self, reader_id=None):
        if reader_id:
            return self.conn.execute("""
                SELECT br.*, r.reader_name, b.book_name, bc.reg_no
                FROM BorrowRecord br
                JOIN Reader r ON br.reader_id = r.reader_id
                JOIN BookCopy bc ON br.reg_no = bc.reg_no
                JOIN Book b ON bc.book_id = b.book_id
                WHERE br.reader_id=? AND br.return_date IS NULL
                ORDER BY br.borrow_date DESC
            """, (reader_id,)).fetchall()
        return self.conn.execute("""
            SELECT br.*, r.reader_name, b.book_name, bc.reg_no
            FROM BorrowRecord br
            JOIN Reader r ON br.reader_id = r.reader_id
            JOIN BookCopy bc ON br.reg_no = bc.reg_no
            JOIN Book b ON bc.book_id = b.book_id
            WHERE br.return_date IS NULL
            ORDER BY br.borrow_date DESC
        """).fetchall()

    def get_all_borrows(self, reader_id=None):
        if reader_id:
            return self.conn.execute("""
                SELECT br.*, r.reader_name, b.book_name
                FROM BorrowRecord br
                JOIN Reader r ON br.reader_id = r.reader_id
                JOIN BookCopy bc ON br.reg_no = bc.reg_no
                JOIN Book b ON bc.book_id = b.book_id
                WHERE br.reader_id=?
                ORDER BY br.borrow_date DESC
            """, (reader_id,)).fetchall()
        return self.conn.execute("""
            SELECT br.*, r.reader_name, b.book_name
            FROM BorrowRecord br
            JOIN Reader r ON br.reader_id = r.reader_id
            JOIN BookCopy bc ON br.reg_no = bc.reg_no
            JOIN Book b ON bc.book_id = b.book_id
            ORDER BY br.borrow_date DESC
        """).fetchall()
