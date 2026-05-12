<template>
  <div>
    <div class="page-header">
      <div>
        <h1><i class="ti ti-building"></i> Gradovi / općine</h1>
        <p>Pregled gradova i općina s pozivnim i poštanskim brojevima.</p>
      </div>
    </div>

    <section class="panel">
      <div class="filters">
        <div class="field search-field">
          <label>Pretraga</label>
          <div class="search-wrap">
            <i class="ti ti-search search-icon"></i>
            <input v-model="filters.search" type="text" placeholder="Grad, regija, poštanski broj, pozivni..." />
            <button v-if="filters.search" class="clear-btn" @click="filters.search = ''">
              <i class="ti ti-x"></i>
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
                <i class="ti ti-search-off empty-icon"></i>
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
            <i class="ti ti-chevron-down"></i>
          </button>
        </div>

        <div v-else-if="filteredCities.length > perPage" class="all-loaded">
          <i class="ti ti-circle-check" style="color: #16a34a;"></i>
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
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { font-family: 'Geist', sans-serif; }

/* ── Page Header ── */
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #111827;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.3px;
}
.page-header h1 i {
  font-size: 26px;
  color: #1B4FD8;
}
.page-header p {
  margin-top: 5px;
  color: #6B7280;
  font-size: 14px;
}

/* ── Panel ── */
.panel {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

/* ── Filters ── */
.filters {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 12px;
  color: #374151;
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Search */
.search-wrap { position: relative; }
.search-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  font-size: 15px;
  pointer-events: none;
}
.search-wrap input {
  padding-left: 34px;
  padding-right: 36px;
  width: 100%;
  box-sizing: border-box;
}
.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #E5E7EB;
  color: #6B7280;
  border: none;
  border-radius: 6px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  font-size: 12px;
}
.clear-btn:hover { background: #D1D5DB; }

input, select {
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 9px 12px;
  font-size: 13px;
  background: #FAFAFA;
  color: #111827;
  font-family: 'Geist', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
input:focus, select:focus {
  outline: none;
  border-color: #DC2626;
  background: white;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.08);
}

/* ── Panel Header ── */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.panel-header h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

.count-pill {
  background: #F3F4F6;
  color: #6B7280;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
}

/* ── Table ── */
table { width: 100%; border-collapse: collapse; }

th {
  text-align: left;
  background: #F9FAFB;
  color: #9CA3AF;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  padding: 10px 12px;
  border-bottom: 1px solid #F3F4F6;
}
th.center { text-align: center; }

td {
  padding: 11px 12px;
  border-bottom: 1px solid #F9FAFB;
  font-size: 13px;
  color: #374151;
  vertical-align: top;
}
td.center { text-align: center; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #FAFAFA; }

.city-name { font-weight: 600; color: #111827; font-size: 13.5px; }
.city-id { font-size: 11px; color: #D1D5DB; margin-top: 2px; font-family: monospace; }

.td-primary { font-weight: 500; color: #374151; }
.td-secondary { font-size: 12px; color: #9CA3AF; margin-top: 2px; }

.area-badge {
  display: inline-flex;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(220, 38, 38, 0.08);
  color: #991B1B;
  border: 1px solid rgba(220, 38, 38, 0.15);
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
  background: #EFF6FF;
  color: #1B4FD8;
  border: 1px solid #DBEAFE;
}
.postal-code { font-family: monospace; font-weight: 600; }
.postal-sep { color: #93C5FD; }

.num-badge {
  display: inline-flex;
  min-width: 28px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  background: #F3F4F6;
  color: #374151;
}
.num-badge.dark { background: #111827; color: white; }
.num-badge.zero { background: #F9FAFB; color: #D1D5DB; }

.muted { color: #D1D5DB; font-size: 13px; }

/* ── Loading ── */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 48px;
  color: #9CA3AF;
  font-size: 14px;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #E5E7EB;
  border-top-color: #DC2626;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Empty ── */
.empty {
  text-align: center;
  padding: 48px 20px;
  color: #9CA3AF;
}
.empty-icon {
  font-size: 32px;
  color: #D1D5DB;
  display: block;
  margin: 0 auto 10px;
}
.empty p { margin: 0; font-size: 14px; }

/* ── Load More ── */
.load-more-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 12px 4px;
  border-top: 1px solid #F3F4F6;
  margin-top: 4px;
}
.load-more-info { font-size: 13px; color: #9CA3AF; }

.load-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: white;
  color: #374151;
  border: 1px solid #E5E7EB;
  padding: 8px 16px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
  transition: 0.15s;
}
.load-more-btn i { font-size: 15px; }
.load-more-btn:hover {
  border-color: #DC2626;
  color: #DC2626;
  background: rgba(220, 38, 38, 0.03);
}

.all-loaded {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 18px 12px 4px;
  border-top: 1px solid #F3F4F6;
  margin-top: 4px;
  font-size: 13px;
  color: #9CA3AF;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .filters { grid-template-columns: 1fr 1fr; }
  .search-field { grid-column: span 2; }
}
@media (max-width: 600px) {
  .filters { grid-template-columns: 1fr; }
  .search-field { grid-column: span 1; }
}
</style>