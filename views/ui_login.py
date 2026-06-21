import tkinter as tk
from tkinter import ttk, messagebox


class LoginFrame(ttk.Frame):
    def __init__(self, parent, db, on_login_success):
        super().__init__(parent)
        self.db = db
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # 居中容器
        center = ttk.Frame(self)
        center.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(center, text='高校图书管理系统', font=('微软雅黑', 24, 'bold')).pack(pady=(0, 30))
        ttk.Label(center, text='用户登录', font=('微软雅黑', 14)).pack(pady=(0, 20))

        form = ttk.Frame(center)
        form.pack()

        ttk.Label(form, text='用户编号：', font=('微软雅黑', 11)).grid(row=0, column=0, sticky='e', pady=8, padx=5)
        self.entry_id = ttk.Entry(form, width=25, font=('微软雅黑', 11))
        self.entry_id.grid(row=0, column=1, pady=8, padx=5)

        ttk.Label(form, text='密　　码：', font=('微软雅黑', 11)).grid(row=1, column=0, sticky='e', pady=8, padx=5)
        self.entry_pw = ttk.Entry(form, width=25, show='*', font=('微软雅黑', 11))
        self.entry_pw.grid(row=1, column=1, pady=8, padx=5)

        btn_frame = ttk.Frame(center)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text='登 录', command=self._login, width=12).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='退 出', command=self.winfo_toplevel().destroy, width=12).pack(side='left', padx=10)

        self.entry_pw.bind('<Return>', lambda e: self._login())
        self.entry_id.focus_set()

    def _login(self):
        uid = self.entry_id.get().strip()
        pw = self.entry_pw.get().strip()
        if not uid or not pw:
            messagebox.showwarning('提示', '请输入用户编号和密码')
            return
        user = self.db.authenticate(uid, pw)
        if user:
            self.on_login_success(dict(user))
        else:
            messagebox.showerror('登录失败', '用户编号或密码错误')
            self.entry_pw.delete(0, 'end')
