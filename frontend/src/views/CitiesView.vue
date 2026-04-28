<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Gradovi / općine</h1>
        <p>Pregled gradova i općina s pozivnim i poštanskim brojevima.</p>
      </div>
    </div>

    <section class="panel">
      <div class="filters">
        <div class="field search-field">
          <label>Pretraga</label>
          <div class="search-wrap">
            <svg class="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="filters.search" type="text" placeholder="Grad, regija, poštanski broj, pozivni..." />
            <button v-if="filters.search" class="clear-btn" @click="filters.search = ''">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>

        <div class="field">
          <label>Entitet</label>
          <select v-model="filters.entity_id" @change="onEntityChange">
            <option value="">Svi entiteti</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Regija</label>
          <select v-model="filters.region_id">
            <option value="">Sve regije</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis gradova/općina</h2>
        <span class="count-pill">{{ filteredCities.length }} gradova</span>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>Učitavanje...</span>
      </div>

      <template v-else>
        <table>
          <thead>
            <tr>
              <th>Grad/općina</th>
              <th>Entitet / Regija</th>
              <th>Pozivni</th>
              <th>Poštanski brojevi</th>
              <th class="center">Pošte</th>
              <th class="center">Lokacije</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="city in visibleCities" :key="city.id">
              <td>
                <div class="city-name">{{ city.name }}</div>
                <div class="city-id">ID {{ city.id }}</div>
              </td>

              <td>
                <div class="td-primary">{{ city.entity_name }}</div>
                <div class="td-secondary">{{ city.region_name }}</div>
              </td>

              <td>
                <span v-if="city.area_code" class="area-badge">{{ city.area_code }}</span>
                <span v-else class="muted">—</span>
              </td>

              <td>
                <div v-if="city.postal_codes.length" class="postal-list">
                  <span v-for="postal in city.postal_codes" :key="postal.id" class="postal-badge">
                    <span class="postal-code">{{ postal.postal_code }}</span>
                    <span class="postal-sep">·</span>
                    {{ postal.postal_name }}
                  </span>
                </div>
                <span v-else class="muted">—</span>
              </td>

              <td class="center">
                <span class="num-badge">{{ city.postal_codes.length }}</span>
              </td>

              <td class="center">
                <span class="num-badge" :class="city.locations_count > 0 ? 'dark' : 'zero'">
                  {{ city.locations_count }}
                </span>
              </td>
            </tr>

            <tr v-if="filteredCities.length === 0">
              <td colspan="6" class="empty">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <p>Nema rezultata za odabrane filtere.</p>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Load more -->
        <div v-if="hasMore" class="load-more-row">
          <div class="load-more-info">
            Prikazano {{ visibleCities.length }} od {{ filteredCities.length }}
          </div>
          <button class="load-more-btn" @click="loadMore">
            Prikaži još {{ Math.min(perPage, filteredCities.length - visibleCount) }}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
        </div>

        <div v-else-if="filteredCities.length > perPage" class="all-loaded">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          Svi gradovi su prikazani
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import api from "../api/client";

const entities = ref([]);
const regions = ref([]);
const cities = ref([]);
const postalCodes = ref([]);
const areaCodes = ref([]);
const locations = ref([]);
const loading = ref(false);

const perPage = 20;
const visibleCount = ref(perPage);

const filters = reactive({ search: "", entity_id: "", region_id: "" });

// Reset visible count when filters change
watch(filters, () => { visibleCount.value = perPage; });

const enrichedCities = computed(() =>
  cities.value.map((city) => {
    const region = regions.value.find((r) => Number(r.id) === Number(city.region_id));
    const entity = entities.value.find((e) => Number(e.id) === Number(region?.entity_id));
    const areaCode = areaCodes.value.find((ac) => Number(ac.region_id) === Number(city.region_id));
    const cityPostals = postalCodes.value.filter((p) => Number(p.city_id) === Number(city.id));
    const cityLocs = locations.value.filter((l) => Number(l.city_id) === Number(city.id));

    return {
      ...city,
      region_name: region?.name || "—",
      entity_id: region?.entity_id || null,
      entity_name: entity?.name || "—",
      area_code: areaCode?.code || null,
      postal_codes: cityPostals,
      locations_count: cityLocs.length,
    };
  })
);

const filteredCities = computed(() => {
  const q = filters.search.trim().toLowerCase();
  return enrichedCities.value.filter((city) => {
    if (filters.entity_id && Number(city.entity_id) !== Number(filters.entity_id)) return false;
    if (filters.region_id && Number(city.region_id) !== Number(filters.region_id)) return false;
    if (!q) return true;

    const postalText = city.postal_codes
      .map((p) => `${p.postal_code} ${p.postal_name}`)
      .join(" ")
      .toLowerCase();

    return (
      city.name.toLowerCase().includes(q) ||
      city.region_name.toLowerCase().includes(q) ||
      city.entity_name.toLowerCase().includes(q) ||
      String(city.area_code || "").includes(q) ||
      postalText.includes(q)
    );
  });
});

const visibleCities = computed(() =>
  filteredCities.value.slice(0, visibleCount.value)
);

const hasMore = computed(() =>
  visibleCount.value < filteredCities.value.length
);

function loadMore() {
  visibleCount.value += perPage;
}

async function loadEntities() {
  const r = await api.get("/entities");
  entities.value = r.data;
}

async function loadRegions() {
  const r = await api.get("/regions");
  regions.value = r.data;
}

async function loadCities() {
  const r = await api.get("/cities");
  cities.value = r.data;
}

async function loadPostalCodes() {
  const r = await api.get("/postal-codes");
  postalCodes.value = r.data;
}

async function loadAreaCodes() {
  const r = await api.get("/area-codes");
  areaCodes.value = r.data;
}

async function loadLocations() {
  const r = await api.get("/locations");
  locations.value = r.data;
}

async function onEntityChange() {
  filters.region_id = "";
  if (!filters.entity_id) {
    await loadRegions();
    return;
  }
  const r = await api.get(`/regions?entity_id=${filters.entity_id}`);
  regions.value = r.data;
}

onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([
      loadEntities(),
      loadRegions(),
      loadCities(),
      loadPostalCodes(),
      loadAreaCodes(),
      loadLocations(),
    ]);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 28px; color: #111827; font-weight: 700; }
.page-header p { margin-top: 5px; color: #6b7280; font-size: 14px; }

.panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 22px 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.04);
}

.filters {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 14px;
}

.field { display: flex; flex-direction: column; gap: 6px; }

label { font-size: 13px; color: #374151; font-weight: 600; }

/* Search */
.search-wrap { position: relative; }
.search-icon {
  position: absolute; left: 11px; top: 50%;
  transform: translateY(-50%);
  color: #9ca3af; pointer-events: none;
}
.search-wrap input { padding-left: 34px; padding-right: 32px; width: 100%; box-sizing: border-box; }
.clear-btn {
  position: absolute; right: 8px; top: 50%;
  transform: translateY(-50%);
  background: #e5e7eb; color: #6b7280;
  border: none; border-radius: 6px;
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; padding: 0;
}
.clear-btn:hover { background: #d1d5db; }

input, select {
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  padding: 10px 12px;
  font-size: 13px;
  background: #fafafa;
  color: #111827;
  transition: 0.15s;
}
input:focus, select:focus {
  outline: none;
  border-color: #dc2626;
  background: white;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
}

/* Panel header */
.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.panel-header h2 { margin: 0; font-size: 16px; font-weight: 700; color: #111827; }

.count-pill {
  background: #f3f4f6;
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
}

/* Table */
table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  background: #f9fafb;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 10px 12px;
  border-bottom: 1px solid #f3f4f6;
}
th.center { text-align: center; }
td {
  padding: 11px 12px;
  border-bottom: 1px solid #f9fafb;
  font-size: 13px;
  color: #374151;
  vertical-align: top;
}
td.center { text-align: center; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }

.city-name { font-weight: 600; color: #111827; font-size: 14px; }
.city-id { font-size: 11px; color: #d1d5db; margin-top: 2px; font-family: monospace; }

.td-primary { font-weight: 500; color: #374151; }
.td-secondary { font-size: 12px; color: #9ca3af; margin-top: 2px; }

.area-badge {
  display: inline-flex;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(220,38,38,0.1);
  color: #991b1b;
  font-family: monospace;
}

.postal-list { display: flex; flex-wrap: wrap; gap: 5px; }
.postal-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 8px;
  font-size: 12px;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #dbeafe;
}
.postal-code { font-family: monospace; font-weight: 600; }
.postal-sep { color: #93c5fd; }

.num-badge {
  display: inline-flex;
  min-width: 28px; height: 24px;
  align-items: center; justify-content: center;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  background: #f3f4f6;
  color: #374151;
}
.num-badge.dark { background: #111827; color: white; }
.num-badge.zero { background: #f9fafb; color: #d1d5db; }

.muted { color: #d1d5db; font-size: 13px; }

/* Loading */
.loading-state {
  display: flex; align-items: center; justify-content: center;
  gap: 10px; padding: 48px;
  color: #9ca3af; font-size: 14px;
}
.spinner {
  width: 20px; height: 20px;
  border: 2px solid #f3f4f6;
  border-top-color: #dc2626;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Empty */
.empty {
  text-align: center;
  padding: 48px 20px;
  color: #9ca3af;
}
.empty svg { display: block; margin: 0 auto 10px; color: #d1d5db; }
.empty p { margin: 0; font-size: 14px; }

/* Load more */
.load-more-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 12px 4px;
  border-top: 1px solid #f3f4f6;
  margin-top: 4px;
}
.load-more-info { font-size: 13px; color: #9ca3af; }
.load-more-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.15s;
}
.load-more-btn:hover {
  border-color: #dc2626;
  color: #dc2626;
  background: rgba(220,38,38,0.03);
}

.all-loaded {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 18px 12px 4px;
  border-top: 1px solid #f3f4f6;
  margin-top: 4px;
  font-size: 13px;
  color: #9ca3af;
}
.all-loaded svg { color: #16a34a; }

@media (max-width: 900px) {
  .filters { grid-template-columns: 1fr 1fr; }
  .search-field { grid-column: span 2; }
}
@media (max-width: 600px) {
  .filters { grid-template-columns: 1fr; }
  .search-field { grid-column: span 1; }
}
</style>