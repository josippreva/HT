<template>
  <div>
    <div class="page-header">
      <h1><i class="ti ti-users"></i> Pretplatnici</h1>
      <p>Pregled, unos i uređivanje pretplatnika s pripadajućim gradom i poštanskim brojem.</p>
    </div>

    <section class="panel">
      <h2>Novi pretplatnik</h2>

      <form class="form-grid" @submit.prevent="saveSubscriber">

        <div class="field full">
          <label>Tip pretplatnika</label>
          <div class="type-toggle">
            <button type="button" :class="['toggle-btn', form.subscriber_type === 'physical_person' ? 'active' : '']" @click="form.subscriber_type = 'physical_person'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Fizička osoba
            </button>
            <button type="button" :class="['toggle-btn', form.subscriber_type === 'legal_entity' ? 'active' : '']" @click="form.subscriber_type = 'legal_entity'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              Pravna osoba
            </button>
          </div>
        </div>

        <template v-if="form.subscriber_type === 'physical_person'">
          <div class="field">
            <label>Ime</label>
            <input v-model="form.first_name" type="text" placeholder="Ime" />
          </div>
          <div class="field">
            <label>Prezime</label>
            <input v-model="form.last_name" type="text" placeholder="Prezime" />
          </div>
        </template>

        <template v-else>
          <div class="field half">
            <label>Naziv firme</label>
            <input v-model="form.company_name" type="text" placeholder="Naziv pravne osobe" />
          </div>
        </template>

        <div v-if="form.subscriber_type === 'physical_person'" class="field">
          <label>JMBG</label>
          <input v-model="form.jmbg" type="text" maxlength="13" placeholder="13 znamenki" />
        </div>
        <div v-else class="field">
          <label>ID broj firme</label>
          <input v-model="form.company_id_number" type="text" placeholder="ID / porezni broj firme" />
        </div>

        <div class="field">
          <label>Kontakt telefon</label>
          <input v-model="form.contact_phone" type="text" placeholder="+387 xx xxx xxx" />
        </div>

        <div class="field half">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="email@primjer.ba" />
        </div>

        <div class="section-label">Adresa</div>

        <div class="field">
          <label>Entitet</label>
          <select v-model="form.entity_id" @change="onEntityChange">
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Županija</label>
          <select v-model="form.region_id" @change="onRegionChange" :disabled="!form.entity_id">
            <option value="">Odaberi županiju</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Grad / općina</label>
          <select v-model="form.city_id" @change="onCityChange" :disabled="!form.region_id">
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">{{ city.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Poštanski broj</label>
          <select v-model="form.postal_code_id" :disabled="!form.city_id">
            <option value="">Odaberi poštanski broj</option>
            <option v-for="postal in postalCodes" :key="postal.id" :value="postal.id">
              {{ postal.postal_code }} — {{ postal.postal_name }}
            </option>
          </select>
        </div>

        <div class="field half">
          <label>Ulica i broj</label>
          <input v-model="form.address" type="text" placeholder="npr. Ulica bb" />
        </div>

        <div class="field full">
          <label>Napomena <span class="optional">(opcionalno)</span></label>
          <textarea v-model="form.note" placeholder="Dodatne napomene..."></textarea>
        </div>

        <div class="actions full">
          <button type="submit" class="btn-primary">
            <i class="ti ti-device-floppy"></i>
            Spremi pretplatnika
          </button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <div class="filters-top">
        <div class="field">
          <label>Pretraga</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Ime, prezime, firma, JMBG, dodijeljeni broj..."
            @input="loadSubscribers"
          />
        </div>
        <div class="field">
          <label>Tip</label>
          <select v-model="typeFilter">
            <option value="">Svi tipovi</option>
            <option value="physical_person">Fizička osoba</option>
            <option value="legal_entity">Pravna osoba</option>
          </select>
        </div>
      </div>

      <div class="filters-bottom">
        <div class="field">
          <label>Entitet</label>
          <select v-model="filters.entity_id" @change="onFilterEntityChange">
            <option value="">Svi entiteti</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Regija</label>
          <select v-model="filters.region_id" @change="onFilterRegionChange" :disabled="!filters.entity_id">
            <option value="">Sve regije</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Grad</label>
          <select v-model="filters.city_id" @change="onFilterCityChange" :disabled="!filters.region_id">
            <option value="">Svi gradovi</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">{{ city.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Lokacija</label>
          <select v-model="filters.location_id" @change="onFilterLocationChange" :disabled="!filters.city_id">
            <option value="">Sve lokacije</option>
            <option v-for="location in locations" :key="location.id" :value="location.id">{{ location.name }}</option>
          </select>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis pretplatnika</h2>
        <span class="count-badge">Ukupno: {{ filteredSubscribers.length }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Naziv</th>
            <th>Tip</th>
            <th>JMBG / Identifikator</th>
            <th>Dodijeljeni broj</th>
            <th>Kontakt</th>
            <th>Adresa</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subscriber in filteredSubscribers" :key="subscriber.id">
            <td>
              <strong>{{ displayName(subscriber) }}</strong>
              <div class="sub-id">ID: {{ subscriber.id }}</div>
            </td>
            <td>
              <span class="subscriber-type-badge" :class="subscriber.subscriber_type === 'legal_entity' ? 'legal' : 'physical'">
                <template v-if="subscriber.subscriber_type === 'physical_person'">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  Fizička osoba
                </template>
                <template v-else>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <rect x="2" y="7" width="20" height="14" rx="2"/>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                  </svg>
                  Pravna osoba
                </template>
              </span>
            </td>
            <td>{{ subscriber.subscriber_type === "legal_entity" ? subscriber.company_id_number || "—" : subscriber.jmbg || "—" }}</td>
            <td>
              <span v-if="subscriber.assigned_phone_numbers?.length">
                {{ subscriber.assigned_phone_numbers.map(num => formatPhoneNumber(num)).join(", ") }}
              </span>
              <span v-else>—</span>
            </td>
            <td>
              <div>{{ subscriber.contact_phone || "—" }}</div>
              <div class="muted">{{ subscriber.email || "" }}</div>
            </td>
            <td>
              <div>{{ subscriber.address || "—" }}</div>
              <div class="muted">{{ subscriber.city_name || "" }}</div>
            </td>
            <td>
              <div class="table-actions">
                <button class="small-btn" @click="startEdit(subscriber)">
                  <i class="ti ti-pencil"></i> Uredi
                </button>
                <button class="small-btn danger" @click="deleteSubscriber(subscriber)">
                  <i class="ti ti-trash"></i> Obriši
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredSubscribers.length === 0">
            <td colspan="7" class="empty">Nema pretplatnika za prikaz.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <EditSubscribers
      :open="editModal.open"
      :subscriber="editModal.subscriber"
      :entities="entities"
      @close="closeEdit"
      @saved="loadSubscribers"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import api from "../api/client";
import EditSubscribers from "../components/EditSubscribers.vue";

const subscribers = ref([]);
const entities    = ref([]);
const regions     = ref([]);
const cities      = ref([]);
const postalCodes = ref([]);
const locations   = ref([]);

const typeFilter = ref("");
const loading    = ref(false);
const error      = ref("");
const success    = ref("");

const filters = reactive({
  search: "", entity_id: "", region_id: "", city_id: "", location_id: "",
});

const form = reactive({
  subscriber_type: "physical_person",
  first_name: "", last_name: "", company_name: "",
  jmbg: "", company_id_number: "",
  entity_id: "", region_id: "", city_id: "", postal_code_id: "",
  address: "", contact_phone: "", email: "", note: "",
});

const editModal = reactive({ open: false, subscriber: null });

const filteredSubscribers = computed(() => {
  if (!typeFilter.value) return subscribers.value;
  return subscribers.value.filter(s => s.subscriber_type === typeFilter.value);
});

function displayName(subscriber) {
  if (subscriber.subscriber_type === "legal_entity") return subscriber.company_name || "-";
  return `${subscriber.first_name || ""} ${subscriber.last_name || ""}`.trim() || "-";
}

function formatPhoneNumber(value) {
  if (!value) return "";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length === 8) return `+387 ${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  if (digits.length === 9) return `+387 ${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  return value;
}

function buildPayload() {
  return {
    subscriber_type: form.subscriber_type,
    first_name: form.subscriber_type === "physical_person" ? form.first_name || null : null,
    last_name: form.subscriber_type === "physical_person" ? form.last_name || null : null,
    company_name: form.subscriber_type === "legal_entity" ? form.company_name || null : null,
    jmbg: form.subscriber_type === "physical_person" ? form.jmbg || null : null,
    company_id_number: form.subscriber_type === "legal_entity" ? form.company_id_number || null : null,
    city_id: form.city_id ? Number(form.city_id) : null,
    postal_code_id: form.postal_code_id ? Number(form.postal_code_id) : null,
    address: form.address || null,
    contact_phone: form.contact_phone || null,
    email: form.email || null,
    note: form.note || null,
  };
}

async function loadEntities() {
  const response = await api.get("/entities");
  entities.value = response.data;
}

async function loadRegions() {
  const response = await api.get("/regions");
  regions.value = response.data;
}

async function loadSubscribers() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.search)      params.append("search",      filters.search);
    if (filters.entity_id)   params.append("entity_id",   filters.entity_id);
    if (filters.region_id)   params.append("region_id",   filters.region_id);
    if (filters.city_id)     params.append("city_id",     filters.city_id);
    if (filters.location_id) params.append("location_id", filters.location_id);
    const response = await api.get(`/subscribers?${params.toString()}`);
    subscribers.value = response.data;
  } finally {
    loading.value = false;
  }
}

async function onEntityChange() {
  form.region_id = form.city_id = form.postal_code_id = "";
  regions.value = cities.value = postalCodes.value = [];
  if (!form.entity_id) return;
  const response = await api.get(`/regions?entity_id=${form.entity_id}`);
  regions.value = response.data;
}

async function onRegionChange() {
  form.city_id = form.postal_code_id = "";
  cities.value = postalCodes.value = [];
  if (!form.region_id) return;
  const response = await api.get(`/cities?region_id=${form.region_id}`);
  cities.value = response.data;
}

async function onCityChange() {
  form.postal_code_id = "";
  postalCodes.value = [];
  if (!form.city_id) return;
  const response = await api.get(`/postal-codes?city_id=${form.city_id}`);
  postalCodes.value = response.data;
}

async function onFilterEntityChange() {
  filters.region_id = filters.city_id = filters.location_id = "";
  regions.value = cities.value = locations.value = [];
  if (filters.entity_id) {
    const response = await api.get(`/regions?entity_id=${filters.entity_id}`);
    regions.value = response.data;
  } else {
    await loadRegions();
  }
  await loadSubscribers();
}

async function onFilterRegionChange() {
  filters.city_id = filters.location_id = "";
  cities.value = locations.value = [];
  if (filters.region_id) {
    const response = await api.get(`/cities?region_id=${filters.region_id}`);
    cities.value = response.data;
  }
  await loadSubscribers();
}

async function onFilterCityChange() {
  filters.location_id = "";
  locations.value = [];
  if (filters.city_id) {
    const response = await api.get("/locations");
    locations.value = response.data.filter(
      (l) => Number(l.city_id) === Number(filters.city_id)
    );
  }
  await loadSubscribers();
}

async function onFilterLocationChange() {
  await loadSubscribers();
}

async function saveSubscriber() {
  error.value = success.value = "";
  try {
    await api.post("/subscribers", buildPayload());
    success.value = "Pretplatnik je uspješno spremljen.";
    resetForm();
    await loadSubscribers();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri spremanju pretplatnika.";
  }
}

function startEdit(subscriber) {
  editModal.subscriber = subscriber;
  editModal.open = true;
}

function closeEdit() {
  editModal.open = false;
  editModal.subscriber = null;
}

function resetForm() {
  form.subscriber_type = "physical_person";
  form.first_name = form.last_name = form.company_name = "";
  form.jmbg = form.company_id_number = "";
  form.entity_id = form.region_id = form.city_id = form.postal_code_id = "";
  form.address = form.contact_phone = form.email = form.note = "";
  regions.value = cities.value = postalCodes.value = [];
}

async function deleteSubscriber(subscriber) {
  if (!confirm(`Obrisati pretplatnika "${displayName(subscriber)}"?`)) return;
  error.value = success.value = "";
  try {
    await api.delete(`/subscribers/${subscriber.id}`);
    success.value = "Pretplatnik je obrisan.";
    await loadSubscribers();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri brisanju pretplatnika.";
  }
}

onMounted(async () => {
  await loadEntities();
  await loadRegions();
  await loadSubscribers();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { font-family: 'Geist', sans-serif; }

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

.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}
.panel h2 { margin-top: 0; margin-bottom: 16px; font-size: 16px; color: #111827; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.field { display: flex; flex-direction: column; }
.field.full { grid-column: span 3; }
.field.half { grid-column: span 2; }
.actions.full { grid-column: span 3; display: flex; gap: 8px; padding-top: 2px; }

.section-label {
  grid-column: span 3;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #9ca3af;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 6px;
  margin-top: 4px;
  display: flex;
  align-items: center;
}

label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.optional { font-weight: 400; color: #9ca3af; font-size: 12px; text-transform: none; letter-spacing: 0; }

.type-toggle { display: flex; gap: 8px; }
.toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #FFFFFF;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 11px 14px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  font-family: 'Geist', sans-serif;
  transition: background 0.12s, color 0.12s, border-color 0.12s, transform 0.12s;
}
.toggle-btn:hover { background: #EDF4FF; color: #1B4FD8; border-color: #7FB3FF; }
.toggle-btn.active { background: #EFF6FF; color: #1B4FD8; border-color: #93C5FD; }
.toggle-btn:active { transform: scale(0.98); }

input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  background: white;
  color: #111827;
  font-family: 'Geist', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
textarea { min-height: 68px; }
select:disabled { background: #f9fafb; color: #9ca3af; cursor: not-allowed; }
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #1B4FD8;
  box-shadow: 0 0 0 3px rgba(27, 79, 216, 0.08);
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
  transition: background 0.15s, color 0.15s, border-color 0.15s, transform 0.12s, box-shadow 0.15s;
}
.btn-primary:hover {
  background: #1B4FD8;
  color: #FFFFFF;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(27, 79, 216, 0.22), 0 2px 6px rgba(124, 58, 237, 0.18);
}
.btn-primary:active { transform: scale(0.98); }
.btn-primary i { font-size: 14px; }

.filters-top {
  display: grid;
  grid-template-columns: 1fr 200px;
  gap: 10px;
  align-items: end;
  margin-bottom: 10px;
}
.filters-bottom {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  align-items: end;
  padding-top: 10px;
  border-top: 1px solid #f3f4f6;
}
.filters-top label, .filters-bottom label { font-size: 11px; }
.filters-top input, .filters-top select, .filters-bottom select { padding: 8px 10px; font-size: 12px; }

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

.muted { color: #6b7280; font-size: 12px; }
.sub-id { font-size: 11px; color: #9ca3af; margin-top: 2px; font-weight: 400; }
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
.table-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.subscriber-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 6px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.01em;
  border: 1px solid transparent;
  white-space: nowrap;
  min-width: 88px;
}
.subscriber-type-badge svg { width: 13px; height: 13px; flex-shrink: 0; }
.subscriber-type-badge.physical { background: #EDF4FF; color: #1B4FD8; border-color: #BFDBFE; }
.subscriber-type-badge.legal    { background: #E5E7EB; color: #111827; border-color: #D1D5DB; }

.small-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
  transition: background 0.15s;
}
.small-btn i { font-size: 13px; }
.small-btn:hover { background: #e5e7eb; }
.small-btn.danger { background: rgba(220,38,38,0.08); color: #dc2626; border-color: rgba(220,38,38,0.2); }
.small-btn.danger:hover { background: rgba(220,38,38,0.15); }

@media (max-width: 900px) {
  .filters-top { grid-template-columns: 1fr; }
  .filters-bottom { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .field.half, .actions.full, .section-label { grid-column: span 1; }
  .type-toggle { flex-direction: column; }
  .filters-bottom { grid-template-columns: 1fr; }
}
</style>