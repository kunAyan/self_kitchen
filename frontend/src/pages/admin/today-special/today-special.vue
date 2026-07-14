<template>
  <view class="today-special-page">
    <view class="page-header">
      <text class="page-title">🌟 今日特选</text>
    </view>

    <view class="current-section" v-if="currentSpecial">
      <view class="current-card">
        <text class="current-label">当前今日特选</text>
        <view class="current-dish">
          <view class="cd-thumb">
            <image
              v-if="currentSpecial.image"
              class="cd-img"
              :src="uploadBase + currentSpecial.image"
              mode="aspectFill"
            />
            <text v-else class="cd-emoji">{{ currentSpecial.category_icon || '🍽️' }}</text>
          </view>
          <view class="cd-info">
            <text class="cd-name">{{ currentSpecial.name }}</text>
            <text class="cd-price">¥{{ (currentSpecial.price / 100).toFixed(2) }}</text>
          </view>
          <view class="cd-badge">今日特选</view>
        </view>
        <button class="clear-btn" @click="clearSpecial">取消今日特选</button>
      </view>
    </view>

    <view class="search-section">
      <input
        class="search-input"
        v-model="searchQuery"
        placeholder="🔍 搜索菜品..."
        placeholder-style="color:#BBB"
      />
    </view>

    <view v-if="filteredDishes.length === 0" class="empty-wrap">
      <EmptyState
        icon="🍽️"
        :text="searchQuery ? '没有匹配的菜品' : '暂无菜品数据'"
        subText="请先在菜品管理中添加上架菜品"
      />
    </view>

    <view v-else class="dish-list">
      <view
        v-for="dish in filteredDishes"
        :key="dish.id"
        class="dish-card"
        :class="{ isCurrent: dish.id === currentSpecial?.id }"
        @click="setTodaySpecial(dish)"
      >
        <view class="dish-thumb">
          <image
            v-if="dish.image"
            class="dish-img"
            :src="uploadBase + dish.image"
            mode="aspectFill"
          />
          <text v-else class="dish-emoji">{{ dish.category_icon || '🍽️' }}</text>
        </view>
        <view class="dish-detail">
          <text class="dish-name">{{ dish.name }}</text>
          <view class="dish-meta-row">
            <text class="dish-cat">{{ dish.category_name }}</text>
            <text class="dish-price">¥{{ (dish.price / 100).toFixed(2) }}</text>
          </view>
        </view>
        <view class="dish-right">
          <view v-if="dish.id === currentSpecial?.id" class="special-badge">
            <text class="badge-text">今日特选</text>
          </view>
          <text v-if="dish.id === currentSpecial?.id" class="selected-icon">★</text>
          <text v-else class="select-hint">设为特选</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { get, put } from '@/api/index'
import { storeAPI } from '@/api/store'
import { UPLOAD_BASE } from '@/config'
import EmptyState from '@/components/EmptyState.vue'

const uploadBase = UPLOAD_BASE

const allDishes = ref([])
const currentSpecial = ref(null)
const searchQuery = ref('')

const filteredDishes = computed(() => {
  if (!searchQuery.value.trim()) return allDishes.value
  const q = searchQuery.value.trim().toLowerCase()
  return allDishes.value.filter(
    (d) =>
      d.name.toLowerCase().includes(q) ||
      (d.category_name && d.category_name.toLowerCase().includes(q))
  )
})

onMounted(async () => {
  // Fetch all available dishes
  try {
    const res = await get('/dishes')
    allDishes.value = res.dishes || []
  } catch (e) {
    console.error('Failed to load dishes', e)
    uni.showToast({ title: '加载菜品失败', icon: 'none' })
  }

  // Fetch current today special
  try {
    const res = await storeAPI.getTodaySpecial()
    if (res.special && res.special.dish) {
      currentSpecial.value = res.special.dish
    }
  } catch (e) {
    console.error('Failed to load today special', e)
  }
})

async function setTodaySpecial(dish) {
  if (currentSpecial.value && currentSpecial.value.id === dish.id) {
    return
  }

  try {
    await put('/admin/today-special', { dish_id: dish.id })
    currentSpecial.value = dish
    uni.showToast({
      title: `「${dish.name}」已设为今日特选`,
      icon: 'success',
    })
  } catch (e) {
    uni.showToast({ title: e.msg || '设置失败', icon: 'none' })
  }
}

async function clearSpecial() {
  uni.showModal({
    title: '确认取消',
    content: '确定取消今日特选吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await put('/admin/today-special', { dish_id: 0 })
          currentSpecial.value = null
          uni.showToast({ title: '已取消今日特选', icon: 'success' })
        } catch (e) {
          uni.showToast({ title: e.msg || '操作失败', icon: 'none' })
        }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.today-special-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

.page-header {
  margin-bottom: 24rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary, #4A4A4A);
}

/* Current special section */
.current-section {
  margin-bottom: 20rpx;
}

.current-card {
  background: linear-gradient(135deg, #FFF0F3, #FFFFFF);
  border: 2rpx solid var(--color-primary, #FF7B93);
  border-radius: 16rpx;
  padding: 24rpx;
}

.current-label {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--color-primary, #FF7B93);
  display: block;
  margin-bottom: 16rpx;
}

.current-dish {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.cd-thumb {
  width: 80rpx;
  height: 80rpx;
  border-radius: 12rpx;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF;
  flex-shrink: 0;
}

.cd-img {
  width: 100%;
  height: 100%;
}

.cd-emoji {
  font-size: 40rpx;
}

.cd-info {
  flex: 1;
}

.cd-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary, #4A4A4A);
  display: block;
}

.cd-price {
  font-size: 24rpx;
  color: var(--color-primary, #FF7B93);
  font-weight: 600;
}

.cd-badge {
  font-size: 20rpx;
  color: #FFF;
  background: var(--color-primary, #FF7B93);
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.clear-btn {
  width: 100%;
  background: #FFF;
  color: var(--color-primary, #FF7B93);
  font-size: 26rpx;
  font-weight: 500;
  border-radius: 16rpx;
  padding: 16rpx;
  border: 2rpx solid var(--color-primary, #FF7B93);
}

/* Search */
.search-section {
  margin-bottom: 20rpx;
}

.search-input {
  height: 72rpx;
  background: var(--bg-card, #FFFFFF);
  border-radius: 36rpx;
  padding: 0 28rpx;
  font-size: 26rpx;
  color: var(--text-primary, #4A4A4A);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

/* Dish list */
.dish-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.dish-card {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: var(--bg-card, #FFFFFF);
  border-radius: 16rpx;
  gap: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  transition: transform 0.15s;
}

.dish-card:active {
  transform: scale(0.98);
}

.dish-card.isCurrent {
  border: 2rpx solid var(--color-primary, #FF7B93);
  background: #FFF8FA;
}

.dish-thumb {
  width: 96rpx;
  height: 96rpx;
  border-radius: 14rpx;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF0F3;
  flex-shrink: 0;
}

.dish-img {
  width: 100%;
  height: 100%;
}

.dish-emoji {
  font-size: 48rpx;
}

.dish-detail {
  flex: 1;
  overflow: hidden;
}

.dish-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary, #4A4A4A);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-meta-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 4rpx;
}

.dish-cat {
  font-size: 22rpx;
  color: var(--text-secondary, #888);
}

.dish-price {
  font-size: 24rpx;
  color: var(--color-primary, #FF7B93);
  font-weight: 600;
}

.dish-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  flex-shrink: 0;
}

.special-badge {
  background: var(--color-primary, #FF7B93);
  border-radius: 12rpx;
  padding: 2rpx 10rpx;
}

.badge-text {
  color: #FFF;
  font-size: 18rpx;
  font-weight: 500;
}

.selected-icon {
  font-size: 28rpx;
  color: var(--color-primary, #FF7B93);
}

.select-hint {
  font-size: 20rpx;
  color: var(--color-primary, #FF7B93);
  font-weight: 500;
}

.empty-wrap {
  padding: 40rpx 0;
}
</style>
