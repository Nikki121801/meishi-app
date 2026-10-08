#程序入口 + 主窗口
import random                                   # 新增：随机数模块，Python 自带，不用装
import tkinter as tk
from tkinter import ttk, messagebox

import db
import service

class ItemDialog:
    """新增 / 修改记录的小弹窗（student 位置改成了 item）"""

    def __init__(self, parent, on_saved, item=None):
        self.on_saved = on_saved
        self.item = item                        # 有值 = 修改；None = 新增
        self.is_edit = item is not None

        self.top = tk.Toplevel(parent)
        self.top.title("修改记录" if self.is_edit else "新增记录")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)

        self.font = ("Microsoft YaHei", 11)
        self._build_ui()

        if self.is_edit:                        # 修改模式：把原数据填进去
            self.food_var.set(item["食物"])
            self.shop_var.set(item["商店"])
            self.id_label.config(text=item["编号"])

        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.top.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.top.winfo_height()) // 3
        self.top.geometry(f"+{x}+{y}")

    def _build_ui(self):
        form = tk.Frame(self.top, padx=20, pady=16)
        form.pack()

        self.food_var = tk.StringVar()
        self.shop_var = tk.StringVar()

        # 第 0 行：编号（只读展示，不允许手输，防止编号重复导致改错数据）
        tk.Label(form, text="编　号：", font=self.font).grid(row=0, column=0, sticky="e", pady=6)
        self.id_label = tk.Label(form, text="保存后自动生成", font=self.font, fg="#888888")
        self.id_label.grid(row=0, column=1, sticky="w", pady=6)

        tk.Label(form, text="食　物：", font=self.font).grid(row=1, column=0, sticky="e", pady=6)
        tk.Entry(form, textvariable=self.food_var, font=self.font, width=22).grid(row=1, column=1, pady=6)

        tk.Label(form, text="商　店：", font=self.font).grid(row=2, column=0, sticky="e", pady=6)
        tk.Entry(form, textvariable=self.shop_var, font=self.font, width=22).grid(row=2, column=1, pady=6)

        buttons = tk.Frame(self.top, pady=12)
        buttons.pack()
        tk.Button(buttons, text="保存", font=self.font, width=10, command=self.save).grid(row=0, column=0, padx=8)
        tk.Button(buttons, text="取消", font=self.font, width=10, command=self.top.destroy).grid(row=0, column=1, padx=8)

        self.top.bind("<Return>", lambda event: self.save())

    def save(self):
        food = self.food_var.get()
        shop = self.shop_var.get()

        if self.is_edit:
            ok, message = service.update_item(self.item["编号"], food, shop)
        else:
            ok, message = service.add_item(food, shop)

        if not ok:
            messagebox.showwarning("提示", message, parent=self.top)
            return

        self.top.destroy()
        self.on_saved()                         # 通知主窗口刷新表格


class MainWindow:
    """主窗口：搜索栏 + 操作按钮 + 数据表格 + 状态栏"""

    def __init__(self, username="用户"):
        self.username = username
        self.root = tk.Tk()
        self.root.title("食物选择")
        self.root.geometry("820x520")
        self.root.minsize(700, 440)

        self.font = ("Microsoft YaHei", 11)
        self.keyword_var = tk.StringVar()

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---------- 顶部标题栏 ----------
        header = tk.Frame(self.root, bg="#c0504d", height=48)      # 暖色，配美食主题
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="食物选择", bg="#c0504d", fg="white",
                 font=("Microsoft YaHei", 14, "bold")).pack(side="left", padx=16)
        tk.Label(header, text=f"当前用户：{self.username}", bg="#c0504d", fg="white",
                 font=("Microsoft YaHei", 10)).pack(side="right", padx=16)

        # ---------- 工具栏 ----------
        toolbar = tk.Frame(self.root, pady=10)
        toolbar.pack(fill="x", padx=12)

        tk.Label(toolbar, text="关键字：", font=self.font).pack(side="left")
        entry = tk.Entry(toolbar, textvariable=self.keyword_var, font=self.font, width=18)
        entry.pack(side="left")
        entry.bind("<Return>", lambda event: self.refresh())        # 回车即搜索

        tk.Button(toolbar, text="查询", font=self.font, width=7,
                  command=self.refresh).pack(side="left", padx=6)
        tk.Button(toolbar, text="清空", font=self.font, width=7,
                  command=self.clear_search).pack(side="left")
        tk.Button(toolbar, text="随机选择", font=self.font, width=9,
                  fg="#b3541e", command=self.random_pick).pack(side="left", padx=6)

        tk.Button(toolbar, text="删除选中", font=self.font, width=9,
                  command=self.delete_selected).pack(side="right")
        tk.Button(toolbar, text="修改选中", font=self.font, width=9,
                  command=self.edit_selected).pack(side="right", padx=6)
        tk.Button(toolbar, text="新增记录", font=self.font, width=9,
                  command=self.add_item).pack(side="right")

        # ---------- 表格（只有 3 列，和你的 CSV 一致）----------
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        columns = ("id", "food", "shop")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)

        headings = {
            "id": ("编号", 100),
            "food": ("食物", 260),
            "shop": ("商店", 240),
        }
        for key, (text, width) in headings.items():
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda event: self.edit_selected())    # 双击 = 修改

        # ---------- 底部状态栏 ----------
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(self.root, textvariable=self.status_var, anchor="w",
                 font=("Microsoft YaHei", 9), fg="#555555").pack(fill="x", padx=12, pady=(0, 6))

    # ---------------- 刷新 ----------------
    def refresh(self):
        """按当前关键字重新读 CSV 并显示"""
        keyword = self.keyword_var.get().strip()

        for item in self.tree.get_children():       # 先清空表格
            self.tree.delete(item)

        records = service.list_items(keyword)       # 再重新填
        for it in records:
            self.tree.insert("", "end", values=(it["编号"], it["食物"], it["商店"]))

        if keyword:
            self.status_var.set(f"关键字「{keyword}」共找到 {len(records)} 条记录")
        else:
            self.status_var.set(f"共 {len(records)} 条记录（双击一行可以修改）")

    def clear_search(self):
        self.keyword_var.set("")
        self.refresh()

    def _get_selected_id(self):
        """取选中行的编号；没选返回 None"""
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        return values[0]                            # 编号（字符串）

    # ---------------- 随机选择 ----------------

    def random_pick(self):
        """从当前表格里的记录中随机抽一条，并高亮出来"""
        items = self.tree.get_children()  # 取出表格里所有行的内部 id
        if not items:  # 空表格不能抽
            messagebox.showinfo("提示", "表格里还没有数据，先新增几条吧")
            return

        chosen = random.choice(items)  # random.choice 从列表里随机挑一个
        values = self.tree.item(chosen, "values")  # 取出这一行的数据（编号/食物/商店）

        self.tree.selection_set(chosen)  # 把它设为"选中"状态（变蓝）
        self.tree.focus(chosen)  # 焦点移过去
        self.tree.see(chosen)  # 如果它在下面看不见，自动滚动到它

        messagebox.showinfo(
            "随机选择结果",
            f"今天就吃这个吧！\n\n【{values[1]}】\n来自：{values[2]}",
            parent=self.root,
        )
        self.status_var.set(f"随机选中：{values[2]} - {values[1]}")

    # ---------------- 增删改 ----------------
    def add_item(self):
        ItemDialog(self.root, on_saved=self.refresh)

    def edit_selected(self):
        item_id = self._get_selected_id()
        if item_id is None:
            messagebox.showinfo("提示", "请先在表格里选中一行")
            return

        item = service.get_item(item_id)
        if item is None:
            messagebox.showwarning("提示", "这条记录已经不存在了，请点「查询」刷新")
            self.refresh()
            return

        ItemDialog(self.root, on_saved=self.refresh, item=item)

    def delete_selected(self):
        item_id = self._get_selected_id()
        if item_id is None:
            messagebox.showinfo("提示", "请先在表格里选中一行")
            return

        item = service.get_item(item_id)
        if item is None:
            messagebox.showwarning("提示", "这条记录已经不存在了，请点「查询」刷新")
            self.refresh()
            return

        if not messagebox.askyesno("确认删除", f"确定要删除「{item['商店']}」的「{item['食物']}」吗？"):
            return

        ok, message = service.delete_item(item_id)
        if ok:
            self.refresh()
            self.status_var.set(message)
        else:
            messagebox.showerror("删除失败", message)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    db.init_data()                  # 确保 CSV 存在
    from login import LoginWindow
    LoginWindow().run()