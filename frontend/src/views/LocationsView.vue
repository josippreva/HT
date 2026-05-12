<template>
  <div>
    <div class="page-header">
      <h1><i class="ti ti-map-pin"></i> Lokacije</h1>
      <p>Kreiranje lokacija kroz hijerarhiju entitet → regija → grad/općina.</p>
    </div>

    <section class="panel">
      <h2>Nova lokacija</h2>

      <form class="form-grid" @submit.prevent="createLocation">
        <div class="field">
          <label>Entitet</label>
          <select v-model="form.entity_id" @change="onEntityChange" required>
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Regija</label>
          <select v-model="form.region_id" @change="onRegionChange" :disabled="!form.entity_id" required>
            <option value="">Odaberi regiju</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Grad / općina</label>
          <select v-model="form.city_id" @change="onCityChange" :disabled="!form.region_id" required>
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">{{ city.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Poštanski broj</label>
          <select v-model="form.postal_code_id" :disabled="!form.city_id" required>
            <option value="">Odaberi poštanski broj</option>
            <option v-for="postal in postalCodes" :key="postal.id" :value="postal.id">
              {{ postal.postal_code }} – {{ postal.postal_name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Naziv lokacije</label>
          <input v-model="form.name" type="text" placeholder="npr. HT Mostar Centar" required />
        </div>

        <div class="field">
          <label>Adresa</label>
          <input v-model="form.address" type="text" placeholder="Adresa lokacije" />
        </div>

        <div class="field full">
          <label>Napomena <span class="optional">(opcionalno)</span></label>
          <textarea v-model="form.note" placeholder="Opcionalna napomena"></textarea>
        </div>

        <div class="actions full">
          <button type="submit" class="btn-primary" :disabled="submitting">
            <i class="ti ti-device-floppy"></i>
            {{ submitting ? "Spremanje..." : "Spremi lokaciju" }}
          </button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis lokacija</h2>
        <span class="count-badge">Ukupno: {{ locations.length }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Naziv</th>
            <th>Grad/općina</th>
            <th>Pošt. broj</th>
            <th>Naziv pošte</th>
            <th>Adresa</th>
            <th>Napomena</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="location in locations" :key="location.id">
            <td><strong>{{ location.name }}</strong></td>
            <td>{{ location.city_name }}</td>
            <td><span class="badge badge-blue">{{ location.postal_code }}</span></td>
            <td>{{ location.postal_name }}</td>
            <td>{{ location.address || "—" }}</td>
            <td>{{ location.note || "—" }}</td>
            <td class="table-actions">
              <button class="small-btn" @click="startEdit(location)">
                <i class="ti ti-pencil"></i> Uredi
              </button>
              <button class="small-btn danger" @click="deleteLocation(location.id)">
                <i class="ti ti-trash"></i> Obriši
              </button>
            </td>
          </tr>
          <tr v-if="locations.length === 0">
            <td colspan="7" class="empty">Nema unesenih lokacija.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-if="editModal.open" class="modal-backdrop" @click.self="closeEdit">
      <div class="modal">
        <h2><i class="ti ti-pencil"></i> Uredi lokaciju</h2>

        <form class="form-grid" @submit.prevent="saveEdit">
          <div class="field">
            <label>Entitet</label>
            <select v-model="editForm.entity_id" @change="onEditEntityChange" required>
              <option value="">Odaberi entitet</option>
              <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
            </select>
          </div>

          <div class="field">
            <label>Regija</label>
            <select v-model="editForm.region_id" @change="onEditRegionChange" :disabled="!editForm.entity_id" required>
              <option value="">Odaberi regiju</option>
              <option v-for="region in editRegions" :key="region.id" :value="region.id">{{ region.name }}</option>
            </select>
          </div>

          <div class="field">
            <label>Grad / općina</label>
            <select v-model="editForm.city_id" @change="onEditCityChange" :disabled="!editForm.region_id" required>
              <option value="">Odaberi grad/općinu</option>
              <option v-for="city in editCities" :key="city.id" :value="city.id">{{ city.name }}</option>
            </select>
          </div>

          <div class="field">
            <label>Poštanski broj</label>
            <select v-model="editForm.postal_code_id" :disabled="!editForm.city_id" required>
              <option value="">Odaberi poštanski broj</option>
              <option v-for="postal in editPostalCodes" :key="postal.id" :value="postal.id">
                {{ postal.postal_code }} – {{ postal.postal_name }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>Naziv lokacije</label>
            <input v-model="editForm.name" type="text" required />
          </div>

          <div class="field">
            <label>Adresa</label>
            <input v-model="editForm.address" type="text" />
          </div>

          <div class="field full">
            <label>Napomena <span class="optional">(opcionalno)</span></label>
            <textarea v-model="editForm.note"></textarea>
          </div>

          <div class="actions full">
            <button type="submit" class="btn-primary" :disabled="editSubmitting">
              <i class="ti ti-device-floppy"></i>
              {{ editSubmitting ? "Spremanje..." : "Spremi izmjene" }}
            </button>
            <button type="button" class="btn-secondary" @click="closeEdit">Odustani</button>
          </div>
        </form>

        <p v-if="editError" class="error">{{ editError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import api from "../api/client";

const entities    = ref([]);
const regions     = ref([]);
const cities      = ref([]);
const postalCodes = ref([]);
const locations   = ref([]);

const loading    = ref(false);
const submitting = ref(false);
const error      = ref("");
const success    = ref("");

const form = reactive({
  entity_id: "", region_id: "", city_id: "", postal_code_id: "",
  name: "", address: "", note: "",
});

const editModal       = reactive({ open: false, id: null });
const editRegions     = ref([]);
const editCities      = ref([]);
const editPostalCodes = ref([]);
const editSubmitting  = ref(false);
const editError       = ref("");

const editForm = reactive({
  entity_id: "", region_id: "", city_id: "", postal_code_id: "",
  name: "", address: "", note: "",
});

async function loadEntities() {
  const { data } = await api.get("/entities");
  entities.value = data;
}

async function loadLocations() {
  loading.value = true;
  try {
    const { data } = await api.get("/locations");
    locations.value = data;
  } finally {
    loading.value = false;
  }
}

async function onEntityChange() {
  form.region_id = form.city_id = form.postal_code_id = "";
  regions.value = cities.value = postalCodes.value = [];
  if (!form.entity_id) return;
  const { data } = await api.get(`/regions?entity_id=${form.entity_id}`);
  regions.value = data;
}

async function onRegionChange() {
  form.city_id = form.postal_code_id = "";
  cities.value = postalCodes.value = [];
  if (!form.region_id) return;
  const { data } = await api.get(`/cities?region_id=${form.region_id}`);
  cities.value = data;
}

async function onCityChange() {
  form.postal_code_id = "";
  postalCodes.value = [];
  if (!form.city_id) return;
  const { data } = await api.get(`/postal-codes?city_id=${form.city_id}`);
  postalCodes.value = data;
}

async function createLocation() {
  error.value = success.value = "";
  submitting.value = true;
  try {
    await api.post("/locations", {
      city_id: Number(form.city_id), postal_code_id: Number(form.postal_code_id),
      name: form.name, address: form.address || null, note: form.note || null,
    });
    Object.assign(form, { entity_id: "", region_id: "", city_id: "", postal_code_id: "", name: "", address: "", note: "" });
    regions.value = cities.value = postalCodes.value = [];
    success.value = "Lokacija je uspješno spremljena.";
    await loadLocations();
  } catch {
    error.value = "Greška pri spremanju lokacije.";
  } finally {
    submitting.value = false;
  }
}

async function startEdit(location) {
  editError.value = "";
  editModal.id = location.id;
  const cityResp   = await api.get(`/cities/${location.city_id}`);
  const regionId   = cityResp.data.region_id;
  const regionResp = await api.get(`/regions/${regionId}`);
  const entityId   = regionResp.data.entity_id;
  const [regionsResp, citiesResp, postalsResp] = await Promise.all([
    api.get(`/regions?entity_id=${entityId}`),
    api.get(`/cities?region_id=${regionId}`),
    api.get(`/postal-codes?city_id=${location.city_id}`),
  ]);
  editRegions.value     = regionsResp.data;
  editCities.value      = citiesResp.data;
  editPostalCodes.value = postalsResp.data;
  Object.assign(editForm, {
    entity_id: entityId, region_id: regionId, city_id: location.city_id,
    postal_code_id: location.postal_code_id, name: location.name,
    address: location.address || "", note: location.note || "",
  });
  editModal.open = true;
}

function closeEdit() {
  editModal.open = false;
  editModal.id   = null;
  editError.value = "";
}

async function onEditEntityChange() {
  editForm.region_id = editForm.city_id = editForm.postal_code_id = "";
  editRegions.value = editCities.value = editPostalCodes.value = [];
  if (!editForm.entity_id) return;
  const { data } = await api.get(`/regions?entity_id=${editForm.entity_id}`);
  editRegions.value = data;
}

async function onEditRegionChange() {
  editForm.city_id = editForm.postal_code_id = "";
  editCities.value = editPostalCodes.value = [];
  if (!editForm.region_id) return;
  const { data } = await api.get(`/cities?region_id=${editForm.region_id}`);
  editCities.value = data;
}

async function onEditCityChange() {
  editForm.postal_code_id = "";
  editPostalCodes.value = [];
  if (!editForm.city_id) return;
  const { data } = await api.get(`/postal-codes?city_id=${editForm.city_id}`);
  editPostalCodes.value = data;
}

async function saveEdit() {
  editError.value = "";
  editSubmitting.value = true;
  try {
    await api.put(`/locations/${editModal.id}`, {
      city_id: Number(editForm.city_id), postal_code_id: Number(editForm.postal_code_id),
      name: editForm.name, address: editForm.address || null, note: editForm.note || null,
    });
    closeEdit();
    await loadLocations();
  } catch {
    editError.value = "Greška pri ažuriranju lokacije.";
  } finally {
    editSubmitting.value = false;
  }
}

async function deleteLocation(id) {
  if (!confirm("Sigurno želiš obrisati ovu lokaciju?")) return;
  try {
    await api.delete(`/locations/${id}`);
    await loadLocations();
  } catch {
    alert("Greška pri brisanju lokacije.");
  }
}

onMounted(async () => {
  await loadEntities();
  await loadLocations();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { font-family: 'Geist', sans-serif; }

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

.panel {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}
.panel > h2 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

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

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.field { display: flex; flex-direction: column; }
.field.full { grid-column: span 3; }
.actions.full { grid-column: span 3; display: flex; gap: 8px; padding-top: 4px; }

label {
  font-size: 12px;
  color: #374151;
  margin-bottom: 5px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.optional { font-weight: 400; color: #9CA3AF; font-size: 12px; letter-spacing: 0; }

input, select, textarea {
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  background: #FAFAFA;
  color: #111827;
  font-family: 'Geist', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
textarea { min-height: 68px; resize: vertical; }
select:disabled { background: #F9FAFB; color: #9CA3AF; cursor: not-allowed; }

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #1B4FD8;
  box-shadow: 0 0 0 3px rgba(27, 79, 216, 0.08);
  background: white;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  background: #EDF4FF;
  color: #1B4FD8;
  border-color: #7FB3FF;

  border-radius: 10px;

  padding: 10px 16px;

  cursor: pointer;

  font-weight: 600;
  font-size: 13px;

  font-family: 'Geist', sans-serif;

  transition:
    background 0.15s,
    color 0.15s,
    border-color 0.15s,
    transform 0.12s;
}

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

.error  { color: #DC2626; margin-top: 10px; font-size: 13px; }
.success { color: #16A34A; margin-top: 10px; font-size: 13px; }
.loading, .empty { text-align: center; color: #6B7280; padding: 24px; font-size: 14px; }

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

.badge {
  display: inline-flex;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
}
.badge-blue { background: #EFF6FF; color: #1B4FD8; border: 1px solid #DBEAFE; }

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

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(2px);
}
.modal {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  width: 680px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  border: 1px solid #E5E7EB;
}
.modal h2 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}
.modal h2 i { color: #1B4FD8; font-size: 18px; }

@media (max-width: 900px) {
  .form-grid { grid-template-columns: 1fr 1fr; }
  .field.full, .actions.full { grid-column: span 2; }
}
@media (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .actions.full { grid-column: span 1; }
}
</style>