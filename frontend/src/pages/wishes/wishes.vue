<template>
  <view class="wishes-page">
    <view class="page-header">
      <text class="page-title">🌟 许愿池</text>
      <view class="coins-badge">🪙 x{{ authStore.user?.wish_coins || 0 }}</view>
    </view>

    <!-- Tabs -->
    <view class="tab-bar">
      <view class="tab" :class="{ active: tab === 'pending' }" @click="tab = 'pending'">🙏 许愿中 ({{ pendingWishes.length }})</view>
      <view class="tab" :class="{ active: tab === 'fulfilled' }" @click="tab = 'fulfilled'">✅ 已实现 ({{ fulfilledWishes.length }})</view>
    </view>

    <!-- Pending wishes -->
    <view v-if="tab === 'pending'">
      <view v-if="pendingWishes.length === 0" class="empty">还没有愿望，快来许第一个愿吧~</view>
      <view v-for="w in pendingWishes" :key="w.id" class="wish-card">
        <view class="wc-left">
          <text class="wc-icon">🙏</text>
          <view class="wc-body">
            <text class="wc-title">{{ w.title }}</text>
            <text class="wc-desc" v-if="w.description">{{ w.description }}</text>
            <text class="wc-meta">{{ w.is_anonymous ? '🎁神秘食客' : w.user_nickname }} · {{ fmt(w.created_at) }}</text>
          </view>
        </view>
        <view class="wc-right">
          <view class="coin-btn" @click="doCoin(w)"><text>🪙</text><text class="coin-num">{{ w.coins || 0 }}</text></view>
          <view class="like-btn" @click="doLike(w)"><text>👍</text><text class="like-num">{{ w.likes || 0 }}</text></view>
          <text v-if="authStore.isAdmin && w.status==='pending'" class="fulfill-btn" @click="doFulfill(w)">✨实现</text>
          <text v-if="w.user_id === authStore.user?.id || authStore.isAdmin" class="del-btn" @click="doDelete(w)">🗑️</text>
        </view>
      </view>
    </view>

    <!-- Fulfilled wishes -->
    <view v-if="tab === 'fulfilled'">
      <view v-if="fulfilledWishes.length === 0" class="empty">还没有实现的愿望</view>
      <view v-for="w in fulfilledWishes" :key="w.id" class="wish-card fulfilled">
        <view class="wc-left">
          <text class="wc-icon">✅</text>
          <view class="wc-body">
            <text class="wc-title">{{ w.title }}</text>
            <text class="wc-desc" v-if="w.description">{{ w.description }}</text>
            <text class="wc-meta">{{ w.user_nickname }} · {{ fmt(w.created_at) }}</text>
            <text class="wc-fulfill-note" v-if="w.fulfill_note">👨‍🍳 {{ w.fulfill_note }}</text>
          </view>
        </view>
        <view class="wc-right">
          <text class="like-num-static">👍{{ w.likes || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- Floating add button -->
    <view class="float-btn" @click="showAdd = true"><text>+</text></view>

    <!-- Add wish modal -->
    <view v-if="showAdd" class="modal-overlay" @click="showAdd = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">🌟 许个愿吧</text>
        <input class="modal-input" v-model="newTitle" placeholder="想吃什么菜？" maxlength="50" />
        <textarea class="modal-textarea" v-model="newDesc" placeholder="描述一下（选填）" maxlength="200" />
        <view class="anon-row" @click="isAnon = !isAnon">
          <text>{{ isAnon ? '🎁' : '👤' }}</text>
          <text class="anon-label">{{ isAnon ? '匿名许愿（大厨实现后揭晓）' : '公开许愿' }}</text>
        </view>
        <view class="modal-btns">
          <button class="mbtn cancel" @click="showAdd = false">取消</button>
          <button class="mbtn confirm" :loading="saving" @click="submitWish">许愿</button>
        </view>
      </view>
    </view>

    <!-- Fulfill modal (admin) -->
    <view v-if="showFulfill" class="modal-overlay" @click="showFulfill = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">✨ 实现愿望</text>
        <text class="fulfill-name">「{{ fulfillTarget?.title }}」</text>
        <input class="modal-input" v-model="fulfillNote" placeholder="说点什么（选填）" maxlength="100" />
        <view class="modal-btns">
          <button class="mbtn cancel" @click="showFulfill = false">取消</button>
          <button class="mbtn confirm" :loading="saving" @click="confirmFulfill">实现</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { get, post, put, del } from '@/api/index'

const authStore = useAuthStore()
const wishes = ref([])
const tab = ref('pending')
const showAdd = ref(false)
const showFulfill = ref(false)
const newTitle = ref('')
const newDesc = ref('')
const isAnon = ref(false)
const fulfillTarget = ref(null)
const fulfillNote = ref('')
const saving = ref(false)

const pendingWishes = computed(() => wishes.value.filter(w => w.status === 'pending'))
const fulfilledWishes = computed(() => wishes.value.filter(w => w.status === 'fulfilled'))

onMounted(async () => {
  await authStore.refreshProfile().catch(() => {})
  fetchWishes()
})

async function fetchWishes() {
  try { const res = await get('/wishes'); wishes.value = res.wishes || [] } catch (e) { console.error(e) }
}

function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso); const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())}`
}

async function submitWish() {
  if (!newTitle.value.trim()) { uni.showToast({ title: '请输入菜名', icon: 'none' }); return }
  saving.value = true
  try {
    await post('/wishes', { title: newTitle.value.trim(), description: newDesc.value.trim(), is_anonymous: isAnon.value })
    uni.showToast({ title: '许愿成功！', icon: 'success' })
    showAdd.value = false; newTitle.value = ''; newDesc.value = ''; isAnon.value = false
    fetchWishes()
    authStore.refreshProfile()
  } catch (e) { uni.showToast({ title: e.msg || '失败', icon: 'none' }) }
  finally { saving.value = false }
}

async function doLike(w) {
  try { await post(`/wishes/${w.id}/like`); w.likes = (w.likes || 0) + 1 } catch (e) {}
}

async function doCoin(w) {
  if ((authStore.user?.wish_coins || 0) <= 0) {
    uni.showToast({ title: '许愿币不足！下月重置', icon: 'none' })
    return
  }
  try {
    const res = await post(`/wishes/${w.id}/coin`)
    w.coins = res.wish.coins
    authStore.user.wish_coins = res.coins_left
    uni.showToast({ title: '投币成功！', icon: 'success' })
  } catch (e) { uni.showToast({ title: e.msg || '投币失败', icon: 'none' }) }
}

function doFulfill(w) { fulfillTarget.value = w; fulfillNote.value = ''; showFulfill.value = true }

async function confirmFulfill() {
  saving.value = true
  try {
    await put(`/admin/wishes/${fulfillTarget.value.id}/fulfill`, { note: fulfillNote.value.trim() })
    uni.showToast({ title: '已实现！', icon: 'success' })
    showFulfill.value = false; fulfillTarget.value = null
    fetchWishes()
  } catch (e) { uni.showToast({ title: e.msg || '失败', icon: 'none' }) }
  finally { saving.value = false }
}

function doDelete(w) {
  uni.showModal({
    title: '删除愿望', content: `确定删除「${w.title}」吗？`,
    success: async (r) => {
      if (r.confirm) {
        try { await del(`/wishes/${w.id}`); fetchWishes() } catch (e) { uni.showToast({ title: '删除失败', icon: 'none' }) }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.wishes-page { min-height: 100vh; background: #FFF5F7; padding: 24rpx 24rpx 120rpx; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.page-title { font-size: 36rpx; font-weight: 700; color: #4A4A4A; }

.tab-bar { display: flex; background: #FFF; border-radius: 16rpx; margin-bottom: 16rpx; overflow: hidden; }
.tab { flex: 1; text-align: center; padding: 20rpx; font-size: 26rpx; color: #999; }
.tab.active { color: #FF7B93; font-weight: 700; background: #FFF5F7; }

.empty { text-align: center; padding: 80rpx 40rpx; color: #CCC; font-size: 28rpx; }

.wish-card { display: flex; justify-content: space-between; align-items: center; background: #FFF; border-radius: 16rpx; padding: 20rpx; margin-bottom: 12rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.wish-card.fulfilled { opacity: 0.75; }
.wc-left { display: flex; gap: 12rpx; flex: 1; min-width: 0; }
.wc-icon { font-size: 36rpx; flex-shrink: 0; }
.wc-body { min-width: 0; }
.wc-title { font-size: 28rpx; font-weight: 600; color: #4A4A4A; display: block; }
.wc-desc { font-size: 24rpx; color: #888; margin-top: 4rpx; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wc-meta { font-size: 22rpx; color: #CCC; margin-top: 4rpx; display: block; }
.wc-fulfill-note { font-size: 22rpx; color: #FF7B93; margin-top: 4rpx; display: block; }
.wc-right { display: flex; flex-direction: column; align-items: flex-end; gap: 8rpx; flex-shrink: 0; margin-left: 12rpx; }
.coins-badge { font-size: 26rpx; font-weight: 600; color: #FF7B93; background: #FFF0F3; padding: 8rpx 20rpx; border-radius: 20rpx; }
.coin-btn { display: flex; align-items: center; gap: 2rpx; padding: 4rpx 8rpx; background: #FFF8E1; border-radius: 12rpx; margin-bottom: 4rpx; }
.coin-num { font-size: 22rpx; color: #F9A825; font-weight: 600; }
.like-btn { display: flex; align-items: center; gap: 4rpx; padding: 4rpx 8rpx; background: #F5F5F5; border-radius: 12rpx; }
.like-num { font-size: 22rpx; color: #888; }
.anon-row { display: flex; align-items: center; gap: 8rpx; padding: 12rpx 0; margin-bottom: 12rpx; }
.anon-label { font-size: 24rpx; color: #888; }
.like-num-static { font-size: 22rpx; color: #BBB; }
.fulfill-btn { font-size: 24rpx; color: #FF7B93; font-weight: 600; padding: 4rpx 12rpx; background: #FFF0F3; border-radius: 12rpx; }
.del-btn { font-size: 24rpx; padding: 4rpx; }

.float-btn { position: fixed; bottom: 40rpx; right: 24rpx; width: 96rpx; height: 96rpx; border-radius: 50%; background: linear-gradient(135deg,#FF7B93,#FFB3C6); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(255,123,147,0.4); z-index: 50; }
.float-btn text { font-size: 48rpx; color: #FFF; font-weight: 300; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { width: 600rpx; background: #FFF; border-radius: 24rpx; padding: 40rpx; }
.modal-title { font-size: 32rpx; font-weight: 600; text-align: center; display: block; margin-bottom: 20rpx; }
.fulfill-name { font-size: 26rpx; color: #FF7B93; text-align: center; display: block; margin-bottom: 16rpx; }
.modal-input { background: #FFF5F7; border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 28rpx; margin-bottom: 16rpx; width: 100%; box-sizing: border-box; }
.modal-textarea { background: #FFF5F7; border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 26rpx; height: 120rpx; margin-bottom: 20rpx; width: 100%; box-sizing: border-box; }
.modal-btns { display: flex; gap: 12rpx; }
.mbtn { flex: 1; padding: 18rpx; border-radius: 24rpx; font-size: 28rpx; border: none; }
.mbtn.cancel { background: #F5F5F5; color: #999; }
.mbtn.confirm { background: linear-gradient(135deg,#FF7B93,#FFB3C6); color: #FFF; }
</style>
