<template>
  <view class="admin-categories">
    <view class="page-header">
      <text class="page-title">📂 分类管理</text>
      <view class="add-btn" @click="showForm = true; editItem = null">
        <text>+ 新增</text>
      </view>
    </view>

    <view v-if="categories.length === 0">
      <EmptyState icon="📂" text="还没有分类" subText="点击上方按钮添加" />
    </view>

    <view v-else class="cat-list">
      <view v-for="cat in categories" :key="cat.id" class="cat-item">
        <text class="cat-icon">{{ cat.icon }}</text>
        <view class="cat-info">
          <text class="cat-name">{{ cat.name }}</text>
          <text class="cat-count">{{ cat.dish_count }} 个菜品</text>
        </view>
        <view class="cat-actions">
          <text class="cat-action" @click="editCat(cat)">✏️</text>
          <text class="cat-action" @click="deleteCat(cat)">🗑️</text>
        </view>
      </view>
    </view>

    <!-- Add/Edit Modal -->
    <view v-if="showForm" class="modal-overlay" @click="showForm = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">{{ editItem ? '编辑分类' : '新增分类' }}</text>
        <input class="cute-input" v-model="form.name" placeholder="分类名称" placeholder-style="color:#CCC" />
        <view class="emoji-picker">
          <text class="picker-label">图标</text>
          <view class="emoji-list">
            <text
              v-for="e in emojis"
              :key="e"
              class="emoji-opt"
              :class="{ selected: form.icon === e }"
              @click="form.icon = e"
            >{{ e }}</text>
          </view>
        </view>
        <view class="modal-actions">
          <button class="modal-btn cancel" @click="showForm = false">取消</button>
          <button class="modal-btn confirm" @click="saveCat">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'

const categories = ref([])
const showForm = ref(false)
const editItem = ref(null)
const form = reactive({ name: '', icon: '🍽️' })

const emojis = ['🍝', '🥤', '🍰', '🥗', '🍜', '🍕', '🍔', '🌮', '🥩', '🍲', '🧁', '🍩', '☕', '🍵', '🍺', '✨', '🔥', '💖']

onMounted(() => fetchCategories())

async function fetchCategories() {
  try {
    const res = await adminAPI.getCategories()
    categories.value = res.categories
  } catch (e) { console.error(e) }
}

function editCat(cat) {
  editItem.value = cat
  form.name = cat.name
  form.icon = cat.icon
  showForm.value = true
}

async function saveCat() {
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入分类名称', icon: 'none' })
    return
  }
  try {
    if (editItem.value) {
      await adminAPI.updateCategory(editItem.value.id, { name: form.name, icon: form.icon })
    } else {
      await adminAPI.createCategory({ name: form.name, icon: form.icon })
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    showForm.value = false
    form.name = ''
    form.icon = '🍽️'
    editItem.value = null
    fetchCategories()
  } catch (e) {
    uni.showToast({ title: e.msg || '保存失败', icon: 'none' })
  }
}

async function deleteCat(cat) {
  uni.showModal({
    title: '确认删除',
    content: `确定删除分类「${cat.name}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await adminAPI.deleteCategory(cat.id)
          uni.showToast({ title: '已删除', icon: 'success' })
          fetchCategories()
        } catch (e) {
          uni.showToast({ title: e.msg || '删除失败', icon: 'none' })
        }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.admin-categories {
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
  color: #4A4A4A;
}

.add-btn {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: #FFF;
  font-size: 24rpx;
  padding: 12rpx 28rpx;
  border-radius: 24rpx;
  font-weight: 600;
}

.cat-list {
  background: #FFF;
  border-radius: 16rpx;
  overflow: hidden;
}

.cat-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #F5F5F5;
}

.cat-item:last-child {
  border-bottom: none;
}

.cat-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
}

.cat-info {
  flex: 1;
}

.cat-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
}

.cat-count {
  font-size: 22rpx;
  color: #AAA;
}

.cat-actions {
  display: flex;
  gap: 16rpx;
}

.cat-action {
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
  color: #4A4A4A;
  text-align: center;
  display: block;
  margin-bottom: 32rpx;
}

.cute-input {
  height: 80rpx;
  background: var(--bg-page, #FFF5F7);
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  margin-bottom: 24rpx;
}

.picker-label {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
}

.emoji-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 24rpx;
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
  background: var(--bg-input, #FFF0F3);
  border: 2rpx solid var(--color-primary, #FF7B93);
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
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: #FFF;
}
</style>
