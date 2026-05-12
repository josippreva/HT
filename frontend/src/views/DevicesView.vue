<template>
  <div>
    <div class="page-header">
      <h1><i class="ti ti-cpu"></i> Uređaji</h1>
      <p>Kreiranje uređaja kroz hijerarhiju entitet → županija → grad/općina → lokacija.</p>
    </div>

    <section class="panel">
      <h2>{{ editingId ? "Uredi uređaj" : "Novi uređaj" }}</h2>

      <form class="form-grid" @submit.prevent="saveDevice">
        <div class="field">
          <label>Entitet</label>
          <select v-model="form.entity_id" @change="onFormEntityChange" required>
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">
              {{ entity.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Regija</label>
          <select v-model="form.region_id" @change="onFormRegionChange" required>
            <option value="">Odaberi regiju</option>
            <option v-for="region in formRegions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Grad / općina</label>
          <select v-model="form.city_id" @change="onFormCityChange" required>
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in formCities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Lokacija</label>
          <select v-model="form.location_id" required>
            <option value="">Odaberi lokaciju</option>
            <option v-for="location in formLocations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Tip uređaja</label>
          <select v-model="form.device_type" required>
            <option value="MSAN">MSAN</option>
            <option value="GPON_OLT">GPON OLT</option>
          </select>
        </div>

        <div class="field">
          <label>Naziv uređaja</label>
          <input v-model="form.name" type="text" placeholder="npr. MSAN-MOSTAR-01" required />
        </div>

        <div class="field">
          <label>Serijski broj</label>
          <input v-model="form.serial_number" type="text" placeholder="Opcionalno" />
        </div>

        <div class="field checkbox-field">
          <label class="checkbox-label">
            <input v-model="form.active" type="checkbox" />
            Aktivan uređaj
          </label>
        </div>

        <div class="actions full">
          <button type="submit" class="btn-primary">
            <i class="ti ti-device-floppy"></i>
            {{ editingId ? "Spremi izmjene" : "Spremi uređaj" }}
          </button>
          <button v-if="editingId" type="button" class="btn-secondary" @click="cancelEdit">
            Odustani
          </button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis uređaja</h2>
        <span class="count-badge">Ukupno: {{ devices.length }}</span>
      </div>

      <div class="filters">
        <div class="field">
          <label>Entitet</label>
          <select v-model="filters.entity_id" @change="onFilterEntityChange">
            <option value="">Svi entiteti</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">
              {{ entity.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Regija</label>
          <select v-model="filters.region_id" @change="onFilterRegionChange">
            <option value="">Sve regije</option>
            <option v-for="region in filterRegions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Grad/općina</label>
          <select v-model="filters.city_id" @change="onFilterCityChange">
            <option value="">Svi gradovi</option>
            <option v-for="city in filterCities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Lokacija</label>
          <select v-model="filters.location_id" @change="loadDevices">
            <option value="">Sve lokacije</option>
            <option v-for="location in filterLocations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Status</label>
          <select v-model="filters.active" @change="loadDevices">
            <option value="">Svi statusi</option>
            <option value="true">Aktivni</option>
            <option value="false">Neaktivni</option>
          </select>
        </div>

        <div class="field">
          <label>Pretraga</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Naziv ili serijski broj"
            @input="loadDevices"
          />
        </div>
      </div>

      <div v-if="loading" class="loading">Učitavanje...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Lokacija</th>
            <th>Uređaj</th>
            <th>Tip</th>
            <th>Serijski broj</th>
            <th>Status</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in devices" :key="device.id">
            <td>{{ device.location_name }}</td>
            <td><strong>{{ device.name }}</strong></td>
            <td>
              <span class="badge" :class="device.device_type === 'MSAN' ? 'badge-red' : 'badge-blue'">
                {{ device.device_type === "GPON_OLT" ? "GPON OLT" : "MSAN" }}
              </span>
            </td>
            <td>{{ device.serial_number || "—" }}</td>
            <td>
              <span class="badge" :class="device.active ? 'badge-green' : 'badge-gray'">
                {{ device.active ? "Aktivan" : "Neaktivan" }}
              </span>
            </td>
            <td class="table-actions">
              <button class="small-btn" @click="startEdit(device)">
                <i class="ti ti-pencil"></i> Uredi
              </button>
              <button class="small-btn danger" @click="deleteDevice(device)">
                <i class="ti ti-trash"></i> Obriši
              </button>
            </td>
          </tr>
          <tr v-if="devices.length === 0">
            <td colspan="6" class="empty">Nema uređaja za prikaz.</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import api from "../api/client";

const entities = ref([]);
const allLocations = ref([]);
const devices = ref([]);

const formRegions = ref([]);
const formCities = ref([]);
const formLocations = ref([]);

const filterRegions = ref([]);
const filterCities = ref([]);
const filterLocations = ref([]);

const loading = ref(false);
const error = ref("");
const success = ref("");
const editingId = ref(null);

const form = reactive({
  entity_id: "", region_id: "", city_id: "", location_id: "",
  name: "", device_type: "MSAN", serial_number: "", active: true,
});

const filters = reactive({
  entity_id: "", region_id: "", city_id: "", location_id: "", active: "", search: "",
});

async function loadEntities() {
  const response = await api.get("/entities");
  entities.value = response.data;
}

async function loadAllLocations() {
  const response = await api.get("/locations");
  allLocations.value = response.data;
  filterLocations.value = response.data;
}

async function onFormEntityChange() {
  form.region_id = form.city_id = form.location_id = "";
  formRegions.value = formCities.value = formLocations.value = [];
  if (!form.entity_id) return;
  const response = await api.get(`/regions?entity_id=${form.entity_id}`);
  formRegions.value = response.data;
}

async function onFormRegionChange() {
  form.city_id = form.location_id = "";
  formCities.value = formLocations.value = [];
  if (!form.region_id) return;
  const response = await api.get(`/cities?region_id=${form.region_id}`);
  formCities.value = response.data;
}

function onFormCityChange() {
  form.location_id = "";
  if (!form.city_id) { formLocations.value = []; return; }
  formLocations.value = allLocations.value.filter(
    (location) => Number(location.city_id) === Number(form.city_id)
  );
}

async function onFilterEntityChange() {
  filters.region_id = filters.city_id = filters.location_id = "";
  filterRegions.value = filterCities.value = filterLocations.value = [];
  if (!filters.entity_id) {
    filterLocations.value = allLocations.value;
    await loadDevices();
    return;
  }
  const response = await api.get(`/regions?entity_id=${filters.entity_id}`);
  filterRegions.value = response.data;
  await loadDevices();
}

async function onFilterRegionChange() {
  filters.city_id = filters.location_id = "";
  filterCities.value = filterLocations.value = [];
  if (!filters.region_id) {
    filterLocations.value = allLocations.value;
    await loadDevices();
    return;
  }
  const response = await api.get(`/cities?region_id=${filters.region_id}`);
  filterCities.value = response.data;
  await loadDevices();
}

function onFilterCityChange() {
  filters.location_id = "";
  if (!filters.city_id) {
    filterLocations.value = allLocations.value;
    loadDevices();
    return;
  }
  filterLocations.value = allLocations.value.filter(
    (location) => Number(location.city_id) === Number(filters.city_id)
  );
  loadDevices();
}

async function loadDevices() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.entity_id) params.append("entity_id", filters.entity_id);
    if (filters.region_id) params.append("region_id", filters.region_id);
    if (filters.city_id) params.append("city_id", filters.city_id);
    if (filters.location_id) params.append("location_id", filters.location_id);
    if (filters.active !== "") params.append("active", filters.active);
    if (filters.search) params.append("search", filters.search);
    const query = params.toString();
    const response = await api.get(query ? `/devices?${query}` : "/devices");
    devices.value = response.data;
  } finally {
    loading.value = false;
  }
}

async function saveDevice() {
  error.value = success.value = "";
  const payload = {
    location_id: Number(form.location_id),
    name: form.name,
    device_type: form.device_type,
    serial_number: form.serial_number || null,
    active: form.active,
  };
  try {
    if (editingId.value) {
      await api.put(`/devices/${editingId.value}`, payload);
      success.value = "Uređaj je uspješno izmijenjen.";
    } else {
      await api.post("/devices", payload);
      success.value = "Uređaj je uspješno spremljen.";
    }
    resetForm();
    await loadDevices();
  } catch {
    error.value = "Greška pri spremanju uređaja.";
  }
}

async function startEdit(device) {
  editingId.value = device.id;
  form.entity_id = device.entity_id;
  await onFormEntityChange();
  form.region_id = device.region_id;
  await onFormRegionChange();
  form.city_id = device.city_id;
  onFormCityChange();
  form.location_id = device.location_id;
  form.name = device.name;
  form.device_type = device.device_type;
  form.serial_number = device.serial_number || "";
  form.active = device.active;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function cancelEdit() { resetForm(); }

function resetForm() {
  editingId.value = null;
  form.entity_id = form.region_id = form.city_id = form.location_id = "";
  form.name = form.serial_number = "";
  form.device_type = "MSAN";
  form.active = true;
  formRegions.value = formCities.value = formLocations.value = [];
}

async function deleteDevice(device) {
  if (!confirm(`Obrisati uređaj "${device.name}"?`)) return;
  try {
    await api.delete(`/devices/${device.id}`);
    success.value = "Uređaj je obrisan.";
    await loadDevices();
  } catch {
    error.value = "Greška pri brisanju uređaja.";
  }
}

onMounted(async () => {
  await loadEntities();
  await loadAllLocations();
  await loadDevices();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { font-family: 'Geist', sans-serif; }

/* ── Page header ── */
.page-header { margin-bottom: 24px; }
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
.page-header p { margin-top: 5px; color: #6B7280; font-size: 14px; }

/* ── Panel ── */
.panel {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}
.panel > h2 { margin-top: 0; margin-bottom: 16px; font-size: 15px; font-weight: 700; color: #111827; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.panel-header h2 { margin: 0; font-size: 15px; font-weight: 700; color: #111827; }

.count-badge {
  background: #F3F4F6;
  color: #6B7280;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid #E5E7EB;
}

/* ── Form ── */
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.field { display: flex; flex-direction: column; }
.actions.full { grid-column: span 3; display: flex; gap: 8px; padding-top: 4px; }

.checkbox-field { justify-content: flex-end; padding-bottom: 2px; }
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #374151;
  font-weight: 600;
  cursor: pointer;
  text-transform: none;
  letter-spacing: 0;
}
.checkbox-label input[type="checkbox"] {
  width: 15px;
  height: 15px;
  border-radius: 4px;
  padding: 0;
  cursor: pointer;
}

label {
  font-size: 12px;
  color: #374151;
  margin-bottom: 5px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

input, select {
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  background: #FAFAFA;
  color: #111827;
  font-family: 'Geist', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
select:disabled { background: #F9FAFB; color: #9CA3AF; cursor: not-allowed; }
input:focus, select:focus {
  outline: none;
  border-color: #DC2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.08);
  background: white;
}

/* ── Buttons ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  background: #EDF4FF;
  color: #1B4FD8;

  border: 1px solid #7FB3FF;
  border-radius: 9px;

  padding: 8px 14px;

  cursor: pointer;

  font-weight: 600;
  font-size: 12.5px;
  line-height: 1;

  font-family: 'Geist', sans-serif;

  transition:
    background 0.15s,
    color 0.15s,
    border-color 0.15s,
    transform 0.12s,
    box-shadow 0.15s;
}

.btn-primary:hover {
  background: #1B4FD8;
  color: #FFFFFF;

  border-color: transparent;

  box-shadow:
    0 4px 12px rgba(27, 79, 216, 0.22),
    0 2px 6px rgba(124, 58, 237, 0.18);
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn-primary i {
  font-size: 14px;
}
/* ── Filters ── */
.filters {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  align-items: end;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F3F4F6;
}
.filters label { font-size: 11px; }
.filters input, .filters select { padding: 8px 10px; font-size: 12px; }

/* ── Feedback ── */
.error   { color: #DC2626; margin-top: 10px; font-size: 13px; }
.success { color: #16A34A; margin-top: 10px; font-size: 13px; }
.loading, .empty { text-align: center; color: #6B7280; padding: 24px; font-size: 14px; }

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
td {
  padding: 10px 12px;
  border-bottom: 1px solid #F9FAFB;
  color: #374151;
  font-size: 13px;
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: #FAFAFA; }
.table-actions { display: flex; gap: 6px; }

/* ── Badges ── */
.badge {
  display: inline-flex;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.badge-red   { background: rgba(220,38,38,0.08);   color: #DC2626; }
.badge-blue  { background: #EFF6FF; color: #1B4FD8; border: 1px solid #DBEAFE; }
.badge-green { background: rgba(22,163,74,0.08);   color: #16A34A; }
.badge-gray  { background: rgba(107,114,128,0.08); color: #6B7280; }

/* ── Small buttons ── */
.small-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #F3F4F6;
  color: #374151;
  border: 1px solid #E5E7EB;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
  transition: background 0.15s;
}
.small-btn i { font-size: 13px; }
.small-btn:hover { background: #E5E7EB; }
.small-btn.danger { background: rgba(220,38,38,0.06); color: #DC2626; border-color: rgba(220,38,38,0.2); }
.small-btn.danger:hover { background: rgba(220,38,38,0.12); }

/* ── Responsive ── */
@media (max-width: 1200px) { .filters { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 900px) {
  .form-grid { grid-template-columns: 1fr 1fr; }
  .actions.full { grid-column: span 2; }
}
@media (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
  .actions.full { grid-column: span 1; }
  .filters { grid-template-columns: 1fr; }
}
</style>