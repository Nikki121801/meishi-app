#业务层（校验、增删改查）
import db


# ---------------- 登录 ----------------
def check_login(username, password):
    return username == db.USERNAME and password == db.PASSWORD


# ---------------- 查询 ----------------
def list_items(keyword=""):
    """返回记录列表；给了关键字就按 食物 或 商店 模糊筛选"""
    items = db.load_items()
    keyword = keyword.strip()
    if keyword:
        items = [
            it for it in items
            if keyword in it["食物"] or keyword in it["商店"]      # 食物或商店里包含关键字
        ]
    # 按编号的数字大小排序；编号不是数字时排在最后
    return sorted(items, key=lambda it: int(it["编号"]) if it["编号"].isdigit() else 999999)


def get_item(item_id):
    """按编号查一条记录，找不到返回 None"""
    for it in db.load_items():
        if it["编号"] == str(item_id):
            return it
    return None


def _next_id(items):
    """算出下一个编号：现有最大编号 + 1"""
    numbers = [int(it["编号"]) for it in items if it["编号"].isdigit()]
    return str(max(numbers) + 1) if numbers else "1"


def _validate(food, shop, items, old_id=None):
    """检查输入；返回错误提示，没问题返回空字符串"""
    if not food.strip():
        return "食物名称不能为空"
    if not shop.strip():
        return "商店名称不能为空"

    # 同一家店里的同一个食物不允许重复（不同店可以有同名食物）
    for it in items:
        if it["编号"] == old_id:            # 修改时跳过自己
            continue
        if it["食物"] == food.strip() and it["商店"] == shop.strip():
            return f"「{shop.strip()}」里已经有「{food.strip()}」了"
    return ""
def add_item(food, shop):
    """新增一条记录（编号自动生成）"""
    items = db.load_items()
    error = _validate(food, shop, items)
    if error:
        return False, error

    items.append({"编号": _next_id(items), "食物": food.strip(), "商店": shop.strip()})
    db.save_items(items)
    return True, "新增成功"


def update_item(item_id, food, shop):
    """按编号修改（编号本身不允许改）"""
    items = db.load_items()
    error = _validate(food, shop, items, old_id=str(item_id))
    if error:
        return False, error

    for it in items:
        if it["编号"] == str(item_id):
            it["食物"] = food.strip()
            it["商店"] = shop.strip()
            db.save_items(items)
            return True, "修改成功"
    return False, "没有找到这条记录，可能已经被删除了"


def delete_item(item_id):
    """按编号删除"""
    items = db.load_items()
    remaining = [it for it in items if it["编号"] != str(item_id)]
    if len(remaining) == len(items):        # 长度没变说明没找到
        return False, "没有找到这条记录，可能已经被删除了"
    db.save_items(remaining)
    return True, "删除成功"