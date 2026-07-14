<template>
  <view class="login-page">
    <!-- Logo area -->
    <view class="logo-area">
      <text class="logo-emoji">🍳</text>
      <text class="logo-text">木糯小厨</text>
      <text class="logo-sub">{{ loginSubtitle }}</text>
    </view>

    <!-- Login card -->
    <view class="login-card">
      <view class="form-area">
        <input
          class="cute-input"
          v-model="username"
          placeholder="用户名"
          placeholder-style="color:#CCCCCC"
        />
        <input
          class="cute-input"
          v-model="password"
          type="password"
          placeholder="密码"
          placeholder-style="color:#CCCCCC"
        />
        <button
          class="cute-btn"
          :class="{ 'cute-btn-pressed': pressed }"
          :loading="loading"
          @touchstart="pressed = true"
          @touchend="pressed = false"
          @click="handleLogin"
        >登 录</button>
      </view>
    </view>

    <view class="footer-text">{{ loginFooter }}</view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { get } from '@/api/index'

const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const pressed = ref(false)
const loginSubtitle = ref('木木和糯糯的小厨房')
const loginFooter = ref('💕 记录每一天的温暖')

onMounted(async () => {
  try {
    const res = await get('/store/config')
    if (res.config) {
      loginSubtitle.value = res.config.login_subtitle || loginSubtitle.value
      loginFooter.value = res.config.login_footer || loginFooter.value
    }
  } catch { /* use defaults */ }
})

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) {
    uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await authStore.login(username.value.trim(), password.value)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/store-intro/store-intro' })
    }, 500)
  } catch (e) {
    uni.showToast({ title: e.msg || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--color-primary-light, #FFB3C6) 0%, var(--bg-page, #FFF5F7) 40%, var(--bg-card, #FFFFFF) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 48rpx 40rpx;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.logo-emoji {
  font-size: 120rpx;
  margin-bottom: 24rpx;
  animation: logo-float 3s ease-in-out infinite;
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16rpx); }
}

.logo-text {
  font-size: 52rpx;
  font-weight: 700;
  color: var(--color-primary, var(--color-primary, #FF7B93));
  margin-bottom: 16rpx;
  letter-spacing: 4rpx;
}

.logo-sub {
  font-size: 26rpx;
  color: #999;
  letter-spacing: 2rpx;
}

.login-card {
  width: 100%;
  max-width: 600rpx;
  background: var(--bg-card, var(--bg-card, #FFFFFF));
  border-radius: var(--radius-xl, 28rpx);
  padding: 56rpx 44rpx;
  box-shadow: 0 4rpx 24rpx rgba(255, 123, 147, 0.15);
}

.form-area {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.cute-input {
  height: 96rpx;
  background: var(--bg-page, #FFF5F7);
  border-radius: 48rpx;
  padding: 0 36rpx;
  font-size: 28rpx;
  color: #4A4A4A;
  border: 2rpx solid transparent;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.cute-input:focus {
  border-color: var(--color-primary, #FF7B93);
}

.cute-btn {
  height: 96rpx;
  background: linear-gradient(135deg, var(--color-primary, #FF7B93), var(--color-primary-light, #FFB3C6));
  color: var(--bg-card, #FFFFFF);
  font-size: 34rpx;
  font-weight: 700;
  border-radius: 48rpx;
  border: none;
  margin-top: 16rpx;
  box-shadow: 0 6rpx 20rpx rgba(255, 123, 147, 0.35);
  letter-spacing: 8rpx;
  transition: transform 0.15s;
}

.cute-btn-pressed {
  transform: scale(0.96);
}

.footer-text {
  margin-top: 80rpx;
  font-size: 22rpx;
  color: #CCC;
}
</style>
