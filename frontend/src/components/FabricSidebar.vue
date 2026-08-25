<template>
  <aside class="fabric-sidebar" :class="{ open: open }" dir="rtl">
    <!-- Header -->
    <header class="sidebar-header">
      <div class="header-content">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5z"/>
            <path d="M4 9h16M9 4v16"/>
          </svg>
        </div>
        <div>
          <h2>انتخاب پارچه</h2>
          <p class="subtitle">{{ currentTab === 'quality' ? 'کالیته مورد نظر را انتخاب کنید' : 'رنگ پارچه را انتخاب کنید' }}</p>
        </div>
      </div>
      <button class="close-btn" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </header>

    <!-- Tabs -->
    <nav class="tabs">
      <button class="tab-btn" :class="{ active: currentTab === 'quality' }" @click="currentTab = 'quality'">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 12l2 2 4-4"/><path d="M12 3c-1.155 0-2.31.09-3.437.27a2.5 2.5 0 0 0-2.021 2.021A17.55 17.55 0 0 0 6 9c0 5.49 4.48 9.53 5.48 10.43a1.5 1.5 0 0 0 2.04 0C14.52 18.53 19 14.49 19 9c0-1.245-.09-2.46-.27-3.645a2.5 2.5 0 0 0-2.021-2.021A17.55 17.55 0 0 0 12 3z"/></svg>
        کالیته پارچه
        <span class="tab-count">{{ clothGroups.length }}</span>
      </button>
      <button class="tab-btn" :class="{ active: currentTab === 'color', disabled: !selectedQuality }" @click="selectedQuality && (currentTab = 'color')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 2C8 2 5 6 5 12s3 10 7 10"/><path d="M12 2c4 0 7 4 7 10s-3 10-7 10"/><path d="M2 12h20"/></svg>
        رنگ پارچه
        <span class="tab-count">{{ selectedQuality ? selectedQuality.clothvariants?.length || 0 : 0 }}</span>
      </button>
    </nav>

    <!-- Content -->
    <main class="sidebar-content">
      <!-- Quality Tab -->
      <section v-show="currentTab === 'quality'">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input v-model="qualitySearch" type="text" placeholder="جستجوی کالیته..." />
        </div>
        <div class="fabric-grid">
          <div
            v-for="group in filteredGroups"
            :key="group.name"
            class="fabric-card"
            :class="{ selected: selectedQuality?.name === group.name }"
            @click="selectQuality(group)"
          >
            <div class="fabric-image">
              <img v-if="group.sample_image" :src="group.sample_image" :alt="group.name" loading="lazy" />
              <div v-else class="fabric-placeholder">{{ group.name.slice(0, 2) }}</div>
            </div>
            <div class="fabric-name">{{ group.name }}</div>
            <div class="fabric-price">{{ group.average_purchase_price }} تومان</div>
            <div v-if="group.cloth_nature" class="fabric-nature">{{ group.cloth_nature }}</div>
          </div>
        </div>
        <div v-if="filteredGroups.length === 0" class="no-results">
          <p>کالیته‌ای یافت نشد</p>
        </div>
      </section>

      <!-- Color Tab -->
      <section v-show="currentTab === 'color'">
        <!-- Selected quality info -->
        <div v-if="selectedQuality" class="selected-quality-info">
          <img v-if="selectedQuality.sample_image" :src="selectedQuality.sample_image" :alt="selectedQuality.name" />
          <div class="quality-details">
            <h3>{{ selectedQuality.name }}</h3>
            <p>{{ selectedQuality.average_purchase_price }} تومان</p>
          </div>
          <button class="change-btn" @click="currentTab = 'quality'">تغییر</button>
        </div>
        <div v-else class="select-first">
          <p>ابتدا کالیته پارچه را انتخاب کنید</p>
          <button @click="currentTab = 'quality'">انتخاب کالیته</button>
        </div>

        <div class="search-box" v-if="selectedQuality">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input v-model="colorSearch" type="text" placeholder="جستجوی رنگ..." />
        </div>

        <div class="fabric-grid" v-if="selectedQuality">
          <div
            v-for="variant in filteredColors"
            :key="variant.name || variant.item_name"
            class="fabric-card"
            :class="{ selected: selectedColor?.name === (variant.name || variant.item_name) }"
            @click="selectColor(variant)"
          >
            <div class="fabric-image">
              <img v-if="variant.image" :src="variant.image" :alt="variant.name" loading="lazy" />
              <div v-else class="fabric-placeholder">{{ (variant.name || variant.item_name || '').slice(0, 2) }}</div>
            </div>
            <div class="fabric-name">{{ variant.name || variant.item_name }}</div>
            <div class="fabric-price">{{ variant.formatted_Price }} تومان</div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="sidebar-footer">
      <div class="selection-summary">
        <span class="summary-label">انتخاب شما:</span>
        <span class="selected-fabric-text">
          {{ selectedQuality && selectedColor ? selectedQuality.name + ' - ' + (selectedColor.name || selectedColor.item_name) : 'پارچه‌ای انتخاب نشده' }}
        </span>
      </div>
      <div class="footer-actions">
        <button class="btn-reset" @click="reset">پیش‌فرض</button>
        <button class="btn-apply" @click="apply" :disabled="!selectedQuality || !selectedColor">اعمال</button>
      </div>
    </footer>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  open: Boolean,
  clothGroups: { type: Array, default: () => [] },
  selectedFabric: { type: Object, default: null }
})
const emit = defineEmits(['close', 'select'])

const currentTab = ref('quality')
const qualitySearch = ref('')
const colorSearch = ref('')
const selectedQuality = ref(null)
const selectedColor = ref(null)

const filteredGroups = computed(() => {
  if (!qualitySearch.value) return props.clothGroups
  const q = qualitySearch.value.toLowerCase()
  return props.clothGroups.filter(g => g.name.toLowerCase().includes(q))
})

const filteredColors = computed(() => {
  if (!selectedQuality.value) return []
  const variants = selectedQuality.value.clothvariants || []
  if (!colorSearch.value) return variants
  const q = colorSearch.value.toLowerCase()
  return variants.filter(v => (v.name || v.item_name || '').toLowerCase().includes(q))
})

function selectQuality(group) {
  selectedQuality.value = group
  selectedColor.value = null
  setTimeout(() => { currentTab.value = 'color' }, 200)
}

function selectColor(variant) {
  selectedColor.value = variant
}

function reset() {
  selectedQuality.value = null
  selectedColor.value = null
  currentTab.value = 'quality'
  emit('select', null)
}

function apply() {
  if (!selectedQuality.value || !selectedColor.value) return
  const variant = selectedColor.value
  const priceRaw = variant.Price || 0
  emit('select', {
    qualityName: selectedQuality.value.name,
    colorName: variant.name || variant.item_name,
    pricePerMeter: priceRaw,
    formattedPrice: variant.formatted_Price || '',
    image: variant.image || selectedQuality.value.sample_image || '',
    itemCode: variant.item_code || '',
    code: variant.code || ''
  })
}

function syncFromSelectedFabric() {
  const selected = props.selectedFabric
  if (!selected) {
    selectedQuality.value = null
    selectedColor.value = null
    return
  }

  const group = props.clothGroups.find((g) => g.name === selected.qualityName)
  if (!group) return

  selectedQuality.value = group
  const matchedVariant = (group.clothvariants || []).find((v) => {
    if (selected.itemCode && (v.item_code || '') === selected.itemCode) return true
    return (v.name || v.item_name) === selected.colorName
  })
  if (matchedVariant) {
    selectedColor.value = matchedVariant
  }
}

watch(() => props.selectedFabric, syncFromSelectedFabric, { immediate: true, deep: true })
watch(() => props.clothGroups, syncFromSelectedFabric, { immediate: true, deep: true })
</script>

<style scoped>
.fabric-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 100000;
  width: 420px;
  max-width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  transform: translate3d(100.1%, 0, 0);
  visibility: hidden;
  transition: transform 0.34s cubic-bezier(0.4, 0, 0.2, 1), visibility 0s 0.34s;
}
.fabric-sidebar.open {
  transform: translate3d(0, 0, 0);
  visibility: visible;
  transition: transform 0.34s cubic-bezier(0.4, 0, 0.2, 1), visibility 0s;
  box-shadow: -4px 0 40px rgba(0,0,0,0.2);
}

/* Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: var(--bg-footer);
  color: var(--text-main);
  flex-shrink: 0;
}
.header-content { display: flex; align-items: center; gap: 12px; }
.header-icon { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.15); border-radius: 12px; }
.header-icon svg { width: 22px; height: 22px; }
.sidebar-header h2 { font-size: 18px; font-weight: 700; margin-bottom: 2px; }
.subtitle { font-size: 13px; opacity: 0.8; }
.close-btn { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.1); border: none; border-radius: 50%; color: #fff; cursor: pointer; transition: background 0.15s; }
.close-btn:hover { background: rgba(255,255,255,0.2); }
.close-btn svg { width: 18px; height: 18px; }

/* Tabs */
.tabs { display: flex; border-bottom: 1px solid var(--glass-border); background: var(--bg-secondary); flex-shrink: 0; }
.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px 12px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #888;
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn svg { width: 16px; height: 16px; }
.tab-btn.active { background: var(--bg-main); color: var(--accent-gold); border-bottom-color: var(--accent-gold); }
.tab-btn.disabled { opacity: 0.4; cursor: not-allowed; }
.tab-count { background: #eee; color: #666; padding: 2px 7px; border-radius: 10px; font-size: 12px; font-weight: 600; }
.tab-btn.active .tab-count { background: var(--accent-gold); color: var(--accent-brown); }

/* Content */
.sidebar-content { flex: 1; overflow-y: auto; padding: 16px; }

/* Search */
.search-box { position: relative; margin-bottom: 16px; }
.search-box svg { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: #aaa; pointer-events: none; }
.search-box input { width: 100%; padding: 10px 40px 10px 12px; border: 1px solid var(--glass-border); border-radius: 10px; background: var(--bg-secondary); font-family: inherit; font-size: 14px; color: var(--text-main); }
.search-box input:focus { outline: none; border-color: var(--accent-gold); background: var(--bg-main); }

/* Fabric Grid */
.fabric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.fabric-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 10px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: var(--glass-bg);
  cursor: pointer;
  transition: all 0.2s;
}
.fabric-card:hover { border-color: var(--accent-gold); background: var(--glass-bg-hover); }
.fabric-card.selected { border-color: var(--accent-gold); background: var(--glass-bg-hover); box-shadow: 0 0 0 1px var(--accent-gold); }
.fabric-image { aspect-ratio: 1; border-radius: 8px; overflow: hidden; background: #f0ebe4; margin-bottom: 8px; }
.fabric-image img { width: 100%; height: 100%; object-fit: cover; }
.fabric-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; color: #503130; }
.fabric-name { font-size: 12px; font-weight: 600; color: var(--text-main); text-align: center; margin-bottom: 2px; }
.fabric-price { font-size: 11px; color: var(--accent-gold); text-align: center; }
.fabric-nature { position: absolute; top: -30px; left: 50%; transform: translateX(-50%); background: #333; color: #fff; font-size: 10px; padding: 4px 8px; border-radius: 6px; white-space: nowrap; display: none; }
.fabric-card:hover .fabric-nature { display: block; }

/* Selected quality info */
.selected-quality-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--glass-bg-hover);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  margin-bottom: 16px;
}
.selected-quality-info img { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; }
.quality-details h3 { font-size: 14px; font-weight: 600; color: var(--text-main); }
.quality-details p { font-size: 12px; color: var(--text-muted); }
.change-btn { margin-right: auto; background: var(--bg-main); border: 1px solid var(--glass-border); color: var(--text-main); padding: 6px 12px; border-radius: 8px; font-family: inherit; font-size: 12px; cursor: pointer; }

/* Select first */
.select-first { text-align: center; padding: 32px 16px; color: #888; }
.select-first p { margin-bottom: 12px; font-size: 14px; }
.select-first button { background: var(--accent-gold); color: var(--accent-brown); border: none; padding: 10px 20px; border-radius: 8px; font-family: inherit; font-size: 14px; cursor: pointer; }

/* No results */
.no-results { text-align: center; padding: 32px; color: #aaa; font-size: 14px; }

/* Footer */
.sidebar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid var(--glass-border);
  background: var(--bg-main);
  flex-shrink: 0;
}
.selection-summary { display: flex; flex-direction: column; gap: 2px; }
.summary-label { font-size: 12px; color: #aaa; }
.selected-fabric-text { font-size: 14px; font-weight: 600; color: var(--accent-gold); }
.footer-actions { display: flex; gap: 8px; }
.btn-reset { padding: 10px 16px; background: var(--bg-secondary); border: 1px solid var(--glass-border); color: var(--text-main); border-radius: 8px; font-family: inherit; font-size: 13px; cursor: pointer; }
.btn-apply { padding: 10px 16px; background: var(--accent-gold); color: var(--accent-brown); border: none; border-radius: 8px; font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-apply:disabled { opacity: 0.4; cursor: not-allowed; }

@media (max-width: 900px) {
  .fabric-sidebar {
    top: auto;
    right: 0;
    left: 0;
    bottom: 0;
    width: 100%;
    max-width: 100%;
    /* Use stable viewport height on mobile to avoid sudden resize while scrolling */
    height: min(76svh, 720px);
    max-height: 76svh;
    border-radius: 22px 22px 0 0;
    transform: translate3d(0, 100.1%, 0);
  }

  .fabric-sidebar.open {
    transform: translate3d(0, 0, 0);
    box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.28);
  }

  .sidebar-header {
    padding: 14px 16px;
    border-radius: 22px 22px 0 0;
  }

  .tabs {
    position: sticky;
    top: 0;
    z-index: 2;
  }

  .sidebar-content {
    padding: 12px;
  }

  .fabric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .sidebar-footer {
    padding: 12px 14px calc(12px + env(safe-area-inset-bottom, 0px));
  }
}
</style>
