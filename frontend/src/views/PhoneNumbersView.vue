<template>
  <div>
    <div class="page-header">
      <h1><i class="ti ti-phone"></i> Brojevi</h1>
      <p>Pregled, filtriranje i upravljanje fiksnim telefonskim brojevima.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card green">
        <span>Slobodni</span>
        <strong>{{ stats.free }}</strong>
      </div>
      <div class="stat-card red">
        <span>Zauzeti</span>
        <strong>{{ stats.busy }}</strong>
      </div>
      <div class="stat-card yellow">
        <span>Karantena</span>
        <strong>{{ stats.quarantine }}</strong>
      </div>
      <div class="stat-card blue">
        <span>Ukupno</span>
        <strong>{{ stats.total }}</strong>
      </div>
    </div>

    <section class="panel">
      <div class="filters">
        <div class="field search">
          <label>Pretraga</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Broj, pretplatnik, OIB, JMBG, interni ID..."
          />
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
          <select v-model="filters.region_id" @change="onRegionChange">
            <option value="">Sve regije</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Grad/općina</label>
          <select v-model="filters.city_id" @change="onCityChange">
            <option value="">Svi gradovi</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">{{ city.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Lokacija</label>
          <select v-model="filters.location_id" @change="onLocationChange">
            <option value="">Sve lokacije</option>
            <option v-for="location in locations" :key="location.id" :value="location.id">{{ location.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Uređaj</label>
          <select v-model="filters.device_id" @change="resetAndLoad">
            <option value="">Svi uređaji</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">{{ device.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Status</label>
          <select v-model="filters.status" @change="resetAndLoad">
            <option value="">Svi statusi</option>
            <option value="slobodan">Slobodan</option>
            <option value="zauzet">Zauzet</option>
            <option value="karantena">Karantena</option>
          </select>
        </div>

        <div class="field">
          <label>Kategorija</label>
          <select v-model="filters.number_category" @change="resetAndLoad">
            <option value="">Sve kategorije</option>
            <option value="premium">Premium</option>
            <option value="gold">Gold</option>
            <option value="silver">Silver</option>
            <option value="bronze">Bronze</option>
            <option value="standard">Standard</option>
          </select>
        </div>

        <div class="field">
          <label>Raspon</label>
          <select v-model="filters.number_range_id" @change="resetAndLoad">
            <option value="">Svi rasponi</option>
            <option v-for="range in ranges" :key="range.id" :value="range.id">
              {{ formatRangeNumber(range.range_start) }} – {{ formatRangeNumber(range.range_end) }} | {{ range.location_name }}
            </option>
          </select>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis brojeva</h2>
        <span class="count-badge">Stranica {{ page }} / {{ pages || 1 }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje brojeva...</div>

      <table v-else>
        <colgroup>
          <col style="width: 152px;">
          <col style="width: 108px;">
          <col style="width: 96px;">
          <col>
          <col style="width: 118px;">
          <col style="width: 160px;">
          <col style="width: 134px;">
        </colgroup>
        <thead>
          <tr>
            <th>Broj</th>
            <th>Kategorija</th>
            <th>Status</th>
            <th>Pretplatnik</th>
            <th>OIB / JMBG</th>
            <th>Lokacija</th>
            <th style="text-align:center;">Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="phone in phoneNumbers" :key="phone.id" :class="categoryRowClass(phone.number_category)">
            <td>
              <strong class="number">{{ formatPhoneNumber(phone.number_value) }}</strong>
            </td>
            <td>
              <span class="category-badge" :class="categoryBadgeClass(phone.number_category)">
                <span v-if="categoryIcon(phone.number_category)" class="category-icon">{{ categoryIcon(phone.number_category) }}</span>
                {{ categoryLabel(phone.number_category) }}
              </span>
            </td>
            <td>
              <span class="badge" :class="statusClass(phone.status)">{{ statusLabel(phone.status) }}</span>
            </td>
            <td>
              <span class="cell-main">{{ phone.subscriber_name || "—" }}</span>
              <span v-if="phone.subscriber_external_id" class="cell-sub">{{ phone.subscriber_external_id }}</span>
            </td>
            <td class="mono-cell">{{ phone.subscriber_oib || phone.subscriber_jmbg || "—" }}</td>
            <td>
              <div class="cell-main">
                {{ phone.location_name }}
              </div>

              <div v-if="phone.city_name" class="cell-sub">
                {{ phone.city_name }}
              </div>
            </td>
            <td>
              <div class="table-actions">
                <template v-if="phone.status === 'slobodan'">
                  <button class="action-btn action-assign" @click="openAssign(phone)" title="Dodijeli pretplatniku">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
                    Dodijeli
                  </button>
                  <button class="action-btn action-warn" @click="quarantinePhone(phone)" title="Karantena">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  </button>
                </template>
                <template v-else-if="phone.status === 'zauzet'">
                  <button class="action-btn action-danger" @click="releasePhone(phone)" title="Oslobodi broj">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="22" y1="10" x2="16" y2="10"/></svg>
                    Oslobodi
                  </button>
                  <button class="action-btn action-warn" @click="quarantinePhone(phone)" title="Karantena">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  </button>
                </template>
                <template v-else-if="phone.status === 'karantena'">
                  <button class="action-btn action-ok" @click="activatePhone(phone)" title="Aktiviraj broj">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                    Aktiviraj
                  </button>
                </template>
              </div>
            </td>
          </tr>
          <tr v-if="phoneNumbers.length === 0">
            <td colspan="7" class="empty">Nema brojeva za prikaz.</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="pages > 1">
        <button class="page-btn" :disabled="page <= 1" @click="changePage(page - 1)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <span class="page-info">{{ page }} <span class="page-sep">/</span> {{ pages }}</span>
        <button class="page-btn" :disabled="page >= pages" @click="changePage(page + 1)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
    </section>

    <!-- ASSIGN MODAL KOMPONENTA -->
    <AssignModal
      v-if="assignModalOpen"
      :phone="selectedPhone"
      @close="closeAssign"
      @assigned="onAssigned"
    />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import api from "../api/client";
import AssignModal from "../components/AssignPhoneModal.vue";

const phoneNumbers = ref([]);
const ranges = ref([]);

const entities = ref([]);
const regions = ref([]);
const cities = ref([]);
const locations = ref([]);
const devices = ref([]);

const loading = ref(false);

const total = ref(0);
const page = ref(1);
const pages = ref(1);
const perPage = 50;

const assignModalOpen = ref(false);
const selectedPhone = ref(null);

const stats = ref({ free: 0, busy: 0, quarantine: 0, total: 0 });

const filters = reactive({
  search: "",
  status: "",
  number_range_id: "",
  number_category: "",
  entity_id: "",
  region_id: "",
  city_id: "",
  location_id: "",
  device_id: "",
});

// =====================
// FORMATIRANJE
// =====================

function formatPhoneNumber(value) {
  if (!value) return "";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length === 8) return `+387 ${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  if (digits.length === 9) return `+387 ${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  return value;
}

function formatRangeNumber(value) {
  if (!value) return "";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length === 8) return `${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  if (digits.length === 9) return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  return value;
}

// =====================
// BADGE HELPERI
// =====================

function statusLabel(status) {
  if (status === "slobodan") return "Slobodan";
  if (status === "zauzet") return "Zauzet";
  if (status === "karantena") return "Karantena";
  return status;
}

function statusClass(status) {
  if (status === "slobodan") return "badge-green";
  if (status === "zauzet") return "badge-red";
  if (status === "karantena") return "badge-yellow";
  return "badge-gray";
}

function categoryLabel(category) {
  if (category === "premium") return "Premium";
  if (category === "gold") return "Gold";
  if (category === "silver") return "Silver";
  if (category === "bronze") return "Bronze";
  return "Standard";
}

function categoryIcon(category) {
  if (category === "premium") return "💎";
  if (category === "gold") return "🥇";
  if (category === "silver") return "🥈";
  if (category === "bronze") return "🥉";
  return "";
}

function categoryBadgeClass(category) {
  if (category === "premium") return "cat-premium";
  if (category === "gold") return "cat-gold";
  if (category === "silver") return "cat-silver";
  if (category === "bronze") return "cat-bronze";
  return "cat-standard";
}

function categoryRowClass(category) {
  if (category === "premium") return "row-premium";
  if (category === "gold") return "row-gold";
  if (category === "silver") return "row-silver";
  if (category === "bronze") return "row-bronze";
  return "";
}

// =====================
// DEBOUNCE ZA PRETRAGU
// =====================

let searchTimer = null;

watch(() => filters.search, () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => resetAndLoad(), 350);
});

// =====================
// FILTERI — KASKADA
// =====================

async function loadEntities() {
  const response = await api.get("/entities");
  entities.value = response.data;
}

async function onEntityChange() {
  filters.region_id = "";
  filters.city_id = "";
  filters.location_id = "";
  filters.device_id = "";
  regions.value = [];
  cities.value = [];
  locations.value = [];
  devices.value = [];
  if (filters.entity_id) {
    const response = await api.get(`/regions?entity_id=${filters.entity_id}`);
    regions.value = response.data;
  }
  resetAndLoad();
}

async function onRegionChange() {
  filters.city_id = "";
  filters.location_id = "";
  filters.device_id = "";
  cities.value = [];
  locations.value = [];
  devices.value = [];
  if (filters.region_id) {
    const response = await api.get(`/cities?region_id=${filters.region_id}`);
    cities.value = response.data;
  }
  resetAndLoad();
}

async function onCityChange() {
  filters.location_id = "";
  filters.device_id = "";
  locations.value = [];
  devices.value = [];
  if (filters.city_id) {
    const response = await api.get("/locations");
    locations.value = response.data.filter((l) => Number(l.city_id) === Number(filters.city_id));
  }
  resetAndLoad();
}

async function onLocationChange() {
  filters.device_id = "";
  devices.value = [];
  if (filters.location_id) {
    const response = await api.get(`/devices?location_id=${filters.location_id}`);
    devices.value = response.data;
  }
  resetAndLoad();
}

// =====================
// UČITAVANJE PODATAKA
// =====================

async function loadRanges() {
  const response = await api.get("/number-ranges");
  ranges.value = response.data;
}

async function loadPhoneNumbers() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    params.append("page", page.value);
    params.append("per_page", perPage);
    if (filters.search) params.append("search", filters.search);
    if (filters.status) params.append("status", filters.status);
    if (filters.number_category) params.append("number_category", filters.number_category);
    if (filters.number_range_id) params.append("number_range_id", filters.number_range_id);
    if (filters.entity_id) params.append("entity_id", filters.entity_id);
    if (filters.region_id) params.append("region_id", filters.region_id);
    if (filters.city_id) params.append("city_id", filters.city_id);
    if (filters.location_id) params.append("location_id", filters.location_id);
    if (filters.device_id) params.append("device_id", filters.device_id);

    const response = await api.get(`/phone-numbers?${params.toString()}`);
    phoneNumbers.value = response.data.data;
    total.value = response.data.total;
    pages.value = response.data.pages;
    stats.value = response.data.stats || { free: 0, busy: 0, quarantine: 0, total: response.data.total || 0 };
  } finally {
    loading.value = false;
  }
}

function resetAndLoad() {
  page.value = 1;
  loadPhoneNumbers();
}

function changePage(newPage) {
  page.value = newPage;
  loadPhoneNumbers();
}

// =====================
// ASSIGN MODAL
// =====================

function openAssign(phone) {
  selectedPhone.value = phone;
  assignModalOpen.value = true;
}

function closeAssign() {
  assignModalOpen.value = false;
  selectedPhone.value = null;
}

async function onAssigned() {
  closeAssign();
  await loadPhoneNumbers();
}

// =====================
// AKCIJE NA BROJEVIMA
// =====================

async function releasePhone(phone) {
  if (!confirm(`Osloboditi broj ${formatPhoneNumber(phone.number_value)}?`)) return;
  await api.post(`/phone-numbers/${phone.id}/release`, { note: "Broj oslobođen kroz aplikaciju" });
  await loadPhoneNumbers();
}

async function quarantinePhone(phone) {
  if (!confirm(`Staviti broj ${formatPhoneNumber(phone.number_value)} u karantenu?`)) return;
  await api.post(`/phone-numbers/${phone.id}/quarantine`, { note: "Broj stavljen u karantenu kroz aplikaciju" });
  await loadPhoneNumbers();
}

async function activatePhone(phone) {
  if (!confirm(`Aktivirati broj ${formatPhoneNumber(phone.number_value)}?`)) return;
  await api.post(`/phone-numbers/${phone.id}/activate`);
  await loadPhoneNumbers();
}

// =====================
// INIT
// =====================

onMounted(async () => {
  await loadEntities();
  await loadRanges();
  await loadPhoneNumbers();
});
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
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
.page-header h1 i { font-size: 26px; color: #1B4FD8; }
.page-header p { margin-top: 5px; color: #6b7280; font-size: 14px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 18px 20px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}
.stat-card span {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
}
.stat-card strong { display: block; margin-top: 6px; font-size: 30px; font-weight: 700; }
.stat-card.green strong { color: #16a34a; }
.stat-card.red strong   { color: #dc2626; }
.stat-card.yellow strong { color: #b45309; }
.stat-card.blue strong  { color: #2563eb; }

.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.panel-header h2 { margin: 0; font-size: 16px; color: #111827; }
.count-badge {
  background: #f3f4f6;
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
}

.filters {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  align-items: end;
}
.field { display: flex; flex-direction: column; }
.field.search { grid-column: span 2; }

label {
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 12px;
  background: white;
  color: #111827;
  transition: border-color 0.15s, box-shadow 0.15s;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
}

table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th {
  text-align: left;
  background: #f9fafb;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 12px;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
  overflow: hidden;
}
td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f2f5;
  color: #374151;
  font-size: 13px;
  vertical-align: middle;
  overflow: hidden;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background-color: rgba(0,0,0,0.018) !important; }

.cell-main {
  display: block;
  font-weight: 600;
  color: #111827;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cell-sub {
  display: block;
  color: #9ca3af;
  font-size: 11px;
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cell-sub-inline { color: #9ca3af; font-size: 11px; font-weight: 400; }
.mono-cell {
  font-family: monospace;
  font-size: 12px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.number {
  font-family: monospace;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.table-actions {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 9px;
  border-radius: 7px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.13s, border-color 0.13s;
  line-height: 1.4;
}
.action-assign { background: rgba(37,99,235,0.09); color: #1d4ed8; border-color: rgba(37,99,235,0.22); }
.action-assign:hover { background: rgba(37,99,235,0.17); border-color: rgba(37,99,235,0.35); }
.action-danger { background: rgba(220,38,38,0.08); color: #b91c1c; border-color: rgba(220,38,38,0.2); }
.action-danger:hover { background: rgba(220,38,38,0.15); border-color: rgba(220,38,38,0.32); }
.action-warn { background: rgba(245,158,11,0.09); color: #92400e; border-color: rgba(245,158,11,0.28); padding: 4px 7px; }
.action-warn:hover { background: rgba(245,158,11,0.17); border-color: rgba(245,158,11,0.4); }
.action-ok { background: rgba(22,163,74,0.09); color: #15803d; border-color: rgba(22,163,74,0.22); }
.action-ok:hover { background: rgba(22,163,74,0.16); border-color: rgba(22,163,74,0.35); }

.row-premium td { background: rgba(109,40,217,0.07); border-bottom-color: rgba(109,40,217,0.1); }
.row-premium .number { color: #6d28d9; }
.row-gold td { background: rgba(180,120,10,0.08); border-bottom-color: rgba(180,120,10,0.12); }
.row-gold .number { color: #92600a; }
.row-silver td { background: rgba(100,116,139,0.08); border-bottom-color: rgba(100,116,139,0.12); }
.row-silver .number { color: #475569; }
.row-bronze td { background: rgba(146,64,14,0.07); border-bottom-color: rgba(146,64,14,0.11); }
.row-bronze .number { color: #92400e; }

.category-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.02em;
  border: 1px solid transparent;
}
.category-icon { font-size: 12px; line-height: 1; }
.cat-premium  { background: rgba(109,40,217,0.12); color: #5b21b6; border-color: rgba(109,40,217,0.28); }
.cat-gold     { background: rgba(180,120,10,0.12); color: #78500a; border-color: rgba(180,120,10,0.3); }
.cat-silver   { background: rgba(100,116,139,0.12); color: #334155; border-color: rgba(100,116,139,0.3); }
.cat-bronze   { background: rgba(146,64,14,0.11); color: #7c2d12; border-color: rgba(146,64,14,0.27); }
.cat-standard { background: #f3f4f6; color: #6b7280; border-color: #e5e7eb; }

.badge {
  display: inline-flex;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.badge-green  { background: rgba(22,163,74,0.1);   color: #16a34a; }
.badge-red    { background: rgba(220,38,38,0.1);   color: #dc2626; }
.badge-blue   { background: rgba(37,99,235,0.1);   color: #2563eb; }
.badge-yellow { background: rgba(245,158,11,0.12); color: #b45309; }
.badge-gray   { background: rgba(107,114,128,0.1); color: #6b7280; }

.loading, .empty { text-align: center; color: #6b7280; padding: 24px; font-size: 14px; }

.pagination { margin-top: 16px; display: flex; justify-content: center; align-items: center; gap: 8px; }
.page-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  width: 34px; height: 34px;
  border-radius: 10px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.page-btn:hover:not(:disabled) { background: #e5e7eb; }
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.page-info { font-size: 13px; font-weight: 600; color: #374151; padding: 0 6px; }
.page-sep { color: #9ca3af; margin: 0 3px; }

@media (max-width: 1100px) {
  .filters { grid-template-columns: repeat(2, 1fr); }
  .field.search { grid-column: span 2; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 720px) {
  .filters { grid-template-columns: 1fr; }
  .field.search { grid-column: span 1; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>