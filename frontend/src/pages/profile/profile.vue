<template>
  <view class="profile-page">
    <!-- Header -->
    <view class="profile-header">
      <view class="avatar-area" @click="changeAvatar">
        <image v-if="authStore.user?.avatar" class="avatar-img" :src="imgBase + authStore.user.avatar" mode="aspectFill" />
        <text v-else class="avatar-emoji">{{ avatarEmoji }}</text>
        <view class="avatar-edit"><text>📷</text></view>
      </view>
      <text class="nickname">{{ authStore.user?.nickname || '食客' }}</text>
      <text class="username-text">@{{ authStore.user?.username || '' }}</text>
      <text class="role-tag">{{ authStore.isAdmin ? '👨‍🍳 大厨' : '👤 食客' }}</text>
    </view>

    <!-- Balance -->
    <view class="balance-card">
      <text class="balance-label">💰 我的余额</text>
      <text class="balance-amount">¥{{ displayBalance }}</text>
      <text class="balance-hint" v-if="!authStore.isAdmin">余额不足联系大厨充值~</text>
    </view>

    <!-- Quick links -->
    <view class="links-row">
      <view class="link-item" @click="goStoreIntro"><text class="link-icon">🏪</text><text class="link-text">店铺</text></view>
      <view class="link-item" @click="goOrders"><text class="link-icon">📋</text><text class="link-text">我的订单</text></view>
      <view class="link-item" @click="goAdmin" v-if="authStore.isAdmin"><text class="link-icon">⚙️</text><text class="link-text">管理</text></view>
    </view>

    <!-- 许愿池预览 -->
    <view class="card" @click="goWishes">
      <view class="preview-row">
        <view><text class="preview-icon">🌟</text><text class="preview-text">许愿池</text></view>
        <view><text class="preview-num">{{ wishCount }}</text><text class="preview-sub">个愿望</text></view>
        <text class="preview-arrow">→</text>
      </view>
    </view>

    <!-- Order stats -->
    <view class="card">
      <text class="card-title">📊 我的点餐</text>
      <view class="stats-mini">
        <view class="smini-item"><text class="smini-num">{{ orderStats.total }}</text><text class="smini-label">总订单</text></view>
        <view class="smini-item"><text class="smini-num">{{ orderStats.thisMonth }}</text><text class="smini-label">本月</text></view>
        <view class="smini-item"><text class="smini-num">¥{{ orderStats.totalSpent }}</text><text class="smini-label">消费</text></view>
      </view>
    </view>

    <!-- Achievements -->
    <view class="card" v-if="badges.length > 0">
      <text class="card-title">🏆 成就徽章</text>
      <view class="badge-row">
        <view v-for="b in badges" :key="b.icon" class="badge-item" :class="{ earned: b.earned }">
          <text class="badge-icon">{{ b.earned ? b.icon : '🔒' }}</text>
          <text class="badge-name">{{ b.name }}</text>
          <text class="badge-desc">{{ b.desc }}</text>
        </view>
      </view>
    </view>

    <!-- My diary & reviews -->
    <view class="card">
      <view class="tab-row">
        <text class="tab-item" :class="{ active: profileTab === 'diary' }" @click="profileTab = 'diary'">📸 日记照片</text>
        <text class="tab-item" :class="{ active: profileTab === 'reviews' }" @click="profileTab = 'reviews'">⭐ 我的评价</text>
      </view>

      <!-- Diary photos -->
      <view v-if="profileTab === 'diary'">
        <view v-if="diaryPhotos.length === 0" class="no-data">还没有上传过照片~</view>
        <view v-else class="photo-grid">
          <image v-for="p in diaryPhotos" :key="p.id" class="photo-thumb" :src="imgBase + p.image_path" mode="aspectFill" @click="previewPhoto(p)" />
        </view>
        <text v-if="diaryPhotos.length > 0" class="view-all" @click="goDiary">查看全部日记 →</text>
      </view>

      <!-- Reviews -->
      <view v-if="profileTab === 'reviews'">
        <view v-if="myReviews.length === 0" class="no-data">还没有评价过菜品~</view>
        <view v-else>
          <view v-for="r in myReviews.slice(0, 5)" :key="r.id" class="review-mini">
            <view class="rm-stars">{"⭐".repeat(r.rating)}</view>
            <text class="rm-content" v-if="r.content">{{ r.content }}</text>
            <text class="rm-dish">—— {{ r.dish_name || '菜品#' + r.dish_id }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Balance logs -->
    <view class="card">
      <text class="card-title">💳 余额变动</text>
      <view v-if="logs.length === 0"><text class="no-logs">暂无记录</text></view>
      <view v-else>
        <view v-for="log in logs.slice(0, 10)" :key="log.id" class="log-item">
          <view class="log-left"><text class="log-action">{{ actionLabel(log.action) }}</text><text class="log-time">{{ fmt(log.created_at) }}</text></view>
          <text class="log-amount" :class="log.amount >= 0 ? 'in' : 'out'">{{ log.amount >= 0 ? '+' : '' }}¥{{ (Math.abs(log.amount)/100).toFixed(2) }}</text>
        </view>
      </view>
    </view>

    <!-- Logout -->
    <view class="logout-area">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>
    <view style="height: 40rpx;"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { ordersAPI } from '@/api/orders'
import { dishesAPI } from '@/api/dishes'
import { get, uploadFile } from '@/api/index'
import { UPLOAD_BASE } from '@/config'

const uploadBase = UPLOAD_BASE
const imgBase = uploadBase
const authStore = useAuthStore()
const logs = ref([])
const orderStats = ref({ total: 0, thisMonth: 0, totalSpent: '0.00', hasNote: false, hasNightSnack: false, activeDays: 0 })
const wishCount = ref(0)
const profileTab = ref('diary')
const diaryPhotos = ref([])
const myReviews = ref([])

const badges = computed(() => {
  const total = orderStats.value.total
  const spent = parseFloat(orderStats.value.totalSpent) || 0
  const reviews = myReviews.value.length
  const photos = diaryPhotos.value.length
  return [
    { icon: '🍽️', name: '初次点单', desc: '下单1次', earned: total >= 1 },
    { icon: '🌟', name: '美食家', desc: '下单10次', earned: total >= 10 },
    { icon: '🏅', name: '常客', desc: '下单30次', earned: total >= 30 },
    { icon: '👑', name: '至尊食神', desc: '下单100次', earned: total >= 100 },
    { icon: '💰', name: '大客户', desc: '消费¥500', earned: spent >= 500 },
    { icon: '💎', name: 'VIP', desc: '消费¥2000', earned: spent >= 2000 },
    { icon: '💵', name: '超级VIP', desc: '消费¥10000', earned: spent >= 10000 },
    { icon: '⭐', name: '点评新秀', desc: '评价1次', earned: reviews >= 1 },
    { icon: '🎯', name: '评论家', desc: '评价10次', earned: reviews >= 10 },
    { icon: '📸', name: '记录者', desc: '上传5张照片', earned: photos >= 5 },
    { icon: '📷', name: '摄影师', desc: '上传20张照片', earned: photos >= 20 },
    { icon: '💝', name: '甜蜜时刻', desc: '下单写了备注', earned: orderStats.value.hasNote },
    { icon: '🌙', name: '夜猫子', desc: '夜宵时段下单', earned: orderStats.value.hasNightSnack },
    { icon: '🔥', name: '连点王', desc: '本月下单7天+', earned: orderStats.value.activeDays >= 7 },
    { icon: '🎉', name: '里程碑', desc: '累计50单', earned: total >= 50 },
  ]
})

const avatarEmoji = computed(() => {
  if (authStore.isAdmin) return '👨‍🍳'
  const map = { lqyispig: '👧', '木木': '🐱', '糯糯': '🐱' }
  return map[authStore.user?.username] || '👤'
})

const displayBalance = computed(() => {
  if (!authStore.user) return '0.00'
  return (authStore.user.balance / 100).toFixed(2)
})

onShow(async () => {
  try {
    await authStore.refreshProfile()
    const res = await ordersAPI.getBalanceLogs()
    logs.value = res.logs || []

    // Order stats
    try {
      const orderRes = await ordersAPI.getList()
      const orders = orderRes.orders || []
      orderStats.value.total = orders.length
      const now = new Date()
      orderStats.value.thisMonth = orders.filter(o => {
        const d = new Date(o.created_at)
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
      }).length
      orderStats.value.hasNote = orders.some(o => o.note && o.note.trim())
      orderStats.value.hasNightSnack = orders.some(o => o.meal_type === 'night_snack')
      const activeDaySet = new Set(orders.map(o => new Date(o.created_at).toDateString()))
      orderStats.value.activeDays = activeDaySet.size
      const totalCents = orders.reduce((s, o) => s + (o.total_amount || 0), 0)
      orderStats.value.totalSpent = (totalCents / 100).toFixed(2)
    } catch { /* ignore */ }

    // Wish count
    try { const wr = await get('/wishes'); wishCount.value = (wr.wishes || []).length } catch {}

    // Recent diary photos (last 7 days)
    try {
      const now = new Date()
      for (let i = 0; i < 7 && diaryPhotos.value.length < 6; i++) {
        const d = new Date(now); d.setDate(d.getDate() - i)
        const ds = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        try {
          const diaryRes = await get(`/diary/${ds}`)
          const mine = (diaryRes.photos || []).filter(p => p.user_id === authStore.user?.id)
          diaryPhotos.value.push(...mine)
        } catch { /* skip */ }
      }
      diaryPhotos.value = diaryPhotos.value.slice(0, 9)
    } catch { diaryPhotos.value = [] }

    // My recent reviews
    try {
      const allDishes = (await dishesAPI.getDishes()).dishes || []
      const reviews = []
      for (const dish of allDishes) {
        try {
          const revRes = await get(`/dishes/${dish.id}/reviews`)
          const mine = (revRes.reviews || []).filter(r => r.user_id === authStore.user?.id)
          reviews.push(...mine.map(r => ({ ...r, dish_name: dish.name })))
        } catch { /* skip */ }
      }
      myReviews.value = reviews.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    } catch { myReviews.value = [] }
  } catch (e) { console.error(e) }
})

function actionLabel(a) {
  const m = { order_payment: '下单', order_refund: '退款', admin_topup: '充值', admin_deduct: '扣减' }
  return m[a] || a
}
function fmt(iso) {
  if (!iso) return '-'
  const d = new Date(iso); const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
function goStoreIntro() { uni.navigateTo({ url: '/pages/store-intro/store-intro' }) }
function goAdmin() { uni.navigateTo({ url: '/pages/admin/dashboard/dashboard' }) }
function goOrders() { uni.switchTab({ url: '/pages/orders/orders' }) }
function goDiary() { uni.switchTab({ url: '/pages/diary/diary' }) }
function goWishes() { uni.navigateTo({ url: '/pages/wishes/wishes' }) }
function previewPhoto(p) {
  uni.previewImage({
    urls: diaryPhotos.value.map(pp => imgBase + pp.image_path),
    current: imgBase + p.image_path,
  })
}

async function changeAvatar() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['album', 'camera'],
    success: async (res) => {
      try {
        await uploadFile('/upload/avatar', res.tempFilePaths[0])
        await authStore.refreshProfile()
        uni.showToast({ title: '头像已更新', icon: 'success' })
      } catch (e) { uni.showToast({ title: '上传失败', icon: 'none' }) }
    },
  })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录', content: '确定退出吗？',
    success: (r) => { if (r.confirm) authStore.logout() },
  })
}
</script>

<style lang="scss" scoped>
.profile-page { min-height: 100vh; background: var(--bg-page, #FFF5F7); }

.profile-header { background: linear-gradient(180deg, var(--color-primary-light, #FFB3C6), #FFD6DF); padding: 60rpx 32rpx 40rpx; display: flex; flex-direction: column; align-items: center; }
.avatar-area { position: relative; width: 120rpx; height: 120rpx; border-radius: 50%; background: #FFF; display: flex; align-items: center; justify-content: center; margin-bottom: 14rpx; overflow: hidden; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1); }
.avatar-img { width: 100%; height: 100%; }
.avatar-emoji { font-size: 60rpx; }
.avatar-edit { position: absolute; bottom: -4rpx; right: -4rpx; width: 40rpx; height: 40rpx; border-radius: 50%; background: #FFF; display: flex; align-items: center; justify-content: center; font-size: 22rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1); }
.nickname { font-size: 36rpx; font-weight: 700; color: #FFF; }
.username-text { font-size: 22rpx; color: rgba(255,255,255,0.7); margin-top: 4rpx; }
.role-tag { font-size: 22rpx; color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.2); padding: 4rpx 20rpx; border-radius: 20rpx; margin-top: 10rpx; }

.balance-card { margin: -30rpx 24rpx 16rpx; background: linear-gradient(135deg,var(--color-primary, #FF7B93),var(--color-primary-light, #FFB3C6)); color: #FFF; text-align: center; padding: 32rpx; border-radius: 20rpx; box-shadow: 0 8rpx 24rpx rgba(255,123,147,0.3); }
.balance-label { font-size: 22rpx; opacity: 0.85; }
.balance-amount { font-size: 60rpx; font-weight: 700; display: block; margin-top: 6rpx; }
.balance-hint { font-size: 20rpx; opacity: 0.7; margin-top: 6rpx; display: block; }

.links-row { display: flex; padding: 0 24rpx; gap: 12rpx; margin-bottom: 16rpx; }
.link-item { flex: 1; background: #FFF; border-radius: 16rpx; padding: 24rpx 12rpx; text-align: center; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.link-icon { font-size: 40rpx; display: block; margin-bottom: 6rpx; }
.link-text { font-size: 22rpx; color: #888; }

.card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin: 0 24rpx 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.card-title { font-size: 26rpx; font-weight: 600; color: #4A4A4A; display: block; margin-bottom: 14rpx; }

.theme-grid { display: flex; gap: 16rpx; justify-content: center; }
.theme-dot { display: flex; flex-direction: column; align-items: center; gap: 6rpx; padding: 16rpx 20rpx; border-radius: 16rpx; }
.theme-dot.active { background: var(--bg-input, #FFF0F3); }
.theme-label { font-size: 20rpx; color: #888; }

.stats-mini { display: flex; gap: 12rpx; }
.smini-item { flex: 1; background: var(--bg-page, #FFF5F7); border-radius: 12rpx; padding: 16rpx; text-align: center; }
.smini-num { font-size: 32rpx; font-weight: 700; color: var(--color-primary, #FF7B93); display: block; }
.smini-label { font-size: 20rpx; color: #999; margin-top: 2rpx; display: block; }

.tab-row { display: flex; gap: 0; margin-bottom: 18rpx; }
.tab-item { flex: 1; text-align: center; padding: 14rpx 0; font-size: 26rpx; color: #999; border-bottom: 2rpx solid transparent; }
.tab-item.active { color: var(--color-primary, #FF7B93); font-weight: 600; border-bottom-color: var(--color-primary, #FF7B93); }

.photo-grid { display: flex; flex-wrap: wrap; gap: 8rpx; }
.photo-thumb { width: calc(33.33% - 6rpx); aspect-ratio: 1; border-radius: 8rpx; }
.view-all { text-align: center; display: block; padding: 16rpx 0 0; font-size: 24rpx; color: var(--color-primary, #FF7B93); }

.review-mini { padding: 14rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.review-mini:last-child { border-bottom: none; }
.rm-stars { font-size: 22rpx; margin-bottom: 4rpx; }
.rm-content { font-size: 24rpx; color: #4A4A4A; display: block; }
.rm-dish { font-size: 22rpx; color: #BBB; margin-top: 2rpx; display: block; }

.preview-row { display: flex; align-items: center; justify-content: space-between; }
.preview-icon { font-size: 32rpx; margin-right: 8rpx; }
.preview-text { font-size: 28rpx; font-weight: 600; color: #4A4A4A; }
.preview-num { font-size: 36rpx; font-weight: 700; color: #FF7B93; }
.preview-sub { font-size: 22rpx; color: #999; margin-left: 4rpx; }
.preview-arrow { font-size: 24rpx; color: #CCC; }

.badge-row { display: flex; flex-wrap: wrap; gap: 12rpx; }
.badge-item { width: calc(33.33% - 8rpx); background: #F5F5F5; border-radius: 12rpx; padding: 16rpx 12rpx; text-align: center; }
.badge-item.earned { background: var(--bg-page, #FFF5F7); border: 1rpx solid #FFD6DF; }
.badge-icon { font-size: 36rpx; display: block; margin-bottom: 4rpx; }
.badge-name { font-size: 22rpx; font-weight: 600; color: #4A4A4A; display: block; }
.badge-item.earned .badge-name { color: var(--color-primary, #FF7B93); }
.badge-desc { font-size: 18rpx; color: #CCC; display: block; }
.badge-item.earned .badge-desc { color: #AAA; }

.no-data { text-align: center; padding: 40rpx; color: #CCC; font-size: 24rpx; }
.no-logs { text-align: center; padding: 30rpx; color: #CCC; font-size: 24rpx; display: block; }
.log-item { display: flex; justify-content: space-between; align-items: center; padding: 12rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.log-item:last-child { border-bottom: none; }
.log-action { font-size: 26rpx; color: #4A4A4A; display: block; }
.log-time { font-size: 22rpx; color: #CCC; }
.log-amount { font-size: 26rpx; font-weight: 600; }
.log-amount.in { color: #7BC8A4; }
.log-amount.out { color: #FF6B6B; }

.logout-area { padding: 24rpx 24rpx; }
.logout-btn { background: #FFF; color: #999; border: 1rpx solid #E0E0E0; border-radius: 24rpx; font-size: 28rpx; padding: 20rpx; }
</style>
