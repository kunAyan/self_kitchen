<template>
  <view class="dish-form-page">
    <view class="page-title">{{ isEdit ? '编辑菜品' : '新增菜品' }}</view>

    <!-- Image upload -->
    <view class="form-section">
      <text class="form-label">菜品图片</text>
      <view class="image-upload" @click="chooseImage">
        <view v-if="previewImage" class="preview-wrap">
          <image class="preview-img" :src="previewImage" mode="aspectFill" />
        </view>
        <view v-else class="upload-placeholder">
          <text class="upload-emoji">{{ form.category_icon || '🍽️' }}</text>
        </view>
        <text class="upload-hint">{{ previewImage ? '点击更换' : '点击上传图片' }}</text>
      </view>
    </view>

    <!-- Category -->
    <view class="form-section">
      <text class="form-label">所属分类</text>
      <picker :range="catNames" @change="onCatChange" :value="catIndex">
        <view class="picker-display">
          <text>{{ catNames[catIndex] || '请选择分类' }}</text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
    </view>

    <!-- Name -->
    <view class="form-section">
      <text class="form-label">菜品名称</text>
      <input class="form-input" v-model="form.name" placeholder="如：番茄肉酱意面" />
    </view>

    <!-- Price -->
    <view class="form-section">
      <text class="form-label">价格（元）</text>
      <input class="form-input" v-model="priceYuan" type="digit" placeholder="如：28.00" />
    </view>

    <!-- Description -->
    <view class="form-section">
      <text class="form-label">描述</text>
      <textarea class="form-textarea" v-model="form.description" placeholder="一句话描述这道菜..." />
    </view>

    <!-- Ingredients -->
    <view class="form-section">
      <text class="form-label">食材清单</text>
      <textarea class="form-textarea" v-model="form.ingredients" placeholder="意面, 番茄, 肉酱, 洋葱..." />
      <text class="form-hint">用逗号分隔，下单后自动汇总成采购清单</text>
    </view>

    <!-- Note -->
    <view class="form-section">
      <text class="form-label">备注标签（限20字）</text>
      <input class="form-input" v-model="form.note" placeholder="如：招牌必点" maxlength="20" />
    </view>

    <!-- Available -->
    <view class="form-section">
      <text class="form-label">上架状态</text>
      <switch :checked="form.is_available" @change="form.is_available = $event.detail.value" color="var(--color-primary, #FF7B93)" />
    </view>

    <!-- Submit -->
    <view class="submit-area">
      <button class="save-btn" :loading="saving" @click="save">保存菜品</button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { UPLOAD_BASE } from '@/config'
const uploadBase = UPLOAD_BASE
import { onLoad } from '@dcloudio/uni-app'
import { adminAPI } from '@/api/admin'
import { dishesAPI } from '@/api/dishes'

const isEdit = ref(false)
const editId = ref(null)
const saving = ref(false)
const previewImage = ref('')
const imageFile = ref('')
const catIndex = ref(0)
const categories = ref([])
const catNames = computed(() => categories.value.map(c => `${c.icon} ${c.name}`))

const form = reactive({
  name: '',
  price: 0,
  category_id: null,
  description: '',
  ingredients: '',
  note: '',
  image: '',
  is_available: true,
})
const priceYuan = ref('')

onLoad(async (options) => {
  // Load categories
  try {
    const res = await dishesAPI.getCategories()
    categories.value = res.categories
  } catch (e) { console.error(e) }

  if (options.id) {
    isEdit.value = true
    editId.value = parseInt(options.id)
    try {
      const res = await adminAPI.getDishes()
      const dish = res.dishes.find(d => d.id === editId.value)
      if (dish) {
        form.name = dish.name
        form.price = dish.price
        form.category_id = dish.category_id
        form.description = dish.description
        form.ingredients = dish.ingredients || ''
        form.note = dish.note || ''
        form.image = dish.image || ''
        form.is_available = dish.is_available
        priceYuan.value = (dish.price / 100).toFixed(2)
        if (dish.image) {
          previewImage.value = `${uploadBase}${dish.image}`
        }
        catIndex.value = categories.value.findIndex(c => c.id === dish.category_id)
      }
    } catch (e) { console.error(e) }
  } else if (categories.value.length > 0) {
    form.category_id = categories.value[0].id
  }
})

function onCatChange(e) {
  catIndex.value = e.detail.value
  form.category_id = categories.value[catIndex.value]?.id || null
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      imageFile.value = res.tempFilePaths[0]
      previewImage.value = res.tempFilePaths[0]
    },
  })
}

async function save() {
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入菜品名称', icon: 'none' })
    return
  }
  const price = Math.round(parseFloat(priceYuan.value) * 100)
  if (isNaN(price) || price <= 0) {
    uni.showToast({ title: '请输入有效价格', icon: 'none' })
    return
  }
  if (!form.category_id) {
    uni.showToast({ title: '请选择分类', icon: 'none' })
    return
  }

  saving.value = true
  try {
    // Upload image first if selected
    let imageFilename = form.image
    if (imageFile.value) {
      const uploadRes = await adminAPI.uploadImage(imageFile.value)
      imageFilename = uploadRes.filename
    }

    const data = {
      name: form.name.trim(),
      price,
      category_id: form.category_id,
      description: form.description.trim(),
      ingredients: form.ingredients.trim(),
      note: (form.note || '').trim().slice(0, 20),
      image: imageFilename,
      is_available: form.is_available,
    }

    if (isEdit.value) {
      await adminAPI.updateDish(editId.value, data)
    } else {
      await adminAPI.createDish(data)
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e) {
    uni.showToast({ title: e.msg || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.dish-form-page {
  min-height: 100vh;
  background: var(--bg-page, #FFF5F7);
  padding: 24rpx;
}

.page-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #4A4A4A;
  margin-bottom: 24rpx;
}

.form-section {
  background: #FFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.form-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
  margin-bottom: 16rpx;
}

.image-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.preview-wrap, .upload-placeholder {
  width: 300rpx;
  height: 200rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.preview-img {
  width: 100%;
  height: 100%;
}

.upload-placeholder {
  background: var(--bg-input, #FFF0F3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-emoji {
  font-size: 72rpx;
}

.upload-hint {
  font-size: 24rpx;
  color: #CCC;
}

.picker-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-page, #FFF5F7);
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
}

.picker-arrow {
  font-size: 20rpx;
  color: #CCC;
}

.form-input {
  height: 80rpx;
  background: var(--bg-page, #FFF5F7);
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
}

.form-textarea {
  background: var(--bg-page, #FFF5F7);
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  min-height: 120rpx;
  width: 100%;
}

.submit-area {
  padding: 32rpx 0;
}

.form-hint { font-size: 20rpx; color: #CCC; margin-top: 6rpx; display: block; }

.save-btn {
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: #FFF;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 24rpx;
  padding: 24rpx;
  border: none;
  box-shadow: 0 4rpx 16rpx rgba(255, 123, 147, 0.3);
}
</style>
