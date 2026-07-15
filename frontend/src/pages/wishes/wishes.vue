<template>
  <view class="wishes-page">
    <view class="page-header">
      <text class="page-title">🌟 许愿池</text>
    </view>

    <!-- Category Tabs -->
    <view class="cat-tabs">
      <view class="cat-tab" :class="{ active: category === 'dish' }" @click="category = 'dish'; fetchWishes()">🍽️ 菜品许愿</view>
      <view class="cat-tab" :class="{ active: category === 'free' }" @click="category = 'free'; fetchWishes()">💫 自由愿望</view>
    </view>

    <!-- Status Tabs -->
    <view class="tab-bar">
      <view class="tab" :class="{ active: tab === 'pending' }" @click="tab = 'pending'">🙏 许愿中 ({{ pendingWishes.length }})</view>
      <view class="tab" :class="{ active: tab === 'fulfilled' }" @click="tab = 'fulfilled'">✅ 已实现 ({{ fulfilledWishes.length }})</view>
    </view>

    <!-- Pending wishes -->
    <view v-if="tab === 'pending'">
      <view v-if="pendingWishes.length === 0" class="empty">
        <text class="empty-icon">🌟</text>
        <text class="empty-text">{{ category === 'dish' ? '还没有菜品愿望，快来许第一个愿吧~' : '还没有自由愿望，写下一个吧~' }}</text>
      </view>
      <view v-for="w in pendingWishes" :key="w.id" class="wish-card" :class="'priority-' + w.priority">
        <view class="wc-priority-bar"></view>
        <view class="wc-main">
          <view class="wc-top">
            <view class="wc-body">
              <view class="wc-title-row">
                <text class="wc-type-icon">{{ category === 'dish' ? '🍽️' : '💫' }}</text>
                <text class="wc-title">{{ w.title }}</text>
              </view>
              <text class="wc-desc" v-if="w.description">"{{ w.description }}"</text>
              <text class="wc-meta">{{ w.user_nickname }} · {{ fmt(w.created_at) }} · {{ prioLabel(w.priority) }}</text>
            </view>
          </view>
          <view class="wc-actions">
            <text v-if="w.user_id === authStore.user?.id || authStore.isAdmin" class="wc-del" @click="doDelete(w)">🗑️</text>
            <text v-if="authStore.isAdmin" class="wc-fulfill" @click="doFulfill(w)">✨ 实现</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Fulfilled wishes -->
    <view v-if="tab === 'fulfilled'">
      <view v-if="fulfilledWishes.length === 0" class="empty">
        <text class="empty-text">还没有实现的愿望</text>
      </view>
      <view v-for="w in fulfilledWishes" :key="w.id" class="wish-card fulfilled">
        <view class="wc-priority-bar done"></view>
        <view class="wc-main">
          <view class="wc-body">
            <view class="wc-title-row">
              <text class="wc-type-icon">✅</text>
              <text class="wc-title done">{{ w.title }}</text>
            </view>
            <text class="wc-desc" v-if="w.description">"{{ w.description }}"</text>
            <text class="wc-meta">{{ w.user_nickname }} · {{ fmt(w.created_at) }}</text>
            <text class="wc-fulfill-note" v-if="w.fulfill_note">👨‍🍳 {{ w.fulfill_note }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Floating add button -->
    <view class="float-btn" @click="showAdd = true"><text>+</text></view>

    <!-- Add wish modal -->
    <view v-if="showAdd" class="modal-overlay" @click="showAdd = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">{{ category === 'dish' ? '🍽️ 想吃什么？' : '💫 许个愿吧' }}</text>
        <input class="modal-input" v-model="newTitle" :placeholder="category === 'dish' ? '想吃什么菜？' : '写下你的愿望...'" maxlength="50" style="width:100%;height:80rpx;line-height:80rpx;padding:0 20rpx;box-sizing:border-box;" />
        <textarea class="modal-textarea" v-model="newDesc" placeholder="描述一下（选填）" maxlength="200" style="width:100%;height:120rpx;padding:16rpx 20rpx;box-sizing:border-box;" />
        <view class="priority-row">
          <text class="priority-label">优先级</text>
          <view class="priority-chips">
            <text class="pchip" :class="{ active: priority === 3 }" @click="priority = 3">🔥超想</text>
            <text class="pchip" :class="{ active: priority === 2 }" @click="priority = 2">😋想吃</text>
            <text class="pchip" :class="{ active: priority === 1 }" @click="priority = 1">🤔随便</text>
          </view>
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
        <input class="modal-input" v-model="fulfillNote" placeholder="说点什么（选填）" maxlength="100" style="width:100%;height:80rpx;line-height:80rpx;padding:0 20rpx;box-sizing:border-box;" />
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
const category = ref('dish')
const showAdd = ref(false)
const showFulfill = ref(false)
const newTitle = ref('')
const newDesc = ref('')
const priority = ref(2)
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
  try {
    const res = await get('/wishes', { category: category.value })
    wishes.value = res.wishes || []
  } catch (e) { console.error(e) }
}

function prioLabel(p) { const m = { 3: '🔥超想', 2: '😋想吃', 1: '🤔随便' }; return m[p] || '' }

function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso); const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())}`
}

async function submitWish() {
  if (!newTitle.value.trim()) { uni.showToast({ title: '请输入内容', icon: 'none' }); return }
  saving.value = true
  try {
    await post('/wishes', {
      title: newTitle.value.trim(),
      description: newDesc.value.trim(),
      category: category.value,
      priority: priority.value,
    })
    uni.showToast({ title: '许愿成功！', icon: 'success' })
    showAdd.value = false; newTitle.value = ''; newDesc.value = ''; priority.value = 2
    fetchWishes()
  } catch (e) { uni.showToast({ title: e.msg || '失败', icon: 'none' }) }
  finally { saving.value = false }
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
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.page-title { font-size: 36rpx; font-weight: 700; color: #4A4A4A; }

.cat-tabs { display: flex; gap: 12rpx; margin-bottom: 12rpx; }
.cat-tab { flex: 1; text-align: center; padding: 18rpx; font-size: 26rpx; font-weight: 600; color: #999; background: #FFF; border-radius: 14rpx; }
.cat-tab.active { color: #FF7B93; background: #FFF0F3; }

.tab-bar { display: flex; background: #FFF; border-radius: 16rpx; margin-bottom: 16rpx; overflow: hidden; }
.tab { flex: 1; text-align: center; padding: 20rpx; font-size: 26rpx; color: #999; }
.tab.active { color: #FF7B93; font-weight: 700; background: #FFF5F7; }

.empty { text-align: center; padding: 80rpx 40rpx; }
.empty-icon { font-size: 64rpx; display: block; margin-bottom: 16rpx; }
.empty-text { font-size: 28rpx; color: #CCC; }

/* Wish card */
.wish-card { display: flex; background: #FFF; border-radius: 16rpx; margin-bottom: 12rpx; overflow: hidden; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.wish-card.fulfilled { opacity: 0.7; }
.wc-priority-bar { width: 8rpx; flex-shrink: 0; background: #E0E0E0; }
.wish-card.priority-3 .wc-priority-bar { background: #FF6B6B; }
.wish-card.priority-2 .wc-priority-bar { background: #FFB347; }
.wish-card.priority-1 .wc-priority-bar { background: #E0E0E0; }
.wc-priority-bar.done { background: #4CAF50; }

.wc-main { flex: 1; padding: 20rpx; display: flex; justify-content: space-between; align-items: flex-start; min-width: 0; }
.wc-body { min-width: 0; flex: 1; }
.wc-title-row { display: flex; align-items: center; gap: 6rpx; margin-bottom: 4rpx; }
.wc-type-icon { font-size: 28rpx; flex-shrink: 0; }
.wc-title { font-size: 28rpx; font-weight: 600; color: #4A4A4A; }
.wc-title.done { text-decoration: line-through; color: #999; }
.wc-desc { font-size: 24rpx; color: #888; display: block; margin-top: 4rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wc-meta { font-size: 22rpx; color: #CCC; margin-top: 6rpx; display: block; }
.wc-fulfill-note { font-size: 22rpx; color: #FF7B93; margin-top: 4rpx; display: block; }

.wc-actions { display: flex; align-items: center; gap: 8rpx; flex-shrink: 0; margin-left: 12rpx; }
.wc-del { font-size: 28rpx; padding: 4rpx; color: #CCC; }
.wc-fulfill { font-size: 24rpx; color: #FFF; background: linear-gradient(135deg,#FF7B93,#FFB3C6); padding: 8rpx 16rpx; border-radius: 20rpx; font-weight: 600; white-space: nowrap; }

/* Priority chips in modal */
.priority-row { display: flex; align-items: center; gap: 12rpx; padding: 12rpx 0; margin-bottom: 12rpx; }
.priority-label { font-size: 24rpx; color: #888; }
.priority-chips { display: flex; gap: 8rpx; }
.pchip { font-size: 24rpx; padding: 8rpx 16rpx; border-radius: 16rpx; background: #F5F5F5; color: #999; }
.pchip.active { background: #FFF0F3; color: #FF7B93; font-weight: 600; }

/* Float button */
.float-btn { position: fixed; bottom: 40rpx; right: 24rpx; width: 96rpx; height: 96rpx; border-radius: 50%; background: linear-gradient(135deg,#FF7B93,#FFB3C6); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(255,123,147,0.4); z-index: 50; }
.float-btn text { font-size: 48rpx; color: #FFF; font-weight: 300; }

/* Modal */
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
