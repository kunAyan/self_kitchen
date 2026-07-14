<template>
  <view class="store-config-page">
    <view class="page-header">
      <text class="page-title">🏪 店铺配置</text>
    </view>

    <!-- 店铺名称 -->
    <view class="form-section">
      <text class="form-label">店铺名称</text>
      <input class="form-input" v-model="form.store_name" placeholder="输入店铺名称" maxlength="50" />
    </view>

    <!-- 店铺大图 -->
    <view class="form-section">
      <text class="form-label">店铺大图</text>
      <view class="image-upload" @click="chooseImage('store')">
        <view v-if="form.store_image" class="preview-wrap">
          <image class="preview-img" :src="uploadBase + form.store_image" mode="aspectFill" />
        </view>
        <view v-else class="upload-placeholder">
          <text class="upload-emoji">🏪</text>
        </view>
        <text class="upload-hint">{{ form.store_image ? '点击更换' : '点击上传店铺大图' }}</text>
      </view>
    </view>

    <!-- 欢迎语 -->
    <view class="form-section">
      <text class="form-label">欢迎语</text>
      <input class="form-input" v-model="form.welcome_message" placeholder="如：欢迎光临～今天想吃点什么？" maxlength="100" />
    </view>

    <!-- 店铺简介 -->
    <view class="form-section">
      <text class="form-label">店铺简介</text>
      <textarea class="form-textarea" v-model="form.store_intro" placeholder="简短介绍你的店铺..." maxlength="300" />
    </view>

    <!-- Banner 文字 -->
    <view class="form-section">
      <text class="form-label">Banner 文字</text>
      <input class="form-input" v-model="form.banner_text" placeholder="显示在页面顶部的标语" maxlength="100" />
    </view>

    <!-- Banner 图片 -->
    <view class="form-section">
      <text class="form-label">Banner 图片</text>
      <view class="image-upload" @click="chooseImage('banner')">
        <view v-if="form.banner_image" class="preview-wrap">
          <image class="preview-img" :src="uploadBase + form.banner_image" mode="aspectFill" />
        </view>
        <view v-else class="upload-placeholder">
          <text class="upload-emoji">🖼️</text>
        </view>
        <text class="upload-hint">{{ form.banner_image ? '点击更换' : '点击上传Banner图片' }}</text>
      </view>
    </view>

    <!-- 登录页标语 -->
    <view class="form-section">
      <text class="form-label">登录页 - 副标题</text>
      <input class="form-input" v-model="form.login_subtitle" placeholder="显示在Logo下方" maxlength="50" />
    </view>
    <view class="form-section">
      <text class="form-label">登录页 - 底部文字</text>
      <input class="form-input" v-model="form.login_footer" placeholder="显示在登录页底部" maxlength="50" />
    </view>

    <!-- 主打菜品 -->
    <view class="form-section">
      <text class="form-label">主打菜品</text>
      <text class="form-desc">选择要标记为主打的菜品（可多选）</text>
      <view class="dish-checkbox-list" v-if="allDishes.length > 0">
        <view
          v-for="dish in allDishes"
          :key="dish.id"
          class="dish-checkbox-item"
          :class="{ selected: featuredSet.has(dish.id) }"
          @click="toggleFeatured(dish.id)"
        >
          <view class="dc-thumb">
            <image v-if="dish.image" class="dc-img" :src="uploadBase + dish.image" mode="aspectFill" />
            <text v-else class="dc-emoji">{{ dish.category_icon || '🍽️' }}</text>
          </view>
          <text class="dc-name">{{ dish.name }}</text>
          <text class="dc-price">¥{{ (dish.price / 100).toFixed(2) }}</text>
          <view class="dc-check">
            <text v-if="featuredSet.has(dish.id)" class="check-mark">✓</text>
          </view>
        </view>
      </view>
      <text v-else class="empty-hint">暂无菜品数据</text>
    </view>

    <!-- 保存 -->
    <view class="submit-area">
      <button class="save-btn" :loading="saving" @click="saveConfig">保存配置</button>
    </view>

    <view class="bottom-spacer"></view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { get, put, uploadFile } from '@/api/index'
import { UPLOAD_BASE } from '@/config'

const uploadBase = UPLOAD_BASE

const form = reactive({
  store_name: '',
  store_image: '',
  welcome_message: '',
  store_intro: '',
  banner_text: '',
  banner_image: '',
  login_subtitle: '',
  login_footer: '',
  featured_dish_ids: [],
})

const allDishes = ref([])
const featuredSet = ref(new Set())
const saving = ref(false)

// Image upload state
const storeImageFile = ref('')
const bannerImageFile = ref('')

onMounted(async () => {
  try {
    const res = await get('/store/config')
    if (res.config) {
      const c = res.config
      form.store_name = c.store_name || ''
      form.store_image = c.store_image || ''
      form.welcome_message = c.welcome_message || ''
      form.store_intro = c.store_intro || ''
      form.banner_text = c.banner_text || ''
      form.banner_image = c.banner_image || ''
      form.login_subtitle = c.login_subtitle || ''
      form.login_footer = c.login_footer || ''
      // featured_dish_ids is stored as JSON string
      try {
        const ids = JSON.parse(c.featured_dish_ids || '[]')
        if (Array.isArray(ids)) {
          form.featured_dish_ids = ids
          featuredSet.value = new Set(ids)
        }
      } catch { form.featured_dish_ids = []; featuredSet.value = new Set() }
    }
  } catch (e) {
    console.error('Failed to load store config', e)
    uni.showToast({ title: '加载配置失败', icon: 'none' })
  }

  // Fetch all dishes for featured selection
  try {
    const res = await get('/dishes')
    if (res.dishes) {
      allDishes.value = res.dishes
    }
  } catch (e) {
    console.error('Failed to load dishes', e)
  }
})

function toggleFeatured(id) {
  const set = new Set(featuredSet.value)
  if (set.has(id)) {
    set.delete(id)
  } else {
    set.add(id)
  }
  featuredSet.value = set
  form.featured_dish_ids = Array.from(set)
}

function chooseImage(field) {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const filePath = res.tempFilePaths[0]
      try {
        uni.showLoading({ title: '上传中...' })
        const uploadRes = await uploadFile('/upload/store', filePath, { type: 'store' })
        uni.hideLoading()
        if (uploadRes.filename) {
          if (field === 'store') {
            form.store_image = uploadRes.filename
          } else if (field === 'banner') {
            form.banner_image = uploadRes.filename
          }
          uni.showToast({ title: '上传成功', icon: 'success' })
        } else {
          uni.showToast({ title: '上传失败，请重试', icon: 'none' })
        }
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: e.msg || '上传失败', icon: 'none' })
      }
    },
  })
}

async function saveConfig() {
  if (!form.store_name.trim()) {
    uni.showToast({ title: '请输入店铺名称', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const data = {
      store_name: form.store_name.trim(),
      store_image: form.store_image,
      welcome_message: form.welcome_message.trim(),
      store_intro: form.store_intro.trim(),
      banner_text: form.banner_text.trim(),
      banner_image: form.banner_image,
      login_subtitle: form.login_subtitle.trim(),
      login_footer: form.login_footer.trim(),
      featured_dish_ids: JSON.stringify(form.featured_dish_ids || []),
    }
    await put('/admin/store/config', data)
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.msg || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.store-config-page {
  min-height: 100vh;
  background: var(--bg-page, var(--bg-page, #FFF5F7));
  padding: 24rpx;
}

.page-header {
  margin-bottom: 24rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary, #4A4A4A);
}

.form-section {
  background: var(--bg-card, var(--bg-card, #FFFFFF));
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.form-label {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--text-primary, #4A4A4A);
  display: block;
  margin-bottom: 16rpx;
}

.form-desc {
  font-size: 22rpx;
  color: var(--text-secondary, #888);
  display: block;
  margin-bottom: 12rpx;
}

.form-input {
  height: 80rpx;
  background: var(--bg-input, var(--bg-input, #FFF0F3));
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: var(--text-primary, #4A4A4A);
}

.form-textarea {
  background: var(--bg-input, var(--bg-input, #FFF0F3));
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  min-height: 120rpx;
  width: 100%;
  color: var(--text-primary, #4A4A4A);
}

.image-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.preview-wrap, .upload-placeholder {
  width: 400rpx;
  height: 240rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.preview-img {
  width: 100%;
  height: 100%;
}

.upload-placeholder {
  background: var(--bg-input, var(--bg-input, #FFF0F3));
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-emoji {
  font-size: 72rpx;
}

.upload-hint {
  font-size: 24rpx;
  color: var(--text-light, #BBB);
}

.dish-checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.dish-checkbox-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: var(--bg-input, var(--bg-input, #FFF0F3));
  border-radius: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.15s;
}

.dish-checkbox-item.selected {
  border-color: var(--color-primary, var(--color-primary, #FF7B93));
  background: var(--bg-page, #FFF5F7);
}

.dc-thumb {
  width: 64rpx;
  height: 64rpx;
  border-radius: 10rpx;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF;
  flex-shrink: 0;
}

.dc-img {
  width: 100%;
  height: 100%;
}

.dc-emoji {
  font-size: 32rpx;
}

.dc-name {
  flex: 1;
  font-size: 26rpx;
  font-weight: 500;
  color: var(--text-primary, #4A4A4A);
}

.dc-price {
  font-size: 24rpx;
  color: var(--color-primary, var(--color-primary, #FF7B93));
  font-weight: 600;
}

.dc-check {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  border: 2rpx solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dish-checkbox-item.selected .dc-check {
  background: var(--color-primary, var(--color-primary, #FF7B93));
  border-color: var(--color-primary, var(--color-primary, #FF7B93));
}

.check-mark {
  color: #FFF;
  font-size: 24rpx;
  font-weight: 700;
}

.empty-hint {
  font-size: 24rpx;
  color: var(--text-light, #BBB);
  display: block;
  text-align: center;
  padding: 20rpx;
}

.submit-area {
  padding: 16rpx 0 32rpx;
}

.save-btn {
  background: linear-gradient(135deg, var(--color-primary, var(--color-primary, #FF7B93)), var(--color-primary-light, #FFB3C6));
  color: #FFF;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 24rpx;
  padding: 24rpx;
  border: none;
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}

.bottom-spacer {
  height: 40rpx;
}
</style>
