<template>
  <view class="dish-card" @click="onAdd">
    <!-- Image Area -->
    <view class="dish-image-wrap" :style="{ backgroundColor: placeholderColor }">
      <image
        v-if="dish.image"
        class="dish-image"
        :src="uploadBase + dish.image"
        mode="aspectFill"
      />
      <text v-else class="dish-placeholder">{{ dish.category_icon || '🍽️' }}</text>
    </view>

    <!-- Info -->
    <view class="dish-info">
      <text class="dish-name">{{ dish.name }}</text>
      <text class="dish-desc" v-if="dish.description">{{ dish.description }}</text>
      <view class="dish-bottom">
        <text class="dish-price">¥{{ (dish.price / 100).toFixed(2) }}</text>
        <view class="add-btn" @click.stop="onAdd">
          <text class="add-icon">+</text>
        </view>
      </view>
    </view>

    <!-- Sold out overlay -->
    <view v-if="!dish.is_available" class="sold-out">
      <text>已售罄</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { UPLOAD_BASE } from '@/config'
const uploadBase = UPLOAD_BASE

const props = defineProps({
  dish: { type: Object, required: true },
})

const emit = defineEmits(['add'])

// Placeholder colors by category
const placeholderColors = {
  '🍝': '#FFE4C4',
  '🥤': '#D4EFFF',
  '🍰': '#FFE0EC',
  '🥗': '#E8F8E0',
  '🍜': '#FFE8D6',
  '✨': '#F5F0FF',
}
const placeholderColor = computed(() => {
  return placeholderColors[props.dish.category_icon] || 'var(--bg-input, #FFF0F3)'
})

function onAdd() {
  if (props.dish.is_available) {
    emit('add', props.dish)
  }
}
</script>

<style lang="scss" scoped>
.dish-card {
  position: relative;
  background: var(--bg-card, #FFFFFF);
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(255, 123, 147, 0.08);
  transition: transform 0.15s;
}

.dish-card:active {
  transform: scale(0.97);
}

.dish-image-wrap {
  width: 100%;
  height: 200rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.dish-image {
  width: 100%;
  height: 100%;
}

.dish-placeholder {
  font-size: 72rpx;
}

.dish-info {
  padding: 16rpx;
}

.dish-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #4A4A4A;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-desc {
  font-size: 22rpx;
  color: #AAA;
  margin-top: 6rpx;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dish-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12rpx;
}

.dish-price {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--color-primary, #FF7B93);
}

.add-btn {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(255, 123, 147, 0.3);
}

.add-btn:active {
  transform: scale(0.9);
}

.add-icon {
  color: var(--bg-card, #FFFFFF);
  font-size: 32rpx;
  font-weight: 600;
  line-height: 1;
}

.sold-out {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sold-out text {
  font-size: 28rpx;
  color: #999;
  font-weight: 600;
}
</style>
