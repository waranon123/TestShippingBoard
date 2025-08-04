<!-- frontend/src/App.vue -->
<template>
  <v-app>
    <!-- Navigation Drawer -->
    <v-navigation-drawer v-if="showNavigation" v-model="drawer" app>
      <v-list nav>
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          value="dashboard"
          :to="{ name: 'dashboard' }"
        ></v-list-item>
        
        <v-list-item
          v-if="canManage"
          prepend-icon="mdi-truck"
          title="Management"
          value="management"
          :to="{ name: 'management' }"
        ></v-list-item>
        
        <v-list-item
          prepend-icon="mdi-chart-box"
          title="Statistics"
          value="statistics"
          :to="{ name: 'statistics' }"
        ></v-list-item>
        
        <v-list-item
          prepend-icon="mdi-television"
          title="TV View"
          value="tv"
          :to="{ name: 'tv' }"
        ></v-list-item>
      </v-list>
      
      <template v-slot:append>
        <v-divider></v-divider>
        <v-list>
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            @click="logout"
          ></v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar v-if="showNavigation" app color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Truck Management System</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-chip v-if="user" color="white" text-color="primary">
        {{ user.username }} ({{ user.role }})
      </v-chip>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <router-view />
    </v-main>

    <!-- Global Snackbar -->
    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      :multi-line="snackbar.multiLine"
      location="top right"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.hide()">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSnackbarStore } from '@/stores/snackbar'
import axios from 'axios'

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

  // Set base URL
  axios.defaults.baseURL = 'http://localhost:8000'
  
  // Initialize auth if token exists
  if (authStore.token) {
    authStore.fetchUser()
  }
})
</script>

<style>
/* Global styles */
.v-application {
  font-family: 'Roboto', sans-serif;
}

.cursor-pointer {
  cursor: pointer;
}
</style>