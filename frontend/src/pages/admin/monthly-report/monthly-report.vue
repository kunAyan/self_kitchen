<template>
  <view class="monthly-report-page">
    <view class="report-header">
      <text class="report-title">📋 月度家庭用餐报告</text>
      <text class="report-period">{{ report.year }} 年 {{ report.month }} 月</text>
    </view>

    <!-- Stats Cards -->
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-icon">📦</text>
        <text class="stat-num">{{ report.total_orders }}</text>
        <text class="stat-label">总订单</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">💰</text>
        <text class="stat-num">¥{{ (report.total_amount / 100).toFixed(2) }}</text>
        <text class="stat-label">总金额</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">👥</text>
        <text class="stat-num">{{ report.active_users }}</text>
        <text class="stat-label">活跃用户</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">💬</text>
        <text class="stat-num">{{ report.new_reviews }}</text>
        <text class="stat-label">新增评价</text>
      </view>
    </view>

    <!-- Top Dish Highlight -->
    <view class="highlight-card top-dish-card">
      <view class="highlight-icon-wrap">
        <text class="highlight-icon">❤️</text>
      </view>
      <text class="highlight-section-title">最爱菜品</text>
      <view class="highlight-content" v-if="report.top_dish">
        <text class="highlight-item-name">{{ report.top_dish }}</text>
        <text class="highlight-item-count">被点了 {{ report.top_dish_count }} 次</text>
      </view>
      <view class="highlight-content" v-else>
        <text class="highlight-empty">暂无数据</text>
      </view>
    </view>

    <!-- Top Chef Highlight -->
    <view class="highlight-card top-chef-card">
      <view class="highlight-icon-wrap">
        <text class="highlight-icon">👨‍🍳</text>
      </view>
      <text class="highlight-section-title">最勤大厨</text>
      <view class="highlight-content" v-if="report.top_chef">
        <text class="highlight-item-name">{{ report.top_chef }}</text>
        <text class="highlight-item-count">掌勺 {{ report.top_chef_count }} 次</text>
      </view>
      <view class="highlight-content" v-else>
        <text class="highlight-empty">暂无数据</text>
      </view>
    </view>

    <!-- Generate Report Button -->
    <view class="generate-section">
      <button class="generate-btn" @click="generateReport">
        <text class="btn-icon">📄</text>
        <text class="btn-text">生成报告</text>
      </button>
    </view>

    <!-- Report Summary Modal -->
    <view v-if="showSummary" class="modal-mask" @click="showSummary = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">📊 {{ report.year }}.{{ String(report.month).padStart(2, '0') }} 月度总结</text>
        </view>
        <view class="modal-body">
          <view class="summary-line">
            <text class="summary-label">本月订单</text>
            <text class="summary-value">{{ report.total_orders }} 单</text>
          </view>
          <view class="summary-line">
            <text class="summary-label">本月消费</text>
            <text class="summary-value">¥{{ (report.total_amount / 100).toFixed(2) }}</text>
          </view>
          <view class="summary-line">
            <text class="summary-label">平均每单</text>
            <text class="summary-value">{{ (report.total_orders ? (report.total_amount / report.total_orders / 100).toFixed(2) : '0.00') }} 元</text>
          </view>
          <view class="divider"></view>
          <view class="summary-line" v-if="report.top_dish">
            <text class="summary-label">最爱菜品</text>
            <text class="summary-value">{{ report.top_dish }}</text>
          </view>
          <view class="summary-line" v-if="report.top_dish">
            <text class="summary-label">点单次数</text>
            <text class="summary-value">{{ report.top_dish_count }} 次</text>
          </view>
          <view class="divider"></view>
          <view class="summary-line" v-if="report.top_chef">
            <text class="summary-label">最勤大厨</text>
            <text class="summary-value">{{ report.top_chef }}</text>
          </view>
          <view class="summary-line" v-if="report.top_chef">
            <text class="summary-label">掌勺次数</text>
            <text class="summary-value">{{ report.top_chef_count }} 次</text>
          </view>
          <view class="divider"></view>
          <view class="summary-line">
            <text class="summary-label">活跃用户</text>
            <text class="summary-value">{{ report.active_users }} 人</text>
          </view>
          <view class="summary-line">
            <text class="summary-label">新增评价</text>
            <text class="summary-value">{{ report.new_reviews }} 条</text>
          </view>
        </view>
        <view class="modal-footer">
          <text class="modal-close" @click="showSummary = false">关闭</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/api/index'

const report = ref({
  year: '',
  month: '',
  total_orders: 0,
  total_amount: 0,
  top_dish: '',
  top_dish_count: 0,
  top_chef: '',
  top_chef_count: 0,
  new_reviews: 0,
  active_users: 0,
})
const showSummary = ref(false)

onMounted(async () => {
  try {
    const res = await get('/admin/monthly-report')
    report.value = res.report || res
  } catch (e) {
    console.error('Failed to load monthly report', e)
    uni.showToast({ title: '加载月度报告失败', icon: 'none' })
  }
})

function generateReport() {
  showSummary.value = true
}
</script>

<style lang="scss" scoped>
.monthly-report-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

/* Header */
.report-header {
  text-align: center;
  margin-bottom: 28rpx;
  padding: 30rpx 0;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), #FF9AAE);
  border-radius: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}

.report-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #FFF;
  display: block;
}

.report-period {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 8rpx;
  display: block;
}

/* Stats Grid */
.stats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.stat-card {
  width: calc(50% - 6rpx);
  background: #FFF;
  border-radius: 16rpx;
  padding: 28rpx 16rpx;
  text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.stat-icon {
  font-size: 40rpx;
  display: block;
  margin-bottom: 8rpx;
}

.stat-num {
  font-size: 38rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  display: block;
}

.stat-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
  display: block;
}

/* Highlight Cards */
.highlight-card {
  background: #FFF;
  border-radius: 20rpx;
  padding: 32rpx 24rpx;
  margin-bottom: 16rpx;
  text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.top-dish-card {
  border-top: 6rpx solid var(--color-primary, #FF7B93);
}

.top-chef-card {
  border-top: 6rpx solid #FF9AAE;
}

.highlight-icon-wrap {
  margin-bottom: 8rpx;
}

.highlight-icon {
  font-size: 52rpx;
}

.highlight-section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
  margin-bottom: 16rpx;
}

.highlight-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.highlight-item-name {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.highlight-item-count {
  font-size: 26rpx;
  color: #888;
}

.highlight-empty {
  font-size: 26rpx;
  color: #CCC;
}

/* Generate Button */
.generate-section {
  margin-top: 8rpx;
  margin-bottom: 32rpx;
}

.generate-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), #FF9AAE);
  border: none;
  border-radius: 48rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}

.generate-btn:active {
  opacity: 0.85;
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #FFF;
}

/* Modal */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  width: 86%;
  max-height: 80vh;
  background: #FFF;
  border-radius: 24rpx;
  overflow-y: auto;
}

.modal-header {
  padding: 32rpx 24rpx 16rpx;
  text-align: center;
}

.modal-title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.modal-body {
  padding: 8rpx 32rpx 24rpx;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14rpx 0;
}

.summary-label {
  font-size: 28rpx;
  color: #666;
}

.summary-value {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
}

.divider {
  height: 1rpx;
  background: #F0F0F0;
  margin: 6rpx 0;
}

.modal-footer {
  padding: 16rpx 0 32rpx;
  text-align: center;
}

.modal-close {
  font-size: 28rpx;
  color: var(--color-primary, #FF7B93);
  font-weight: 600;
  padding: 12rpx 40rpx;
}
</style>
