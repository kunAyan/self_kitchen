<template>
  <view class="admin-dashboard">
    <view class="dash-header"><text class="dash-title">📊 木糯小厨 · 管理后台</text></view>

    <!-- Stats -->
    <view class="stats-grid">
      <view class="stat-card"><text class="stat-icon">📦</text><text class="stat-num">{{ stats.pending_orders }}</text><text class="stat-label">待处理订单</text></view>
      <view class="stat-card"><text class="stat-icon">🍽️</text><text class="stat-num">{{ stats.total_dishes }}</text><text class="stat-label">在售菜品</text></view>
      <view class="stat-card"><text class="stat-icon">📋</text><text class="stat-num">{{ stats.today_orders }}</text><text class="stat-label">今日订单</text></view>
    </view>

    <!-- Customer balances -->
    <view class="card">
      <text class="card-title">💰 用户余额</text>
      <view v-for="c in stats.customers" :key="c.id" class="customer-row" @click="goUser(c.id)">
        <text class="cust-icon">{{ c.role === 'admin' ? '👨‍🍳' : '👤' }}</text>
        <view class="cust-info"><text class="cust-name">{{ c.nickname }}</text><text class="cust-user">@{{ c.username }}</text></view>
        <text class="cust-balance">¥{{ (c.balance / 100).toFixed(2) }}</text>
        <text class="cust-arrow">→</text>
      </view>
    </view>

    <!-- Quick actions -->
    <view class="card">
      <text class="card-title">⚡ 快捷操作</text>
      <view class="action-grid">
        <view class="action-item" @click="navTo('/pages/admin/dishes/dishes')"><text class="act-icon">🍽️</text><text>菜品管理</text></view>
        <view class="action-item" @click="navTo('/pages/admin/categories/categories')"><text class="act-icon">📂</text><text>分类管理</text></view>
        <view class="action-item" @click="navTo('/pages/admin/orders/orders')"><text class="act-icon">📦</text><text>订单处理</text></view>
        <view class="action-item" @click="navTo('/pages/admin/user/user')"><text class="act-icon">💳</text><text>余额管理</text></view>
        <view class="action-item" @click="navTo('/pages/admin/store-config/store-config')"><text class="act-icon">🏪</text><text>店铺配置</text></view>
        <view class="action-item" @click="navTo('/pages/admin/special-dates/special-dates')"><text class="act-icon">📅</text><text>纪念日</text></view>
        <view class="action-item" @click="navTo('/pages/admin/today-special/today-special')"><text class="act-icon">⭐</text><text>今日特供</text></view>
        <view class="action-item" @click="navTo('/pages/admin/sales-stats/sales-stats')"><text class="act-icon">📈</text><text>销量统计</text></view>
        <view class="action-item" @click="navTo('/pages/admin/monthly-report/monthly-report')"><text class="act-icon">📄</text><text>月度报告</text></view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/api/index'

const stats = ref({ customers: [], pending_orders: 0, total_dishes: 0, today_orders: 0 })

onMounted(async () => {
  try {
    const res = await get('/admin/dashboard')
    stats.value = res.stats
  } catch (e) { console.error(e) }
})

function navTo(url) { uni.navigateTo({ url }) }
function goUser(id) { uni.navigateTo({ url: `/pages/admin/user/user?id=${id}` }) }
</script>

<style lang="scss" scoped>
.admin-dashboard { min-height: 100vh; background: #FFF5F7; padding: 24rpx; }
.dash-header { margin-bottom: 20rpx; }
.dash-title { font-size: 32rpx; font-weight: 700; color: #4A4A4A; }
.stats-grid { display: flex; gap: 12rpx; margin-bottom: 16rpx; }
.stat-card { flex: 1; background: #FFF; border-radius: 16rpx; padding: 24rpx 16rpx; text-align: center; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.stat-icon { font-size: 36rpx; display: block; margin-bottom: 6rpx; }
.stat-num { font-size: 36rpx; font-weight: 700; color: #FF7B93; display: block; }
.stat-label { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.card-title { font-size: 26rpx; font-weight: 600; color: #4A4A4A; display: block; margin-bottom: 16rpx; }
.customer-row { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.customer-row:last-child { border-bottom: none; }
.cust-icon { font-size: 36rpx; margin-right: 12rpx; }
.cust-info { flex: 1; }
.cust-name { font-size: 28rpx; font-weight: 600; display: block; }
.cust-user { font-size: 22rpx; color: #AAA; }
.cust-balance { font-size: 28rpx; font-weight: 700; color: #FF7B93; margin-right: 8rpx; }
.cust-arrow { color: #CCC; }
.action-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.action-item { width: calc(33.33% - 8rpx); background: #FFF5F7; border-radius: 12rpx; padding: 20rpx; text-align: center; font-size: 24rpx; color: #4A4A4A; }
.act-icon { font-size: 36rpx; display: block; margin-bottom: 6rpx; }
.action-item:active { background: #FFE0E6; }
</style>
