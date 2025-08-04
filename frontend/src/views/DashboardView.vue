<!-- frontend/src/views/DashboardView.vue - เพิ่ม Date Filter -->
<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <span class="text-h5">Truck Management Dashboard</span>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="exportCSV" prepend-icon="mdi-download">
              Export CSV
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <!-- Date Filter Component -->
            <DateFilter
              v-model:from-date="dateFrom"
              v-model:to-date="dateTo"
              @change="handleDateChange"
            />
            
            <v-divider class="mb-4"></v-divider>
            
            <!-- Search Field -->
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-text>
          
          <v-data-table
            :headers="headers"
            :items="filteredTrucks"
            :search="search"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.created_at="{ item }">
              {{ formatDateTime(item.created_at) }}
            </template>
            
            <template v-slot:item.status_preparation="{ item }">
              <StatusChip
                :status="item.status_preparation"
                @click="updateStatus(item.id, 'preparation', item.status_preparation)"
              />
            </template>
            
            <template v-slot:item.status_loading="{ item }">
              <StatusChip
                :status="item.status_loading"
                @click="updateStatus(item.id, 'loading', item.status_loading)"
              />
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                class="mr-2"
                @click="editItem(item)"
                v-if="canEdit"
              >
                mdi-pencil
              </v-icon>
              <v-icon
                small
                @click="deleteItem(item)"
                v-if="canDelete"
              >
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Edit Dialog (unchanged) -->
    <v-dialog v-model="dialog" max-width="500px">
      <!-- ... existing dialog content ... -->
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTruckStore } from '@/stores/trucks'
import StatusChip from '@/components/StatusChip.vue'
import DateFilter from '@/components/DateFilter.vue'
import { saveAs } from 'file-saver'

const authStore = useAuthStore()
const truckStore = useTruckStore()

// Date filter states
const dateFrom = ref(null)
const dateTo = ref(null)

const search = ref('')
const dialog = ref(false)
const editedIndex = ref(-1)
const editedItem = ref({
  terminal: '',
  truck_no: '',
  dock_code: '',
  truck_route: '',
  preparation_start: '',
  preparation_end: '',
  loading_start: '',
  loading_end: ''
})

const defaultItem = {
  terminal: '',
  truck_no: '',
  dock_code: '',
  truck_route: '',
  preparation_start: '',
  preparation_end: '',
  loading_start: '',
  loading_end: ''
}

const headers = [
  { title: 'Date', key: 'created_at' },
  { title: 'Terminal', key: 'terminal' },
  { title: 'Truck No.', key: 'truck_no' },
  { title: 'Dock Code', key: 'dock_code' },
  { title: 'Truck Route', key: 'truck_route' },
  { title: 'Prep. Start', key: 'preparation_start' },
  { title: 'Prep. End', key: 'preparation_end' },
  { title: 'Loading Start', key: 'loading_start' },
  { title: 'Loading End', key: 'loading_end' },
  { title: 'Prep. Status', key: 'status_preparation' },
  { title: 'Loading Status', key: 'status_loading' },
 // { title: 'Actions', key: 'actions', sortable: false }
]

const loading = computed(() => truckStore.loading)
const trucks = computed(() => truckStore.trucks)
const filteredTrucks = computed(() => trucks.value)
const canEdit = computed(() => authStore.hasRole('user'))
const canDelete = computed(() => authStore.hasRole('admin'))

// Date filter handler
const handleDateChange = () => {
  truckStore.setDateFilter(dateFrom.value, dateTo.value)
  truckStore.fetchTrucks()
}

// Format date time
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateStatus = async (id, type, currentStatus) => {
  if (!canEdit.value) return
  
  const statuses = ['On Process', 'Delay', 'Finished']
  const currentIndex = statuses.indexOf(currentStatus)
  const nextStatus = statuses[(currentIndex + 1) % 3]
  
  try {
    await truckStore.updateStatus(id, type, nextStatus)
  } catch (error) {
    console.error('Failed to update status:', error)
  }
}

const editItem = (item) => {
  editedIndex.value = trucks.value.indexOf(item)
  editedItem.value = Object.assign({}, item)
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this truck?')) {
    try {
      await truckStore.deleteTruck(item.id)
    } catch (error) {
      console.error('Failed to delete truck:', error)
    }
  }
}

const close = () => {
  dialog.value = false
  editedItem.value = Object.assign({}, defaultItem)
  editedIndex.value = -1
}

const save = async () => {
  try {
    if (editedIndex.value > -1) {
      await truckStore.updateTruck(trucks.value[editedIndex.value].id, editedItem.value)
    } else {
      await truckStore.createTruck(editedItem.value)
    }
    close()
  } catch (error) {
    console.error('Failed to save truck:', error)
  }
}

const exportCSV = () => {
  const csvContent = [
    headers.filter(h => h.key !== 'actions').map(h => h.title).join(','),
    ...trucks.value.map(truck => 
      headers.filter(h => h.key !== 'actions').map(h => {
        if (h.key === 'created_at') {
          return formatDateTime(truck[h.key])
        }
        return truck[h.key] || ''
      }).join(',')
    )
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const fileName = dateFrom.value && dateTo.value 
    ? `truck_data_${dateFrom.value}_to_${dateTo.value}.csv`
    : `truck_data_${new Date().toISOString().split('T')[0]}.csv`
  saveAs(blob, fileName)
}

onMounted(() => {
  truckStore.fetchTrucks()
})
</script>