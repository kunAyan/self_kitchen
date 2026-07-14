import { get } from './index'

export const storeAPI = {
  getConfig: () => get('/store/config'),
  getTodaySpecial: () => get('/today-special'),
}
