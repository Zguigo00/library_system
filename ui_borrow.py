import tkinter as tk
from tkinter import ttk, messagebox


class BorrowFrame(ttk.Frame):
    ACTIVE_COLS = [
        ('borrow_id', '借阅编号', 80), ('reader_id', '借书证号', 100),
        ('reader_name', '姓名', 80), ('book_name', '书名', 150),
        ('reg_no', '馆藏注册号', 140), ('borrow_date', '借书日期', 100),
        ('due_date', '应还日期', 100),
    ]
    HISTORY_COLS = [
        ('borrow_id', '借阅编号', 80), ('reader_id', '借书证号', 100),
        ('reader_name', '姓名', 80), ('book_name', '书名', 150),
        ('borrow_date', '借书日期', 100), ('due_date', '应还日期', 100),
        ('return_date', '归还日期', 100), ('fine', '罚款', 70),
        ('is_lost', '丢失', 50),
    ]

    def __init__(self, parent, db, user_info):
        super().__init__(parent)
        self.db = db
        self.user_info = user_info
        self.is_admin = user_info['role'] == '管理员'
        self._build_ui()
        self.refresh_active()
        self.refresh_history()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # ─── 借书/还书操作 ───
        op_frame = ttk.Frame(notebook)
        notebook.add(op_frame, text='借书 / 还书')
        self._build_op_tab(op_frame)

        # ─── 未还记录 ───
        active_frame = ttk.Frame(notebook)
        notebook.add(active_frame, text='未还记录')
        self._build_active_tab(active_frame)

        # ─── 历史记录 ───
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text='借阅历史')
        self._build_history_tab(history_frame)

    def _build_op_tab(self, parent):
        # 借书区域
        borrow_lf = ttk.LabelFrame(parent, text='借书操作')
        borrow_lf.pack(fill='x', padx=10, pady=10)

        row = ttk.Frame(borrow_lf)
        row.pack(fill='x', padx=5, pady=10)
        ttk.Label(row, text='借书证号：').pack(side='left', padx=5)
        self.borrow_rid = ttk.Entry(row, width=15)
        self.borrow_rid.pack(side='left', padx=5)
        ttk.Label(row, text='馆藏注册号：').pack(side='left', padx=5)
        self.borrow_reg = ttk.Entry(row, width=18)
        self.borrow_reg.pack(side='left', padx=5)
        ttk.Button(row, text='确认借书', command=self._do_borrow).pack(side='left', padx=15)

        if not self.is_admin:
            # 读者自动填充自己的ID
            self.borrow_rid.insert(0, self.user_info['user_id'])
            self.borrow_rid.configure(state='disabled')

        # 还书区域
        return_lf = ttk.LabelFrame(parent, text='还书操作')
        return_lf.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        toolbar = ttk.Frame(return_lf)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text='刷新列表', command=self.refresh_active).pack(side='left', padx=5)

        cols = [c[0] for c in self.ACTIVE_COLS]
        self.return_tree = ttk.Treeview(return_lf, columns=cols, show='headings', selectmode='browse')
        for key, label, width in self.ACTIVE_COLS:
            self.return_tree.heading(key, text=label)
            self.return_tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(return_lf, orient='vertical', command=self.return_tree.yview)
        self.return_tree.configure(yscrollcommand=vsb.set)
        self.return_tree.pack(fill='both', expand=True, padx=5, pady=(0, 5), side='left')
        vsb.pack(fill='y', side='right', pady=(0, 5))

        btn_frame = ttk.Frame(return_lf)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text='归还选中图书', command=self._do_return).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='标记丢失', command=self._do_lost).pack(side='left', padx=5)

    def _build_active_tab(self, parent):
        cols = [c[0] for c in self.ACTIVE_COLS]
        self.active_tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode='browse')
        for key, label, width in self.ACTIVE_COLS:
            self.active_tree.heading(key, text=label)
            self.active_tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(parent, orient='vertical', command=self.active_tree.yview)
        self.active_tree.configure(yscrollcommand=vsb.set)
        self.active_tree.pack(fill='both', expand=True, padx=5, pady=5, side='left')
        vsb.pack(fill='y', side='right', pady=5)

    def _build_history_tab(self, parent):
        cols = [c[0] for c in self.HISTORY_COLS]
        self.history_tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode='browse')
        for key, label, width in self.HISTORY_COLS:
            self.history_tree.heading(key, text=label)
            self.history_tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(parent, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        self.history_tree.pack(fill='both', expand=True, padx=5, pady=5, side='left')
        vsb.pack(fill='y', side='right', pady=5)

    def refresh_active(self):
        reader_id = None if self.is_admin else self.user_info['user_id']
        records = self.db.get_active_borrows(reader_id)
        for tree in (self.return_tree, self.active_tree):
            for item in tree.get_children():
                tree.delete(item)
            for r in records:
                tree.insert('', 'end', values=[r[c[0]] for c in self.ACTIVE_COLS])

    def refresh_history(self):
        reader_id = None if self.is_admin else self.user_info['user_id']
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for r in self.db.get_all_borrows(reader_id):
            vals = []
            for c in self.HISTORY_COLS:
                v = r[c[0]]
                if c[0] == 'is_lost':
                    v = '是' if v else '否'
                vals.append(v)
            self.history_tree.insert('', 'end', values=vals)

    def _do_borrow(self):
        rid = self.borrow_rid.get().strip()
        reg = self.borrow_reg.get().strip()
        if not rid or not reg:
            messagebox.showwarning('提示', '请输入借书证号和馆藏注册号')
            return
        ok, msg = self.db.borrow_book(rid, reg)
        if ok:
            messagebox.showinfo('成功', msg)
            self.borrow_reg.delete(0, 'end')
            self.refresh_active()
            self.refresh_history()
        else:
            messagebox.showerror('借书失败', msg)

    def _do_return(self):
        sel = self.return_tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一条未还记录')
            return
        borrow_id = self.return_tree.item(sel[0])['values'][0]
        ok, msg = self.db.return_book(borrow_id, is_lost=False)
        if ok:
            messagebox.showinfo('成功', msg)
            self.refresh_active()
            self.refresh_history()
        else:
            messagebox.showerror('失败', msg)

    def _do_lost(self):
        sel = self.return_tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一条未还记录')
            return
        borrow_id = self.return_tree.item(sel[0])['values'][0]
        if messagebox.askyesno('确认', '确定将此书标记为丢失？将产生罚款。'):
            ok, msg = self.db.return_book(borrow_id, is_lost=True)
            if ok:
                messagebox.showinfo('成功', msg)
                self.refresh_active()
                self.refresh_history()
            else:
                messagebox.showerror('失败', msg)
