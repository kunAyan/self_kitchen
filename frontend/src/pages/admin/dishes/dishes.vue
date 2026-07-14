<template>
  <view class="admin-dishes">
    <view class="page-header">
      <text class="page-title">🍽️ 菜品管理</text>
      <view class="header-right">
        <text v-if="selectedIds.length > 0" class="select-count">已选 {{ selectedIds.length }}</text>
        <text v-if="dishes.length > 0" class="select-all-btn" @click="toggleSelectAll">{{ selectAll ? '取消全选' : '全选' }}</text>
        <view class="add-btn" @click="goAdd"><text>+ 新增菜品</text></view>
      </view>
    </view>

    <view v-if="dishes.length === 0">
      <EmptyState icon="🍽️" text="还没有菜品" subText="点击上方按钮添加" />
    </view>

    <view v-else class="dish-list">
      <view v-for="dish in dishes" :key="dish.id" class="dish-row" :class="{ selected: selectedIds.includes(dish.id) }">
        <view class="dish-check" @click="toggleSelect(dish.id)">
          <text>{{ selectedIds.includes(dish.id) ? '☑️' : '⬜' }}</text>
        </view>
        <view class="dish-thumb" :style="{ backgroundColor: getColor(dish) }">
          <image v-if="dish.image" class="thumb-img" :src="uploadBase + dish.image" mode="aspectFill" />
          <text v-else class="thumb-emoji">{{ dish.category_icon || '🍽️' }}</text>
        </view>
        <view class="dish-detail">
          <text class="dish-name">{{ dish.name }}</text>
          <text class="dish-meta">{{ dish.category_name }} · ¥{{ (dish.price / 100).toFixed(2) }}</text>
        </view>
        <view class="dish-status" :class="{ off: !dish.is_available }">
          <text @click="toggleDish(dish)">{{ dish.is_available ? '上架中' : '已下架' }}</text>
        </view>
        <view class="dish-actions">
          <text @click="goEdit(dish)">✏️</text>
          <text @click="deleteDish(dish)">🗑️</text>
        </view>
      </view>
    </view>

    <!-- Batch action bar -->
    <view v-if="selectedIds.length > 0" class="batch-bar">
      <button class="batch-btn on" @click="batchAction('mark_available')">✅ 一键上架</button>
      <button class="batch-btn off" @click="batchAction('mark_unavailable')">🚫 一键下架</button>
      <button class="batch-btn clear" @click="selectedIds = []; selectAll = false">✕ 取消</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'
import { put } from '@/api/index'
import { UPLOAD_BASE } from '@/config'
import EmptyState from '@/components/EmptyState.vue'

const uploadBase = UPLOAD_BASE
const dishes = ref([])
const selectedIds = ref([])
const selectAll = ref(false)

onMounted(() => fetchDishes())

async function fetchDishes() {
  try { const res = await adminAPI.getDishes(); dishes.value = res.dishes } catch (e) { console.error(e) }
}

function getColor(dish) {
  const colors = { '🍝': '#FFE4C4', '🥤': '#D4EFFF', '🍰': '#FFE0EC', '🥗': '#E8F8E0', '🍜': '#FFE8D6' }
  return colors[dish.category_icon] || '#FFF0F3'
}

function goAdd() { uni.navigateTo({ url: '/pages/admin/dish-form/dish-form' }) }
function goEdit(dish) { uni.navigateTo({ url: `/pages/admin/dish-form/dish-form?id=${dish.id}` }) }

function toggleSelect(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
  selectAll.value = selectedIds.value.length === dishes.value.length
}

function toggleSelectAll() {
  if (selectAll.value) { selectedIds.value = []; selectAll.value = false }
  else { selectedIds.value = dishes.value.map(d => d.id); selectAll.value = true }
}

async function toggleDish(dish) {
  try {
    await adminAPI.updateDish(dish.id, { is_available: !dish.is_available })
    uni.showToast({ title: dish.is_available ? '已下架' : '已上架', icon: 'success' })
    fetchDishes()
  } catch (e) { uni.showToast({ title: '操作失败', icon: 'none' }) }
}

async function batchAction(action) {
  uni.showModal({
    title: '确认批量操作',
    content: `确定对 ${selectedIds.value.length} 个菜品执行此操作吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          const result = await put('/admin/dishes/batch', { ids: selectedIds.value, action })
          uni.showToast({ title: result.msg || '操作成功', icon: 'success' })
          selectedIds.value = []; selectAll.value = false
          fetchDishes()
        } catch (e) { uni.showToast({ title: e.msg || '操作失败', icon: 'none' }) }
      }
    },
  })
}

async function deleteDish(dish) {
  uni.showModal({
    title: '确认删除', content: `确定删除「${dish.name}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try { await adminAPI.deleteDish(dish.id); uni.showToast({ title: '已删除', icon: 'success' }); fetchDishes() }
        catch (e) { uni.showToast({ title: e.msg || '删除失败', icon: 'none' }) }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.admin-dishes { min-height: 100vh; background: #FFF5F7; padding: 24rpx 24rpx 120rpx; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; flex-wrap: wrap; gap: 12rpx; }
.page-title { font-size: 32rpx; font-weight: 700; color: #4A4A4A; }
.header-right { display: flex; align-items: center; gap: 12rpx; }
.select-count { font-size: 24rpx; color: #FF7B93; font-weight: 600; }
.select-all-btn { font-size: 24rpx; color: #7EC8E3; padding: 8rpx 16rpx; }
.add-btn { background: linear-gradient(135deg, #FF7B93, #FFB3C6); color: #FFF; font-size: 24rpx; padding: 12rpx 28rpx; border-radius: 24rpx; font-weight: 600; }

.dish-list { background: #FFF; border-radius: 16rpx; overflow: hidden; }
.dish-row { display: flex; align-items: center; padding: 20rpx; border-bottom: 1rpx solid #F5F5F5; gap: 12rpx; }
.dish-row:last-child { border-bottom: none; }
.dish-row.selected { background: #FFF5F7; }
.dish-check { font-size: 36rpx; padding: 4rpx; flex-shrink: 0; }
.dish-thumb { width: 70rpx; height: 70rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; overflow: hidden; }
.thumb-img { width: 100%; height: 100%; border-radius: 12rpx; }
.thumb-emoji { font-size: 36rpx; }
.dish-detail { flex: 1; overflow: hidden; }
.dish-name { font-size: 26rpx; font-weight: 600; color: #4A4A4A; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dish-meta { font-size: 22rpx; color: #AAA; }
.dish-status { font-size: 20rpx; color: #7BC8A4; background: #E8F5E9; padding: 4rpx 12rpx; border-radius: 12rpx; }
.dish-status.off { color: #999; background: #F5F5F5; }
.dish-actions { display: flex; gap: 12rpx; font-size: 28rpx; }

.batch-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #FFF; padding: 16rpx 24rpx; padding-bottom: calc(16rpx + env(safe-area-inset-bottom)); box-shadow: 0 -2rpx 12rpx rgba(0,0,0,0.08); display: flex; gap: 12rpx; z-index: 50; }
.batch-btn { flex: 1; text-align: center; padding: 18rpx; border-radius: 24rpx; font-size: 26rpx; border: none; font-weight: 600; }
.batch-btn.on { background: #E8F5E9; color: #4CAF50; }
.batch-btn.off { background: #FFEBEE; color: #F44336; }
.batch-btn.clear { flex: none; background: #F5F5F5; color: #999; padding: 18rpx 24rpx; }
</style>
