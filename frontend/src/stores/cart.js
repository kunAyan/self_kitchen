import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])  // [{ dish, quantity }]

  const totalCount = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const totalAmount = computed(() =>
    items.value.reduce((s, i) => s + i.dish.price * i.quantity, 0)
  )

  function addDish(dish, quantity = 1) {
    const existing = items.value.find(i => i.dish.id === dish.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({ dish, quantity })
    }
  }

  function removeDish(dishId) {
    items.value = items.value.filter(i => i.dish.id !== dishId)
  }

  function updateQuantity(dishId, quantity) {
    if (quantity <= 0) {
      removeDish(dishId)
      return
    }
    const item = items.value.find(i => i.dish.id === dishId)
    if (item) {
      item.quantity = quantity
    }
  }

  function clear() {
    items.value = []
  }

  return { items, totalCount, totalAmount, addDish, removeDish, updateQuantity, clear }
})
