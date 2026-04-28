<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Brojevi</h1>
        <p>Pregled, filtriranje i upravljanje fiksnim telefonskim brojevima.</p>
      </div>
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
            @input="resetAndLoad"
          />
        </div>

        <div class="field">
          <label>Entitet</label>
          <select v-model="filters.entity_id" @change="onEntityChange">
            <option value="">Svi entiteti</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">
              {{ entity.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Županija</label>
          <select v-model="filters.region_id" @change="onRegionChange">
            <option value="">Sve županije</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Grad/općina</label>
          <select v-model="filters.city_id" @change="onCityChange">
            <option value="">Svi gradovi</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Lokacija</label>
          <select v-model="filters.location_id" @change="onLocationChange">
            <option value="">Sve lokacije</option>
            <option v-for="location in locations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Uređaj</label>
          <select v-model="filters.device_id" @change="resetAndLoad">
            <option value="">Svi uređaji</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">
              {{ device.name }}
            </option>
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
          <label>Raspon</label>
          <select v-model="filters.number_range_id" @change="resetAndLoad">
            <option value="">Svi rasponi</option>
            <option v-for="range in ranges" :key="range.id" :value="range.id">
              {{ formatPhoneNumber(range.range_start) }} - {{ formatPhoneNumber(range.range_end) }} | {{ range.location_name }}
            </option>
          </select>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis brojeva</h2>
        <span class="muted">Stranica {{ page }} / {{ pages || 1 }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje brojeva...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Broj</th>
            <th>Status</th>
            <th>Pretplatnik</th>
            <th>OIB/JMBG</th>
            <th>Lokacija</th>
            <th>Raspon</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="phone in phoneNumbers" :key="phone.id">
            <td>
              <strong class="number">{{ formatPhoneNumber(phone.number_value) }}</strong>
            </td>
            <td>
              <span class="badge" :class="statusClass(phone.status)">
                {{ statusLabel(phone.status) }}
              </span>
            </td>
            <td>
              <strong>{{ phone.subscriber_name || "-" }}</strong>
              <div v-if="phone.subscriber_external_id" class="muted">
                {{ phone.subscriber_external_id }}
              </div>
            </td>
            <td>{{ phone.subscriber_oib || phone.subscriber_jmbg || "-" }}</td>
            <td>
              {{ phone.location_name }}
              <div class="muted">{{ phone.city_name }}</div>
            </td>
            <td>
              {{ formatPhoneNumber(phone.range_start) }} - {{ formatPhoneNumber(phone.range_end) }}
            </td>
            <td class="actions-cell">
              <button v-if="phone.status === 'slobodan'" class="small-btn" @click="openAssign(phone)">
                Dodijeli
              </button>
              <button v-if="phone.status === 'zauzet'" class="small-btn danger" @click="releasePhone(phone)">
                Oslobodi
              </button>
              <button v-if="phone.status !== 'karantena'" class="small-btn warning" @click="quarantinePhone(phone)">
                Karantena
              </button>
              <button v-if="phone.status === 'karantena'" class="small-btn" @click="activatePhone(phone)">
                Aktiviraj
              </button>
            </td>
          </tr>
          <tr v-if="phoneNumbers.length === 0">
            <td colspan="7" class="empty">Nema brojeva za prikaz.</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="pages > 1">
        <button :disabled="page <= 1" @click="changePage(page - 1)">Prethodna</button>
        <span>{{ page }} / {{ pages }}</span>
        <button :disabled="page >= pages" @click="changePage(page + 1)">Sljedeća</button>
      </div>
    </section>

    <!-- ─── ASSIGN MODAL ─── -->
    <div v-if="assignModalOpen" class="modal-overlay" @click.self="closeAssign">
      <div class="modal">

        <!-- Header -->
        <div class="modal-header">
          <div class="modal-title-group">
            <div class="modal-phone-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.35 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 5.45 5.45l.96-.96a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21 16.92z"/></svg>
              {{ formatPhoneNumber(selectedPhone?.number_value) }}
            </div>
            <h3>Dodjela broja pretplatniku</h3>
            <p class="modal-subtitle">
              {{ selectedPhone?.entity_name }} / {{ selectedPhone?.region_name }} / {{ selectedPhone?.city_name }} / {{ selectedPhone?.location_name }}
            </p>
          </div>
          <button class="close-btn" @click="closeAssign">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <!-- Body: two columns -->
        <div class="modal-body">

          <!-- LEFT: search + list -->
          <div class="modal-col modal-col-list">
            <div class="search-bar-wrapper">
              <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input
                ref="subscriberSearchInput"
                v-model="subscriberFilters.search"
                type="text"
                class="search-bar"
                placeholder="Ime, OIB, JMBG, interni ID..."
                @input="() => {}"
              />
              <button v-if="subscriberFilters.search" class="search-clear" @click="clearSubscriberSearch">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            <div class="type-tabs">
              <button
                class="type-tab"
                :class="{ active: subscriberFilters.type === '' }"
                @click="setSubscriberType('')"
              >Svi</button>
              <button
                class="type-tab"
                :class="{ active: subscriberFilters.type === 'physical_person' }"
                @click="setSubscriberType('physical_person')"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                Fizička osoba
              </button>
              <button
                class="type-tab"
                :class="{ active: subscriberFilters.type === 'legal_entity' }"
                @click="setSubscriberType('legal_entity')"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                Pravna osoba
              </button>
            </div>

            <div class="subscriber-list-scroll">
              <div v-if="subscribersLoading" class="sub-loading">
                <div class="spinner"></div>
                <span>Pretraga...</span>
              </div>

              <template v-else>
                <div
                  v-for="subscriber in filteredSubscribers"
                  :key="subscriber.id"
                  class="subscriber-row"
                  :class="{ selected: Number(assignForm.subscriber_id) === Number(subscriber.id) }"
                  @click="selectSubscriber(subscriber)"
                >
                  <div class="subscriber-avatar" :class="subscriber.subscriber_type === 'legal_entity' ? 'avatar-blue' : 'avatar-red'">
                    <svg v-if="subscriber.subscriber_type === 'legal_entity'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </div>

                  <div class="subscriber-info">
                    <strong>{{ subscriberName(subscriber) }}</strong>
                    <span class="subscriber-meta">
                      {{ subscriber.oib || subscriber.jmbg || subscriber.external_id || "Bez identifikatora" }}
                      <span v-if="subscriber.city_name" class="meta-sep">·</span>
                      {{ subscriber.city_name }}
                    </span>
                  </div>

                  <div class="subscriber-check">
                    <svg v-if="Number(assignForm.subscriber_id) === Number(subscriber.id)" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                </div>

                <div v-if="filteredSubscribers.length === 0" class="sub-empty">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                  <p>Nema rezultata za &ldquo;{{ subscriberFilters.search || "odabrane filtere" }}&rdquo;</p>
                  <RouterLink class="create-link-inline" to="/subscribers">Kreiraj novog pretplatnika</RouterLink>
                </div>
              </template>
            </div>
          </div>

          <!-- RIGHT: selected subscriber + note -->
          <div class="modal-col modal-col-detail">
            <div v-if="selectedSubscriber" class="selected-subscriber-card">
              <div class="selected-header">
                <span class="selected-label">Odabrani pretplatnik</span>
                <button class="deselect-btn" @click="deselectSubscriber">Poništi</button>
              </div>
              <div class="selected-name">{{ subscriberName(selectedSubscriber) }}</div>
              <div class="selected-meta-grid">
                <div class="selected-meta-item">
                  <span class="meta-key">Tip</span>
                  <span class="badge" :class="selectedSubscriber.subscriber_type === 'legal_entity' ? 'badge-blue' : 'badge-red'">
                    {{ selectedSubscriber.subscriber_type === 'legal_entity' ? 'Pravna osoba' : 'Fizička osoba' }}
                  </span>
                </div>
                <div v-if="selectedSubscriber.oib || selectedSubscriber.jmbg" class="selected-meta-item">
                  <span class="meta-key">{{ selectedSubscriber.oib ? 'OIB' : 'JMBG' }}</span>
                  <span class="meta-val">{{ selectedSubscriber.oib || selectedSubscriber.jmbg }}</span>
                </div>
                <div v-if="selectedSubscriber.external_id" class="selected-meta-item">
                  <span class="meta-key">Interni ID</span>
                  <span class="meta-val">{{ selectedSubscriber.external_id }}</span>
                </div>
                <div v-if="selectedSubscriber.city_name" class="selected-meta-item">
                  <span class="meta-key">Grad</span>
                  <span class="meta-val">{{ selectedSubscriber.city_name }}</span>
                </div>
              </div>
            </div>

            <div v-else class="no-selection-placeholder">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <p>Odaberi pretplatnika<br>s popisa lijevo</p>
            </div>

            <div class="note-field">
              <label>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                Napomena <span class="optional">(opcionalno)</span>
              </label>
              <textarea v-model="assignForm.note" placeholder="Npr. ugovor br. 1234, zamjena uređaja..."></textarea>
            </div>

            <RouterLink class="create-subscriber-link" to="/subscribers">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Kreiraj novog pretplatnika
            </RouterLink>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <p v-if="error" class="error">{{ error }}</p>
          <div class="footer-actions">
            <button class="secondary" @click="closeAssign">Odustani</button>
            <button
              class="primary-btn"
              :disabled="!assignForm.subscriber_id"
              @click="assignPhone"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Dodijeli broj
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import api from "../api/client";

const phoneNumbers = ref([]);
const ranges = ref([]);
const subscribers = ref([]);

const entities = ref([]);
const regions = ref([]);
const cities = ref([]);
const locations = ref([]);
const devices = ref([]);
const subscriberCities = ref([]);

const loading = ref(false);
const subscribersLoading = ref(false);
const error = ref("");

const total = ref(0);
const page = ref(1);
const pages = ref(1);
const perPage = 50;

const assignModalOpen = ref(false);
const selectedPhone = ref(null);
const selectedSubscriber = ref(null);
const subscriberSearchInput = ref(null);

const filters = reactive({
  search: "",
  status: "",
  number_range_id: "",
  entity_id: "",
  region_id: "",
  city_id: "",
  location_id: "",
  device_id: "",
});

const subscriberFilters = reactive({
  search: "",
  type: "",
  city_id: "",
});

const assignForm = reactive({
  subscriber_id: "",
  note: "",
});

const stats = ref({
  free: 0,
  busy: 0,
  quarantine: 0,
  total: 0,
});

const filteredSubscribers = computed(() => {
  const q = subscriberFilters.search.toLowerCase().trim();

  return subscribers.value.filter((subscriber) => {
    const matchesType =
      !subscriberFilters.type || subscriber.subscriber_type === subscriberFilters.type;
    const matchesCity =
      !subscriberFilters.city_id ||
      Number(subscriber.city_id) === Number(subscriberFilters.city_id);

    if (!matchesType || !matchesCity) return false;

    if (!q) return true;

    const fullName = `${subscriber.first_name || ""} ${subscriber.last_name || ""}`.toLowerCase();
    const company = (subscriber.company_name || "").toLowerCase();
    const oib = (subscriber.oib || "").toLowerCase();
    const jmbg = (subscriber.jmbg || "").toLowerCase();
    const extId = (subscriber.external_id || "").toLowerCase();

    return (
      fullName.includes(q) ||
      company.includes(q) ||
      oib.includes(q) ||
      jmbg.includes(q) ||
      extId.includes(q)
    );
  });
});

function formatPhoneNumber(value) {
  if (!value) return "";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length === 8) return `${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  if (digits.length === 9) return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  return value;
}

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

function subscriberName(subscriber) {
  if (!subscriber) return "-";
  if (subscriber.subscriber_type === "legal_entity") return subscriber.company_name || "-";
  return `${subscriber.first_name || ""} ${subscriber.last_name || ""}`.trim() || "-";
}

function selectSubscriber(subscriber) {
  assignForm.subscriber_id = subscriber.id;
  selectedSubscriber.value = subscriber;
}

function deselectSubscriber() {
  assignForm.subscriber_id = "";
  selectedSubscriber.value = null;
}

function setSubscriberType(type) {
  subscriberFilters.type = type;
  // No need to reload — filteredSubscribers is computed
}

function clearSubscriberSearch() {
  subscriberFilters.search = "";
}

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
    locations.value = response.data.filter(
      (location) => Number(location.city_id) === Number(filters.city_id)
    );
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

stats.value = response.data.stats || {
  free: 0,
  busy: 0,
  quarantine: 0,
  total: response.data.total || 0,
};
  } finally {
    loading.value = false;
  }
}

async function loadSubscribers() {
  subscribersLoading.value = true;
  try {
    const query = subscriberFilters.search
      ? `?search=${encodeURIComponent(subscriberFilters.search)}`
      : "";
    const response = await api.get(`/subscribers${query}`);
    subscribers.value = response.data;
  } finally {
    subscribersLoading.value = false;
  }
}

async function loadSubscriberCitiesForSelectedPhone() {
  subscriberCities.value = [];
  if (!selectedPhone.value?.region_id) return;
  const response = await api.get(`/cities?region_id=${selectedPhone.value.region_id}`);
  subscriberCities.value = response.data;
}

function resetAndLoad() {
  page.value = 1;
  loadPhoneNumbers();
}

function changePage(newPage) {
  page.value = newPage;
  loadPhoneNumbers();
}

async function openAssign(phone) {
  selectedPhone.value = phone;
  selectedSubscriber.value = null;
  assignForm.subscriber_id = "";
  assignForm.note = "";
  subscriberFilters.search = "";
  subscriberFilters.type = "";
  subscriberFilters.city_id = phone.city_id || "";
  error.value = "";
  assignModalOpen.value = true;

  await loadSubscriberCitiesForSelectedPhone();
  await loadSubscribers();

  await nextTick();
  subscriberSearchInput.value?.focus();
}

function closeAssign() {
  assignModalOpen.value = false;
  selectedPhone.value = null;
  selectedSubscriber.value = null;
}

async function assignPhone() {
  error.value = "";
  if (!assignForm.subscriber_id) {
    error.value = "Odaberi pretplatnika s popisa.";
    return;
  }
  try {
    await api.post(`/phone-numbers/${selectedPhone.value.id}/assign`, {
      subscriber_id: Number(assignForm.subscriber_id),
      note: assignForm.note || null,
    });
    closeAssign();
    await loadPhoneNumbers();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri dodjeli broja.";
  }
}

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

onMounted(async () => {
  await loadEntities();
  await loadRanges();
  await loadPhoneNumbers();
});
</script>

<style scoped>
/* ─── PAGE ─── */
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 30px; color: #111827; }
.page-header p { margin-top: 6px; color: #6b7280; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}

.stat-card,
.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}

.stat-card { padding: 20px; }
.stat-card span { color: #6b7280; font-size: 13px; font-weight: 800; }
.stat-card strong { display: block; margin-top: 8px; font-size: 34px; }
.stat-card.green strong { color: #16a34a; }
.stat-card.red strong { color: #dc2626; }
.stat-card.yellow strong { color: #b45309; }
.stat-card.blue strong { color: #2563eb; }

.panel { padding: 24px; margin-bottom: 24px; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.panel h2 { margin: 0; color: #111827; }

.filters {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.field { display: flex; flex-direction: column; margin-bottom: 14px; }
.field.search { grid-column: span 2; }

label { font-size: 14px; color: #374151; margin-bottom: 6px; font-weight: 700; }

input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 12px 13px;
  font-size: 14px;
  background: white;
  color: #111827;
}
textarea { min-height: 80px; }
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.12);
}

table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  background: #f9fafb;
  color: #6b7280;
  font-size: 13px;
  padding: 13px;
  border-bottom: 1px solid #e5e7eb;
}
td {
  padding: 13px;
  border-bottom: 1px solid #eef2f7;
  color: #374151;
  font-size: 14px;
}

.number { color: #111827; font-family: monospace; font-size: 15px; }

.actions-cell { display: flex; gap: 8px; flex-wrap: wrap; }

button {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border: none;
  padding: 12px 17px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
button:disabled { opacity: 0.45; cursor: not-allowed; }
button.secondary { background: #6b7280; }

.small-btn { padding: 8px 11px; border-radius: 9px; font-size: 12px; }
.small-btn.danger { background: #dc2626; }
.small-btn.warning { background: #f59e0b; color: #111827; }

.badge {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.badge-green { background: rgba(22,163,74,0.12); color: #16a34a; }
.badge-red { background: rgba(220,38,38,0.12); color: #dc2626; }
.badge-blue { background: rgba(37,99,235,0.12); color: #2563eb; }
.badge-yellow { background: rgba(245,158,11,0.16); color: #b45309; }
.badge-gray { background: rgba(107,114,128,0.12); color: #6b7280; }

.empty, .loading { text-align: center; color: #6b7280; padding: 28px; }
.muted { color: #6b7280; font-size: 13px; }

.pagination {
  margin-top: 18px;
  display: flex;
  justify-content: center;
  gap: 14px;
  align-items: center;
}

/* ─── MODAL OVERLAY ─── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(3px);
}

.modal {
  width: 860px;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 48px);
  background: white;
  border-radius: 24px;
  box-shadow: 0 40px 100px rgba(15,23,42,0.28);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Modal header */
.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
}

.modal-title-group { display: flex; flex-direction: column; gap: 4px; }

.modal-phone-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: linear-gradient(135deg, rgba(220,38,38,0.1), rgba(37,99,235,0.1));
  border: 1px solid rgba(220,38,38,0.2);
  color: #dc2626;
  font-family: monospace;
  font-size: 15px;
  font-weight: 800;
  padding: 6px 12px;
  border-radius: 10px;
  width: fit-content;
  margin-bottom: 4px;
}

.modal-title-group h3 { margin: 0; font-size: 18px; color: #111827; }
.modal-subtitle { margin: 0; color: #6b7280; font-size: 13px; }

.close-btn {
  background: #f3f4f6;
  color: #374151;
  padding: 8px;
  border-radius: 10px;
  flex-shrink: 0;
}
.close-btn:hover { background: #e5e7eb; }

/* Modal body: two column layout */
.modal-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.modal-col {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 20px;
}

.modal-col-list {
  border-right: 1px solid #e5e7eb;
}

/* Search bar */
.search-bar-wrapper {
  position: relative;
  margin-bottom: 10px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
}

.search-bar {
  width: 100%;
  padding: 10px 36px 10px 36px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 14px;
  background: #f9fafb;
  box-sizing: border-box;
}
.search-bar:focus {
  outline: none;
  background: white;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.12);
}

.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #e5e7eb;
  color: #6b7280;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.search-clear:hover { background: #d1d5db; }

/* Type tabs */
.type-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.type-tab {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  justify-content: center;
}
.type-tab:hover { background: #e5e7eb; }
.type-tab.active {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border-color: transparent;
}

/* Subscriber list */
.subscriber-list-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
}

.subscriber-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 11px 13px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.12s;
}
.subscriber-row:last-child { border-bottom: none; }
.subscriber-row:hover { background: #fafafa; }
.subscriber-row.selected { background: rgba(220,38,38,0.04); }

.subscriber-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar-blue { background: rgba(37,99,235,0.1); color: #2563eb; }
.avatar-red { background: rgba(220,38,38,0.1); color: #dc2626; }

.subscriber-info { flex: 1; min-width: 0; }
.subscriber-info strong { font-size: 14px; color: #111827; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.subscriber-meta { color: #9ca3af; font-size: 12px; display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.meta-sep { color: #d1d5db; }

.subscriber-check {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
  flex-shrink: 0;
}

/* Empty & loading states */
.sub-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 10px;
  color: #9ca3af;
  font-size: 14px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top-color: #dc2626;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.sub-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 8px;
  color: #9ca3af;
  text-align: center;
}
.sub-empty p { margin: 0; font-size: 14px; line-height: 1.5; }

.create-link-inline {
  margin-top: 4px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}
.create-link-inline:hover { text-decoration: underline; }

/* Right column: selected subscriber */
.selected-subscriber-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.selected-label { font-size: 11px; font-weight: 800; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; }

.deselect-btn {
  background: none;
  color: #dc2626;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 6px;
  border: 1px solid rgba(220,38,38,0.3);
}
.deselect-btn:hover { background: rgba(220,38,38,0.06); }

.selected-name { font-size: 17px; font-weight: 800; color: #111827; margin-bottom: 12px; }

.selected-meta-grid { display: flex; flex-direction: column; gap: 8px; }
.selected-meta-item { display: flex; justify-content: space-between; align-items: center; }
.meta-key { font-size: 12px; color: #9ca3af; font-weight: 700; }
.meta-val { font-size: 13px; color: #374151; font-weight: 600; }

.no-selection-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #d1d5db;
  text-align: center;
  gap: 10px;
  border: 2px dashed #e5e7eb;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 16px;
}
.no-selection-placeholder p { margin: 0; font-size: 14px; color: #9ca3af; line-height: 1.6; }

/* Note field */
.note-field { margin-bottom: 14px; }
.note-field label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #374151;
  font-weight: 700;
  margin-bottom: 6px;
}
.optional { font-weight: 400; color: #9ca3af; }
.note-field textarea {
  width: 100%;
  min-height: 80px;
  resize: vertical;
  box-sizing: border-box;
  font-size: 13px;
  border-radius: 12px;
  border: 1px solid #d1d5db;
  padding: 10px 12px;
}

/* Create subscriber link */
.create-subscriber-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  padding: 8px 12px;
  transition: 0.15s;
}
.create-subscriber-link:hover {
  color: #dc2626;
  border-color: rgba(220,38,38,0.4);
  background: rgba(220,38,38,0.04);
}

/* Modal footer */
.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  gap: 12px;
}

.footer-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.primary-btn {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: none;
  cursor: pointer;
}
.primary-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.error { color: #dc2626; font-size: 13px; margin: 0; }

/* ─── RESPONSIVE ─── */
@media (max-width: 1100px) {
  .filters, .stats-grid { grid-template-columns: 1fr 1fr; }
  .field.search { grid-column: span 2; }
}

@media (max-width: 800px) {
  .modal-body { grid-template-columns: 1fr; overflow-y: auto; }
  .modal-col-list { border-right: none; border-bottom: 1px solid #e5e7eb; max-height: 360px; }
}

@media (max-width: 720px) {
  .filters, .stats-grid { grid-template-columns: 1fr; }
  .field.search { grid-column: span 1; }
}
</style>