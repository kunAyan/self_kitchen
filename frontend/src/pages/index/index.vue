<template>
  <view class="menu-page">
    <!-- ===== Top Bar ===== -->
    <view class="top-bar">
      <view class="brand">
        <text class="brand-icon">🍳</text>
        <text class="brand-name">木糯小厨</text>
      </view>
      <view class="balance-tag" @click="goProfile">
        <text class="balance-icon">💰</text>
        <text class="balance-text">¥{{ displayBalance }}</text>
      </view>
    </view>

    <!-- ===== Banner Area (horizontal scroll) ===== -->
    <scroll-view
      class="banner-scroll"
      scroll-x
      :show-scrollbar="false"
      v-if="todaySpecial || popularDishes.length > 0"
    >
      <!-- Today Special -->
      <view v-if="todaySpecial" class="banner-item special-item" @click="onDishClick(todaySpecial)">
        <view class="special-badge">⭐ 今日特供</view>
        <view class="special-body">
          <image
            v-if="todaySpecial.image"
            class="special-img"
            :src="imageUrl(todaySpecial.image)"
            mode="aspectFill"
          />
          <text v-else class="special-emoji">{{ todaySpecial.category_icon || '🍽️' }}</text>
          <view class="special-info">
            <text class="special-name">{{ todaySpecial.name }}</text>
            <text class="special-price">¥{{ priceFormat(todaySpecial.price) }}</text>
          </view>
        </view>
      </view>

      <!-- Popular Dishes -->
      <view class="banner-section popular-section">
        <view class="section-head">🔥 人气排行</view>
        <view class="popular-list">
          <view
            v-for="dish in popularDishes"
            :key="dish.id"
            class="banner-item popular-item"
            @click="onDishClick(dish)"
          >
            <view class="popular-rank" :class="'rank-' + (popularDishes.indexOf(dish) + 1)">
              <text>{{ popularDishes.indexOf(dish) + 1 }}</text>
            </view>
            <image
              v-if="dish.image"
              class="popular-img"
              :src="imageUrl(dish.image)"
              mode="aspectFill"
            />
            <text v-else class="popular-emoji">{{ dish.category_icon || '🍽️' }}</text>
            <text class="popular-name">{{ dish.name }}</text>
            <text class="popular-price">¥{{ priceFormat(dish.price) }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- ===== Search Bar ===== -->
    <view class="search-bar-wrap">
      <input class="search-bar" v-model="searchQuery" placeholder="🔍 搜索菜品..." placeholder-style="color:#CCC" />
      <text v-if="searchQuery" class="search-clear" @click="searchQuery = ''">✕</text>
    </view>

    <!-- ===== Main Content: Sidebar + Dish List ===== -->
    <view class="main-content">
      <!-- Left Sidebar (categories) -->
      <scroll-view class="sidebar" scroll-y :show-scrollbar="false">
        <view
          v-for="cat in dishesStore.categoryWithAll"
          :key="cat.id"
          class="sidebar-item"
          :class="{ active: dishesStore.activeCategoryId === cat.id }"
          @click="dishesStore.setActiveCategory(cat.id)"
        >
          <text class="sidebar-icon">{{ cat.icon || '🍽️' }}</text>
          <text class="sidebar-name">{{ cat.name }}</text>
        </view>
      </scroll-view>

      <!-- Right Dish List -->
      <scroll-view
        class="dish-scroll"
        scroll-y
        :show-scrollbar="false"
        refresher-enabled
        :refresher-triggered="isRefreshing"
        @refresherrefresh="onRefresh"
      >
        <!-- Loading -->
        <view v-if="dishesStore.loading && dishesStore.dishes.length === 0" class="state-wrap">
          <text class="state-text">正在加载美味...</text>
        </view>

        <!-- Empty -->
        <view v-else-if="searchedDishes.length === 0" class="state-wrap">
          <EmptyState icon="🍽️" text="暂无菜品" subText="该分类暂时没有菜品哦~" />
        </view>

        <!-- Dish Cards -->
        <view v-else class="dish-list">
          <view
            v-for="dish in searchedDishes"
            :key="dish.id"
            class="dish-card-wrapper"
          >
            <!-- Inline dish card -->
            <view class="dish-card" @click="onDishClick(dish)">
              <!-- Image -->
              <view class="dish-image-wrap" :style="{ backgroundColor: placeholderColor(dish.category_icon) }">
                <image
                  v-if="dish.image"
                  class="dish-image"
                  :src="imageUrl(dish.image)"
                  mode="aspectFill"
                />
                <text v-else class="dish-placeholder">{{ dish.category_icon || '🍽️' }}</text>
              </view>

              <!-- Info -->
              <view class="dish-info">
                <text class="dish-name">{{ dish.name }}</text>
                <view class="dish-meta">
                  <text class="dish-sold">已售 {{ dish.sold_count || 0 }}</text>
                </view>
                <view v-if="dish.note" class="dish-note">
                  <text class="note-emoji">📌</text>
                  <text class="note-text">{{ dish.note }}</text>
                </view>
                <view class="dish-bottom">
                  <text class="dish-price">¥{{ priceFormat(dish.price) }}</text>
                  <!-- Cart quantity stepper -->
                  <view v-if="dish.is_available" class="cart-stepper">
                    <view v-if="getCartQty(dish.id) > 0" class="stepper">
                      <view class="step-btn" @click.stop="onReduceDish(dish)"><text>−</text></view>
                      <text class="step-qty">{{ getCartQty(dish.id) }}</text>
                      <view class="step-btn" @click.stop="onAddDish(dish)"><text>+</text></view>
                    </view>
                    <view v-else class="add-btn" @click.stop="onAddDish(dish)">
                      <text class="add-icon">+</text>
                    </view>
                  </view>
                  <text v-else class="sold-out-tag">已售罄</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- Bottom spacer for cart bar -->
        <view style="height: 140rpx;"></view>
      </scroll-view>
    </view>

    <!-- ===== Random Dish Button ===== -->
    <view class="random-btn" :class="{ shaking: isShaking }" @click="onRandomPick">
      <text class="random-emoji">🎲</text>
    </view>

    <!-- ===== Floating Cart Bar ===== -->
    <view v-if="cartStore.totalCount > 0" class="cart-float" @click="goCart">
      <view class="cart-float-left">
        <view class="cart-badge">{{ cartStore.totalCount }}</view>
        <text class="cart-total">¥{{ (cartStore.totalAmount / 100).toFixed(2) }}</text>
      </view>
      <view class="cart-float-right">
        <text class="cart-go-text">去结算</text>
        <text class="cart-arrow">→</text>
      </view>
    </view>

    <!-- ===== Random Dish Modal ===== -->
    <view v-if="showRandomModal" class="modal-overlay" @click="closeRandomModal">
      <view class="random-modal" @click.stop>
        <view class="random-modal-icon">🎲</view>
        <text class="random-modal-title">今日推荐</text>

        <view v-if="randomDish" class="random-dish-display">
          <view class="random-img-wrap" :style="{ backgroundColor: placeholderColor(randomDish.category_icon) }">
            <image
              v-if="randomDish.image"
              class="random-img"
              :src="imageUrl(randomDish.image)"
              mode="aspectFill"
            />
            <text v-else class="random-placeholder">{{ randomDish.category_icon || '🍽️' }}</text>
          </view>
          <text class="random-dish-name">{{ randomDish.name }}</text>
          <text class="random-dish-price">¥{{ priceFormat(randomDish.price) }}</text>
          <text v-if="randomDish.note" class="random-dish-note">{{ randomDish.note }}</text>
        </view>

        <view class="random-actions">
          <view class="random-btn-action random-btn-secondary" @click="onRandomPickRandom">
            <text>再摇一次</text>
          </view>
          <view class="random-btn-action random-btn-primary" @click="onRandomConfirm">
            <text>就它了</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useDishesStore } from '@/stores/dishes'
import { useCartStore } from '@/stores/cart'
import { storeAPI } from '@/api/store'
import { UPLOAD_BASE } from '@/config'
import EmptyState from '@/components/EmptyState.vue'

const authStore = useAuthStore()
const dishesStore = useDishesStore()
const cartStore = useCartStore()

// ===== Banner State =====
const todaySpecial = ref(null)
const popularDishes = ref([])
const isRefreshing = ref(false)
const searchQuery = ref('')

// ===== Random Dish State =====
const showRandomModal = ref(false)
const randomDish = ref(null)
const isShaking = ref(false)

// ===== Computed =====
const searchedDishes = computed(() => {
  if (!searchQuery.value.trim()) return dishesStore.filteredDishes
  const q = searchQuery.value.trim().toLowerCase()
  return dishesStore.filteredDishes.filter(d =>
    d.name.toLowerCase().includes(q) ||
    (d.description && d.description.toLowerCase().includes(q)) ||
    (d.note && d.note.toLowerCase().includes(q))
  )
})
const displayBalance = computed(() => {
  if (!authStore.user) return '0.00'
  return (authStore.user.balance / 100).toFixed(2)
})

// All available dishes for random pick
const allAvailableDishes = computed(() => {
  return dishesStore.dishes.filter(d => d.is_available)
})

// ===== Placeholder Colors =====
const colorMap = {
  '🍝': '#FFE4C4',
  '🥤': '#D4EFFF',
  '🍰': '#FFE0EC',
  '🥗': '#E8F8E0',
  '🍜': '#FFE8D6',
  '✨': '#F5F0FF',
}

function placeholderColor(icon) {
  return colorMap[icon] || 'var(--bg-input, #FFF0F3)'
}

// ===== Helpers =====
function imageUrl(filename) {
  if (!filename) return ''
  if (filename.startsWith('http')) return filename
  return UPLOAD_BASE + filename
}

function priceFormat(price) {
  return (price / 100).toFixed(2)
}

// ===== Lifecycle =====
onShow(async () => {
  if (!authStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }

  // Refresh profile for balance
  authStore.refreshProfile().catch(() => {})

  // Load core data
  await dishesStore.fetchAll()

  // Load today special
  loadTodaySpecial()

  // Load popular dishes (from store data, sorted by sold_count)
  loadPopularDishes()
})

// ===== Data Loading =====
async function loadTodaySpecial() {
  try {
    const res = await storeAPI.getTodaySpecial()
    todaySpecial.value = (res.special && res.special.dish) ? res.special.dish : null
  } catch (e) {
    todaySpecial.value = null
  }
}

function loadPopularDishes() {
  // Sort by sold_count descending, take top 3
  const sorted = [...dishesStore.dishes]
    .filter(d => d.is_available)
    .sort((a, b) => (b.sold_count || 0) - (a.sold_count || 0))
  popularDishes.value = sorted.slice(0, 3)
}

async function onRefresh() {
  isRefreshing.value = true
  try {
    await dishesStore.fetchAll()
    loadTodaySpecial()
    loadPopularDishes()
  } catch (e) {
    console.error('Refresh failed:', e)
  } finally {
    isRefreshing.value = false
  }
}

// ===== Dish Actions =====
function onDishClick(dish) {
  uni.navigateTo({ url: '/pages/dish-detail/dish-detail?id=' + dish.id })
}

function getCartQty(dishId) {
  const item = cartStore.items.find(i => i.dish.id === dishId)
  return item ? item.quantity : 0
}

function onAddDish(dish) {
  if (!dish.is_available) return
  cartStore.addDish(dish, 1)
  uni.showToast({ title: `已加 ${dish.name}`, icon: 'success', duration: 600 })
}

function onReduceDish(dish) {
  const item = cartStore.items.find(i => i.dish.id === dish.id)
  if (item && item.quantity > 1) {
    cartStore.updateQuantity(dish.id, item.quantity - 1)
  } else {
    cartStore.removeDish(dish.id)
  }
}

// ===== Random Dish =====
function doRandomPick() {
  const available = allAvailableDishes.value
  if (available.length === 0) {
    uni.showToast({ title: '暂时没有可选的菜品', icon: 'none' })
    return null
  }
  const idx = Math.floor(Math.random() * available.length)
  return available[idx]
}

function onRandomPick() {
  isShaking.value = true
  setTimeout(() => { isShaking.value = false }, 600)
  const dish = doRandomPick()
  if (!dish) return
  randomDish.value = dish
  showRandomModal.value = true
}

function onRandomPickRandom() {
  const dish = doRandomPick()
  if (dish) {
    randomDish.value = dish
  }
}

function onRandomConfirm() {
  if (randomDish.value && randomDish.value.is_available) {
    cartStore.addDish(randomDish.value, 1)
    uni.showToast({
      title: `已加入 ${randomDish.value.name}`,
      icon: 'success',
      duration: 800,
    })
  }
  showRandomModal.value = false
  randomDish.value = null
}

function closeRandomModal() {
  showRandomModal.value = false
  randomDish.value = null
}

// ===== Navigation =====
function goCart() {
  uni.navigateTo({ url: '/pages/cart/cart' })
}

function goProfile() {
  uni.switchTab({ url: '/pages/profile/profile' })
}
</script>

<style lang="scss" scoped>
.menu-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  display: flex;
  flex-direction: column;
}

/* ===== Top Bar ===== */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 24rpx;
  background: var(--bg-card, #FFFFFF);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  position: relative;
  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.brand-icon {
  font-size: 36rpx;
}

.brand-name {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.balance-tag {
  display: flex;
  align-items: center;
  background: var(--bg-page, #FFF5F7);
  border-radius: 24rpx;
  padding: 8rpx 20rpx;
  gap: 6rpx;
}

.balance-icon {
  font-size: 24rpx;
}

.balance-text {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--color-primary, #FF7B93);
}

/* ===== Banner Area ===== */
.banner-scroll {
  background: var(--bg-card, #FFFFFF);
  padding: 16rpx 0;
  white-space: nowrap;
}

.banner-section {
  display: inline-block;
  vertical-align: top;
}

.section-head {
  font-size: 24rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  margin-bottom: 12rpx;
  padding-left: 4rpx;
}

.banner-item {
  display: inline-block;
  vertical-align: top;
  margin-right: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
  cursor: pointer;
}

.banner-item:active {
  opacity: 0.85;
}

/* Today Special */
.special-item {
  width: 340rpx;
  background: linear-gradient(135deg, #FFF8E1, #FFF0D0);
  margin-left: 24rpx;
}

.special-badge {
  font-size: 24rpx;
  font-weight: 700;
  color: #B8860B;
  padding: 12rpx 16rpx 4rpx;
}

.special-body {
  padding: 0 16rpx 16rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.special-img, .special-emoji {
  width: 100%;
  height: 160rpx;
  border-radius: 12rpx;
}

.special-emoji {
  background: #FFE8C0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64rpx;
}

.special-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.special-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #4A4A4A;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.special-price {
  font-size: 28rpx;
  font-weight: 800;
  color: var(--color-primary, #FF7B93);
  margin-left: 8rpx;
}

/* Popular */
.popular-section {
  margin-left: 8rpx;
}

.popular-list {
  display: flex;
  gap: 16rpx;
}

.popular-item {
  width: 200rpx;
  background: var(--bg-page, #FFF5F7);
  padding: 12rpx;
  position: relative;
}

.popular-rank {
  position: absolute;
  top: 6rpx;
  left: 6rpx;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.popular-rank text {
  font-size: 20rpx;
  font-weight: 700;
  color: var(--bg-card, #FFFFFF);
}

.rank-1 {
  background: #FF6B35;
}

.rank-2 {
  background: #FF8C5A;
}

.rank-3 {
  background: #FFB085;
}

.popular-img, .popular-emoji {
  width: 100%;
  height: 140rpx;
  border-radius: 12rpx;
}

.popular-emoji {
  background: #FFE0E8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56rpx;
}

.popular-name {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: #4A4A4A;
  margin-top: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.popular-price {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  margin-top: 4rpx;
}

/* ===== Search Bar ===== */
.search-bar-wrap { position: relative; padding: 12rpx 24rpx; background: #FFF; }
.search-bar { height: 68rpx; background: var(--bg-page, #FFF5F7); border-radius: 34rpx; padding: 0 48rpx 0 28rpx; font-size: 26rpx; }
.search-clear { position: absolute; right: 40rpx; top: 50%; transform: translateY(-50%); font-size: 28rpx; color: #CCC; padding: 8rpx; }

/* ===== Main Content ===== */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 180rpx;
  background: var(--bg-card, #FFFFFF);
  flex-shrink: 0;
  border-right: 1rpx solid var(--bg-input, #FFF0F3);
}

.sidebar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24rpx 8rpx;
  min-height: 100rpx;
  transition: all 0.2s;
  position: relative;
}

.sidebar-item.active {
  background: var(--bg-page, #FFF5F7);
}

.sidebar-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8rpx;
  bottom: 8rpx;
  width: 6rpx;
  background: var(--color-primary, #FF7B93);
  border-radius: 0 6rpx 6rpx 0;
}

.sidebar-icon {
  font-size: 36rpx;
  margin-bottom: 6rpx;
}

.sidebar-name {
  font-size: 22rpx;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.sidebar-item.active .sidebar-name {
  color: var(--color-primary, #FF7B93);
  font-weight: 700;
}

/* Dish list (right side) */
.dish-scroll {
  flex: 1;
  background: var(--bg-page, #FFF5F7);
}

.state-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 120rpx 48rpx;
}

.state-text {
  font-size: 28rpx;
  color: #CCC;
}

.dish-list {
  padding: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.dish-card-wrapper { width: 100%; }

/* Inline Dish Card */
.dish-card {
  display: flex;
  background: var(--bg-card, #FFFFFF);
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(255, 123, 147, 0.06);
  transition: transform 0.15s;
}

.dish-card:active {
  transform: scale(0.985);
}

.dish-image-wrap {
  width: 180rpx;
  height: 180rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.dish-image {
  width: 100%;
  height: 100%;
}

.dish-placeholder {
  font-size: 64rpx;
}

.dish-info {
  flex: 1;
  padding: 16rpx 20rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}

.dish-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.dish-meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 4rpx;
}

.dish-sold {
  font-size: 20rpx;
  color: #BBB;
}

.dish-note {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-top: 4rpx;
}

.note-emoji {
  font-size: 20rpx;
}

.note-text {
  font-size: 20rpx;
  color: #B8860B;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8rpx;
}

.dish-price {
  font-size: 30rpx;
  font-weight: 800;
  color: var(--color-primary, #FF7B93);
}

.add-btn {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(255, 123, 147, 0.3);
}

.add-btn:active, .step-btn:active {
  transform: scale(0.88);
}

.cart-stepper { flex-shrink: 0; }
.stepper { display: flex; align-items: center; gap: 6rpx; }
.step-btn { width: 44rpx; height: 44rpx; border-radius: 50%; background: var(--bg-input, #FFF0F3); display: flex; align-items: center; justify-content: center; }
.step-btn text { font-size: 28rpx; color: var(--color-primary, #FF7B93); font-weight: 600; }
.step-qty { font-size: 26rpx; font-weight: 700; color: var(--color-primary, #FF7B93); min-width: 32rpx; text-align: center; }

.add-icon {
  color: var(--bg-card, #FFFFFF);
  font-size: 36rpx;
  font-weight: 600;
  line-height: 1;
}

.sold-out-tag {
  font-size: 22rpx;
  color: #CCC;
  font-weight: 600;
  padding: 6rpx 16rpx;
  background: #F5F5F5;
  border-radius: 20rpx;
}

/* ===== Random Dish Button (fixed bottom-right) ===== */
.random-btn {
  position: fixed;
  bottom: 140rpx;
  right: 24rpx;
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(255, 123, 147, 0.4);
  z-index: 100;
  transition: transform 0.2s;
}

.random-btn:active {
  transform: scale(0.9);
}
.random-btn.shaking {
  animation: shake 0.6s ease-in-out;
}
@keyframes shake {
  0%, 100% { transform: rotate(0deg) scale(1); }
  15% { transform: rotate(-25deg) scale(1.1); }
  30% { transform: rotate(20deg) scale(1.1); }
  45% { transform: rotate(-15deg) scale(1.05); }
  60% { transform: rotate(10deg) scale(1.05); }
  75% { transform: rotate(-5deg); }
}

.random-emoji {
  font-size: 40rpx;
}

/* ===== Floating Cart Bar ===== */
.cart-float {
  position: fixed;
  bottom: 20rpx;
  left: 24rpx;
  right: 24rpx;
  height: 96rpx;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), #FF889C);
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(255, 123, 147, 0.35);
  z-index: 100;
}

.cart-float-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.cart-badge {
  min-width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--bg-card, #FFFFFF);
  color: var(--color-primary, #FF7B93);
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4rpx;
}

.cart-total {
  color: var(--bg-card, #FFFFFF);
  font-size: 34rpx;
  font-weight: 700;
}

.cart-float-right {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.cart-go-text {
  color: var(--bg-card, #FFFFFF);
  font-size: 28rpx;
  font-weight: 600;
}

.cart-arrow {
  color: var(--bg-card, #FFFFFF);
  font-size: 28rpx;
}

/* ===== Random Dish Modal ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.random-modal {
  width: 600rpx;
  background: var(--bg-card, #FFFFFF);
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: popIn 0.3s ease-out;
}

@keyframes popIn {
  from {
    transform: scale(0.7);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.random-modal-icon {
  font-size: 72rpx;
  margin-bottom: 12rpx;
}

.random-modal-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
  margin-bottom: 32rpx;
}

.random-dish-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.random-img-wrap {
  width: 260rpx;
  height: 200rpx;
  border-radius: 20rpx;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.random-img {
  width: 100%;
  height: 100%;
}

.random-placeholder {
  font-size: 80rpx;
}

.random-dish-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #4A4A4A;
  margin-top: 20rpx;
}

.random-dish-price {
  font-size: 36rpx;
  font-weight: 800;
  color: var(--color-primary, #FF7B93);
  margin-top: 8rpx;
}

.random-dish-note {
  font-size: 24rpx;
  color: #B8860B;
  margin-top: 8rpx;
  text-align: center;
}

.random-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 36rpx;
  width: 100%;
}

.random-btn-action {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 600;
  transition: opacity 0.2s;
}

.random-btn-action:active {
  opacity: 0.85;
}

.random-btn-secondary {
  background: var(--bg-input, #FFF0F3);
  color: var(--color-primary, #FF7B93);
}

.random-btn-primary {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: var(--bg-card, #FFFFFF);
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}
</style>
