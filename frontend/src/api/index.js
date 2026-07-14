// API request wrapper for uni-app v2
import { API_BASE } from '../config'

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token') || ''

    const headers = { 'Content-Type': 'application/json', ...(options.header || {}) }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: API_BASE + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: headers,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          uni.reLaunch({ url: '/pages/login/login' })
          reject(res.data)
        } else {
          reject(res.data)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误，请重试', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const get = (url, data) => request({ url, method: 'GET', data })
export const post = (url, data) => request({ url, method: 'POST', data })
export const put = (url, data) => request({ url, method: 'PUT', data })
export const del = (url, data) => request({ url, method: 'DELETE', data })

// File upload
export const uploadFile = (url, filePath, formData = {}) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token') || ''
    uni.uploadFile({
      url: API_BASE + url,
      filePath,
      name: 'file',
      formData,
      header: token ? { 'Authorization': `Bearer ${token}` } : {},
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(res.data))
        } else {
          reject(JSON.parse(res.data))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

export default request
