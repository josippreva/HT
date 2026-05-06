<template>
  <div>
    <div class="page-header">
      <h1>Lokacije</h1>
      <p>Kreiranje lokacija kroz hijerarhiju entitet → regija → grad/općina.</p>
    </div>

    <section class="panel">
      <h2>Nova lokacija</h2>

      <form class="form-grid" @submit.prevent="createLocation">
        <div class="field">
          <label>Entitet</label>
          <select v-model="form.entity_id" @change="onEntityChange" required>
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">
              {{ entity.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Regija</label>
          <select v-model="form.region_id" @change="onRegionChange" :disabled="!form.entity_id" required>
            <option value="">Odaberi regiju</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Grad / općina</label>
          <select v-model="form.city_id" @change="onCityChange" :disabled="!form.region_id" required>
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
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
              <button class="small-btn" @click="startEdit(location)">Uredi</button>
              <button class="small-btn danger" @click="deleteLocation(location.id)">Obriši</button>
            </td>
          </tr>
          <tr v-if="locations.length === 0">
            <td colspan="7" class="empty">Nema unesenih lokacija.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Edit modal -->
    <div v-if="editModal.open" class="modal-backdrop" @click.self="closeEdit">
      <div class="modal">
        <h2>Uredi lokaciju</h2>

        <form class="form-grid" @submit.prevent="saveEdit">
          <div class="field">
            <label>Entitet</label>
            <select v-model="editForm.entity_id" @change="onEditEntityChange" required>
              <option value="">Odaberi entitet</option>
              <option v-for="entity in entities" :key="entity.id" :value="entity.id">
                {{ entity.name }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>Regija</label>
            <select v-model="editForm.region_id" @change="onEditRegionChange" :disabled="!editForm.entity_id" required>
              <option value="">Odaberi regiju</option>
              <option v-for="region in editRegions" :key="region.id" :value="region.id">
                {{ region.name }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>Grad / općina</label>
            <select v-model="editForm.city_id" @change="onEditCityChange" :disabled="!editForm.region_id" required>
              <option value="">Odaberi grad/općinu</option>
              <option v-for="city in editCities" :key="city.id" :value="city.id">
                {{ city.name }}
              </option>
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
  entity_id:      "",
  region_id:      "",
  city_id:        "",
  postal_code_id: "",
  name:           "",
  address:        "",
  note:           "",
});

const editModal       = reactive({ open: false, id: null });
const editRegions     = ref([]);
const editCities      = ref([]);
const editPostalCodes = ref([]);
const editSubmitting  = ref(false);
const editError       = ref("");

const editForm = reactive({
  entity_id:      "",
  region_id:      "",
  city_id:        "",
  postal_code_id: "",
  name:           "",
  address:        "",
  note:           "",
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
      city_id:        Number(form.city_id),
      postal_code_id: Number(form.postal_code_id),
      name:    form.name,
      address: form.address || null,
      note:    form.note    || null,
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
    entity_id:      entityId,
    region_id:      regionId,
    city_id:        location.city_id,
    postal_code_id: location.postal_code_id,
    name:           location.name,
    address:        location.address || "",
    note:           location.note    || "",
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
      city_id:        Number(editForm.city_id),
      postal_code_id: Number(editForm.postal_code_id),
      name:    editForm.name,
      address: editForm.address || null,
      note:    editForm.note    || null,
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

input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  background: white;
  color: #111827;
  transition: border-color 0.15s, box-shadow 0.15s;
}
textarea { min-height: 68px; }
select:disabled { background: #f9fafb; color: #9ca3af; cursor: not-allowed; }
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
}

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
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
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
.badge-blue { background: rgba(37,99,235,0.1); color: #2563eb; }

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
.small-btn.danger { background: rgba(220,38,38,0.08); color: #dc2626; border-color: rgba(220,38,38,0.2); }
.small-btn.danger:hover { background: rgba(220,38,38,0.15); }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}
.modal {
  background: #fff;
  border-radius: 22px;
  padding: 24px;
  width: 680px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.modal h2 { margin: 0 0 16px; font-size: 16px; color: #111827; }

@media (max-width: 900px) {
  .form-grid { grid-template-columns: 1fr 1fr; }
  .field.full, .actions.full { grid-column: span 2; }
}
@media (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .actions.full { grid-column: span 1; }
}
</style>