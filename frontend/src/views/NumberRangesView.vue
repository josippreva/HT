<template>
  <div>
    <div class="page-header">
      <h1>Rasponi</h1>
      <p>Interna dodjela RAK blokova na lokacije i generiranje fiksnih brojeva.</p>
    </div>

    <section class="panel">
      <h2>Novi interni raspon</h2>

      <form class="form-grid" @submit.prevent="createRange">

        <div class="field full">
          <label>RAK blok</label>
          <select v-model="form.rak_block_id" @change="onRakBlockChange" required>
            <option value="">Odaberi RAK blok</option>
            <option v-for="block in rakBlocks" :key="block.id" :value="block.id">
              {{ block.area_code }} | {{ block.block_start }} – {{ block.block_end }} | {{ block.operator_name }}
            </option>
          </select>
        </div>

        <div v-if="blockResolving" class="field full resolve-hint">
          <div class="spinner-inline"></div>
          Određivanje regije po area code-u...
        </div>
        <div v-else-if="resolvedRegionName" class="field full resolve-hint success-hint">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          Regija prepoznata: <strong>{{ resolvedRegionName }}</strong>
        </div>
        <div v-else-if="form.rak_block_id && !blockResolving && !resolvedRegionName" class="field full resolve-hint warn-hint">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Area code nije pronađen — odaberi grad ručno.
        </div>

        <div class="field">
          <label>Grad/općina</label>
          <select
            v-model="form.city_id"
            @change="onCityChange"
            :disabled="!form.rak_block_id || blockResolving"
            required
          >
            <option value="">
              {{ blockResolving ? 'Učitavanje...' : citiesForRegion.length ? 'Odaberi grad' : 'Odaberi RAK blok prvo' }}
            </option>
            <option v-for="city in citiesForRegion" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Lokacija</label>
          <select v-model="form.location_id" @change="onLocationChange" :disabled="!form.city_id" required>
            <option value="">
              {{ !form.city_id ? 'Odaberi grad prvo' : 'Odaberi lokaciju' }}
            </option>
            <option v-for="location in locationsForCity" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
          <span v-if="form.city_id && locationsForCity.length === 0" class="field-hint">
            Nema lokacija za odabrani grad.
          </span>
        </div>

        <div class="field">
          <label>Uređaj</label>
          <select v-model="form.device_id" :disabled="!form.location_id" required>
            <option value="">
              {{ !form.location_id ? 'Odaberi lokaciju prvo' : devicesForLocation.length === 0 ? 'Nema uređaja na lokaciji' : 'Odaberi uređaj' }}
            </option>
            <option v-for="device in devicesForLocation" :key="device.id" :value="device.id">
              {{ device.name }} — {{ device.device_type }}
            </option>
          </select>
          <span v-if="form.location_id && devicesForLocation.length === 0" class="field-hint">
            Nema uređaja za odabranu lokaciju.
          </span>
        </div>

        <div class="field">
          <label>Naziv raspona <span class="optional">(opcionalno)</span></label>
          <input v-model="form.name" type="text" placeholder="npr. Mostar blok 1" />
        </div>

        <div class="field">
          <label>Od broja</label>
          <input v-model="form.range_start" type="text" placeholder="npr. 36500000" required />
        </div>

        <div class="field">
          <label>Do broja</label>
          <input v-model="form.range_end" type="text" placeholder="npr. 36500099" required />
        </div>

        <div class="actions full">
          <button type="submit" class="btn-primary">Spremi raspon</button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis raspona</h2>
        <span class="count-badge">Ukupno: {{ ranges.length }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Naziv</th>
            <th>Raspon</th>
            <th>Veličina</th>
            <th>RAK blok</th>
            <th>Lokacija</th>
            <th>Uređaj</th>
            <th>Status</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="range in ranges" :key="range.id">
            <td><strong>{{ range.name || "—" }}</strong></td>
            <td>{{ range.range_start }} – {{ range.range_end }}</td>
            <td>{{ range.range_size }}</td>
            <td>{{ range.rak_block_start }} – {{ range.rak_block_end }}</td>
            <td>{{ range.location_name }} — {{ range.city_name }}</td>
            <td>{{ range.device_name || "—" }}</td>
            <td>
              <span class="badge" :class="range.generated ? 'badge-green' : 'badge-gray'">
                {{ range.generated ? "Generirano" : "Nije generirano" }}
              </span>
            </td>
            <td class="table-actions">
              <button v-if="!range.generated" class="small-btn generate" @click="generateNumbers(range)">
                Generiraj
              </button>
            </td>
          </tr>
          <tr v-if="ranges.length === 0">
            <td colspan="8" class="empty">Nema unesenih raspona.</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import api from "../api/client";

const rakBlocks = ref([]);
const allLocations = ref([]);
const ranges = ref([]);

const resolvedRegionId = ref(null);
const resolvedRegionName = ref("");
const citiesForRegion = ref([]);
const locationsForCity = ref([]);
const devicesForLocation = ref([]);

const loading = ref(false);
const blockResolving = ref(false);
const error = ref("");
const success = ref("");

const form = reactive({
  rak_block_id: "",
  city_id: "",
  location_id: "",
  device_id: "",
  name: "",
  range_start: "",
  range_end: "",
});

const selectedBlock = computed(() =>
  rakBlocks.value.find((b) => String(b.id) === String(form.rak_block_id))
);

async function loadRakBlocks() {
  const response = await api.get("/rak-number-blocks");
  rakBlocks.value = response.data;
}

async function loadAllLocations() {
  const response = await api.get("/locations");
  allLocations.value = response.data;
}

async function loadRanges() {
  loading.value = true;
  try {
    const response = await api.get("/number-ranges");
    ranges.value = response.data;
  } finally {
    loading.value = false;
  }
}

async function onRakBlockChange() {
  form.city_id = "";
  form.location_id = "";
  form.device_id = "";
  resolvedRegionId.value = null;
  resolvedRegionName.value = "";
  citiesForRegion.value = [];
  locationsForCity.value = [];
  devicesForLocation.value = [];
  error.value = "";

  if (!form.rak_block_id || !selectedBlock.value) return;

  const areaCode = selectedBlock.value.area_code;
  if (!areaCode) return;

  blockResolving.value = true;
  try {
    const response = await api.get("/area-codes");
    const areaCodes = response.data;
    const match = areaCodes.find((ac) => String(ac.code) === String(areaCode));

    if (!match) {
      const citiesRes = await api.get("/cities");
      citiesForRegion.value = citiesRes.data;
      return;
    }

    resolvedRegionId.value = match.region_id;
    resolvedRegionName.value = match.region_name;

    const citiesRes = await api.get(`/cities?region_id=${match.region_id}`);
    citiesForRegion.value = citiesRes.data;

    if (match.city_id) {
      form.city_id = match.city_id;
      await onCityChange();
    }
  } catch (err) {
    error.value = "Greška pri određivanju regije za odabrani RAK blok.";
  } finally {
    blockResolving.value = false;
  }
}

async function onCityChange() {
  form.location_id = "";
  form.device_id = "";
  locationsForCity.value = [];
  devicesForLocation.value = [];
  if (!form.city_id) return;
  locationsForCity.value = allLocations.value.filter(
    (loc) => Number(loc.city_id) === Number(form.city_id)
  );
}

async function onLocationChange() {
  form.device_id = "";
  devicesForLocation.value = [];
  if (!form.location_id) return;
  const response = await api.get(`/devices?location_id=${form.location_id}`);
  devicesForLocation.value = response.data;
}

async function createRange() {
  error.value = "";
  success.value = "";
  try {
    await api.post("/number-ranges", {
      rak_block_id: Number(form.rak_block_id),
      location_id: Number(form.location_id),
      device_id: Number(form.device_id),
      name: form.name || null,
      range_start: form.range_start,
      range_end: form.range_end,
    });
    Object.assign(form, {
      rak_block_id: "", city_id: "", location_id: "",
      device_id: "", name: "", range_start: "", range_end: "",
    });
    resolvedRegionId.value = null;
    resolvedRegionName.value = "";
    citiesForRegion.value = [];
    locationsForCity.value = [];
    devicesForLocation.value = [];
    success.value = "Raspon je uspješno spremljen.";
    await loadRanges();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri spremanju raspona.";
  }
}

async function generateNumbers(range) {
  if (!confirm(`Generirati brojeve za raspon ${range.range_start} – ${range.range_end}?`)) return;
  error.value = "";
  success.value = "";
  try {
    const response = await api.post(`/phone-numbers/generate/${range.id}`);
    success.value = response.data.message;
    await loadRanges();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri generiranju brojeva.";
  }
}

onMounted(async () => {
  await Promise.all([loadRakBlocks(), loadAllLocations()]);
  await loadRanges();
});
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 28px; color: #111827; }
.page-header p { margin-top: 5px; color: #6b7280; font-size: 14px; }

.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}
.panel h2 { margin-top: 0; margin-bottom: 16px; font-size: 16px; color: #111827; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.panel-header h2 { margin: 0; }
.count-badge {
  background: #f3f4f6;
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.field { display: flex; flex-direction: column; }
.field.full { grid-column: span 3; }
.actions.full { grid-column: span 3; display: flex; gap: 8px; padding-top: 2px; }

label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.optional { font-weight: 400; color: #9ca3af; font-size: 12px; text-transform: none; letter-spacing: 0; }

input, select {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  background: white;
  color: #111827;
  transition: border-color 0.15s, box-shadow 0.15s;
}
select:disabled { background: #f9fafb; color: #9ca3af; cursor: not-allowed; }
input:focus, select:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
}

.field-hint { font-size: 11px; color: #f59e0b; margin-top: 4px; }

.resolve-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 9px 13px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  background: #f9fafb;
}
.resolve-hint.success-hint {
  background: rgba(22,163,74,0.06);
  border-color: rgba(22,163,74,0.25);
  color: #15803d;
}
.resolve-hint.warn-hint {
  background: rgba(245,158,11,0.06);
  border-color: rgba(245,158,11,0.3);
  color: #b45309;
}

.spinner-inline {
  width: 14px;
  height: 14px;
  border: 2px solid #e5e7eb;
  border-top-color: #dc2626;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.btn-primary {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 13px;
}

.error { color: #dc2626; margin-top: 10px; font-size: 13px; }
.success { color: #16a34a; margin-top: 10px; font-size: 13px; }
.loading, .empty { text-align: center; color: #6b7280; padding: 24px; font-size: 14px; }

table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  background: #f9fafb;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 10px 12px;
  border-bottom: 1px solid #e5e7eb;
}
td {
  padding: 10px 12px;
  border-bottom: 1px solid #eef2f7;
  color: #374151;
  font-size: 13px;
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
.table-actions { display: flex; gap: 6px; }

.badge {
  display: inline-flex;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.badge-green { background: rgba(22,163,74,0.1); color: #16a34a; }
.badge-gray { background: rgba(107,114,128,0.1); color: #6b7280; }

.small-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.small-btn:hover { background: #e5e7eb; }

.small-btn.generate {
  background: rgba(37,99,235,0.1);
  color: #2563eb;
  border-color: rgba(37,99,235,0.25);
}
.small-btn.generate:hover { background: rgba(37,99,235,0.18); }
@media (max-width: 900px) {
  .form-grid { grid-template-columns: 1fr 1fr; }
  .field.full, .actions.full { grid-column: span 2; }
}
@media (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .actions.full { grid-column: span 1; }
}
</style>