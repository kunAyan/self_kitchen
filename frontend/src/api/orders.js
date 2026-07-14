import { get, post, put } from './index'

export const ordersAPI = {
  create: (items, note, chefUserId, mealType) =>
    post('/orders', { items, note, chef_user_id: chefUserId, meal_type: mealType }),
  getList: (params) => get('/orders', params),
  getDetail: (id) => get(`/orders/${id}`),
  cancel: (id) => put(`/orders/${id}/cancel`),
  recordMood: (id, mood, moodNote) => put(`/orders/${id}/mood`, { mood, mood_note: moodNote }),
  getBalanceLogs: () => get('/balance/logs'),
}
