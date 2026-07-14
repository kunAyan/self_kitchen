<template>
  <view class="cart-page">
    <view v-if="cartStore.items.length === 0">
      <EmptyState icon="🛒" text="购物车空空如也" subText="去菜单页面逛逛吧~" />
    </view>

    <view v-else class="cart-content">
      <view class="cart-list">
        <view v-for="item in cartStore.items" :key="item.dish.id" class="cart-item">
          <view class="cart-item-img" :style="{ backgroundColor: placeholderColor(item.dish) }">
            <image v-if="item.dish.image" class="cart-img" :src="imgUrl(item.dish.image)" mode="aspectFill" />
            <text v-else class="cart-placeholder">{{ item.dish.category_icon || '🍽️' }}</text>
          </view>
          <view class="cart-item-info">
            <text class="cart-item-name">{{ item.dish.name }}</text>
            <text class="cart-item-price">¥{{ (item.dish.price / 100).toFixed(2) }}</text>
          </view>
          <view class="qty-stepper">
            <view class="qty-btn" @click="cartStore.updateQuantity(item.dish.id, item.quantity - 1)"><text>−</text></view>
            <text class="qty-num">{{ item.quantity }}</text>
            <view class="qty-btn" @click="cartStore.updateQuantity(item.dish.id, item.quantity + 1)"><text>+</text></view>
          </view>
        </view>
      </view>

      <!-- Chef + Meal type selectors (v2) -->
      <view class="options-card">
        <view class="opt-row">
          <text class="opt-label">👨‍🍳 谁来做？</text>
          <view class="opt-chips">
            <view v-for="c in chefs" :key="c.id" class="chip" :class="{ active: chefId === c.id }" @click="chefId = c.id">{{ c.nickname }}</view>
          </view>
        </view>
        <view class="opt-row">
          <text class="opt-label">🍽️ 餐段</text>
          <view class="opt-chips">
            <view v-for="m in meals" :key="m.value" class="chip" :class="{ active: mealType === m.value }" @click="mealType = mealType === m.value ? '' : m.value">
              {{ m.icon }} {{ m.label }}
            </view>
          </view>
        </view>
      </view>

      <view class="note-section">
        <input class="note-input" v-model="note" placeholder="写备注…（比如少辣、多点葱）" placeholder-style="color:#CCC" />
      </view>

      <view class="submit-bar">
        <view class="submit-info">
          <text class="submit-label">合计</text>
          <text class="submit-total">¥{{ (cartStore.totalAmount / 100).toFixed(2) }}</text>
        </view>
        <button class="submit-btn" :class="{ disabled: !canOrder }" :disabled="!canOrder" :loading="submitting" @click="submitOrder">
          {{ balanceInsufficient ? '余额不足~' : '提交订单' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { UPLOAD_BASE } from '@/config'
const uploadBase = UPLOAD_BASE
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { ordersAPI } from '@/api/orders'
import { get } from '@/api/index'
import EmptyState from '@/components/EmptyState.vue'

const cartStore = useCartStore()
const authStore = useAuthStore()
const note = ref('')
const submitting = ref(false)
const chefId = ref(0)
const mealType = ref('')
const chefs = ref([])

const meals = [
  { value: 'breakfast', label: '早餐', icon: '🌅' },
  { value: 'lunch', label: '午餐', icon: '☀️' },
  { value: 'dinner', label: '晚餐', icon: '🌙' },
  { value: 'snack', label: '下午茶', icon: '🍰' },
  { value: 'night_snack', label: '夜宵', icon: '🌃' },
]

const canOrder = computed(() => authStore.user && authStore.user.balance >= cartStore.totalAmount)
const balanceInsufficient = computed(() => authStore.user && authStore.user.balance < cartStore.totalAmount)

onMounted(async () => {
  // Refresh user to get latest balance
  await authStore.refreshProfile().catch(() => {})
  // Fetch users for chef selection
  try {
    const res = await get('/auth/users').catch(() => ({ users: [] }))
    chefs.value = res.users || []
  } catch { chefs.value = [] }
  // Set default chef
  if (chefs.value.length === 0) {
    chefs.value = [
      { id: 1, nickname: '大厨👨‍🍳', role: 'admin' },
      { id: 2, nickname: '小吃货👧', role: 'customer' },
    ]
  }
  if (authStore.isAdmin) {
    const gf = chefs.value.find(u => u.username === 'lqyispig' || u.id === 2)
    chefId.value = gf ? gf.id : 2
  } else {
    chefId.value = authStore.user?.id || 1
  }
})

function imgUrl(path) { return `${uploadBase}${path}` }
function placeholderColor(dish) {
  const colors = { '🍝': '#FFE4C4', '🥤': '#D4EFFF', '🍰': '#FFE0EC', '🥗': '#E8F8E0', '🍜': '#FFE8D6' }
  return colors[dish.category_icon] || 'var(--bg-input, #FFF0F3)'
}

async function submitOrder() {
  if (!canOrder.value) return
  submitting.value = true
  try {
    const items = cartStore.items.map(i => ({ dish_id: i.dish.id, quantity: i.quantity }))
    await ordersAPI.create(items, note.value.trim(), chefId.value, mealType.value)
    uni.showToast({ title: '下单成功！', icon: 'success' })
    cartStore.clear()
    note.value = ''
    mealType.value = ''
    await authStore.refreshProfile()
    setTimeout(() => uni.switchTab({ url: '/pages/orders/orders' }), 800)
  } catch (e) {
    uni.showToast({ title: e.msg || '下单失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.cart-page { min-height: 100vh; background: var(--bg-page, #FFF5F7); padding-bottom: 120rpx; }
.cart-list { padding: 16rpx 24rpx; }
.cart-item { display: flex; align-items: center; background: #FFF; border-radius: 16rpx; padding: 20rpx; margin-bottom: 12rpx; }
.cart-item-img { width: 100rpx; height: 100rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; }
.cart-img { width: 100%; height: 100%; }
.cart-placeholder { font-size: 48rpx; }
.cart-item-info { flex: 1; margin-left: 20rpx; }
.cart-item-name { font-size: 28rpx; font-weight: 600; color: #4A4A4A; display: block; }
.cart-item-price { font-size: 26rpx; color: var(--color-primary, #FF7B93); margin-top: 6rpx; }
.qty-stepper { display: flex; align-items: center; gap: 12rpx; }
.qty-btn { width: 48rpx; height: 48rpx; border-radius: 50%; background: var(--bg-input, #FFF0F3); display: flex; align-items: center; justify-content: center; }
.qty-btn text { font-size: 32rpx; color: var(--color-primary, #FF7B93); font-weight: 600; }
.qty-num { font-size: 28rpx; font-weight: 600; min-width: 40rpx; text-align: center; }

.options-card { background: #FFF; margin: 16rpx 24rpx; border-radius: 16rpx; padding: 24rpx; }
.opt-row { margin-bottom: 16rpx; }
.opt-row:last-child { margin-bottom: 0; }
.opt-label { font-size: 26rpx; font-weight: 600; color: #4A4A4A; display: block; margin-bottom: 12rpx; }
.opt-chips { display: flex; flex-wrap: wrap; gap: 12rpx; }
.chip { padding: 10rpx 24rpx; border-radius: 20rpx; background: #F5F5F5; font-size: 24rpx; color: #888; }
.chip.active { background: var(--bg-input, #FFF0F3); color: var(--color-primary, #FF7B93); font-weight: 600; border: 2rpx solid var(--color-primary, #FF7B93); }

.note-section { padding: 16rpx 24rpx; }
.note-input { height: 80rpx; background: #FFF; border-radius: 16rpx; padding: 0 24rpx; font-size: 26rpx; }

.submit-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #FFF; padding: 20rpx 32rpx; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); box-shadow: 0 -2rpx 12rpx rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: space-between; }
.submit-label { font-size: 24rpx; color: #999; }
.submit-total { font-size: 40rpx; font-weight: 700; color: var(--color-primary, #FF7B93); }
.submit-btn { background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6)); color: #FFF; font-size: 30rpx; font-weight: 600; border-radius: 24rpx; padding: 16rpx 40rpx; border: none; box-shadow: 0 4rpx 16rpx rgba(255,123,147,0.3); }
.submit-btn.disabled { background: #DDD; color: #999; box-shadow: none; font-size: 24rpx; }
</style>
