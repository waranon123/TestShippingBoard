<template>
  <v-container fluid fill-height>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login to Truck Management System</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="login" ref="form">
              <v-text-field
                v-model="username"
                prepend-icon="mdi-account"
                label="Username"
                required
                :rules="[v => !!v || 'Username is required']"
              ></v-text-field>
              <v-text-field
                v-model="password"
                prepend-icon="mdi-lock"
                label="Password"
                type="password"
                required
                :rules="[v => !!v || 'Password is required']"
              ></v-text-field>
              <v-alert v-if="error" type="error" class="mb-3">
                {{ error }}
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="login" :loading="loading">Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref(null)
const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)
const error = ref('')

const login = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return
  
  loading.value = true
  error.value = ''
  
  try {
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push('/dashboard')
    } else {
      error.value = 'Invalid username or password'
    }
  } catch (err) {
    error.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>