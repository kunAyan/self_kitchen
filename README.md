# 🍳 木糯小厨 — 家庭点餐小程序

四人家庭点餐+生活记录微信小程序：大厨配置菜品，家人点单，共享日记。

## 功能

### 🧑‍🍳 管理端（admin）

| 模块 | 功能 |
|------|------|
| 📊 仪表盘 | 总览统计 + 各用户余额 + 全部快捷入口 |
| 🏪 店铺配置 | 名称/大图/Banner/欢迎语/主打菜/登录页文案 |
| 📂 分类管理 | CRUD + emoji 图标选择 |
| 🍽️ 菜品管理 | CRUD + 多图 + 食材清单 + 备注标签 + **批量上下架** |
| 📦 订单处理 | 全部订单筛选 + 接单(设出餐时间)/拒单(退款)/完成 |
| 👤 用户管理 | 创建/编辑/密码重置 + **充值/扣减余额** |
| ⭐ 今日特供 | 每日选一道菜突出展示 |
| 💝 纪念日 | CRUD + 每年重复标记 |
| 📈 销量统计 | 热销排行 + 餐段分布 + 月度趋势 |
| 📄 月度报告 | 订单/金额/最爱菜/最勤厨师 |

### 👨‍👩‍👧‍👦 客户端

| 模块 | 功能 |
|------|------|
| 🔑 登录 | 仅登录，无注册 |
| 🏠 店铺简介 | 每次登录展示：特供/人气/招牌/最新日记 |
| 🍽️ 菜单 | 美团式侧边栏 + 菜品搜索 + 购物车加减器 + 🎲随机点菜 |
| ⭐ 收藏 | ❤️收藏常点菜品 |
| 🛒 购物车 | 厨师选择 + 餐段(早/午/晚/茶/宵) + 备注 + 余额校验 |
| 📋 订单 | 状态筛选 + 下拉刷新 + 📋再来一单 |
| 😋 用餐心情 | 完成后记录 emoji 心情 |
| ⭐ 评价 | 星级+文字 + 大厨可回复 |
| 🛒 食材清单 | 订单详情自动汇总采购清单 |
| 👤 个人中心 | 头像/余额/点餐统计/成就徽章(15种)/日记照片/评价历史 |
| 📅 共享日记 | 日历+列表双视图 + 照片上传 + 写日记+心情 + 订单自动标记 + 纪念日标记 |
| 🌟 许愿池 | 三个用户许愿想吃的菜 → 点赞附议 → 大厨实现+留言 |

### 🔔 系统

| 功能 | 说明 |
|------|------|
| 🔴 订单角标 | TabBar 待处理数字红点 |
| 📥 下拉刷新 | 订单页 |
| 🎲 摇骰子 | 随机点菜动画 |
| 🔒 购物车隔离 | 登出自动清空，切换账号不残留 |
| 🖼️ 图片本地存储 | 换电脑只需改 config.js |
| 📦 批量操作 | 菜品管理多选 + 一键上下架 |

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | uni-app (Vue 3) → 微信小程序 |
| 后端 | Python Flask + SQLAlchemy |
| 数据库 | SQLite |
| 认证 | JWT (7天) |

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python3 seed.py      # 初始化数据
python3 app.py       # → http://localhost:5099
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev:mp-weixin
```

微信开发者工具打开 `frontend/dist/dev/mp-weixin`，勾选「不校验合法域名」。

### 3. 手机访问

修改 `frontend/src/config.js` 中的 IP 为电脑局域网 IP，重新编译后扫码预览。

## 账户

| 用户名 | 密码 | 角色 | 初始余额 |
|--------|------|------|----------|
| `admin` | `admin123` | 管理员 | ¥500 |
| `lqyispig` | `210303` | 小吃货 | ¥200 |
| `木木` | `260119` | 食客 | ¥50 |
| `糯糯` | `241122` | 食客 | ¥50 |

## 项目结构

```
project_cook/
├── backend/                  # Flask API
│   ├── app.py, config.py, extensions.py
│   ├── models.py             # 13 数据模型
│   ├── seed.py               # 种子数据
│   └── api/                  # 8 API 模块，56 接口
├── frontend/                 # uni-app
│   └── src/
│       ├── config.js         # API 地址（唯一需修改的配置）
│       ├── pages/            # 20 页面
│       ├── components/       # 3 组件
│       ├── stores/           # 3 Pinia Store
│       └── api/              # 8 API 模块
└── README.md
```

## 数据库

13 张表：users, dish_categories, dishes, dish_images, orders, order_items, balance_logs, reviews, store_config, daily_photos, daily_notes, today_special, special_dates

## 开发命令

```bash
# 后端
cd backend
python3 seed.py          # 重置数据库
python3 app.py           # 启动

# 前端
cd frontend
npm run dev:mp-weixin    # 开发编译
```
