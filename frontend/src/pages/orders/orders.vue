<template>
  <view class="orders-page">
    <view class="status-tabs">
      <view v-for="tab in tabs" :key="tab.value" class="status-tab" :class="{ active: activeTab === tab.value }" @click="activeTab = tab.value; fetchOrders()">
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <view v-if="orders.length === 0">
      <EmptyState icon="📋" text="暂无订单" subText="去菜单页面点餐吧~" />
    </view>

    <scroll-view v-else class="order-list" scroll-y refresher-enabled :refresher-triggered="refreshing" @refresherrefresh="onRefresh">
      <view v-for="order in orders" :key="order.id" class="order-card" @click="goDetail(order.id)">
        <view class="order-top">
          <view class="order-badges">
            <OrderStatusTag :status="order.status" />
            <text v-if="order.meal_type" class="meal-badge">{{ mealLabel(order.meal_type) }}</text>
          </view>
          <text class="order-amount">¥{{ (order.total_amount / 100).toFixed(2) }}</text>
        </view>
        <view class="order-meta">
          <text class="order-no">#{{ order.order_no.slice(-8) }}</text>
          <text class="order-chef" v-if="order.chef_nickname">👨‍🍳{{ order.chef_nickname }}</text>
          <text class="order-time">{{ formatTime(order.created_at) }}</text>
        </view>
        <view v-if="order.estimated_time" class="order-eta">
          <text>⏱ 预计 {{ formatTime(order.estimated_time) }} 出餐</text>
        </view>
        <view v-if="order.mood" class="order-mood">
          <text>{{ order.mood }} {{ order.mood_note }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { ordersAPI } from '@/api/orders'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'

const activeTab = ref('')
const orders = ref([])
const refreshing = ref(false)
const tabs = [
  { label: '全部', value: '' }, { label: '待接单', value: 'pending' },
  { label: '进行中', value: 'accepted' }, { label: '已完成', value: 'completed' },
]

onShow(() => fetchOrders())

async function fetchOrders() {
  try {
    const params = activeTab.value ? { status: activeTab.value } : {}
    const res = await ordersAPI.getList(params)
    orders.value = res.orders
  } catch (e) { console.error(e) }
}

async function onRefresh() {
  refreshing.value = true
  await fetchOrders()
  refreshing.value = false
}

function mealLabel(type) {
  const map = { breakfast: '🌅', lunch: '☀️', dinner: '🌙', snack: '🍰', night_snack: '🌃' }
  return map[type] || ''
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function goDetail(id) { uni.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` }) }
</script>

<style lang="scss" scoped>
.orders-page { min-height: 100vh; background: var(--bg-page, #FFF5F7); }
.status-tabs { display: flex; background: #FFF; padding: 8rpx 24rpx; gap: 8rpx; }
.status-tab { flex: 1; text-align: center; padding: 16rpx 0; font-size: 24rpx; color: #999; border-radius: 12rpx; }
.status-tab.active { color: var(--color-primary, #FF7B93); font-weight: 600; background: var(--bg-input, #FFF0F3); }
.order-list { padding: 16rpx 24rpx; }
.order-card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.order-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8rpx; }
.order-badges { display: flex; gap: 8rpx; align-items: center; }
.meal-badge { font-size: 22rpx; }
.order-amount { font-size: 36rpx; font-weight: 700; color: var(--color-primary, #FF7B93); }
.order-meta { display: flex; gap: 16rpx; margin-bottom: 6rpx; }
.order-no { font-size: 22rpx; color: #AAA; }
.order-chef { font-size: 22rpx; color: #888; }
.order-time { font-size: 22rpx; color: #CCC; margin-left: auto; }
.order-eta { font-size: 22rpx; color: #7EC8E3; }
.order-mood { margin-top: 8rpx; padding-top: 8rpx; border-top: 1rpx solid #F5F5F5; font-size: 24rpx; }
</style>
