<template>
  <view class="admin-user">
    <view class="page-header"><text class="page-title">💳 用户管理</text></view>

    <!-- Customer list -->
    <view v-if="!selectedUser" class="card">
      <text class="card-title">选择用户</text>
      <view v-for="u in users" :key="u.id" class="user-row" @click="selectUser(u)">
        <text class="u-icon">👤</text>
        <view class="u-info"><text class="u-name">{{ u.nickname }}</text><text class="u-user">@{{ u.username }}</text></view>
        <text class="u-balance">¥{{ (u.balance / 100).toFixed(2) }}</text>
        <text class="u-arrow">→</text>
      </view>
    </view>

    <!-- Selected user detail -->
    <view v-if="selectedUser">
      <view class="back-row" @click="selectedUser = null"><text>← 返回列表</text></view>

      <view class="user-card">
        <text class="user-nickname">{{ selectedUser.nickname }}</text>
        <text class="user-username">@{{ selectedUser.username }}</text>
        <view class="balance-display">
          <text class="bal-label">当前余额</text>
          <text class="bal-value">¥{{ displayBalance }}</text>
        </view>
      </view>

      <!-- Adjust balance -->
      <view class="card">
        <text class="card-title">调整余额（元）</text>
        <view class="adjust-row">
          <view class="adj-type" :class="{ active: adjType === 'add' }" @click="adjType = 'add'"><text>➕ 充值</text></view>
          <view class="adj-type" :class="{ active: adjType === 'deduct' }" @click="adjType = 'deduct'"><text>➖ 扣减</text></view>
        </view>
        <view class="quick-chips">
          <view v-for="a in quickAmounts" :key="a" class="chip" :class="{ sel: adjAmount === a }" @click="adjAmount = a"><text>¥{{ a }}</text></view>
        </view>
        <view class="custom-row">
          <input class="adj-input" v-model="customAdj" type="digit" placeholder="自定义金额" placeholder-style="color:#CCC" />
          <button class="adj-btn add" v-if="adjType === 'add'" :loading="adjusting" @click="doAdjust">确认充值</button>
          <button class="adj-btn deduct" v-else :loading="adjusting" @click="doAdjust">确认扣减</button>
        </view>
      </view>

      <!-- Edit user -->
      <view class="card">
        <text class="card-title">编辑信息</text>
        <input class="info-input" v-model="editNickname" placeholder="昵称" />
        <input class="info-input" v-model="editPassword" placeholder="新密码（留空不修改）" type="password" />
        <button class="save-info-btn" @click="saveUser">保存信息</button>
      </view>

      <!-- Logs -->
      <view class="card">
        <text class="card-title">变动记录</text>
        <view v-for="log in logs" :key="log.id" class="log-row">
          <view class="log-l"><text class="log-act">{{ actionLabel(log.action) }}</text><text class="log-t">{{ fmt(log.created_at) }}</text></view>
          <text class="log-amt" :class="log.amount >= 0 ? 'in' : 'out'">{{ log.amount >= 0 ? '+' : '' }}¥{{ (Math.abs(log.amount) / 100).toFixed(2) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { get, put } from '@/api/index'

const users = ref([])
const selectedUser = ref(null)
const logs = ref([])
const adjType = ref('add')
const adjAmount = ref(50)
const customAdj = ref('')
const adjusting = ref(false)
const editNickname = ref('')
const editPassword = ref('')
const quickAmounts = [10, 20, 50, 100, 200]

const displayBalance = computed(() => {
  if (!selectedUser.value) return '0.00'
  return ((selectedUser.value.balance || 0) / 100).toFixed(2)
})

onLoad(async (opts) => {
  try {
    const res = await get('/admin/users')
    users.value = res.users || []
    if (opts.id) {
      const u = users.value.find(u => u.id === parseInt(opts.id))
      if (u) selectUser(u)
    }
  } catch (e) { console.error(e) }
})

async function selectUser(u) {
  selectedUser.value = u
  editNickname.value = u.nickname
  editPassword.value = ''
  try {
    const res = await get(`/admin/users/${u.id}`)
    logs.value = res.balance_logs || []
  } catch (e) { console.error(e) }
}

async function doAdjust() {
  const raw = customAdj.value ? parseFloat(customAdj.value) : adjAmount.value
  if (!raw || raw <= 0) { uni.showToast({ title: '请输入金额', icon: 'none' }); return }
  let amount = Math.round(raw * 100)
  if (adjType.value === 'deduct') amount = -amount

  adjusting.value = true
  try {
    const res = await put(`/admin/users/${selectedUser.value.id}/balance`, { amount })
    selectedUser.value = res.user
    customAdj.value = ''
    uni.showToast({ title: res.msg || '操作成功', icon: 'success' })
    const detail = await get(`/admin/users/${selectedUser.value.id}`)
    logs.value = detail.balance_logs || []
  } catch (e) { uni.showToast({ title: e.msg || '操作失败', icon: 'none' }) }
  finally { adjusting.value = false }
}

async function saveUser() {
  try {
    const data = {}
    if (editNickname.value.trim()) data.nickname = editNickname.value.trim()
    if (editPassword.value.trim()) data.password = editPassword.value.trim()
    if (Object.keys(data).length === 0) { uni.showToast({ title: '无修改', icon: 'none' }); return }
    const res = await put(`/admin/users/${selectedUser.value.id}`, data)
    selectedUser.value = res.user
    editPassword.value = ''
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch (e) { uni.showToast({ title: e.msg || '保存失败', icon: 'none' }) }
}

function actionLabel(a) {
  const m = { order_payment: '下单', order_refund: '退款', admin_topup: '充值', admin_deduct: '扣减' }
  return m[a] || a
}
function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso); const p = n => String(n).padStart(2, '0')
  return `${d.getMonth()+1}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
</script>

<style lang="scss" scoped>
.admin-user { min-height: 100vh; background: #FFF5F7; padding: 24rpx; }
.page-header { margin-bottom: 20rpx; }
.page-title { font-size: 32rpx; font-weight: 700; color: #4A4A4A; }

.card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.card-title { font-size: 26rpx; font-weight: 600; color: #4A4A4A; display: block; margin-bottom: 14rpx; }
.back-row { padding: 12rpx 0; color: #FF7B93; font-size: 26rpx; }

.user-row { display: flex; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.user-row:last-child { border-bottom: none; }
.u-icon { font-size: 36rpx; margin-right: 12rpx; }
.u-info { flex: 1; }
.u-name { font-size: 28rpx; font-weight: 600; }
.u-user { font-size: 22rpx; color: #AAA; }
.u-balance { font-size: 28rpx; font-weight: 700; color: #FF7B93; margin-right: 8rpx; }
.u-arrow { color: #CCC; }

.user-card { background: linear-gradient(135deg,#FF7B93,#FFB3C6); border-radius: 20rpx; padding: 32rpx; text-align: center; margin-bottom: 16rpx; }
.user-nickname { font-size: 36rpx; font-weight: 700; color: #FFF; display: block; }
.user-username { font-size: 24rpx; color: rgba(255,255,255,0.7); }
.balance-display { margin-top: 20rpx; }
.bal-label { font-size: 22rpx; color: rgba(255,255,255,0.7); }
.bal-value { font-size: 56rpx; font-weight: 700; color: #FFF; display: block; }

.adjust-row { display: flex; gap: 12rpx; margin-bottom: 16rpx; }
.adj-type { flex: 1; text-align: center; padding: 16rpx; border-radius: 12rpx; background: #F5F5F5; font-size: 26rpx; }
.adj-type.active.add { background: #E8F5E9; color: #4CAF50; font-weight: 600; }
.adj-type.active.deduct { background: #FFEBEE; color: #F44336; font-weight: 600; }

.quick-chips { display: flex; flex-wrap: wrap; gap: 10rpx; margin-bottom: 16rpx; }
.chip { padding: 10rpx 24rpx; border-radius: 20rpx; background: #F5F5F5; font-size: 24rpx; color: #888; }
.chip.sel { background: #FFF0F3; color: #FF7B93; font-weight: 600; border: 2rpx solid #FF7B93; }

.custom-row { display: flex; gap: 12rpx; }
.adj-input { flex: 1; height: 80rpx; background: #FFF5F7; border-radius: 12rpx; padding: 0 20rpx; font-size: 28rpx; }
.adj-btn { color: #FFF; border-radius: 24rpx; padding: 16rpx 32rpx; font-size: 26rpx; border: none; white-space: nowrap; }
.adj-btn.add { background: linear-gradient(135deg,#7BC8A4,#8FD4B4); }
.adj-btn.deduct { background: linear-gradient(135deg,#FF6B6B,#FF8A8A); }

.info-input { height: 80rpx; background: #FFF5F7; border-radius: 12rpx; padding: 0 20rpx; font-size: 26rpx; margin-bottom: 12rpx; }
.save-info-btn { background: linear-gradient(135deg,#FF7B93,#FFB3C6); color: #FFF; border-radius: 24rpx; padding: 18rpx; font-size: 28rpx; border: none; }

.log-row { display: flex; justify-content: space-between; align-items: center; padding: 14rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.log-row:last-child { border-bottom: none; }
.log-act { font-size: 26rpx; color: #4A4A4A; display: block; }
.log-t { font-size: 22rpx; color: #CCC; }
.log-amt { font-size: 26rpx; font-weight: 600; }
.log-amt.in { color: #7BC8A4; }
.log-amt.out { color: #FF6B6B; }
</style>
