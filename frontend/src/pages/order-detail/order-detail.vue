<template>
  <view v-if="!order" class="loading-wrap"><text>加载中...</text></view>
  <view class="detail-page" v-else-if="order">
    <!-- Status timeline -->
    <view class="card">
      <view class="timeline">
        <view class="tl-item done"><view class="tl-dot"></view><view class="tl-info"><text class="tl-title">已下单</text><text class="tl-time">{{ fmt(order.created_at) }}</text></view></view>
        <view class="tl-item" :class="{ done: isDone('accepted'), rejected: order.status === 'rejected' }"><view class="tl-dot"></view><view class="tl-info"><text class="tl-title">{{ order.status === 'rejected' ? '已拒单' : '已接单' }}</text></view></view>
        <view class="tl-item" :class="{ done: isDone('completed') }"><view class="tl-dot"></view><view class="tl-info"><text class="tl-title">已完成</text><text class="tl-time" v-if="order.status==='completed'">{{ fmt(order.updated_at) }}</text></view></view>
      </view>
    </view>

    <!-- Chef + meal info -->
    <view class="card">
      <view class="info-row"><text class="info-label">订单编号</text><text class="info-value">#{{ order.order_no }}</text></view>
      <view class="info-row"><text class="info-label">状态</text><OrderStatusTag :status="order.status" /></view>
      <view class="info-row" v-if="order.chef_nickname"><text class="info-label">厨师</text><text class="info-value">👨‍🍳 {{ order.chef_nickname }}</text></view>
      <view class="info-row" v-if="order.meal_type"><text class="info-label">餐段</text><text class="info-value">{{ mealLabel(order.meal_type) }}</text></view>
      <view class="info-row" v-if="order.placed_by_nickname"><text class="info-label">代下单</text><text class="info-value">{{ order.placed_by_nickname }} 代点</text></view>
      <view class="info-row" v-if="order.estimated_time"><text class="info-label">预计出餐</text><text class="info-value" style="color:#7EC8E3">⏱ {{ fmt(order.estimated_time) }}</text></view>
      <view class="info-row" v-if="order.note"><text class="info-label">备注</text><text class="info-value" style="color:#FF7B93">{{ order.note }}</text></view>
    </view>

    <!-- Items -->
    <view class="card">
      <text class="section-title">菜品明细</text>
      <view v-for="item in order.items" :key="item.id" class="order-item">
        <view class="oi-left"><text class="oi-name">{{ item.dish_name }}</text><text class="oi-price">¥{{ (item.price/100).toFixed(2) }}</text></view>
        <view class="oi-right"><text class="oi-qty">x{{ item.quantity }}</text><text class="oi-sub">¥{{ (item.subtotal/100).toFixed(2) }}</text></view>
      </view>
      <view class="divider"></view>
      <view class="total-row"><text class="total-label">合计</text><text class="total-amount">¥{{ (order.total_amount/100).toFixed(2) }}</text></view>
    </view>

    <!-- Mood (v2) -->
    <view v-if="order.status === 'completed' && !order.mood" class="card mood-card" @click="showMood = true">
      <text>😋 记录用餐心情</text>
    </view>
    <view v-if="order.mood" class="card">
      <view class="mood-display">
        <text class="mood-emoji">{{ order.mood }}</text>
        <text class="mood-text">{{ order.mood_note || '用餐愉快~' }}</text>
      </view>
    </view>

    <!-- Ingredient list -->
    <view class="card" v-if="combinedIngredients.length > 0">
      <text class="section-title">🛒 食材采购清单</text>
      <view class="ingredient-tags">
        <text v-for="(ing, i) in combinedIngredients" :key="i" class="ing-tag">{{ ing }}</text>
      </view>
    </view>

    <!-- Actions -->
    <view class="action-area">
      <button class="reorder-btn" @click="handleReorder">📋 再来一单</button>
    </view>
    <view class="action-area" v-if="order.status === 'pending'">
      <button class="cancel-btn" @click="handleCancel">取消订单</button>
    </view>

    <!-- Mood modal -->
    <view v-if="showMood" class="modal-overlay" @click="showMood = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">用餐心情</text>
        <view class="emoji-options">
          <text v-for="e in emojis" :key="e.icon" class="emoji-opt" :class="{ selected: moodEmoji === e.icon }" @click="moodEmoji = e.icon">{{ e.icon }}</text>
        </view>
        <input class="mood-input" v-model="moodText" placeholder="说点什么..." />
        <button class="mood-btn" @click="saveMood">保存</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { ordersAPI } from '@/api/orders'
import { dishesAPI } from '@/api/dishes'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import OrderStatusTag from '@/components/OrderStatusTag.vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const order = ref(null)
const showMood = ref(false)
const ingredientsMap = ref({})

const combinedIngredients = computed(() => {
  if (!order.value || !order.value.items) return []
  const allIngs = new Set()
  for (const item of order.value.items) {
    const ings = ingredientsMap.value[item.dish_id]
    if (ings) {
      ings.split(/[,，]/).forEach(i => {
        const t = i.trim()
        if (t) allIngs.add(t)
      })
    }
  }
  return [...allIngs]
})
const moodEmoji = ref('😋')
const moodText = ref('')
const emojis = [{ icon: '😋' }, { icon: '😊' }, { icon: '😐' }, { icon: '😞' }]

onLoad(async (opts) => {
  try {
    const res = await ordersAPI.getDetail(opts.id)
    order.value = res.order
    // Fetch ingredients for each dish
    if (order.value && order.value.items) {
      for (const item of order.value.items) {
        try {
          const dishRes = await dishesAPI.getDish(item.dish_id)
          if (dishRes.dish && dishRes.dish.ingredients) {
            ingredientsMap.value[item.dish_id] = dishRes.dish.ingredients
          }
        } catch { /* skip */ }
      }
    }
  } catch (e) { uni.showToast({ title: '加载失败', icon: 'none' }) }
})

function isDone(s) {
  const map = { pending: 0, accepted: 1, completed: 2 }
  return (map[order.value?.status] || 0) >= (map[s] || 0)
}
function mealLabel(t) {
  const m = { breakfast: '🌅早餐', lunch: '☀️午餐', dinner: '🌙晚餐', snack: '🍰下午茶', night_snack: '🌃夜宵' }
  return m[t] || t
}
function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function handleReorder() {
  if (!order.value || !order.value.items) return
  for (const item of order.value.items) {
    cartStore.addDish({ id: item.dish_id, name: item.dish_name, price: item.price, image: item.dish_image, category_icon: '🍽️', is_available: true }, item.quantity)
  }
  uni.showToast({ title: '已加入购物车', icon: 'success' })
  uni.navigateTo({ url: '/pages/cart/cart' })
}

async function handleCancel() {
  uni.showModal({
    title: '确认取消', content: '取消后退还余额，确定吗？',
    success: async (r) => {
      if (r.confirm) {
        try {
          await ordersAPI.cancel(order.value.id)
          uni.showToast({ title: '已取消', icon: 'success' })
          await authStore.refreshProfile()
          const res = await ordersAPI.getDetail(order.value.id); order.value = res.order
        } catch (e) { uni.showToast({ title: e.msg || '取消失败', icon: 'none' }) }
      }
    },
  })
}

async function saveMood() {
  try {
    await ordersAPI.recordMood(order.value.id, moodEmoji.value, moodText.value)
    uni.showToast({ title: '已记录', icon: 'success' })
    showMood.value = false
    const res = await ordersAPI.getDetail(order.value.id); order.value = res.order
  } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
}
</script>

<style lang="scss" scoped>
.detail-page { min-height: 100vh; background: #FFF5F7; padding: 16rpx 0; }
.card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin: 16rpx 24rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.timeline { padding: 8rpx 0; }
.tl-item { display: flex; align-items: flex-start; padding-left: 40rpx; position: relative; padding-bottom: 32rpx; }
.tl-item:last-child { padding-bottom: 0; }
.tl-item::before { content:''; position:absolute; left:16rpx; top:32rpx; bottom:0; width:2rpx; background:#EEE; }
.tl-item:last-child::before { display:none; }
.tl-item.done::before { background:#FF7B93; }
.tl-dot { position:absolute; left:8rpx; top:4rpx; width:18rpx; height:18rpx; border-radius:50%; background:#EEE; border:3rpx solid #FFF; z-index:1; }
.tl-item.done .tl-dot { background:#FF7B93; }
.tl-item.rejected .tl-dot { background:#FF6B6B; }
.tl-info { margin-left:12rpx; }
.tl-title { font-size:28rpx; font-weight:600; color:#CCC; }
.tl-item.done .tl-title { color:#4A4A4A; }
.tl-time { font-size:22rpx; color:#BBB; }
.info-row { display:flex; justify-content:space-between; align-items:center; padding:12rpx 0; border-bottom:1rpx solid #F5F5F5; }
.info-row:last-child { border-bottom:none; }
.info-label { font-size:26rpx; color:#999; }
.info-value { font-size:26rpx; color:#4A4A4A; }
.section-title { font-size:28rpx; font-weight:600; margin-bottom:16rpx; }
.order-item { display:flex; justify-content:space-between; padding:12rpx 0; }
.oi-name { font-size:26rpx; color:#4A4A4A; }
.oi-price { font-size:22rpx; color:#AAA; }
.oi-qty { font-size:26rpx; color:#888; }
.oi-sub { font-size:24rpx; font-weight:600; color:#FF7B93; }
.divider { height:1rpx; background:#F0F0F0; margin:16rpx 0; }
.total-row { display:flex; justify-content:space-between; }
.total-label { font-size:28rpx; font-weight:600; }
.total-amount { font-size:36rpx; font-weight:700; color:#FF7B93; }
.mood-card { text-align:center; font-size:28rpx; color:#FF7B93; padding:28rpx; }
.mood-display { display:flex; align-items:center; gap:12rpx; }
.mood-emoji { font-size:48rpx; }
.mood-text { font-size:26rpx; color:#888; }
.action-area { padding:24rpx; }
.reorder-btn { background: linear-gradient(135deg,#7EC8E3,#9BD5EB); color:#FFF; border:none; border-radius:24rpx; font-size:28rpx; padding:16rpx; margin-bottom:8rpx; }
.cancel-btn { background:#FFF; color:#FF6B6B; border:2rpx solid #FF6B6B; border-radius:24rpx; font-size:28rpx; padding:16rpx; }
.ingredient-tags { display: flex; flex-wrap: wrap; gap: 10rpx; }
.ing-tag { background: #FFF5F7; color: #FF7B93; font-size: 22rpx; padding: 6rpx 16rpx; border-radius: 16rpx; border: 1rpx solid #FFD6DF; }
.modal-overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:100; }
.modal-card { width:560rpx; background:#FFF; border-radius:24rpx; padding:40rpx; }
.modal-title { font-size:32rpx; font-weight:600; text-align:center; display:block; margin-bottom:24rpx; }
.emoji-options { display:flex; justify-content:center; gap:24rpx; margin-bottom:24rpx; }
.emoji-opt { font-size:60rpx; padding:8rpx; border-radius:12rpx; }
.emoji-opt.selected { background:#FFF0F3; border:2rpx solid #FF7B93; }
.mood-input { background:#FFF5F7; border-radius:12rpx; padding:16rpx 20rpx; font-size:26rpx; margin-bottom:20rpx; }
.mood-btn { background:linear-gradient(135deg,#FF7B93,#FFB3C6); color:#FFF; border-radius:24rpx; font-size:28rpx; padding:20rpx; border:none; }
</style>
