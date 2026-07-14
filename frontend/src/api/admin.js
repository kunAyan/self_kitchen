import { get, post, put, del, uploadFile } from './index'

export const adminAPI = {
  getDashboard: () => get('/admin/dashboard'),

  // Users
  getUsers: () => get('/admin/users'),
  createUser: (data) => post('/admin/users', data),
  getUser: (id) => get(`/admin/users/${id}`),
  updateUser: (id, data) => put(`/admin/users/${id}`, data),
  adjustBalance: (id, amount) => put(`/admin/users/${id}/balance`, { amount }),

  // Categories
  getCategories: () => get('/admin/categories'),
  createCategory: (data) => post('/admin/categories', data),
  updateCategory: (id, data) => put(`/admin/categories/${id}`, data),
  deleteCategory: (id) => del(`/admin/categories/${id}`),

  // Dishes
  getDishes: (params) => get('/admin/dishes', params),
  createDish: (data) => post('/admin/dishes', data),
  updateDish: (id, data) => put(`/admin/dishes/${id}`, data),
  deleteDish: (id) => del(`/admin/dishes/${id}`),

  // Orders
  getOrders: (params) => get('/admin/orders', params),
  getOrder: (id) => get(`/admin/orders/${id}`),
  updateOrderStatus: (id, status, estTime) =>
    put(`/admin/orders/${id}/status`, { status, estimated_time: estTime }),

  // Special dates
  getSpecialDates: () => get('/admin/special-dates'),
  createSpecialDate: (data) => post('/admin/special-dates', data),
  updateSpecialDate: (id, data) => put(`/admin/special-dates/${id}`, data),
  deleteSpecialDate: (id) => del(`/admin/special-dates/${id}`),

  // Upload
  uploadImage: (filePath) => uploadFile('/upload/image', filePath),
  uploadStoreImage: (filePath, type) => uploadFile('/upload/store', filePath, { type }),
}
