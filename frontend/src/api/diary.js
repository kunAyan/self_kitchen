import { get, post, put, del, uploadFile } from './index'

export const diaryAPI = {
  getMonth: (year, month) => get('/diary', { year, month }),
  getDate: (date) => get(`/diary/${date}`),
  uploadPhoto: (date, filePath) => uploadFile(`/diary/${date}/photos`, filePath),
  deletePhoto: (id) => del(`/diary/photos/${id}`),
  createNote: (date, data) => post(`/diary/${date}/notes`, data),
  updateNote: (id, data) => put(`/diary/notes/${id}`, data),
  deleteNote: (id) => del(`/diary/notes/${id}`),
}
