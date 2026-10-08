#登录窗口
import tkinter as tk
from tkinter import messagebox

import service


class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("食物选择 - 登录")
        self.root.geometry("360x240")
        self.root.resizable(False, False)
        self.font = ("Microsoft YaHei", 11)

        self._build_ui()
        self._center_window()
        self.root.bind("<Return>", lambda event: self.do_login())     # 回车直接登录

    def _build_ui(self):
        tk.Label(self.root, text="食物选择",
                 font=("Microsoft YaHei", 16, "bold")).pack(pady=(20, 4))
        tk.Label(self.root, text="默认账号：admin / admin123",
                 font=("Microsoft YaHei", 9), fg="gray").pack()

        form = tk.Frame(self.root)
        form.pack(pady=16)

        tk.Label(form, text="用户名：", font=self.font).grid(row=0, column=0, sticky="e", pady=6)
        self.username_entry = tk.Entry(form, font=self.font, width=18)
        self.username_entry.grid(row=0, column=1, pady=6)
        self.username_entry.insert(0, "admin")            # 预填，省得你每次打字

        tk.Label(form, text="密　码：", font=self.font).grid(row=1, column=0, sticky="e", pady=6)
        self.password_entry = tk.Entry(form, font=self.font, width=18, show="*")
        self.password_entry.grid(row=1, column=1, pady=6)

        tk.Button(self.root, text="登 录", font=self.font, width=16,
                  command=self.do_login).pack(pady=6)

        self.username_entry.focus_set()

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        if not service.check_login(username, password):        # ← 和 service.py 对接的唯一一行
            messagebox.showerror("登录失败", "用户名或密码错误")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
            return

        self.root.destroy()                                    # 关掉登录窗口
        from main import MainWindow                            # 函数内导入，避免循环导入
        MainWindow(username).run()                             # 打开主窗口

    def run(self):
        self.root.mainloop()