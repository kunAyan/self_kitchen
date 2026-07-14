<script setup>
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { useAuthStore } from './stores/auth'
import { API_BASE } from './config'

onLaunch(() => {
  const authStore = useAuthStore()
  authStore.checkLogin()
})

onShow(() => {
  const authStore = useAuthStore()
  const pages = getCurrentPages()
  if (pages.length > 0) {
    const currentPage = pages[pages.length - 1]
    if (authStore.isLoggedIn && currentPage.route === 'pages/login/login') {
      uni.reLaunch({ url: '/pages/store-intro/store-intro' })
    }
  }
  // Update order badge on tabBar (index 2 = orders tab)
  if (authStore.isLoggedIn) {
    const token = uni.getStorageSync('token') || ''
    if (token) {
      uni.request({
        url: API_BASE + '/orders?status=pending',
        header: { 'Authorization': `Bearer ${token}` },
        success: (res) => {
          if (res.statusCode === 200) {
            const count = (res.data.orders || []).length
            if (count > 0) {
              uni.setTabBarBadge({ index: 2, text: String(count) })
            } else {
              uni.removeTabBarBadge({ index: 2 })
            }
          }
        },
        fail: () => {},
      })
    }
  }
})
</script>

<style lang="scss">
page {
  --color-primary: var(--color-primary, #FF7B93);
  --color-primary-light: var(--color-primary-light, #FFB3C6);
  --color-primary-dark: var(--color-primary-dark, #E06A7E);
  --color-primary-bg: var(--bg-page, #FFF5F7);
  --color-success: #7BC8A4;
  --color-warning: #FFD93D;
  --color-danger: #FF6B6B;
  --color-info: #7EC8E3;
  --bg-page: var(--bg-page, #FFF5F7);
  --bg-card: var(--bg-card, #FFFFFF);
  --bg-input: var(--bg-input, #FFF0F3);
  --text-primary: #4A4A4A;
  --text-secondary: #888888;
  --text-light: #BBBBBB;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-xl: 28px;
  --radius-round: 50%;
  --shadow-card: 0 2px 12px rgba(255, 123, 147, 0.12);
  --shadow-btn: 0 4px 12px rgba(255, 123, 147, 0.25);
  --font-family: -apple-system, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-family: var(--font-family);
  font-size: 28rpx;
  color: var(--text-primary);
  background-color: var(--bg-page);
}

view, text, image, button, input, scroll-view {
  box-sizing: border-box;
}
</style>
