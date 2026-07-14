<template>
  <view class="sales-stats-page">
    <view class="page-header">
      <text class="page-title">📈 销售统计</text>
    </view>

    <!-- Top Dishes Ranking -->
    <view class="card">
      <text class="card-title">🏆 热销菜品 TOP 10</text>
      <view
        v-for="(dish, idx) in stats.top_dishes"
        :key="dish.name"
        class="dish-row"
        :class="{ 'rank-gold': idx === 0, 'rank-silver': idx === 1, 'rank-bronze': idx === 2 }"
      >
        <view class="rank-section">
          <text v-if="idx === 0" class="medal">🥇</text>
          <text v-else-if="idx === 1" class="medal">🥈</text>
          <text v-else-if="idx === 2" class="medal">🥉</text>
          <text v-else class="rank-num">{{ idx + 1 }}</text>
        </view>
        <view class="dish-info">
          <text class="dish-name">{{ dish.name }}</text>
          <text class="dish-price">¥{{ (dish.price / 100).toFixed(2) }}</text>
        </view>
        <view class="dish-count">
          <text class="count-num">{{ dish.sold_count }}</text>
          <text class="count-label">份</text>
        </view>
      </view>
      <view v-if="!stats.top_dishes || stats.top_dishes.length === 0" class="empty-hint">
        <text>暂无销售数据</text>
      </view>
    </view>

    <!-- Meal Type Breakdown -->
    <view class="card">
      <text class="card-title">🍳 餐类分布</text>
      <view class="meal-grid">
        <view
          v-for="meal in stats.meal_stats"
          :key="meal.type"
          class="meal-card"
        >
          <text class="meal-emoji">{{ mealEmoji(meal.type) }}</text>
          <text class="meal-label">{{ mealLabel(meal.type) }}</text>
          <text class="meal-count">{{ meal.count }}</text>
        </view>
      </view>
      <view v-if="!stats.meal_stats || stats.meal_stats.length === 0" class="empty-hint">
        <text>暂无餐类数据</text>
      </view>
    </view>

    <!-- Monthly Trend -->
    <view class="card">
      <text class="card-title">📊 月度趋势（近 6 个月）</text>
      <view class="monthly-list">
        <view
          v-for="m in stats.monthly"
          :key="m.year + '-' + m.month"
          class="month-card"
        >
          <text class="month-label">{{ m.year }}.{{ String(m.month).padStart(2, '0') }}</text>
          <view class="month-stat">
            <text class="month-orders">📦 {{ m.count || 0 }} 单</text>
            <text class="month-amount">¥{{ ((m.total || 0) / 100).toFixed(2) }}</text>
          </view>
        </view>
      </view>
      <view v-if="!stats.monthly || stats.monthly.length === 0" class="empty-hint">
        <text>暂无月度数据</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/api/index'

const stats = ref({ top_dishes: [], meal_stats: [], monthly: [] })

onMounted(async () => {
  try {
    const res = await get('/admin/sales-stats')
    stats.value = res
  } catch (e) {
    console.error('Failed to load sales stats', e)
    uni.showToast({ title: '加载销售统计失败', icon: 'none' })
  }
})

function mealEmoji(type) {
  const map = {
    breakfast: '🌅',
    lunch: '☀️',
    dinner: '🌙',
    snack: '🍪',
    night_snack: '🌃',
  }
  return map[type] || '🍽️'
}

function mealLabel(type) {
  const map = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '茶点',
    night_snack: '夜宵',
  }
  return map[type] || type
}
</script>

<style lang="scss" scoped>
.sales-stats-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

.page-header {
  margin-bottom: 20rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #4A4A4A;
}

/* Card */
.card {
  background: #FFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #4A4A4A;
  display: block;
  margin-bottom: 20rpx;
}

/* Top Dishes Ranking */
.dish-row {
  display: flex;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #F5F5F5;
}

.dish-row:last-child {
  border-bottom: none;
}

.rank-gold {
  background: linear-gradient(90deg, #FFF9E6, transparent);
  margin: 0 -24rpx;
  padding: 18rpx 24rpx;
}

.rank-silver {
  background: linear-gradient(90deg, #F5F7FA, transparent);
  margin: 0 -24rpx;
  padding: 18rpx 24rpx;
}

.rank-bronze {
  background: linear-gradient(90deg, #FFF0EA, transparent);
  margin: 0 -24rpx;
  padding: 18rpx 24rpx;
}

.rank-section {
  width: 60rpx;
  text-align: center;
  flex-shrink: 0;
}

.medal {
  font-size: 36rpx;
}

.rank-num {
  font-size: 28rpx;
  font-weight: 700;
  color: #BBB;
}

.dish-info {
  flex: 1;
  margin-left: 12rpx;
}

.dish-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
}

.dish-price {
  font-size: 22rpx;
  color: var(--color-primary, #FF7B93);
  margin-top: 4rpx;
  display: block;
}

.dish-count {
  text-align: right;
  flex-shrink: 0;
}

.count-num {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.count-label {
  font-size: 22rpx;
  color: #999;
  margin-left: 4rpx;
}

/* Meal Type */
.meal-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.meal-card {
  width: calc(33.33% - 8rpx);
  background: var(--bg-page, #FFF5F7);
  border-radius: 14rpx;
  padding: 20rpx 12rpx;
  text-align: center;
}

.meal-emoji {
  font-size: 40rpx;
  display: block;
  margin-bottom: 6rpx;
}

.meal-label {
  font-size: 24rpx;
  color: #4A4A4A;
  display: block;
  margin-bottom: 4rpx;
}

.meal-count {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  display: block;
}

/* Monthly Trend */
.monthly-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.month-card {
  background: var(--bg-page, #FFF5F7);
  border-radius: 14rpx;
  padding: 20rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.month-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #4A4A4A;
}

.month-stat {
  text-align: right;
}

.month-orders {
  font-size: 24rpx;
  color: #666;
  display: block;
}

.month-amount {
  font-size: 28rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  display: block;
  margin-top: 2rpx;
}

/* Empty */
.empty-hint {
  text-align: center;
  padding: 30rpx 0;
  font-size: 26rpx;
  color: #CCC;
}
</style>
