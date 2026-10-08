import csv                      # 读写 CSV
import os                       # 处理路径

# db.py 自己所在的文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ★★★ 如果你把 CSV 改名了，改这里 ★★★
CSV_FILE = os.path.join(BASE_DIR, "食物1.csv")

# CSV 里的表头（必须和你 Excel 第一行完全一致，一个字都不能差）
FIELDS = ["编号", "食物", "商店"]


def load_items():
    """读取所有记录，返回列表：[{'编号': '1', '食物': '麻辣烫1', '商店': '冒泡泡'}, ...]"""
    if not os.path.exists(CSV_FILE):        # 文件不存在
        print("找不到数据文件：", CSV_FILE)
        return []

    items = []
    # utf-8-sig：对应 Excel 的「CSV UTF-8」，能吃掉开头的 BOM，中文不乱码
    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):       # 每行变成一个字典
            # 跳过 Excel 里可能的空行 / 分隔行
            if not any(str(v).strip() for v in row.values() if v is not None):
                continue
            # 只取我们关心的三个字段，顺便把首尾空格去掉
            items.append({
                "编号": str(row.get("编号", "")).strip(),
                "食物": str(row.get("食物", "")).strip(),
                "商店": str(row.get("商店", "")).strip(),
            })
    return items


def save_items(items):
    """把整个列表写回 CSV（会覆盖原文件）"""
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()        # 先写表头那一行
        writer.writerows(items)     # 再逐行写数据


def init_data():
    """程序启动时调用；CSV 不存在就建一个只有表头的空文件"""
    if not os.path.exists(CSV_FILE):
        save_items([])

USERNAME = "admin"
PASSWORD = "admin123"

if __name__ == "__main__":
    print(load_items())
