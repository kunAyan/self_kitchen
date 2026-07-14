import { get } from './index'

export const dishesAPI = {
  getCategories: () => get('/categories'),
  getDishes: (params = {}) => get('/dishes', params),
  getDish: (id) => get(`/dishes/${id}`),
}
