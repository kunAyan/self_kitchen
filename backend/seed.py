"""Seed database with v2 initial data — 木糯小厨."""

from app import create_app
from extensions import db
from models import User, DishCategory, Dish, StoreConfig


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        if User.query.first():
            db.drop_all()
            db.create_all()

        # --- Users (lower initial balances) ---
        admin = User(username='admin', nickname='大厨👨‍🍳', role='admin', balance=50000)
        admin.set_password('admin123')

        gf = User(username='lqyispig', nickname='小吃货👧', role='customer', balance=20000)
        gf.set_password('210303')

        mumu = User(username='木木', nickname='木木🐱', role='customer', balance=5000)
        mumu.set_password('260119')

        nuonuo = User(username='糯糯', nickname='糯糯🐱', role='customer', balance=5000)
        nuonuo.set_password('241122')

        db.session.add_all([admin, gf, mumu, nuonuo])
        db.session.flush()

        # --- Categories ---
        cats_data = [
            {'name': '主食', 'icon': '🍝', 'sort_order': 1},
            {'name': '饮品', 'icon': '🥤', 'sort_order': 2},
            {'name': '甜点', 'icon': '🍰', 'sort_order': 3},
            {'name': '小食', 'icon': '🥗', 'sort_order': 4},
        ]
        categories = {}
        for cd in cats_data:
            c = DishCategory(**cd)
            db.session.add(c)
            db.session.flush()
            categories[cd['name']] = c.id

        # --- Dishes ---
        dishes_data = [
            {'cat': '主食', 'name': '番茄肉酱意面', 'price': 3200, 'note': '招牌必点', 'desc': '酸甜可口的经典意面',
             'ing': '意面, 番茄, 猪肉末, 洋葱, 芝士, 橄榄油'},
            {'cat': '主食', 'name': '蛋炒饭', 'price': 1500, 'note': '', 'desc': '粒粒分明的黄金蛋炒饭',
             'ing': '米饭, 鸡蛋, 葱花, 盐, 油'},
            {'cat': '主食', 'name': '红烧牛肉面', 'price': 2800, 'note': '大厨推荐', 'desc': '大块牛肉配浓郁汤底',
             'ing': '面条, 牛肉, 酱油, 八角, 姜, 葱'},
            {'cat': '饮品', 'name': '珍珠奶茶', 'price': 1200, 'note': '人气第一', 'desc': 'Q弹珍珠搭配香浓奶茶',
             'ing': '红茶, 牛奶, 珍珠, 糖浆'},
            {'cat': '饮品', 'name': '冰美式咖啡', 'price': 1800, 'note': '', 'desc': '提神醒脑经典美式',
             'ing': '咖啡豆, 冰水'},
            {'cat': '饮品', 'name': '柠檬气泡水', 'price': 1000, 'note': '夏日特饮', 'desc': '清爽酸甜的夏日特饮',
             'ing': '柠檬, 气泡水, 蜂蜜'},
            {'cat': '甜点', 'name': '提拉米苏', 'price': 2500, 'note': '', 'desc': '意式经典，层层甜蜜',
             'ing': '马斯卡彭芝士, 咖啡, 手指饼干, 可可粉, 鸡蛋'},
            {'cat': '甜点', 'name': '草莓蛋糕', 'price': 2200, 'note': '小吃货最爱', 'desc': '新鲜草莓搭配松软蛋糕',
             'ing': '面粉, 草莓, 奶油, 鸡蛋, 糖'},
            {'cat': '小食', 'name': '炸鸡翅', 'price': 1800, 'note': '', 'desc': '外酥里嫩，香脆可口',
             'ing': '鸡翅, 面粉, 油, 辣椒粉, 蒜'},
            {'cat': '小食', 'name': '水果沙拉', 'price': 1600, 'note': '清爽健康', 'desc': '新鲜时令水果拼盘',
             'ing': '苹果, 香蕉, 草莓, 酸奶, 蜂蜜'},
        ]
        for i, dd in enumerate(dishes_data):
            db.session.add(Dish(
                category_id=categories[dd['cat']],
                name=dd['name'], price=dd['price'],
                note=dd['note'], description=dd['desc'],
                ingredients=dd.get('ing', ''),
                sort_order=i + 1,
            ))

        # --- Store config ---
        defaults = {
            'store_name': '木糯小厨',
            'store_image': '',
            'store_intro': '木木和糯糯的小厨房，记录每一天的温暖 💕',
            'banner_image': '',
            'banner_text': '欢迎来到木糯小厨~',
            'welcome_message': '今天想吃什么呢？',
            'featured_dish_ids': '[]',
            'login_subtitle': '木木和糯糯的小厨房',
            'login_footer': '💕 记录每一天的温暖',
        }
        for k, v in defaults.items():
            db.session.add(StoreConfig(key=k, value=v))

        db.session.commit()
        print("✅ 木糯小厨 seed data created!")
        print(f"   Users: admin(¥500), lqyispig(¥200), 木木(¥50), 糯糯(¥50)")
        print(f"   Categories: {len(cats_data)}, Dishes: {len(dishes_data)}")


if __name__ == '__main__':
    seed()
