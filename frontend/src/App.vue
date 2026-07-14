<script setup>
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { useAuthStore } from './stores/auth'
import { API_BASE } from './config'

const themeColors = {
  pink:   { primary: '#FF7B93', bg: '#FFF5F7', light: '#FFB3C6', dark: '#E06A7E' },
  blue:   { primary: '#7EC8E3', bg: '#F0F8FB', light: '#B3D9EB', dark: '#5BA8C8' },
  green:  { primary: '#7BC8A4', bg: '#F0F8F2', light: '#B3D9C4', dark: '#5BA878' },
  purple: { primary: '#B39DDB', bg: '#F8F5FB', light: '#D1C4E9', dark: '#8E6DB8' },
}

function applyTheme(name) {
  const c = themeColors[name] || themeColors.pink
  uni.setNavigationBarColor({ frontColor: '#ffffff', backgroundColor: c.primary })
  uni.setTabBarStyle({ color: '#999999', selectedColor: c.primary, backgroundColor: '#FFFFFF' })
  // Set page background via the page style API
  uni.setBackgroundColor({ backgroundColor: c.bg, backgroundColorTop: c.primary, backgroundColorBottom: c.bg })
  // Store for next launch
  uni.setStorageSync('theme', name)
}

onLaunch(() => {
  const authStore = useAuthStore()
  authStore.checkLogin()
  const savedTheme = uni.getStorageSync('theme') || 'pink'
  applyTheme(savedTheme)
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
  --color-primary: #FF7B93;
  --color-primary-light: #FFB3C6;
  --color-primary-dark: #E06A7E;
  --color-primary-bg: #FFF5F7;
  --color-success: #7BC8A4;
  --color-warning: #FFD93D;
  --color-danger: #FF6B6B;
  --color-info: #7EC8E3;
  --bg-page: #FFF5F7;
  --bg-card: #FFFFFF;
  --bg-input: #FFF0F3;
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
