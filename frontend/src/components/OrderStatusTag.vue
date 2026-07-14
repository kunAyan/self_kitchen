<template>
  <view class="status-tag" :class="'status-' + status">
    <text>{{ label }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const label = computed(() => {
  const map = {
    pending: '待接单',
    accepted: '已接单',
    completed: '已完成',
    rejected: '已拒单',
    cancelled: '已取消',
  }
  return map[props.status] || props.status
})
</script>

<style lang="scss" scoped>
.status-tag {
  display: inline-flex;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;
}

.status-pending {
  background: #FFF3E0;
  color: #FF9800;
}

.status-accepted {
  background: #E3F2FD;
  color: #2196F3;
}

.status-completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.status-rejected {
  background: #FFEBEE;
  color: #F44336;
}

.status-cancelled {
  background: #F5F5F5;
  color: #9E9E9E;
}
</style>
