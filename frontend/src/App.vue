<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSnackbarStore } from '@/stores/snackbar'
import axios from 'axios'
import API_BASE_URL from '@/config/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const snackbar = useSnackbarStore()

const drawer = ref(true)

// Computed properties
const showNavigation = computed(() => {
  return authStore.isAuthenticated && route.name !== 'login'
})

const user = computed(() => authStore.user)
const canManage = computed(() => authStore.hasRole('user'))

// Methods
const logout = () => {
  authStore.logout()
  router.push('/login')
}

// Set up axios interceptors
onMounted(() => {
  // Set base URL
  axios.defaults.baseURL = API_BASE_URL
  
  // Request interceptor
  axios.interceptors.request.use(
    (config) => {
      if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        authStore.logout()
        router.push('/login')
      }
      return Promise.reject(error)
    }
  )
  
  // Initialize auth if token exists
  if (authStore.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`
    authStore.fetchUser()
  }
})
</script>
