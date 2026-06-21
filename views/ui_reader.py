import tkinter as tk
from tkinter import ttk, messagebox


class ReaderManageFrame(ttk.Frame):
    COLUMNS = [
        ('reader_id', '借书证号', 100), ('reader_name', '姓名', 80),
        ('reader_sex', '性别', 50), ('birth_date', '出生日期', 100),
        ('id_card', '身份证号', 150), ('dept', '单位', 120),
        ('phone', '电话', 110), ('reg_date', '办证日期', 100),
        ('borrow_range', '借阅范围', 80), ('max_borrow', '最大借书', 70),
        ('borrow_period', '借期(天)', 70), ('occupation', '职业', 70),
    ]

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text='新增读者', command=self._add).pack(side='left', padx=2)
        ttk.Button(toolbar, text='编辑', command=self._edit).pack(side='left', padx=2)
        ttk.Button(toolbar, text='删除', command=self._delete).pack(side='left', padx=2)
        ttk.Button(toolbar, text='刷新', command=self.refresh).pack(side='left', padx=2)

        ttk.Label(toolbar, text='搜索：').pack(side='left', padx=(20, 2))
        self.search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side='left', padx=2)
        ttk.Button(toolbar, text='查询', command=self._search).pack(side='left', padx=2)
        ttk.Button(toolbar, text='显示全部', command=self.refresh).pack(side='left', padx=2)

        # 表格
        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(self, columns=cols, show='headings', selectmode='browse')
        for key, label, width in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor='center')
        vsb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill='both', expand=True, padx=5, pady=(0, 5), side='left')
        vsb.pack(fill='y', side='right', pady=(0, 5))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in self.db.get_all_readers():
            self.tree.insert('', 'end', values=[r[c[0]] for c in self.COLUMNS])

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self.refresh()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in self.db.search_readers(kw):
            self.tree.insert('', 'end', values=[r[c[0]] for c in self.COLUMNS])

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一条记录')
            return None
        return self.tree.item(sel[0])['values']

    def _add(self):
        self._open_dialog('新增读者')

    def _edit(self):
        vals = self._get_selected()
        if vals:
            self._open_dialog('编辑读者', vals)

    def _delete(self):
        vals = self._get_selected()
        if not vals:
            return
        if messagebox.askyesno('确认', f"确定删除读者 [{vals[0]}] {vals[1]}？"):
            ok, msg = self.db.delete_reader(vals[0])
            if ok:
                self.refresh()
                messagebox.showinfo('成功', msg)
            else:
                messagebox.showerror('失败', msg)

    def _open_dialog(self, title, vals=None):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.grab_set()

        fields = [
            ('借书证号', 'reader_id'), ('姓名', 'reader_name'),
            ('性别(男/女)', 'reader_sex'), ('出生日期(YYYY-MM-DD)', 'birth_date'),
            ('身份证号', 'id_card'), ('单位', 'dept'),
            ('通讯地址', 'address'), ('邮政编码', 'zip_code'),
            ('联系电话', 'phone'), ('借阅范围', 'borrow_range'),
            ('最大借书数', 'max_borrow'), ('借书期限(天)', 'borrow_period'),
            ('职业', 'occupation'),
        ]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dlg, text=label + '：').grid(row=i, column=0, sticky='e', padx=5, pady=3)
            e = ttk.Entry(dlg, width=30)
            e.grid(row=i, column=1, padx=5, pady=3)
            entries[key] = e

        if vals:
            # vals is list aligned with COLUMNS
            col_keys = [c[0] for c in self.COLUMNS]
            for i, key in enumerate(col_keys):
                if key in entries:
                    entries[key].insert(0, vals[i] if vals[i] else '')
            # reader_id 不可编辑
            entries['reader_id'].configure(state='disabled')

        def _save():
            data = {}
            for key, e in entries.items():
                data[key] = e.get().strip()
            if not data['reader_id'] or not data['reader_name']:
                messagebox.showwarning('提示', '借书证号和姓名不能为空')
                return
            if vals:  # 编辑
                self.db.update_reader(data['reader_id'], (
                    data['reader_name'], data['reader_sex'], data['birth_date'],
                    data['id_card'], data['dept'], data['address'], data['zip_code'],
                    data['phone'], data['borrow_range'],
                    int(data['max_borrow'] or 10), int(data['borrow_period'] or 30),
                    data['occupation']
                ))
            else:  # 新增
                self.db.add_reader((
                    data['reader_id'], data['reader_name'], data['reader_sex'],
                    data['birth_date'], data['id_card'], data['dept'], data['address'],
                    data['zip_code'], data['phone'], data.get('reg_date', ''),
                    data['borrow_range'], int(data['max_borrow'] or 10),
                    int(data['borrow_period'] or 30), data['occupation']
                ))
                # 同时创建登录账号
                try:
                    self.db.add_user(data['reader_id'], data['reader_name'], '123456', '读者')
                except Exception:
                    pass
            self.refresh()
            dlg.destroy()

        btn = ttk.Button(dlg, text='保存', command=_save)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=10)
