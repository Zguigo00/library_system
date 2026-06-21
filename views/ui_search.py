import tkinter as tk
from tkinter import ttk, messagebox


class SearchFrame(ttk.Frame):
    BOOK_COLS = [
        ('book_id', '书号', 100), ('book_name', '书名', 150),
        ('author', '作者', 100), ('publisher', '出版单位', 120),
        ('pub_date', '出版日期', 100), ('edition', '版次', 50),
        ('price', '单价', 70), ('summary', '内容提要', 200),
        ('class_no', '分类号', 80), ('call_no', '索书号', 80),
        ('total_copies', '藏书册数', 70),
    ]

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self._build_ui()

    def _build_ui(self):
        # 搜索区域
        search_frame = ttk.LabelFrame(self, text='图书检索')
        search_frame.pack(fill='x', padx=10, pady=10)

        row1 = ttk.Frame(search_frame)
        row1.pack(fill='x', padx=5, pady=5)
        ttk.Label(row1, text='检索方式：').pack(side='left', padx=5)
        self.field_var = tk.StringVar(value='书名')
        fields = ['书号', '书名', '作者', '出版单位', '内容提要', '分类号', '索书号', '馆藏注册号']
        ttk.Combobox(row1, textvariable=self.field_var, values=fields,
                     state='readonly', width=12).pack(side='left', padx=5)
        ttk.Label(row1, text='关键字：').pack(side='left', padx=5)
        self.keyword_var = tk.StringVar()
        entry = ttk.Entry(row1, textvariable=self.keyword_var, width=30)
        entry.pack(side='left', padx=5)
        entry.bind('<Return>', lambda e: self._search())
        ttk.Button(row1, text='搜 索', command=self._search).pack(side='left', padx=10)
        ttk.Button(row1, text='显示全部', command=self._show_all).pack(side='left', padx=5)

        # 结果表格
        result_frame = ttk.LabelFrame(self, text='搜索结果')
        result_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        cols = [c[0] for c in self.BOOK_COLS]
        self.tree = ttk.Treeview(result_frame, columns=cols, show='headings', selectmode='browse')
        for key, label, width in self.BOOK_COLS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(result_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5, side='left')
        vsb.pack(fill='y', side='right', pady=5)

        # 副本信息区域
        copy_frame = ttk.LabelFrame(self, text='副本详情')
        copy_frame.pack(fill='x', padx=10, pady=(0, 10))
        self.copy_label = ttk.Label(copy_frame, text='选择一本图书查看副本信息', font=('微软雅黑', 10))
        self.copy_label.pack(padx=10, pady=5, anchor='w')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _search(self):
        field = self.field_var.get()
        kw = self.keyword_var.get().strip()
        if not kw:
            messagebox.showwarning('提示', '请输入搜索关键字')
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        if field == '馆藏注册号':
            results = self.db.search_by_reg_no(kw)
            for r in results:
                vals = [r[c[0]] for c in self.BOOK_COLS if c[0] in r.keys()]
                if len(vals) < len(self.BOOK_COLS):
                    vals = [r.get(c[0], '') for c in self.BOOK_COLS]
                self.tree.insert('', 'end', values=vals)
        else:
            results = self.db.search_books(field, kw)
            for b in results:
                self.tree.insert('', 'end', values=[b[c[0]] for c in self.BOOK_COLS])
        self.copy_label.configure(text=f'找到 {len(results)} 条结果')

    def _show_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in self.db.get_all_books():
            self.tree.insert('', 'end', values=[b[c[0]] for c in self.BOOK_COLS])
        self.copy_label.configure(text='显示全部图书')

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        book_id = self.tree.item(sel[0])['values'][0]
        copies = self.db.get_copies_by_book(book_id)
        if copies:
            lines = []
            for c in copies:
                lines.append(f"注册号: {c['reg_no']}  书库: {c['library_room']}  "
                             f"入库日期: {c['in_date']}  状态: {c['status']}")
            self.copy_label.configure(text='\n'.join(lines))
        else:
            self.copy_label.configure(text='暂无副本信息')
