<template>
  <view class="special-dates-page">
    <view class="page-header">
      <text class="page-title">💝 纪念日管理</text>
      <view class="add-btn" @click="openCreate">
        <text>+ 新增纪念日</text>
      </view>
    </view>

    <view v-if="dates.length === 0">
      <EmptyState icon="💝" text="还没有纪念日" subText="点击上方按钮添加" />
    </view>

    <view v-else class="date-list">
      <view v-for="item in dates" :key="item.id" class="date-item">
        <text class="date-icon">{{ item.icon }}</text>
        <view class="date-info">
          <view class="date-title-row">
            <text class="date-title">{{ item.title }}</text>
            <text v-if="item.repeat_yearly" class="repeat-badge">每年重复</text>
          </view>
          <text class="date-value">{{ item.date }}</text>
        </view>
        <view class="date-actions">
          <text class="date-action" @click="openEdit(item)">✏️</text>
          <text class="date-action" @click="confirmDelete(item)">🗑️</text>
        </view>
      </view>
    </view>

    <!-- Add/Edit Modal -->
    <view v-if="showModal" class="modal-overlay" @click="closeModal">
      <view class="modal-card" @click.stop>
        <text class="modal-title">{{ isEditing ? '编辑纪念日' : '新增纪念日' }}</text>

        <!-- Title -->
        <input
          class="cute-input"
          v-model="form.title"
          placeholder="纪念日名称"
          placeholder-style="color:#CCC"
          maxlength="30"
        />

        <!-- Date -->
        <input
          class="cute-input"
          v-model="form.date"
          placeholder="日期 (YYYY-MM-DD)"
          placeholder-style="color:#CCC"
        />

        <!-- Emoji icon picker -->
        <view class="emoji-section">
          <text class="picker-label">图标</text>
          <view class="emoji-list">
            <text
              v-for="e in emojiOptions"
              :key="e"
              class="emoji-opt"
              :class="{ selected: form.icon === e }"
              @click="form.icon = e"
            >{{ e }}</text>
          </view>
        </view>

        <!-- Repeat yearly toggle -->
        <view class="toggle-section">
          <text class="picker-label">每年重复</text>
          <switch
            :checked="form.repeat_yearly"
            @change="form.repeat_yearly = $event.detail.value"
            color="#FF7B93"
          />
        </view>

        <view class="modal-actions">
          <button class="modal-btn cancel" @click="closeModal">取消</button>
          <button class="modal-btn confirm" :loading="saving" @click="saveDate">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '@/api/index'
import EmptyState from '@/components/EmptyState.vue'

const dates = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const editId = ref(null)
const saving = ref(false)

const form = reactive({
  title: '',
  date: '',
  icon: '',
  repeat_yearly: false,
})

const defaultIcon = '💕'

const emojiOptions = [
  '💕', '💖', '💗', '🎂', '🎉', '🎊', '🐱', '🐾',
  '⭐', '✨', '📌', '🏠', '🌸', '🎄', '🎃',
]

onMounted(() => fetchDates())

async function fetchDates() {
  try {
    const res = await get('/admin/special-dates')
    dates.value = res.special_dates || []
  } catch (e) {
    console.error('Failed to load special dates', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function resetForm() {
  form.title = ''
  form.date = ''
  form.icon = defaultIcon
  form.repeat_yearly = false
}

function openCreate() {
  isEditing.value = false
  editId.value = null
  resetForm()
  showModal.value = true
}

function openEdit(item) {
  isEditing.value = true
  editId.value = item.id
  form.title = item.title
  form.date = item.date
  form.icon = item.icon || defaultIcon
  form.repeat_yearly = !!item.repeat_yearly
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveDate() {
  if (!form.title.trim()) {
    uni.showToast({ title: '请输入纪念日名称', icon: 'none' })
    return
  }
  if (!form.date.trim()) {
    uni.showToast({ title: '请输入日期', icon: 'none' })
    return
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(form.date.trim())) {
    uni.showToast({ title: '日期格式错误，请使用 YYYY-MM-DD', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const data = {
      title: form.title.trim(),
      date: form.date.trim(),
      icon: form.icon || defaultIcon,
      repeat_yearly: form.repeat_yearly,
    }

    if (isEditing.value) {
      await put('/admin/special-dates/' + editId.value, data)
    } else {
      await post('/admin/special-dates', data)
    }

    uni.showToast({ title: '保存成功', icon: 'success' })
    closeModal()
    fetchDates()
  } catch (e) {
    uni.showToast({ title: e.msg || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

function confirmDelete(item) {
  uni.showModal({
    title: '确认删除',
    content: `确定删除纪念日「${item.title}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await del('/admin/special-dates/' + item.id)
          uni.showToast({ title: '已删除', icon: 'success' })
          fetchDates()
        } catch (e) {
          uni.showToast({ title: e.msg || '删除失败', icon: 'none' })
        }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.special-dates-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary, #4A4A4A);
}

.add-btn {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), #FFB3C6);
  color: #FFF;
  font-size: 24rpx;
  padding: 12rpx 28rpx;
  border-radius: 24rpx;
  font-weight: 600;
}

.date-list {
  background: var(--bg-card, #FFFFFF);
  border-radius: 16rpx;
  overflow: hidden;
}

.date-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #F5F5F5;
}

.date-item:last-child {
  border-bottom: none;
}

.date-icon {
  font-size: 44rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.date-info {
  flex: 1;
}

.date-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 4rpx;
}

.date-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary, #4A4A4A);
}

.repeat-badge {
  font-size: 20rpx;
  color: var(--color-primary, #FF7B93);
  background: #FFF0F3;
  padding: 2rpx 12rpx;
  border-radius: 12rpx;
  font-weight: 500;
}

.date-value {
  font-size: 24rpx;
  color: var(--text-secondary, #888);
}

.date-actions {
  display: flex;
  gap: 16rpx;
  flex-shrink: 0;
}

.date-action {
  font-size: 32rpx;
  padding: 8rpx;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-card {
  width: 600rpx;
  background: #FFF;
  border-radius: 24rpx;
  padding: 40rpx;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary, #4A4A4A);
  text-align: center;
  display: block;
  margin-bottom: 32rpx;
}

.cute-input {
  height: 80rpx;
  background: var(--bg-input, #FFF0F3);
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  margin-bottom: 24rpx;
  color: var(--text-primary, #4A4A4A);
}

.emoji-section {
  margin-bottom: 24rpx;
}

.picker-label {
  font-size: 24rpx;
  color: var(--text-secondary, #888);
  display: block;
  margin-bottom: 12rpx;
}

.emoji-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.emoji-opt {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  border-radius: 12rpx;
  background: #F5F5F5;
}

.emoji-opt.selected {
  background: #FFF0F3;
  border: 2rpx solid var(--color-primary, #FF7B93);
}

.toggle-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.modal-actions {
  display: flex;
  gap: 16rpx;
}

.modal-btn {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  border: none;
}

.modal-btn.cancel {
  background: #F5F5F5;
  color: #999;
}

.modal-btn.confirm {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), #FFB3C6);
  color: #FFF;
}
</style>
