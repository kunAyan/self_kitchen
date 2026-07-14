import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import { useCartStore } from '@/stores/cart'

export const useAuthStore = defineStore('auth', () => {
  const token = ref('')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function checkLogin() {
    const savedToken = uni.getStorageSync('token')
    const savedUser = uni.getStorageSync('user')
    if (savedToken) {
      token.value = savedToken
      user.value = savedUser
    }
  }

  async function login(username, password) {
    const res = await authAPI.login(username, password)
    token.value = res.token
    user.value = res.user
    uni.setStorageSync('token', res.token)
    uni.setStorageSync('user', res.user)
    return res
  }

  async function register(username, password, nickname) {
    const res = await authAPI.register(username, password, nickname)
    token.value = res.token
    user.value = res.user
    uni.setStorageSync('token', res.token)
    uni.setStorageSync('user', res.user)
    return res
  }

  async function refreshProfile() {
    const res = await authAPI.getProfile()
    user.value = res.user
    uni.setStorageSync('user', res.user)
  }

  function logout() {
    token.value = ''
    user.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('user')
    useCartStore().clear()
    uni.reLaunch({ url: '/pages/login/login' })
  }

  return { token, user, isLoggedIn, isAdmin, checkLogin, login, register, refreshProfile, logout }
})
