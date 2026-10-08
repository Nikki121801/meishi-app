# -*- coding: utf-8 -*-
"""
app.py —— 美食店铺管理系统（网页版）
本地运行：python app.py  →  http://127.0.0.1:5000
云端部署：上传 app.py + requirements.txt + seed.csv 即可
"""
import os
import random
import shutil
from flask import Flask, redirect, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "meishi-app-2024"          # 用于加密登录状态，可改成任意字符串

# ---------------- 文件位置 ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.csv")      # 程序实际读写的数据文件
SEED_FILE = os.path.join(BASE_DIR, "seed.csv")      # 初始数据（你的那份数据）

# ---------------- 登录账号 ----------------
USERNAME = "admin"
PASSWORD = "admin123"

# ---------------- 网页模板 ----------------
PAGE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>美食店铺管理系统</title>
  <style>
    body { font-family: -apple-system, "Microsoft YaHei", sans-serif; margin: 0; background: #f6f6f6; }
    .bar { background: #c0504d; color: #fff; padding: 14px 16px; font-size: 18px; font-weight: bold; }
    .box { padding: 14px; max-width: 720px; margin: 0 auto; }
    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px 10px; border-bottom: 1px solid #eee; text-align: left; font-size: 15px; }
    th { background: #f0f0f0; }
    input { padding: 10px; font-size: 15px; border: 1px solid #ccc; border-radius: 6px; width: 44%; box-sizing: border-box; }
    button { padding: 10px 16px; font-size: 15px; border: 0; border-radius: 6px; background: #c0504d; color: #fff; }
    .pick { background: #b3541e; }
    .gray { background: #777; }
    a.del { color: #c0504d; text-decoration: none; }
    .result { background: #fff7e6; border: 1px solid #f0c36d; padding: 12px; border-radius: 8px; margin: 12px 0; font-size: 17px; }
    .login { max-width: 320px; margin: 60px auto; background: #fff; padding: 24px; border-radius: 10px; }
    .login input { width: 100%; margin-bottom: 10px; }
    .login button { width: 100%; }
  </style>
</head>
<body>
  <div class="bar">美食店铺管理系统</div>
  <div class="box">

  {% if not logged %}
    <div class="login">
      <form method="post" action="/login">
        <input name="username" placeholder="用户名" value="admin">
        <input name="password" type="password" placeholder="密码">
        <button type="submit">登录</button>
      </form>
    </div>
  {% else %}

    <form method="get" action="/" style="margin-bottom:10px">
      <input name="kw" value="{{ kw }}" placeholder="搜索食物或商店">
      <button type="submit">查询</button>
      <a href="/"><button type="button" class="gray">清空</button></a>
    </form>

    <form method="post" action="/add" style="margin-bottom:14px">
      <input name="food" placeholder="食物，如：麻辣烫" required>
      <input name="shop" placeholder="商店，如：冒泡泡" required>
      <button type="submit">新增</button>
    </form>

    <p>
      <a href="/pick{% if kw %}?kw={{ kw }}{% endif %}"><button class="pick">🎲 随机选择</button></a>
      　共 {{ items|length }} 条
      <a href="/logout" style="float:right;color:#888;font-size:13px">退出</a>
    </p>

    {% if picked %}
      <div class="result">今天就吃这个吧！　<b>{{ picked.食物 }}</b>　—— {{ picked.商店 }}</div>
    {% endif %}

    <table>
      <tr><th>编号</th><th>食物</th><th>商店</th><th>操作</th></tr>
      {% for it in items %}
      <tr>
        <td>{{ it.编号 }}</td>
        <td>{{ it.食物 }}</td>
        <td>{{ it.商店 }}</td>
        <td><a class="del" href="/delete/{{ it.编号 }}?kw={{ kw }}">删除</a></td>
      </tr>
      {% endfor %}
    </table>

  {% endif %}
  </div>
</body>
</html>
"""


# ---------------- 数据读写 ----------------
def _ensure_data_file():
    """第一次运行时，把 seed.csv 复制成 data.csv 当作可修改的数据文件"""
    if not os.path.exists(DATA_FILE) and os.path.exists(SEED_FILE):
        shutil.copyfile(SEED_FILE, DATA_FILE)


def load_items():
    """从 CSV 读全部记录"""
    _ensure_data_file()
    if not os.path.exists(DATA_FILE):
        return []
    import csv
    items = []
    with open(DATA_FILE, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not any(str(v).strip() for v in row.values() if v is not None):
                continue
            items.append({
                "编号": str(row.get("编号", "")).strip(),
                "食物": str(row.get("食物", "")).strip(),
                "商店": str(row.get("商店", "")).strip(),
            })
    return items


def save_items(items):
    """把全部记录写回 CSV"""
    import csv
    with open(DATA_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["编号", "食物", "商店"])
        writer.writeheader()
        writer.writerows(items)


def next_id(items):
    """算出下一个编号"""
    numbers = [int(it["编号"]) for it in items if it["编号"].isdigit()]
    return str(max(numbers) + 1) if numbers else "1"


def filter_items(items, keyword):
    """按关键字筛选（食物或商店包含关键字）"""
    keyword = (keyword or "").strip()
    if not keyword:
        return items
    return [it for it in items if keyword in it["食物"] or keyword in it["商店"]]


# ---------------- 页面路由 ----------------
@app.route("/")
def index():
    """首页；没登录就只显示登录框"""
    if not session.get("logged"):
        return render_template_string(PAGE, logged=False, items=[], picked=None, kw="")

    kw = request.args.get("kw", "")
    items = filter_items(load_items(), kw)
    return render_template_string(PAGE, logged=True, items=items, picked=None, kw=kw)


@app.route("/login", methods=["POST"])
def login():
    """校验账号密码"""
    if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
        session["logged"] = True
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add", methods=["POST"])
def add():
    """新增记录"""
    if not session.get("logged"):
        return redirect("/")
    food = request.form.get("food", "").strip()
    shop = request.form.get("shop", "").strip()
    if food and shop:
        items = load_items()
        items.append({"编号": next_id(items), "食物": food, "商店": shop})
        save_items(items)
    return redirect("/")


@app.route("/delete/<item_id>")
def delete(item_id):
    """按编号删除"""
    if not session.get("logged"):
        return redirect("/")
    items = load_items()
    remaining = [it for it in items if it["编号"] != str(item_id)]
    if len(remaining) != len(items):
        save_items(remaining)
    kw = request.args.get("kw", "")
    return redirect(f"/?kw={kw}")


@app.route("/pick")
def pick():
    """随机抽一条：搜了关键字就只在筛选结果里抽"""
    if not session.get("logged"):
        return redirect("/")
    kw = request.args.get("kw", "")
    items = filter_items(load_items(), kw)
    picked = random.choice(items) if items else None
    return render_template_string(PAGE, logged=True, items=items, picked=picked, kw=kw)


if __name__ == "__main__":
    _ensure_data_file()
    port = int(os.environ.get("PORT", 5000))
    print("=" * 46)
    print(f"本机访问：http://127.0.0.1:{port}")
    print("=" * 46)
    app.run(host="0.0.0.0", port=port)