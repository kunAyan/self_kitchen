import { post, get, put } from './index'

export const authAPI = {
  login: (username, password) => post('/auth/login', { username, password }),
  getProfile: () => get('/auth/profile'),
  updateProfile: (data) => put('/auth/profile', data),
}
