import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dishesAPI } from '@/api/dishes'

export const useDishesStore = defineStore('dishes', () => {
  const categories = ref([])
  const dishes = ref([])
  const loading = ref(false)
  const activeCategoryId = ref(0)  // 0 = all

  async function fetchAll() {
    loading.value = true
    try {
      const [catRes, dishRes] = await Promise.all([
        dishesAPI.getCategories(),
        dishesAPI.getDishes(),
      ])
      categories.value = catRes.categories
      dishes.value = dishRes.dishes
    } catch (e) {
      console.error('Failed to fetch dishes:', e)
    } finally {
      loading.value = false
    }
  }

  function setActiveCategory(categoryId) {
    activeCategoryId.value = categoryId
  }

  const filteredDishes = computed(() => {
    if (activeCategoryId.value === 0) return dishes.value
    return dishes.value.filter(d => d.category_id === activeCategoryId.value)
  })

  const categoryWithAll = computed(() => {
    const allCount = dishes.value.filter(d => d.is_available).length
    return [
      { id: 0, name: '全部', icon: '🍽️', dish_count: allCount },
      ...categories.value,
    ]
  })

  return {
    categories, dishes, loading, activeCategoryId,
    fetchAll, setActiveCategory, filteredDishes, categoryWithAll,
  }
})
