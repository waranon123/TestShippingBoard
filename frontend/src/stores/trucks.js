
import { defineStore } from 'pinia'
import axios from 'axios'

export const useTruckStore = defineStore('trucks', {
  state: () => ({
    trucks: [],
    stats: {
      total_trucks: 0,
      preparation_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
      loading_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
      terminal_stats: {}
    },
    loading: false,
    error: null,
    websocket: null,
    dateFilter: {
      fromDate: null,
      toDate: null
    }
  }),

  actions: {
    async fetchTrucks(filters = {}) {
      this.loading = true
      try {
        const allFilters = {
          ...filters,
          date_from: this.dateFilter.fromDate,
          date_to: this.dateFilter.toDate
        }

        Object.keys(allFilters).forEach(key => {
          if (allFilters[key] === undefined || allFilters[key] === null) {
            delete allFilters[key]
          }
        })

        const params = new URLSearchParams(allFilters)
        const response = await axios.get(`/api/trucks?${params}`)
        this.trucks = response.data || []
      } catch (error) {
        this.error = error.message
        this.trucks = []
      } finally {
        this.loading = false
      }
    },

    setDateFilter(fromDate, toDate) {
      this.dateFilter.fromDate = fromDate
      this.dateFilter.toDate = toDate
    },

    async fetchStats(filters = {}) {
      try {
        const allFilters = {
          ...filters,
          date_from: this.dateFilter.fromDate,
          date_to: this.dateFilter.toDate
        }

        Object.keys(allFilters).forEach(key => {
          if (allFilters[key] === undefined || allFilters[key] === null) {
            delete allFilters[key]
          }
        })

        const params = new URLSearchParams(allFilters)
        const response = await axios.get(`/api/stats?${params}`)
        this.stats = response.data || {
          total_trucks: 0,
          preparation_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
          loading_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
          terminal_stats: {}
        }
        return this.stats
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        this.stats = {
          total_trucks: 0,
          preparation_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
          loading_stats: { 'On Process': 0, Delay: 0, Finished: 0 },
          terminal_stats: {}
        }
        return this.stats
      }
    },

    async createTruck(truckData) {
      try {
        const response = await axios.post('/api/trucks', truckData)
        return response.data
      } catch (error) {
        throw error
      }
    },

    async updateTruck(id, truckData) {
      try {
        const response = await axios.put(`/api/trucks/${id}`, truckData)
        return response.data
      } catch (error) {
        throw error
      }
    },

    async deleteTruck(id) {
      try {
        await axios.delete(`/api/trucks/${id}`)
      } catch (error) {
        throw error
      }
    },

    async updateStatus(id, statusType, status) {
      try {
        const response = await axios.patch(`/api/trucks/${id}/status`, null, {
          params: { status_type: statusType, status }
        })
        return response.data
      } catch (error) {
        throw error
      }
    },

    connectWebSocket() {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      this.websocket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`)

      this.websocket.onmessage = async (event) => {
        const message = JSON.parse(event.data)

        switch (message.type) {
          case 'truck_created':
            if (this.isWithinDateFilter(message.data.created_at)) {
              this.trucks.push(message.data)
              await this.fetchStats() // Refresh stats on truck creation
            }
            break
          case 'truck_updated':
          case 'status_updated':
            const index = this.trucks.findIndex(t => t.id === message.data.id)
            if (index !== -1) {
              this.trucks[index] = message.data
              await this.fetchStats() // Refresh stats on update
            }
            break
          case 'truck_deleted':
            this.trucks = this.trucks.filter(t => t.id !== message.data.id)
            await this.fetchStats() // Refresh stats on deletion
            break
        }
      }

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    },

    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close()
        this.websocket = null
      }
    },

    isWithinDateFilter(dateString) {
      if (!this.dateFilter.fromDate && !this.dateFilter.toDate) return true

      const date = new Date(dateString)
      const dateOnly = date.toISOString().split('T')[0]

      if (this.dateFilter.fromDate && dateOnly < this.dateFilter.fromDate) return false
      if (this.dateFilter.toDate && dateOnly > this.dateFilter.toDate) return false

      return true
    }
  }
})
