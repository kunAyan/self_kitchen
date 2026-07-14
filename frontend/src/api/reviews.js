import { get, post, del } from './index'

export const reviewsAPI = {
  getList: (dishId) => get(`/dishes/${dishId}/reviews`),
  create: (dishId, data) => post(`/dishes/${dishId}/reviews`, data),
  delete: (id) => del(`/reviews/${id}`),
}
