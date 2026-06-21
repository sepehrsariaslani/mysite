<template>
  <div class="dealers-page" dir="rtl">
    <CategoryBar />

    <section class="dealers-section">
      <div class="dealers-hero">
        <h1>نمایندگی‌های فروش دنروم</h1>
        <p>نزدیک‌ترین نمایندگی را در شهر خود پیدا کنید</p>
        <div class="search-bar">
          <input type="text" placeholder="نام شهر یا استان..." v-model="searchQuery">
        </div>
      </div>

      <div class="dealers-content">
        <div class="map-container">
          <div class="map-header">
            <h3>نقشه ایران</h3>
            <span class="selected-province">{{ selectedProvinceName || 'یک استان را انتخاب کنید' }}</span>
          </div>
          <div class="iran-map">
            <!-- Simplified Iran SVG -->
            <svg viewBox="0 0 700 730" class="iran-svg">
              <path v-for="p in provincePaths" :key="p.id"
                :id="p.id" :d="p.d"
                :class="{ 'has-dealer': p.hasDealer, 'selected': selectedProvince === p.id }"
                @click="selectProvince(p.id)"
                @mouseenter="hoverProvince = p.name"
                @mouseleave="hoverProvince = ''"
              />
            </svg>
          </div>
        </div>

        <div class="dealers-list-panel">
          <div class="list-header">
            <h2>نمایندگی‌ها</h2>
            <span class="count">{{ filteredDealers.length }} مورد</span>
          </div>
          <div class="dealers-grid">
            <div class="dealer-card" v-for="d in filteredDealers" :key="d.id">
              <div class="dealer-info">
                <h3>{{ d.name }}</h3>
                <p>{{ d.city }}، {{ d.provinceName }}</p>
                <span class="badge" :class="d.badge">{{ d.badge === 'gold' ? 'طلایی' : 'نقره‌ای' }}</span>
              </div>
              <div class="dealer-contact">
                <span>{{ d.phone }}</span>
                <span>{{ d.workHours }}</span>
              </div>
            </div>
          </div>
          <div v-if="filteredDealers.length === 0" class="empty-state">
            موردی یافت نشد
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CategoryBar from '../components/CategoryBar.vue'

const searchQuery = ref('')
const selectedProvince = ref(null)
const hoverProvince = ref('')
const dealers = ref([])

const provincePaths = [
  { id: 'tehran', name: 'تهران', hasDealer: true, d: 'M262,172 L285,188 L318,192 L350,185 L365,160 L380,165 L385,215 L365,245 L330,258 L295,255 L265,235 L252,205 Z' },
  { id: 'isfahan', name: 'اصفهان', hasDealer: true, d: 'M198,312 L232,305 L245,325 L265,335 L298,325 L335,355 L372,410 L388,470 L365,525 L318,548 L260,538 L212,515 L178,478 L165,432 L175,382 L185,342 Z' },
  { id: 'fars', name: 'فارس', hasDealer: true, d: 'M142,502 L162,475 L178,478 L212,515 L260,538 L318,548 L365,525 L388,568 L365,618 L315,648 L252,658 L195,642 L148,608 L125,562 L122,518 Z' }
]

onMounted(async () => {
  try {
    const res = await fetch('/api/method/mysite.api.get_dealers')
    const data = await res.json()
    dealers.value = data.message || []
  } catch (err) {
    console.error('Failed to fetch dealers:', err)
  }
})

const selectedProvinceName = computed(() => {
  if (hoverProvince.value) return hoverProvince.value
  const p = provincePaths.find(x => x.id === selectedProvince.value)
  return p ? p.name : ''
})

const filteredDealers = computed(() => {
  return dealers.value.filter(d => {
    const mProvince = !selectedProvince.value || d.province === selectedProvince.value
    const mSearch = !searchQuery.value || (d.name || '').includes(searchQuery.value) || (d.city || '').includes(searchQuery.value)
    return mProvince && mSearch
  })
})

function selectProvince(id) {
  selectedProvince.value = (selectedProvince.value === id) ? null : id
}
</script>

<style scoped>
.dealers-page {
  background: #0a0a0a;
  min-height: 100vh;
  font-family: 'Peyda', sans-serif;
  color: white;
}

.dealers-hero {
  padding: 120px 24px 60px;
  text-align: center;
  position: relative;
  z-index: 10;
}

.dealers-hero h1 { font-size: 3.5rem; font-weight: 1000; margin-bottom: 16px; color: white; }
.dealers-hero p { font-size: 1.25rem; color: rgba(255, 255, 255, 0.4); margin-bottom: 40px; }

.search-bar {
  max-width: 600px;
  margin: 0 auto;
}
.search-bar input {
  width: 100%;
  padding: 18px 28px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  color: white;
  font-family: inherit;
  font-size: 1.1rem;
  transition: 0.3s;
}
.search-bar input:focus {
  background: rgba(255, 255, 255, 0.05);
  border-color: white;
  outline: none;
}

.dealers-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 100px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 40px;
}

.map-container {
  background: rgba(255, 255, 255, 0.03);
  padding: 40px;
  border-radius: 40px;
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 100px rgba(0,0,0,0.5);
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}
.map-header h3 { font-size: 1.5rem; font-weight: 900; }
.selected-province { color: #ff9800; font-weight: 800; }

.iran-map {
  padding: 20px;
}
.iran-svg path {
  fill: rgba(255, 255, 255, 0.05);
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 1;
  transition: 0.3s;
  cursor: pointer;
}
.iran-svg path:hover { fill: rgba(255, 255, 255, 0.1); }
.iran-svg path.has-dealer { fill: rgba(255, 152, 0, 0.2); }
.iran-svg path.selected { fill: #ff9800; stroke: white; stroke-width: 2; }

.dealers-list-panel {
  background: rgba(255, 255, 255, 0.03);
  padding: 40px;
  border-radius: 40px;
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 100px rgba(0,0,0,0.5);
}
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.list-header h2 { font-size: 2rem; font-weight: 900; }
.count { font-weight: 900; color: #ff9800; font-size: 1.4rem; }

.dealers-grid { display: flex; flex-direction: column; gap: 20px; max-height: 700px; overflow-y: auto; padding-right: 10px; }
.dealers-grid::-webkit-scrollbar { width: 4px; }
.dealers-grid::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }

.dealer-card {
  background: rgba(255, 255, 255, 0.02);
  padding: 30px;
  border-radius: 28px;
  cursor: pointer;
  transition: 0.4s;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.dealer-card:hover { border-color: white; transform: translateX(-8px); background: rgba(255, 255, 255, 0.05); }

.dealer-info h3 { color: white; font-size: 1.3rem; margin-bottom: 8px; font-weight: 800; }
.dealer-info p { color: rgba(255, 255, 255, 0.5); font-weight: 500; margin-bottom: 12px; }

.badge { font-size: 0.75rem; padding: 5px 14px; border-radius: 100px; color: white; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; }
.badge.gold { background: linear-gradient(135deg, #ff9800, #f44336); box-shadow: 0 10px 20px rgba(244, 67, 54, 0.2); }
.badge.silver { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.1); }

.dealer-contact { display: flex; gap: 30px; margin-top: 20px; font-size: 0.95rem; color: rgba(255, 255, 255, 0.4); border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 20px; font-weight: 600; }

@media (max-width: 1024px) { .dealers-content { grid-template-columns: 1fr; } }
</style>
