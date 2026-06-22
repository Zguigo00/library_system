import tkinter as tk
from tkinter import ttk, messagebox


class BookManageFrame(ttk.Frame):
    BOOK_COLS = [
        ('book_id', '书号', 100), ('book_name', '书名', 150),
        ('author', '作者', 100), ('publisher', '出版单位', 120),
        ('pub_date', '出版日期', 100), ('edition', '版次', 50),
        ('price', '单价', 70), ('class_no', '分类号', 80),
        ('call_no', '索书号', 80), ('total_copies', '藏书册数', 70),
    ]
    COPY_COLS = [
        ('reg_no', '馆藏注册号', 140), ('library_room', '所在书库', 100),
        ('in_date', '入库日期', 100), ('status', '状态', 60),
    ]

    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        self._build_ui()
        self.refresh_books()

    def _build_ui(self):
        # 上半部分：图书列表
        top = ttk.LabelFrame(self, text='图书列表')
        top.pack(fill='both', expand=True, padx=5, pady=5)

        toolbar = ttk.Frame(top)
        toolbar.pack(fill='x', padx=5, pady=3)
        ttk.Button(toolbar, text='新增图书', command=self._add_book).pack(side='left', padx=2)
        ttk.Button(toolbar, text='编辑图书', command=self._edit_book).pack(side='left', padx=2)
        ttk.Button(toolbar, text='删除图书', command=self._del_book).pack(side='left', padx=2)
        ttk.Button(toolbar, text='刷新', command=self.refresh_books).pack(side='left', padx=2)

        cols = [c[0] for c in self.BOOK_COLS]
        self.book_tree = ttk.Treeview(top, columns=cols, show='headings', selectmode='browse', height=8)
        for key, label, width in self.BOOK_COLS:
            self.book_tree.heading(key, text=label)
            self.book_tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(top, orient='vertical', command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=vsb.set)
        self.book_tree.pack(fill='both', expand=True, padx=5, pady=(0, 5), side='left')
        vsb.pack(fill='y', side='right', pady=(0, 5))
        self.book_tree.bind('<<TreeviewSelect>>', self._on_book_select)

        # 下半部分：副本列表
        bottom = ttk.LabelFrame(self, text='图书副本')
        bottom.pack(fill='both', expand=True, padx=5, pady=5)

        ctoolbar = ttk.Frame(bottom)
        ctoolbar.pack(fill='x', padx=5, pady=3)
        ttk.Button(ctoolbar, text='新增副本', command=self._add_copy).pack(side='left', padx=2)
        ttk.Button(ctoolbar, text='删除副本', command=self._del_copy).pack(side='left', padx=2)

        ccols = [c[0] for c in self.COPY_COLS]
        self.copy_tree = ttk.Treeview(bottom, columns=ccols, show='headings', selectmode='browse', height=6)
        for key, label, width in self.COPY_COLS:
            self.copy_tree.heading(key, text=label)
            self.copy_tree.column(key, width=width, anchor='center')
        vsb2 = ttk.Scrollbar(bottom, orient='vertical', command=self.copy_tree.yview)
        self.copy_tree.configure(yscrollcommand=vsb2.set)
        self.copy_tree.pack(fill='both', expand=True, padx=5, pady=(0, 5), side='left')
        vsb2.pack(fill='y', side='right', pady=(0, 5))

    def refresh_books(self):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        for b in self.presenter.get_all_books():
            self.book_tree.insert('', 'end', values=[b[c[0]] for c in self.BOOK_COLS])
        self._clear_copies()

    def _clear_copies(self):
        for item in self.copy_tree.get_children():
            self.copy_tree.delete(item)

    def _on_book_select(self, event):
        sel = self.book_tree.selection()
        if not sel:
            return
        vals = self.book_tree.item(sel[0])['values']
        book_id = vals[0]
        self._clear_copies()
        for c in self.presenter.get_copies_by_book(book_id):
            self.copy_tree.insert('', 'end', values=[c['reg_no'], c['library_room'],
                                                      c['in_date'], c['status']])

    def _get_selected_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一本图书')
            return None
        return self.book_tree.item(sel[0])['values']

    def _add_book(self):
        self._open_book_dialog('新增图书')

    def _edit_book(self):
        vals = self._get_selected_book()
        if vals:
            self._open_book_dialog('编辑图书', vals)

    def _del_book(self):
        vals = self._get_selected_book()
        if not vals:
            return
        if messagebox.askyesno('确认', f"确定删除图书 [{vals[0]}]《{vals[1]}》及其所有副本？"):
            ok, msg = self.presenter.delete_book(vals[0])
            if ok:
                self.refresh_books()
                messagebox.showinfo('成功', msg)
            else:
                messagebox.showerror('失败', msg)

    def _open_book_dialog(self, title, vals=None):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.grab_set()

        fields = [
            ('书号', 'book_id'), ('书名', 'book_name'), ('作者', 'author'),
            ('出版单位', 'publisher'), ('出版日期(YYYY-MM-DD)', 'pub_date'),
            ('版次', 'edition'), ('单价', 'price'), ('内容提要', 'summary'),
            ('分类号', 'class_no'), ('索书号', 'call_no'), ('藏书册数', 'total_copies'),
        ]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dlg, text=label + '：').grid(row=i, column=0, sticky='e', padx=5, pady=3)
            e = ttk.Entry(dlg, width=35)
            e.grid(row=i, column=1, padx=5, pady=3)
            entries[key] = e

        if vals:
            col_keys = [c[0] for c in self.BOOK_COLS]
            for i, key in enumerate(col_keys):
                if key in entries:
                    entries[key].insert(0, vals[i] if vals[i] else '')
            entries['book_id'].configure(state='disabled')

        def _save():
            data = {k: e.get().strip() for k, e in entries.items()}
            if not data['book_id'] or not data['book_name']:
                messagebox.showwarning('提示', '书号和书名不能为空')
                return
            if vals:
                self.presenter.update_book(data['book_id'], (
                    data['book_name'], data['author'], data['publisher'],
                    data['pub_date'], int(data['edition'] or 1),
                    float(data['price'] or 0), data['summary'],
                    data['class_no'], data['call_no'], int(data['total_copies'] or 0)
                ))
            else:
                self.presenter.add_book((
                    data['book_id'], data['book_name'], data['author'],
                    data['publisher'], data['pub_date'], int(data['edition'] or 1),
                    float(data['price'] or 0), data['summary'],
                    data['class_no'], data['call_no'], int(data['total_copies'] or 0)
                ))
            self.refresh_books()
            dlg.destroy()

        ttk.Button(dlg, text='保存', command=_save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _add_copy(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一本图书')
            return
        book_id = self.book_tree.item(sel[0])['values'][0]

        dlg = tk.Toplevel(self)
        dlg.title('新增副本')
        dlg.resizable(False, False)
        dlg.grab_set()

        ttk.Label(dlg, text='馆藏注册号：').grid(row=0, column=0, padx=5, pady=5)
        e_reg = ttk.Entry(dlg, width=25)
        e_reg.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dlg, text='所在书库：').grid(row=1, column=0, padx=5, pady=5)
        e_room = ttk.Entry(dlg, width=25)
        e_room.insert(0, '综合书库')
        e_room.grid(row=1, column=1, padx=5, pady=5)

        def _save():
            reg = e_reg.get().strip()
            room = e_room.get().strip()
            if not reg:
                messagebox.showwarning('提示', '注册号不能为空')
                return
            self.presenter.add_copy(reg, book_id, room)
            self._on_book_select(None)
            dlg.destroy()

        ttk.Button(dlg, text='保存', command=_save).grid(row=2, column=0, columnspan=2, pady=10)

    def _del_copy(self):
        sel = self.copy_tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一个副本')
            return
        reg_no = self.copy_tree.item(sel[0])['values'][0]
        if messagebox.askyesno('确认', f"确定删除副本 {reg_no}？"):
            ok, msg = self.presenter.delete_copy(reg_no)
            if ok:
                self._on_book_select(None)
            else:
                messagebox.showerror('失败', msg)
