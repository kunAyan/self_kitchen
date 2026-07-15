<template>
  <view class="diary-page">
    <!-- Month header -->
      <view class="view-toggle">
        <view class="vt-seg"><text class="vt-btn" :class="{ active: diaryView === 'calendar' }" @click="diaryView = 'calendar'">📅 日历</text><text class="vt-btn" :class="{ active: diaryView === 'list' }" @click="diaryView = 'list'">📋 列表</text></view>
      </view>
    <view class="month-header">
      <text class="month-arrow" @click="prevMonth">←</text>
      <text class="month-title">{{ year }}年{{ month }}月</text>
      <text class="month-arrow" @click="nextMonth">→</text>
    </view>

    <!-- Calendar View -->
    <view v-if="diaryView === 'calendar'">
      <view class="weekdays">
        <text v-for="d in weekdays" :key="d" class="wd">{{ d }}</text>
      </view>
      <view class="calendar">
        <view v-for="(day, i) in calendarDays" :key="i" class="cal-cell" :class="{ dim: !day, today: isToday(day), hasOrder: hasOrder(day), special: hasSpecial(day) }" @click="day ? selectDate(day) : null">
          <view v-if="day" class="cal-moods">
            <text v-for="(m, mi) in getMoods(day)" :key="mi" class="cal-mood-emoji">{{ m.mood }}</text>
          </view>
          <text v-if="day" class="cal-day">{{ day }}</text>
          <view v-if="day && hasOrder(day)" class="cal-dot"></view>
          <text v-if="day && hasSpecial(day)" class="cal-special-text">{{ getSpecialTitle(day) }}</text>
        </view>
      </view>
    </view>

    <!-- List View -->
    <view v-if="diaryView === 'list'" class="diary-list-view">
      <view v-if="listDates.length === 0" class="no-data">本月暂无记录</view>
      <view v-for="d in listDates" :key="d.date" class="diary-list-item" @click="selectDateStr(d.date)">
        <view class="dli-header">
          <text class="dli-date">{{ d.date }}</text>
          <text class="dli-badges">{{ d.hasOrder ? '📋' : '' }} {{ d.hasPhoto ? '📸' : '' }} {{ d.hasNote ? '💬' : '' }}</text>
        </view>
      </view>
    </view>

    <!-- Monthly summary (when no date selected) -->
    <view v-if="!selectedDate" class="month-summary card">
      <text class="ms-title">📊 {{ month }}月概览</text>
      <view class="ms-row">
        <view class="ms-item"><text class="ms-num">{{ monthOrderCount }}</text><text class="ms-label">笔订单</text></view>
        <view class="ms-item"><text class="ms-num">{{ monthPhotoCount }}</text><text class="ms-label">张照片</text></view>
        <view class="ms-item"><text class="ms-num">{{ monthNoteCount }}</text><text class="ms-label">篇日记</text></view>
      </view>
      <text class="ms-hint">👆 点击日期查看详情</text>
    </view>

    <!-- Selected date detail -->
    <view v-if="selectedDate" class="date-detail card">
      <text class="date-title">{{ selectedDate }}</text>

      <!-- Moods card -->
      <view class="day-section mood-section">
        <text class="day-label">😊 全家心情</text>
        <view class="mood-user-list">
          <view v-for="u in allUsersMoods" :key="u.user_id" class="mood-user-row">
            <text class="mood-user-nickname">{{ u.nickname }}</text>
            <text v-if="u.mood" class="mood-user-emoji">{{ u.mood }}</text>
            <text v-if="u.mood && u.content" class="mood-user-desc">"{{ u.content }}"</text>
            <text v-else-if="!u.mood" class="mood-user-empty">— (未记录)</text>
            <text v-if="u.mood && (u.user_id === authStore.user?.id || authStore.isAdmin)" class="mood-user-del" @click="deleteMoodNote(u.note_id)">🗑️</text>
          </view>
        </view>
        <view class="note-add" @click="showNoteInput = true"><text>+ 写心情</text></view>
      </view>

      <!-- Orders on this day -->
      <view v-if="dayOrders.length > 0" class="day-section">
        <text class="day-label">📋 当日订单</text>
        <view v-for="o in dayOrders" :key="o.id" class="day-order">
          <view class="do-line"><text class="do-label">时间：</text><text class="do-val">{{ mealLabel(o.meal_type) }} {{ fmt(o.created_at) }}</text></view>
          <view class="do-line"><text class="do-label">主厨：</text><text class="do-val">👨‍🍳 {{ o.chef_nickname || '未知' }}</text></view>
          <view class="do-line"><text class="do-label">吃货：</text><text class="do-val">{{ o.user_nickname || '未知' }}</text></view>
          <view class="do-line" v-if="o.note"><text class="do-label">备注：</text><text class="do-val">{{ o.note }}</text></view>
          <view class="do-total">¥{{ (o.total_amount / 100).toFixed(2) }}</view>
        </view>
      </view>

      <!-- Photos -->
      <view class="day-section">
        <text class="day-label">📸 照片 ({{ dayPhotos.length }})</text>
        <view class="photo-grid">
          <image v-for="p in dayPhotos" :key="p.id" class="photo-thumb" :src="uploadBase + p.image_path" mode="aspectFill" @click="previewPhoto(p)" />
          <view class="photo-add" @click="uploadPhoto"><text>+</text></view>
        </view>
      </view>

      <!-- Notes -->
      <view class="day-section">
        <text class="day-label">💬 日记</text>
        <view v-for="n in dayNotes" :key="n.id" class="note-item">
          <view class="note-header">
            <text class="note-user">{{ n.user_nickname }}</text>
            <text class="note-mood" v-if="n.mood">{{ n.mood }}</text>
            <text class="note-time">{{ fmt(n.created_at) }}</text>
            <text v-if="n.user_id === authStore.user?.id || authStore.isAdmin" class="note-del" @click="deleteNote(n.id)">🗑️</text>
          </view>
          <text class="note-content">{{ n.content }}</text>
        </view>
        <view class="note-add" @click="showNoteInput = true"><text>+ 写日记</text></view>
      </view>
    </view>

    <!-- Write note modal -->
    <view v-if="showNoteInput" class="modal-overlay" @click="showNoteInput = false">
      <view class="modal-card" @click.stop>
        <text class="modal-title">写日记</text>
        <view class="mood-pick">
          <text v-for="m in moods" :key="m" class="mood-opt" :class="{ selected: newMood === m }" @click="newMood = m">{{ m }}</text>
        </view>
        <textarea class="note-textarea" v-model="newNote" placeholder="记录今天..." />
        <button class="note-save-btn" @click="saveNote">保存</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UPLOAD_BASE } from '@/config'
const uploadBase = UPLOAD_BASE
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { diaryAPI } from '@/api/diary'

const authStore = useAuthStore()
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const weekdays = ['一', '二', '三', '四', '五', '六', '日']

const orderDates = ref({})
const specialDates = ref([])
const moodDates = ref({})
const selectedDate = ref('')
const dayPhotos = ref([])
const dayNotes = ref([])
const dayOrders = ref([])
const showNoteInput = ref(false)
const newNote = ref('')
const newMood = ref('😊')
const moods = ['😋', '😊', '😐', '😞', '🥰', '😴', '🎉', '💕']
const diaryView = ref('calendar')

const monthOrderCount = computed(() => Object.values(orderDates.value).reduce((s, v) => s + v, 0))
const monthPhotoCount = ref(0)
const monthNoteCount = ref(0)

const listDates = computed(() => {
  const dates = []
  const totalDays = new Date(year.value, month.value, 0).getDate()
  for (let d = 1; d <= totalDays; d++) {
    const ds = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const hasOrder = !!orderDates.value[ds]
    const hasPhoto = false // Will be populated from API
    const hasNote = false
    if (hasOrder) dates.push({ date: ds, hasOrder, hasPhoto, hasNote })
  }
  return dates
})

onShow(() => fetchMonth())

async function fetchMonth() {
  try {
    const res = await diaryAPI.getMonth(year.value, month.value)
    orderDates.value = res.order_dates || {}
    specialDates.value = res.special_dates || []
    moodDates.value = res.mood_dates || {}
    monthPhotoCount.value = Object.values(res.photo_dates || {}).reduce((s, v) => s + v, 0)
    monthNoteCount.value = Object.values(res.note_dates || {}).reduce((s, v) => s + v, 0)
    selectedDate.value = ''
  } catch (e) { console.error(e) }
}

const calendarDays = computed(() => {
  const first = new Date(year.value, month.value - 1, 1)
  const last = new Date(year.value, month.value, 0)
  const startDow = first.getDay() || 7 // Mon=1..Sun=7
  const days = []
  for (let i = 1; i < startDow; i++) days.push(null)
  for (let d = 1; d <= last.getDate(); d++) days.push(d)
  return days
})

function isToday(d) {
  if (!d) return false
  const t = new Date()
  return year.value === t.getFullYear() && month.value === t.getMonth() + 1 && d === t.getDate()
}
function dateStr(d) {
  return `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}
function hasOrder(d) { return !!orderDates.value[dateStr(d)] }
function hasSpecial(d) {
  return specialDates.value.some(s => {
    const sd = new Date(s.date)
    return sd.getMonth() + 1 === month.value && sd.getDate() === d
  })
}
function getSpecialTitle(d) {
  const s = specialDates.value.find(s => {
    const sd = new Date(s.date)
    return sd.getMonth() + 1 === month.value && sd.getDate() === d
  })
  return s ? s.icon + s.title : ''
}

function getMoods(d) {
  const ds = dateStr(d)
  return moodDates.value[ds] || []
}

async function selectDate(d) {
  const ds = dateStr(d)
  selectedDate.value = ds
  try {
    const res = await diaryAPI.getDate(ds)
    dayPhotos.value = res.photos || []
    dayNotes.value = res.notes || []
    dayOrders.value = res.orders || []
  } catch (e) { console.error(e) }
}

function prevMonth() {
  if (month.value === 1) { year.value--; month.value = 12 }
  else month.value--
  fetchMonth()
}
function nextMonth() {
  if (month.value === 12) { year.value++; month.value = 1 }
  else month.value++
  fetchMonth()
}

function mealLabel(t) {
  const m = { breakfast: '🌅早', lunch: '☀️午', dinner: '🌙晚', snack: '🍰茶', night_snack: '🌃宵' }
  return m[t] || ''
}
function fmt(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const p = n => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}`
}

async function uploadPhoto() {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album', 'camera'],
    success: async (res) => {
      for (const fp of res.tempFilePaths) {
        try { await diaryAPI.uploadPhoto(selectedDate.value, fp) } catch (e) {}
      }
      uni.showToast({ title: '上传完成', icon: 'success' })
      if (selectedDate.value) selectDateStr(selectedDate.value)
    },
  })
}

async function selectDateStr(ds) {
  try {
    const res = await diaryAPI.getDate(ds)
    dayPhotos.value = res.photos || []
    dayNotes.value = res.notes || []
    dayOrders.value = res.orders || []
  } catch (e) {}
}

function previewPhoto(p) {
  uni.previewImage({
    urls: dayPhotos.value.map(pp => `${uploadBase}${pp.image_path}`),
    current: `${uploadBase}${p.image_path}`,
  })
}

async function saveNote() {
  if (!newNote.value.trim()) return
  try {
    await diaryAPI.createNote(selectedDate.value, { content: newNote.value, mood: newMood.value })
    uni.showToast({ title: '已保存', icon: 'success' })
    showNoteInput.value = false; newNote.value = ''; newMood.value = '😊'
    selectDateStr(selectedDate.value)
  } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
}

async function deleteNote(id) {
  uni.showModal({
    title: '删除日记', content: '确定删除吗？',
    success: async (r) => {
      if (r.confirm) {
        try { await diaryAPI.deleteNote(id); selectDateStr(selectedDate.value) } catch (e) {}
      }
    },
  })
}

const allUsersMoods = computed(() => {
  // Get all family members' moods for the selected date
  // Build from existing dayNotes data
  const moodMap = {}
  // Populate from dayNotes (notes already have user_id, mood, content)
  for (const note of dayNotes.value) {
    if (note.mood || note.content) {
      moodMap[note.user_id] = {
        user_id: note.user_id,
        nickname: note.user_nickname,
        mood: note.mood || '',
        content: note.content || '',
        note_id: note.id,
      }
    }
  }
  // Also check dayOrders for users who ordered but haven't written mood
  const seen = new Set(Object.keys(moodMap))
  for (const o of dayOrders.value) {
    const uid = String(o.user_id)
    if (!seen.has(uid)) {
      seen.add(uid)
      moodMap[uid] = {
        user_id: o.user_id,
        nickname: o.user_nickname,
        mood: '',
        content: '',
        note_id: null,
      }
    }
  }
  return Object.values(moodMap)
})

async function deleteMoodNote(noteId) {
  if (!noteId) return
  uni.showModal({
    title: '删除心情', content: '确定删除这条心情吗？',
    success: async (r) => {
      if (r.confirm) {
        try { await diaryAPI.deleteNote(noteId); selectDateStr(selectedDate.value) } catch (e) {}
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.diary-page { min-height: 100vh; background: var(--bg-page, #FFF5F7); padding: 16rpx 24rpx; }

.month-header { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; }
.month-arrow { font-size: 36rpx; color: var(--color-primary, #FF7B93); padding: 12rpx; }
.month-title { font-size: 34rpx; font-weight: 700; color: #4A4A4A; }

.weekdays { display: flex; margin-bottom: 8rpx; }
.wd { flex: 1; text-align: center; font-size: 24rpx; color: #BBB; padding: 12rpx 0; }

.calendar { display: flex; flex-wrap: wrap; background: #FFF; border-radius: 16rpx; padding: 8rpx; }
.cal-cell { width: calc(100% / 7); height: 120rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-radius: 12rpx; overflow: hidden; }
.cal-cell.dim { opacity: 0; pointer-events: none; }
.cal-cell.today { background: var(--bg-input, #FFF0F3); }
.cal-cell.hasOrder { font-weight: 700; }
.cal-moods { display: flex; justify-content: center; gap: 2rpx; height: 32rpx; align-items: center; margin-bottom: 2rpx; }
.cal-mood-emoji { font-size: 24rpx; line-height: 1; }
.cal-day { font-size: 20rpx; color: #4A4A4A; line-height: 1; }
.cal-dot { width: 8rpx; height: 8rpx; border-radius: 50%; background: var(--color-primary, #FF7B93); position: absolute; top: 6rpx; right: 8rpx; }
.cal-special-text { font-size: 16rpx; color: var(--color-primary, #FF7B93); position: absolute; top: 2rpx; left: 4rpx; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 90%; }

.month-summary { text-align: center; }
.ms-title { font-size: 28rpx; font-weight: 600; color: #4A4A4A; display: block; margin-bottom: 20rpx; }
.ms-row { display: flex; gap: 12rpx; margin-bottom: 20rpx; }
.ms-item { flex: 1; background: var(--bg-page, #FFF5F7); border-radius: 12rpx; padding: 20rpx 12rpx; }
.ms-num { font-size: 36rpx; font-weight: 700; color: var(--color-primary, #FF7B93); display: block; }
.ms-label { font-size: 22rpx; color: #999; margin-top: 4rpx; display: block; }
.ms-hint { font-size: 22rpx; color: #CCC; }

.card { background: #FFF; border-radius: 16rpx; padding: 24rpx; margin-top: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.date-title { font-size: 32rpx; font-weight: 700; color: var(--color-primary, #FF7B93); display: block; margin-bottom: 16rpx; }

.day-section { margin-bottom: 20rpx; }
.day-label { font-size: 24rpx; font-weight: 600; color: #888; display: block; margin-bottom: 8rpx; }
.mood-section { margin-bottom: 20rpx; }
.mood-user-list { display: flex; flex-direction: column; gap: 8rpx; }
.mood-user-row { display: flex; align-items: center; gap: 8rpx; padding: 8rpx 0; }
.mood-user-nickname { font-size: 24rpx; color: #999; min-width: 120rpx; }
.mood-user-emoji { font-size: 32rpx; }
.mood-user-desc { font-size: 24rpx; color: #4A4A4A; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mood-user-empty { font-size: 22rpx; color: #CCC; }
.mood-user-del { font-size: 24rpx; padding: 4rpx; }
.day-order { background: var(--bg-page, #FFF5F7); border-radius: 12rpx; padding: 16rpx 20rpx; margin-bottom: 10rpx; }
.do-line { display: flex; padding: 4rpx 0; }
.do-label { font-size: 24rpx; color: #999; width: 100rpx; flex-shrink: 0; }
.do-val { font-size: 24rpx; color: #4A4A4A; }
.do-total { font-size: 28rpx; font-weight: 700; color: var(--color-primary, #FF7B93); text-align: right; margin-top: 6rpx; }

.photo-grid { display: flex; flex-wrap: wrap; gap: 8rpx; }
.photo-thumb { width: calc(33.33% - 6rpx); aspect-ratio: 1; border-radius: 8rpx; }
.photo-add { width: calc(33.33% - 6rpx); aspect-ratio: 1; border-radius: 8rpx; border: 2rpx dashed #DDD; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: #DDD; }

.note-item { padding: 16rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.note-item:last-child { border-bottom: none; }
.note-header { display: flex; align-items: center; gap: 8rpx; margin-bottom: 8rpx; }
.note-user { font-size: 24rpx; font-weight: 600; color: var(--color-primary, #FF7B93); }
.note-mood { font-size: 24rpx; }
.note-time { font-size: 20rpx; color: #CCC; margin-left: auto; }
.note-del { font-size: 24rpx; padding: 4rpx; }
.note-content { font-size: 26rpx; color: #4A4A4A; line-height: 1.6; }
.note-add { text-align: center; padding: 16rpx; color: var(--color-primary, #FF7B93); font-size: 26rpx; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { width: 600rpx; background: #FFF; border-radius: 24rpx; padding: 40rpx; }
.modal-title { font-size: 32rpx; font-weight: 600; text-align: center; display: block; margin-bottom: 20rpx; }
.view-toggle { display: flex; justify-content: center; padding: 12rpx 0; }
.vt-seg { display: flex; background: #F0F0F0; border-radius: 24rpx; padding: 4rpx; }
.vt-btn { font-size: 26rpx; padding: 12rpx 32rpx; border-radius: 20rpx; color: #999; }
.vt-btn.active { background: #FFF; color: var(--color-primary, #FF7B93); font-weight: 600; box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.08); }

.diary-list-view { background: #FFF; border-radius: 16rpx; padding: 16rpx; }
.diary-list-item { padding: 20rpx 16rpx; border-bottom: 1rpx solid #F5F5F5; }
.diary-list-item:last-child { border-bottom: none; }
.dli-header { display: flex; justify-content: space-between; align-items: center; }
.dli-date { font-size: 28rpx; font-weight: 600; color: #4A4A4A; }
.dli-badges { font-size: 28rpx; }
.no-data { text-align: center; padding: 60rpx; color: #CCC; font-size: 26rpx; }

.mood-pick { display: flex; justify-content: center; gap: 16rpx; margin-bottom: 20rpx; }
.mood-opt { font-size: 44rpx; padding: 4rpx; border-radius: 8rpx; }
.mood-opt.selected { background: var(--bg-input, #FFF0F3); }
.note-textarea { background: var(--bg-page, #FFF5F7); border-radius: 12rpx; padding: 20rpx; font-size: 26rpx; width: 100%; min-height: 160rpx; margin-bottom: 20rpx; box-sizing: border-box; }
.note-save-btn { background: linear-gradient(135deg,var(--color-primary, #FF7B93),var(--color-primary-light, #FFB3C6)); color: #FFF; border-radius: 24rpx; font-size: 28rpx; padding: 20rpx; border: none; }
</style>
