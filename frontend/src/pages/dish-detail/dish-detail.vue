<template>
  <view class="detail-page">
    <!-- Loading state -->
    <view v-if="loading" class="loading-wrap">
      <text class="loading-text">加载中...</text>
    </view>

    <!-- Error state -->
    <view v-else-if="error" class="error-wrap">
      <EmptyState icon="😵" :text="error" subText="请返回重试" />
      <view class="back-btn" @click="goBack">返回菜单</view>
    </view>

    <!-- Content -->
    <template v-else-if="dish">
      <!-- Image carousel -->
      <swiper
        class="image-swiper"
        :indicator-dots="imageList.length > 1"
        indicator-color="rgba(255,255,255,0.4)"
        indicator-active-color="var(--color-primary, #FF7B93)"
        autoplay
        interval="4000"
        circular
      >
        <swiper-item v-for="(img, idx) in imageList" :key="idx">
          <view class="swiper-slide">
            <image
              v-if="img"
              class="swiper-image"
              :src="img"
              mode="aspectFill"
            />
            <view v-else class="swiper-placeholder" :style="{ backgroundColor: placeholderBg }">
              <text class="placeholder-emoji">{{ dish.category_icon || '🍽️' }}</text>
            </view>
          </view>
        </swiper-item>
      </swiper>

      <!-- Dish info -->
      <view class="info-section">
        <view class="info-header">
          <text class="dish-name">{{ dish.name }}</text>
          <view v-if="!dish.is_available" class="sold-out-badge">已下架</view>
        </view>

        <view class="dish-price-row">
          <text class="dish-price">¥{{ priceFormat(dish.price) }}</text>
          <text class="dish-sold">已售 {{ dish.sold_count || 0 }}</text>
        </view>

        <view v-if="dish.note" class="dish-note-banner">
          <text class="note-icon">💡</text>
          <text class="note-text">{{ dish.note }}</text>
        </view>

        <view v-if="dish.description" class="dish-desc">
          <text class="desc-label">描述</text>
          <text class="desc-text">{{ dish.description }}</text>
        </view>
      </view>

      <!-- Add to cart -->
      <view class="fav-btn" :class="{ favorited: isFavorited }" @click="toggleFavorite"><text>{{ isFavorited ? '❤️' : '🤍' }} 收藏</text></view>
      <view v-if="dish.is_available" class="cart-section">
        <view class="stepper">
          <text class="stepper-label">数量</text>
          <view class="stepper-controls">
            <view class="stepper-btn" :class="{ disabled: quantity <= 1 }" @click="decrement">
              <text>-</text>
            </view>
            <text class="stepper-value">{{ quantity }}</text>
            <view class="stepper-btn" @click="increment">
              <text>+</text>
            </view>
          </view>
        </view>

        <view class="add-cart-btn" @click="onAddToCart">
          <text class="add-cart-text">加入购物车</text>
          <text class="add-cart-sub">¥{{ priceFormat(dish.price * quantity) }}</text>
        </view>
      </view>

      <!-- Reviews section -->
      <view class="reviews-section">
        <view class="reviews-header">
          <view class="reviews-title-left">
            <text class="reviews-title">评价</text>
            <text class="reviews-count">({{ reviews.length }})</text>
            <view v-if="reviews.length > 0" class="reviews-average">
              <text class="avg-stars" v-for="i in 5" :key="i">{{ i <= avgRating ? '⭐' : '☆' }}</text>
              <text class="avg-score">{{ avgRating.toFixed(1) }}</text>
            </view>
          </view>
          <view class="write-review-btn" @click="openReviewModal">
            <text class="write-review-text">写评价</text>
          </view>
        </view>

        <!-- Review list -->
        <view v-if="reviewsLoading" class="reviews-loading">
          <text>加载评价中...</text>
        </view>

        <view v-else-if="reviews.length === 0" class="reviews-empty">
          <EmptyState icon="💬" text="暂无评价" subText="来写第一条评价吧~" />
        </view>

        <view v-else class="review-list">
          <view v-for="review in reviews" :key="review.id" class="review-item">
            <view class="review-user">
              <view class="review-avatar">
                <text>{{ review.user_nickname ? review.user_nickname.charAt(0) : '?' }}</text>
              </view>
              <view class="review-user-info">
                <text class="review-nickname">{{ review.user_nickname || '匿名用户' }}</text>
                <view class="review-stars">
                  <text v-for="i in 5" :key="i" class="star">{{ i <= review.rating ? '⭐' : '☆' }}</text>
                </view>
              </view>
              <text class="review-time">{{ formatTime(review.created_at) }}</text>
            </view>
            <text v-if="review.content" class="review-content">{{ review.content }}</text>
          </view>
        </view>
      </view>

      <!-- Bottom spacer for fixed bar -->
      <view style="height: 40rpx;"></view>
    </template>

    <!-- Write review modal -->
    <view v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
      <view class="modal-content" @click.stop>
        <view class="modal-title">写评价</view>

        <view class="star-selector">
          <text class="star-label">评分</text>
          <view class="stars-row">
            <text
              v-for="i in 5"
              :key="i"
              class="selectable-star"
              :class="{ active: i <= reviewRating }"
              @click="reviewRating = i"
            >
              {{ i <= reviewRating ? '⭐' : '☆' }}
            </text>
          </view>
        </view>

        <textarea
          class="review-textarea"
          v-model="reviewContent"
          placeholder="说说这道菜怎么样..."
          maxlength="500"
        />
        <text class="char-count">{{ reviewContent.length }}/500</text>

        <view class="modal-actions">
          <view class="modal-btn cancel-btn" @click="closeReviewModal">取消</view>
          <view class="modal-btn submit-btn" :class="{ disabled: submittingReview }" @click="submitReview">
            <text v-if="!submittingReview">提交评价</text>
            <text v-else>提交中...</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { dishesAPI } from '@/api/dishes'
import { reviewsAPI } from '@/api/reviews'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { UPLOAD_BASE } from '@/config'
import EmptyState from '@/components/EmptyState.vue'

const cartStore = useCartStore()
const authStore = useAuthStore()
const favorites = ref(JSON.parse((authStore.user?.favorite_dish_ids) || '[]'))
const isFavorited = computed(() => favorites.value.includes(dish.value?.id))
function toggleFavorite() {
  if (!dish.value) return
  const idx = favorites.value.indexOf(dish.value.id)
  if (idx >= 0) favorites.value.splice(idx, 1)
  else favorites.value.push(dish.value.id)
  authStore.user.favorite_dish_ids = JSON.stringify(favorites.value)
  uni.setStorageSync('user', authStore.user)
  uni.showToast({ title: idx >= 0 ? '已取消收藏' : '已收藏', icon: 'success' })
}

const dish = ref(null)
const loading = ref(true)
const error = ref('')
const quantity = ref(1)

// Reviews
const reviews = ref([])
const reviewsLoading = ref(false)
const showReviewModal = ref(false)
const reviewRating = ref(5)
const reviewContent = ref('')
const submittingReview = ref(false)

// Placeholder colors by category icon
const placeholderColors = {
  '🍝': '#FFE4C4',
  '🥤': '#D4EFFF',
  '🍰': '#FFE0EC',
  '🥗': '#E8F8E0',
  '🍜': '#FFE8D6',
  '✨': '#F5F0FF',
}
const placeholderBg = computed(() => {
  if (!dish.value) return 'var(--bg-input, #FFF0F3)'
  return placeholderColors[dish.value.category_icon] || 'var(--bg-input, #FFF0F3)'
})

// Build image list from dish.images (array) or dish.image (string)
const imageList = computed(() => {
  if (!dish.value) return []
  const urls = []
  if (dish.value.images && Array.isArray(dish.value.images) && dish.value.images.length > 0) {
    dish.value.images.forEach(img => {
      if (img) urls.push(UPLOAD_BASE + img)
    })
  }
  if (urls.length === 0 && dish.value.image) {
    urls.push(UPLOAD_BASE + dish.value.image)
  }
  if (urls.length === 0) {
    urls.push('')
  }
  return urls
})

// Average rating
const avgRating = computed(() => {
  if (reviews.value.length === 0) return 0
  const sum = reviews.value.reduce((s, r) => s + r.rating, 0)
  return sum / reviews.value.length
})

function priceFormat(price) {
  return (price / 100).toFixed(2)
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = String(date.getHours()).padStart(2, '0')
    const min = String(date.getMinutes()).padStart(2, '0')
    return `${month}/${day} ${hour}:${min}`
  } catch {
    return dateStr
  }
}

// Fetch dish detail
async function fetchDish(id) {
  loading.value = true
  error.value = ''
  try {
    const res = await dishesAPI.getDish(id)
    dish.value = res.dish || res
    quantity.value = 1
  } catch (e) {
    error.value = e.msg || '获取菜品信息失败'
  } finally {
    loading.value = false
  }
}

// Fetch reviews
async function fetchReviews() {
  if (!dish.value) return
  reviewsLoading.value = true
  try {
    const res = await reviewsAPI.getList(dish.value.id)
    reviews.value = res.reviews || res || []
  } catch (e) {
    console.error('Failed to load reviews:', e)
    reviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

// Quantity stepper
function increment() {
  quantity.value++
}

function decrement() {
  if (quantity.value > 1) {
    quantity.value--
  }
}

// Add to cart
function onAddToCart() {
  if (!dish.value || !dish.value.is_available) return
  cartStore.addDish(dish.value, quantity.value)
  uni.showToast({
    title: `已加入 ${dish.value.name} x${quantity.value}`,
    icon: 'success',
    duration: 1200,
  })
}

// Review modal
function openReviewModal() {
  reviewRating.value = 5
  reviewContent.value = ''
  showReviewModal.value = true
}

function closeReviewModal() {
  showReviewModal.value = false
}

async function submitReview() {
  if (submittingReview.value) return
  if (!reviewContent.value.trim()) {
    uni.showToast({ title: '请填写评价内容', icon: 'none' })
    return
  }
  submittingReview.value = true
  try {
    await reviewsAPI.create(dish.value.id, {
      rating: reviewRating.value,
      content: reviewContent.value.trim(),
    })
    uni.showToast({ title: '评价成功', icon: 'success' })
    showReviewModal.value = false
    fetchReviews()
  } catch (e) {
    uni.showToast({ title: e.msg || '评价失败，请重试', icon: 'none' })
  } finally {
    submittingReview.value = false
  }
}

function goBack() {
  uni.navigateBack()
}

onLoad((options) => {
  const id = parseInt(options.id)
  if (!id) {
    error.value = '缺少菜品ID'
    loading.value = false
    return
  }
  fetchDish(id)
  fetchReviews()
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding-bottom: 40rpx;
}

/* Loading & Error */
.loading-wrap, .error-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 48rpx;
  min-height: 60vh;
}

.loading-text {
  font-size: 28rpx;
  color: #CCC;
}

.back-btn {
  margin-top: 24rpx;
  padding: 16rpx 48rpx;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  border-radius: 40rpx;
  color: #FFF;
  font-size: 28rpx;
  font-weight: 600;
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.25);
}

/* Image Swiper */
.image-swiper {
  width: 100%;
  height: 600rpx;
}

.swiper-slide {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-input, #FFF0F3);
}

.swiper-image {
  width: 100%;
  height: 100%;
}

.swiper-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-emoji {
  font-size: 120rpx;
}

/* Info Section */
.info-section {
  background: var(--bg-card, #FFFFFF);
  border-radius: 24rpx 24rpx 0 0;
  margin-top: -24rpx;
  padding: 32rpx;
  position: relative;
  z-index: 2;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.dish-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #4A4A4A;
  flex: 1;
}

.fav-btn { text-align: center; padding: 16rpx; margin: 0 24rpx; border-radius: 12rpx; background: #FFF; font-size: 26rpx; }
.fav-btn.favorited { background: var(--bg-input, #FFF0F3); color: var(--color-primary, #FF7B93); }
.sold-out-badge {
  padding: 6rpx 20rpx;
  background: #F0F0F0;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #999;
  font-weight: 600;
}

.dish-price-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 16rpx;
}

.dish-price {
  font-size: 40rpx;
  font-weight: 800;
  color: var(--color-primary, #FF7B93);
}

.dish-sold {
  font-size: 24rpx;
  color: #AAA;
}

.dish-note-banner {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 20rpx;
  padding: 16rpx 20rpx;
  background: #FFF8E1;
  border-radius: 12rpx;
}

.note-icon {
  font-size: 28rpx;
}

.note-text {
  font-size: 24rpx;
  color: #B8860B;
  flex: 1;
}

.dish-desc {
  margin-top: 24rpx;
  padding: 20rpx;
  background: var(--bg-page, #FFF5F7);
  border-radius: 12rpx;
}

.desc-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #888;
  display: block;
  margin-bottom: 8rpx;
}

.desc-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
}

/* Cart Section */
.cart-section {
  background: var(--bg-card, #FFFFFF);
  margin-top: 16rpx;
  padding: 32rpx;
  border-radius: 24rpx;
}

.stepper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.stepper-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
}

.stepper-controls {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--bg-page, #FFF5F7);
  border-radius: 32rpx;
  overflow: hidden;
}

.stepper-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary, #FF7B93);
  color: var(--bg-card, #FFFFFF);
  font-size: 32rpx;
  font-weight: 700;
  transition: opacity 0.2s;
}

.stepper-btn:active {
  opacity: 0.8;
}

.stepper-btn.disabled {
  background: #E0E0E0;
  color: #AAA;
}

.stepper-value {
  min-width: 80rpx;
  text-align: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #4A4A4A;
}

.add-cart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  height: 88rpx;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  border-radius: 44rpx;
  box-shadow: 0 4rpx 20rpx rgba(255, 123, 147, 0.35);
}

.add-cart-btn:active {
  opacity: 0.9;
}

.add-cart-text {
  color: var(--bg-card, #FFFFFF);
  font-size: 32rpx;
  font-weight: 700;
}

.add-cart-sub {
  color: rgba(255, 255, 255, 0.8);
  font-size: 26rpx;
  font-weight: 600;
}

/* Reviews Section */
.reviews-section {
  background: var(--bg-card, #FFFFFF);
  margin-top: 16rpx;
  padding: 32rpx;
  border-radius: 24rpx;
}

.reviews-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.reviews-title-left {
  display: flex;
  align-items: center;
  gap: 8rpx;
  flex-wrap: wrap;
}

.reviews-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #4A4A4A;
}

.reviews-count {
  font-size: 26rpx;
  color: #AAA;
}

.reviews-average {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-left: 12rpx;
}

.avg-stars {
  font-size: 22rpx;
}

.avg-score {
  font-size: 24rpx;
  color: var(--color-primary, #FF7B93);
  font-weight: 700;
  margin-left: 4rpx;
}

.write-review-btn {
  padding: 12rpx 28rpx;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  border-radius: 28rpx;
}

.write-review-btn:active {
  opacity: 0.85;
}

.write-review-text {
  color: var(--bg-card, #FFFFFF);
  font-size: 24rpx;
  font-weight: 600;
}

.reviews-loading, .reviews-empty {
  padding: 40rpx 0;
  text-align: center;
  color: #CCC;
  font-size: 26rpx;
}

/* Review List */
.review-item {
  padding: 24rpx 0;
  border-bottom: 1rpx solid var(--bg-input, #FFF0F3);
}

.review-item:last-child {
  border-bottom: none;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.review-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary-light, #FFB3C6), #FFD6E0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.review-avatar text {
  font-size: 24rpx;
  color: var(--bg-card, #FFFFFF);
  font-weight: 700;
}

.review-user-info {
  flex: 1;
}

.review-nickname {
  font-size: 26rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
}

.review-stars {
  display: flex;
  gap: 2rpx;
  margin-top: 4rpx;
}

.star {
  font-size: 20rpx;
}

.review-time {
  font-size: 20rpx;
  color: #CCC;
}

.review-content {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-top: 12rpx;
  line-height: 1.6;
}

/* Review Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  width: 100%;
  background: var(--bg-card, #FFFFFF);
  border-radius: 32rpx 32rpx 0 0;
  padding: 40rpx 32rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.25s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.modal-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #4A4A4A;
  text-align: center;
  margin-bottom: 32rpx;
}

.star-selector {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.star-label {
  font-size: 26rpx;
  color: #888;
  font-weight: 600;
}

.stars-row {
  display: flex;
  gap: 8rpx;
}

.selectable-star {
  font-size: 48rpx;
  cursor: pointer;
  transition: transform 0.15s;
}

.selectable-star:active {
  transform: scale(1.2);
}

.review-textarea {
  width: 100%;
  height: 200rpx;
  background: var(--bg-page, #FFF5F7);
  border-radius: 16rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #4A4A4A;
  box-sizing: border-box;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #CCC;
  margin-top: 8rpx;
}

.modal-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 32rpx;
}

.modal-btn {
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

.modal-btn:active {
  opacity: 0.85;
}

.cancel-btn {
  background: var(--bg-input, #FFF0F3);
  color: var(--color-primary, #FF7B93);
}

.submit-btn {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: var(--bg-card, #FFFFFF);
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}

.submit-btn.disabled {
  opacity: 0.6;
}
</style>
