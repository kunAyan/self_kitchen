<template>
  <view class="admin-orders">
    <view class="page-header">
      <text class="page-title">📦 订单管理</text>
    </view>

    <!-- Status filter -->
    <view class="filter-bar">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value; fetchOrders()"
      >
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <view v-if="orders.length === 0">
      <EmptyState icon="📦" text="暂无订单" />
    </view>

    <view v-else class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card">
        <view class="order-top">
          <view class="order-user">
            <text class="user-nickname">{{ order.user_nickname }}</text>
            <OrderStatusTag :status="order.status" />
          </view>
          <text class="order-amount">¥{{ (order.total_amount / 100).toFixed(2) }}</text>
        </view>

        <view class="order-meta">
          <text class="order-no">#{{ order.order_no.slice(-8) }}</text>
          <text class="order-time">{{ formatTime(order.created_at) }}</text>
        </view>

        <view class="order-note" v-if="order.note">
          <text>📝 {{ order.note }}</text>
        </view>

        <!-- Action buttons -->
        <view class="order-actions" v-if="order.status === 'pending' || order.status === 'accepted'">
          <button
            v-if="order.status === 'pending'"
            class="act-btn accept"
            @click="handleAction(order.id, 'accepted')"
          >接单</button>
          <button
            v-if="order.status === 'pending'"
            class="act-btn reject"
            @click="handleAction(order.id, 'rejected')"
          >拒单</button>
          <button
            v-if="order.status === 'accepted'"
            class="act-btn complete"
            @click="handleAction(order.id, 'completed')"
          >完成</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import EmptyState from '@/components/EmptyState.vue'

const activeTab = ref('')
const orders = ref([])

const tabs = [
  { label: '全部', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'accepted' },
  { label: '已完成', value: 'completed' },
]

onMounted(() => fetchOrders())

async function fetchOrders() {
  try {
    const params = activeTab.value ? { status: activeTab.value } : {}
    const res = await adminAPI.getOrders(params)
    orders.value = res.orders
  } catch (e) { console.error(e) }
}

async function handleAction(orderId, status) {
  try {
    await adminAPI.updateOrderStatus(orderId, status)
    const labelMap = { accepted: '已接单', rejected: '已拒单', completed: '已完成' }
    uni.showToast({ title: labelMap[status], icon: 'success' })
    fetchOrders()
  } catch (e) {
    uni.showToast({ title: e.msg || '操作失败', icon: 'none' })
  }
}

function formatTime(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style lang="scss" scoped>
.admin-orders {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

.page-header {
  margin-bottom: 16rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #4A4A4A;
}

.filter-bar {
  display: flex;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  font-size: 24rpx;
  color: #999;
  background: #FFF;
  border-radius: 12rpx;
}

.filter-tab.active {
  color: var(--color-primary, #FF7B93);
  font-weight: 600;
  background: var(--bg-input, #FFF0F3);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.order-card {
  background: #FFF;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.order-user {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.user-nickname {
  font-size: 28rpx;
  font-weight: 600;
}

.order-amount {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.order-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.order-no, .order-time {
  font-size: 22rpx;
  color: #CCC;
}

.order-note {
  background: var(--bg-page, #FFF5F7);
  padding: 12rpx 16rpx;
  border-radius: 8rpx;
  margin-bottom: 16rpx;
}

.order-note text {
  font-size: 24rpx;
  color: #888;
}

.order-actions {
  display: flex;
  gap: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #F5F5F5;
}

.act-btn {
  flex: 1;
  text-align: center;
  padding: 16rpx;
  border-radius: 20rpx;
  font-size: 26rpx;
  border: none;
}

.act-btn.accept {
  background: linear-gradient(135deg, #7BC8A4, #8FD4B4);
  color: #FFF;
}

.act-btn.reject {
  background: #FFF5F5;
  color: #FF6B6B;
  border: 2rpx solid #FF6B6B;
}

.act-btn.complete {
  background: linear-gradient(135deg, #7EC8E3, #9BD5EB);
  color: #FFF;
}
</style>
