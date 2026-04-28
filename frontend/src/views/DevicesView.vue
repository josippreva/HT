<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Uređaji</h1>
        <p>Kreiranje uređaja kroz hijerarhiju entitet → županija → grad/općina → lokacija.</p>
      </div>
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
          <label>
            <input v-model="form.active" type="checkbox" />
            Aktivan uređaj
          </label>
        </div>

        <div class="actions full">
          <button type="submit">
            {{ editingId ? "Spremi izmjene" : "Spremi uređaj" }}
          </button>

          <button v-if="editingId" type="button" class="secondary" @click="cancelEdit">
            Odustani
          </button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <h2>Popis uređaja</h2>

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

      <div v-if="loading">Učitavanje...</div>

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

            <td>{{ device.serial_number || "-" }}</td>

            <td>
              <span class="badge" :class="device.active ? 'badge-green' : 'badge-gray'">
                {{ device.active ? "Aktivan" : "Neaktivan" }}
              </span>
            </td>

            <td class="table-actions">
              <button class="small-btn" @click="startEdit(device)">Edit</button>
              <button class="small-btn danger" @click="deleteDevice(device)">Delete</button>
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
  entity_id: "",
  region_id: "",
  city_id: "",
  location_id: "",
  name: "",
  device_type: "MSAN",
  serial_number: "",
  active: true,
});

const filters = reactive({
  entity_id: "",
  region_id: "",
  city_id: "",
  location_id: "",
  active: "",
  search: "",
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
  form.region_id = "";
  form.city_id = "";
  form.location_id = "";
  formRegions.value = [];
  formCities.value = [];
  formLocations.value = [];

  if (!form.entity_id) return;

  const response = await api.get(`/regions?entity_id=${form.entity_id}`);
  formRegions.value = response.data;
}

async function onFormRegionChange() {
  form.city_id = "";
  form.location_id = "";
  formCities.value = [];
  formLocations.value = [];

  if (!form.region_id) return;

  const response = await api.get(`/cities?region_id=${form.region_id}`);
  formCities.value = response.data;
}

function onFormCityChange() {
  form.location_id = "";

  if (!form.city_id) {
    formLocations.value = [];
    return;
  }

  formLocations.value = allLocations.value.filter(
    (location) => Number(location.city_id) === Number(form.city_id)
  );
}

async function onFilterEntityChange() {
  filters.region_id = "";
  filters.city_id = "";
  filters.location_id = "";

  filterRegions.value = [];
  filterCities.value = [];
  filterLocations.value = [];

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
  filters.city_id = "";
  filters.location_id = "";

  filterCities.value = [];
  filterLocations.value = [];

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
  error.value = "";
  success.value = "";

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
  } catch (err) {
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

function cancelEdit() {
  resetForm();
}

function resetForm() {
  editingId.value = null;

  form.entity_id = "";
  form.region_id = "";
  form.city_id = "";
  form.location_id = "";
  form.name = "";
  form.device_type = "MSAN";
  form.serial_number = "";
  form.active = true;

  formRegions.value = [];
  formCities.value = [];
  formLocations.value = [];
}

async function deleteDevice(device) {
  const confirmed = confirm(`Obrisati uređaj "${device.name}"?`);

  if (!confirmed) return;

  try {
    await api.delete(`/devices/${device.id}`);
    success.value = "Uređaj je obrisan.";
    await loadDevices();
  } catch (err) {
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
.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 30px;
  color: #111827;
}

.page-header p {
  margin-top: 6px;
  color: #6b7280;
}

.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}

.panel h2 {
  margin-top: 0;
  margin-bottom: 18px;
  font-size: 20px;
  color: #111827;
}

.form-grid,
.filters {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.filters {
  grid-template-columns: repeat(6, 1fr);
  margin-bottom: 22px;
}

.field {
  display: flex;
  flex-direction: column;
}

.checkbox-field {
  justify-content: center;
}

.checkbox-field label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.actions.full {
  grid-column: span 2;
  display: flex;
  gap: 10px;
}

label {
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 600;
}

input,
select {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 12px 13px;
  font-size: 14px;
  background: white;
  color: #111827;
}

input:focus,
select:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.12);
}

button {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border: none;
  padding: 13px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
}

button.secondary {
  background: #6b7280;
}

.small-btn {
  padding: 8px 11px;
  border-radius: 9px;
  font-size: 12px;
}

.small-btn.danger {
  background: #dc2626;
}

.error {
  color: #dc2626;
  margin-top: 12px;
}

.success {
  color: #16a34a;
  margin-top: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

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

.table-actions {
  display: flex;
  gap: 8px;
}

.badge {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.badge-red {
  background: rgba(220,38,38,0.12);
  color: #dc2626;
}

.badge-blue {
  background: rgba(37,99,235,0.12);
  color: #2563eb;
}

.badge-green {
  background: rgba(22,163,74,0.12);
  color: #16a34a;
}

.badge-gray {
  background: rgba(107,114,128,0.12);
  color: #6b7280;
}

.empty {
  text-align: center;
  color: #6b7280;
  padding: 28px;
}

@media (max-width: 1200px) {
  .filters {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 760px) {
  .form-grid,
  .filters {
    grid-template-columns: 1fr;
  }

  .actions.full {
    grid-column: span 1;
  }
}
</style>