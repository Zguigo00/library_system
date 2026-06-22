import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from models.init_data import init_sample_data
from views.ui_login import LoginFrame
from views.ui_reader import ReaderManageFrame
from views.ui_book import BookManageFrame
from views.ui_search import SearchFrame
from views.ui_borrow import BorrowFrame
from presenters.presenter_borrow import BorrowPresenter
from presenters.presenter_reader import ReaderPresenter
from presenters.presenter_book import BookPresenter


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('高校图书管理系统')
        self.geometry('1100x700')
        self.minsize(900, 600)

        self.db = Database()
        self.current_user = None

        # 设置样式
        style = ttk.Style()
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('Treeview', font=('微软雅黑', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('微软雅黑', 10, 'bold'))

        self._show_login()

    def _show_login(self):
        self._clear()
        self.current_user = None
        self.title('高校图书管理系统 — 登录')
        login = LoginFrame(self, self.db, self._on_login)
        login.pack(fill='both', expand=True)

    def _on_login(self, user):
        self.current_user = user
        self.title(f'高校图书管理系统 — {user["user_name"]}({user["role"]})')
        self._show_main()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _show_main(self):
        self._clear()

        # 顶部导航栏
        nav = ttk.Frame(self)
        nav.pack(fill='x', padx=5, pady=5)

        ttk.Label(nav, text=f'当前用户：{self.current_user["user_name"]}  '
                             f'角色：{self.current_user["role"]}',
                  font=('微软雅黑', 10)).pack(side='left', padx=10)

        ttk.Button(nav, text='图书检索', command=self._show_search).pack(side='left', padx=3)
        ttk.Button(nav, text='借书 / 还书', command=self._show_borrow).pack(side='left', padx=3)

        if self.current_user['role'] == '管理员':
            ttk.Button(nav, text='读者管理', command=self._show_reader).pack(side='left', padx=3)
            ttk.Button(nav, text='图书管理', command=self._show_book).pack(side='left', padx=3)

        ttk.Button(nav, text='退出登录', command=self._confirm_logout).pack(side='right', padx=10)
        ttk.Button(nav, text='修改密码', command=self._change_password).pack(side='right', padx=3)

        # 内容区域
        self.content = ttk.Frame(self)
        self.content.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        # 默认显示检索
        self._show_search()

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _show_search(self):
        self._clear_content()
        SearchFrame(self.content, self.db).pack(fill='both', expand=True)

    def _show_borrow(self):
        self._clear_content()
        presenter = BorrowPresenter(self.db, self.current_user)
        BorrowFrame(self.content, presenter, self.current_user).pack(fill='both', expand=True)

    def _show_reader(self):
        self._clear_content()
        presenter = ReaderPresenter(self.db)
        ReaderManageFrame(self.content, presenter).pack(fill='both', expand=True)

    def _show_book(self):
        self._clear_content()
        presenter = BookPresenter(self.db)
        BookManageFrame(self.content, presenter).pack(fill='both', expand=True)

    def _confirm_logout(self):
        if messagebox.askyesno('确认', '确定退出登录？'):
            self._show_login()

    def _change_password(self):
        dlg = tk.Toplevel(self)
        dlg.title('修改密码')
        dlg.resizable(False, False)
        dlg.grab_set()

        ttk.Label(dlg, text='旧密码：').grid(row=0, column=0, padx=10, pady=8, sticky='e')
        e_old = ttk.Entry(dlg, width=25, show='*')
        e_old.grid(row=0, column=1, padx=10, pady=8)
        ttk.Label(dlg, text='新密码：').grid(row=1, column=0, padx=10, pady=8, sticky='e')
        e_new = ttk.Entry(dlg, width=25, show='*')
        e_new.grid(row=1, column=1, padx=10, pady=8)
        ttk.Label(dlg, text='确认新密码：').grid(row=2, column=0, padx=10, pady=8, sticky='e')
        e_confirm = ttk.Entry(dlg, width=25, show='*')
        e_confirm.grid(row=2, column=1, padx=10, pady=8)

        def _save():
            old = e_old.get().strip()
            new = e_new.get().strip()
            confirm = e_confirm.get().strip()
            if not old or not new:
                messagebox.showwarning('提示', '密码不能为空')
                return
            if new != confirm:
                messagebox.showerror('错误', '两次输入的新密码不一致')
                return
            ok = self.db.change_password(self.current_user['user_id'], old, new)
            if ok:
                messagebox.showinfo('成功', '密码修改成功')
                dlg.destroy()
            else:
                messagebox.showerror('失败', '旧密码错误')

        ttk.Button(dlg, text='确认修改', command=_save).grid(row=3, column=0, columnspan=2, pady=10)

    def destroy(self):
        self.db.close()
        super().destroy()


def main():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library.db')
    if not os.path.exists(db_path):
        init_sample_data()
    app = MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
