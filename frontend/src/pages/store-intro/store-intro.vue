<template>
  <view class="intro-page">
    <view v-if="loading" class="loading-wrap">
      <text class="loading-emoji">🍳</text>
      <text class="loading-text">加载中...</text>
    </view>

    <scroll-view v-else class="content-scroll" scroll-y :show-scrollbar="false">
      <!-- Store image -->
      <view class="image-section">
        <image v-if="config.store_image" class="store-image" :src="imgBase + config.store_image" mode="aspectFill" />
        <view v-else class="image-placeholder"><text class="ph-emoji">🍳</text><text class="ph-text">木糯小厨</text></view>
      </view>

      <!-- Store info -->
      <view class="info-section">
        <text class="store-name">{{ config.store_name || '木糯小厨' }}</text>
        <text class="store-intro" v-if="config.store_intro">{{ config.store_intro }}</text>
        <text class="welcome-text">{{ config.welcome_message || '今天想吃什么呢？' }}</text>
      </view>

      <!-- Stats row -->
      <view class="stats-row">
        <view class="stat-item"><text class="stat-num">{{ stats.totalDishes }}</text><text class="stat-label">道菜品</text></view>
        <view class="stat-item"><text class="stat-num">{{ stats.todayOrders }}</text><text class="stat-label">今日订单</text></view>
        <view class="stat-item"><text class="stat-num">{{ stats.diaryDays }}</text><text class="stat-label">天记录</text></view>
      </view>

      <!-- Today special -->
      <view v-if="todaySpecial" class="special-section" @click="goMenu">
        <text class="section-title">⭐ 今日特供</text>
        <view class="special-card">
          <view class="sp-img-wrap" :style="{ backgroundColor: placeholderColor(todaySpecial.category_icon) }">
            <image v-if="todaySpecial.image" class="sp-img" :src="imgBase + todaySpecial.image" mode="aspectFill" />
            <text v-else class="sp-emoji">{{ todaySpecial.category_icon || '🍽️' }}</text>
          </view>
          <view class="sp-info">
            <text class="sp-name">{{ todaySpecial.name }}</text>
            <text class="sp-price">¥{{ (todaySpecial.price / 100).toFixed(2) }}</text>
            <text class="sp-desc" v-if="todaySpecial.description">{{ todaySpecial.description }}</text>
          </view>
          <text class="sp-arrow">→</text>
        </view>
      </view>

      <!-- Banner -->
      <view v-if="config.banner_text" class="banner-card">
        <text class="banner-text">{{ config.banner_text }}</text>
      </view>

      <!-- Featured dishes -->
      <view v-if="featuredDishes.length > 0" class="featured-section">
        <text class="section-title">✨ 招牌推荐</text>
        <scroll-view class="dish-scroll" scroll-x :show-scrollbar="false">
          <view class="dish-track">
            <view v-for="dish in featuredDishes" :key="dish.id" class="dish-card" @click="goMenu">
              <view class="dc-img-wrap" :style="{ backgroundColor: placeholderColor(dish.category_icon) }">
                <image v-if="dish.image" class="dc-img" :src="imgBase + dish.image" mode="aspectFill" />
                <text v-else class="dc-emoji">{{ dish.category_icon || '🍽️' }}</text>
              </view>
              <view class="dc-info">
                <text class="dc-name">{{ dish.name }}</text>
                <text class="dc-price">¥{{ (dish.price / 100).toFixed(2) }}</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- Latest diary -->
      <view v-if="latestNote" class="diary-section">
        <text class="section-title">📝 最新日记</text>
        <view class="diary-card">
          <text class="diary-mood">{{ latestNote.mood || '📝' }}</text>
          <text class="diary-content">{{ latestNote.content }}</text>
          <text class="diary-meta">{{ latestNote.user_nickname }} · {{ fmt(latestNote.created_at) }}</text>
        </view>
      </view>

      <!-- Enter button -->
      <view class="action-section">
        <button class="enter-btn" @click="goMenu">进入菜单 →</button>
      </view>
      <view style="height: 60rpx;"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { UPLOAD_BASE } from '@/config'
const uploadBase = UPLOAD_BASE
import { storeAPI } from '@/api/store'
import { dishesAPI } from '@/api/dishes'
import { get } from '@/api/index'

const imgBase = uploadBase
const loading = ref(true)
const config = ref({})
const allDishes = ref([])
const todaySpecial = ref(null)
const stats = ref({ totalDishes: 0, todayOrders: 0, diaryDays: 0 })
const latestNote = ref(null)

const featuredDishes = computed(() => {
  const ids = []
  try {
    const parsed = JSON.parse(config.value.featured_dish_ids || '[]')
    if (Array.isArray(parsed)) ids.push(...parsed)
  } catch { /* ignore */ }
  if (ids.length === 0) return allDishes.value.slice(0, 6)
  const map = new Map(allDishes.value.map(d => [d.id, d]))
  return ids.map(id => map.get(id)).filter(Boolean)
})

function placeholderColor(icon) {
  const colors = { '🍝': '#FFE4C4', '🥤': '#D4EFFF', '🍰': '#FFE0EC', '🥗': '#E8F8E0', '🍜': '#FFE8D6', '✨': '#F5F0FF' }
  return colors[icon] || 'var(--bg-input, #FFF0F3)'
}
function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso); const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

onMounted(async () => {
  try {
    const [configRes, dishesRes, specialRes, dashboardRes] = await Promise.all([
      storeAPI.getConfig(),
      dishesAPI.getDishes(),
      storeAPI.getTodaySpecial(),
      get('/admin/dashboard').catch(() => ({ stats: { total_dishes: 0, today_orders: 0 } })),
    ])
    config.value = configRes.config || configRes
    allDishes.value = dishesRes.dishes || []
    if (specialRes.special && specialRes.special.dish) {
      todaySpecial.value = specialRes.special.dish
    }
    if (dashboardRes.stats) {
      stats.value.totalDishes = dashboardRes.stats.total_dishes || allDishes.value.length
      stats.value.todayOrders = dashboardRes.stats.today_orders || 0
    }
    // Fetch latest diary note
    try {
      const now = new Date()
      const dateStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`
      const diaryRes = await get(`/diary/${dateStr}`)
      if (diaryRes.notes && diaryRes.notes.length > 0) {
        latestNote.value = diaryRes.notes[0]
      }
      if (diaryRes.photos) stats.value.diaryDays = 1 // simplified: this date has records
    } catch { /* diary may be empty */ }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

function goMenu() { uni.switchTab({ url: '/pages/index/index' }) }
</script>

<style lang="scss" scoped>
.intro-page { min-height: 100vh; background: var(--bg-page, #FFF5F7); }
.loading-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; gap: 20rpx; }
.loading-emoji { font-size: 80rpx; animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.1)} }
.loading-text { font-size: 28rpx; color: #CCC; }
.content-scroll { height: 100vh; }

.image-section { width:100%; height:480rpx; overflow:hidden; }
.store-image { width:100%; height:100%; }
.image-placeholder { width:100%; height:100%; background:linear-gradient(135deg,var(--color-primary-light, #FFB3C6),#FFD6DE); display:flex; flex-direction:column; align-items:center; justify-content:center; }
.ph-emoji { font-size:120rpx; animation:float 3s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16rpx)} }
.ph-text { font-size:36rpx; color:#FFF; font-weight:700; margin-top:16rpx; }

.info-section { padding:36rpx 36rpx 8rpx; text-align:center; }
.store-name { font-size:44rpx; font-weight:700; color:var(--color-primary, #FF7B93); display:block; letter-spacing:4rpx; }
.store-intro { font-size:26rpx; color:#999; display:block; margin-top:12rpx; line-height:1.6; }
.welcome-text { font-size:28rpx; color:#666; display:block; margin-top:10rpx; }

.stats-row { display:flex; padding:20rpx 36rpx; gap:12rpx; }
.stat-item { flex:1; background:#FFF; border-radius:16rpx; padding:20rpx; text-align:center; box-shadow:0 2rpx 8rpx rgba(0,0,0,0.04); }
.stat-num { font-size:36rpx; font-weight:700; color:var(--color-primary, #FF7B93); display:block; }
.stat-label { font-size:22rpx; color:#999; }

.special-section { padding:8rpx 36rpx 16rpx; }
.section-title { font-size:28rpx; font-weight:600; color:#4A4A4A; display:block; margin-bottom:14rpx; }
.special-card { display:flex; align-items:center; background:#FFF; border-radius:16rpx; padding:16rpx; box-shadow:0 2rpx 12rpx rgba(255,123,147,0.12); border:2rpx solid var(--color-primary-light, #FFB3C6); }
.sp-img-wrap { width:100rpx; height:100rpx; border-radius:12rpx; display:flex; align-items:center; justify-content:center; flex-shrink:0; overflow:hidden; }
.sp-img { width:100%; height:100%; }
.sp-emoji { font-size:48rpx; }
.sp-info { flex:1; margin-left:16rpx; }
.sp-name { font-size:28rpx; font-weight:600; display:block; }
.sp-price { font-size:26rpx; color:var(--color-primary, #FF7B93); font-weight:600; }
.sp-desc { font-size:22rpx; color:#AAA; margin-top:4rpx; }
.sp-arrow { font-size:28rpx; color:#CCC; }

.banner-card { margin:8rpx 36rpx; background:linear-gradient(135deg,var(--bg-input, #FFF0F3),#FFE4EA); border-radius:12rpx; padding:24rpx; text-align:center; }
.banner-text { font-size:26rpx; color:var(--color-primary, #FF7B93); line-height:1.6; }

.featured-section { padding:16rpx 36rpx; }
.dish-scroll { white-space:nowrap; }
.dish-track { display:inline-flex; gap:16rpx; padding-bottom:8rpx; }
.dish-card { width:220rpx; background:#FFF; border-radius:12rpx; overflow:hidden; box-shadow:0 2rpx 8rpx rgba(0,0,0,0.06); flex-shrink:0; }
.dc-img-wrap { width:220rpx; height:170rpx; display:flex; align-items:center; justify-content:center; }
.dc-img { width:100%; height:100%; }
.dc-emoji { font-size:56rpx; }
.dc-info { padding:12rpx 14rpx 16rpx; }
.dc-name { font-size:24rpx; font-weight:600; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.dc-price { font-size:22rpx; color:var(--color-primary, #FF7B93); font-weight:600; }

.diary-section { padding:8rpx 36rpx 16rpx; }
.diary-card { background:#FFF; border-radius:16rpx; padding:20rpx; box-shadow:0 2rpx 8rpx rgba(0,0,0,0.04); }
.diary-mood { font-size:36rpx; display:block; margin-bottom:8rpx; }
.diary-content { font-size:26rpx; color:#4A4A4A; line-height:1.6; display:block; }
.diary-meta { font-size:22rpx; color:#CCC; margin-top:8rpx; display:block; }

.action-section { padding:32rpx 48rpx 40rpx; display:flex; justify-content:center; }
.enter-btn { width:100%; max-width:500rpx; height:96rpx; background:linear-gradient(135deg,var(--color-primary, #FF7B93),var(--color-primary-light, #FFB3C6)); border-radius:48rpx; border:none; font-size:34rpx; font-weight:700; color:#FFF; letter-spacing:4rpx; box-shadow:0 8rpx 24rpx rgba(255,123,147,0.35); }
.enter-btn:active { transform:scale(.96); }
</style>
