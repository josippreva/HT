<template>
  <div>
    <div class="page-header">
      <h1>Pretplatnici</h1>
      <p>Pregled, unos i uređivanje pretplatnika s pripadajućim gradom i poštanskim brojem.</p>
    </div>

    <section class="panel">
      <h2>{{ editingId ? "Uredi pretplatnika" : "Novi pretplatnik" }}</h2>

      <form class="form-grid" @submit.prevent="saveSubscriber">

        <!-- Tip -->
        <div class="field full">
          <label>Tip pretplatnika</label>
          <div class="type-toggle">
            <button
              type="button"
              :class="['toggle-btn', form.subscriber_type === 'physical_person' ? 'active' : '']"
              @click="form.subscriber_type = 'physical_person'"
            >
              👤 Fizička osoba
            </button>
            <button
              type="button"
              :class="['toggle-btn', form.subscriber_type === 'legal_entity' ? 'active' : '']"
              @click="form.subscriber_type = 'legal_entity'"
            >
              🏢 Pravna osoba
            </button>
          </div>
        </div>

        <!-- Ime/Prezime ili Naziv firme -->
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
          <div class="field full">
            <label>Naziv firme</label>
            <input v-model="form.company_name" type="text" placeholder="Naziv pravne osobe" />
          </div>
        </template>

        <!-- JMBG + Kontakt -->
        <div class="field">
          <label>JMBG</label>
          <input v-model="form.jmbg" type="text" maxlength="13" placeholder="13 znamenki" />
        </div>

        <div class="field">
          <label>Kontakt telefon</label>
          <input v-model="form.contact_phone" type="text" placeholder="+387 xx xxx xxx" />
        </div>

        <div class="field full">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="email@primjer.ba" />
        </div>

        <!-- Adresa sekcija -->
        <div class="field full section-label">Adresa</div>

        <div class="field">
          <label>Entitet</label>
          <select v-model="form.entity_id" @change="onEntityChange">
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">
              {{ entity.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Županija</label>
          <select v-model="form.region_id" @change="onRegionChange" :disabled="!form.entity_id">
            <option value="">Odaberi županiju</option>
            <option v-for="region in regions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Grad/općina</label>
          <select v-model="form.city_id" @change="onCityChange" :disabled="!form.region_id">
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
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

        <div class="field full">
          <label>Ulica i broj</label>
          <input v-model="form.address" type="text" placeholder="npr. Ulica bb" />
        </div>

        <!-- Napomena -->
        <div class="field full">
          <label>Napomena <span class="optional">(opcionalno)</span></label>
          <textarea v-model="form.note" placeholder="Dodatne napomene..."></textarea>
        </div>

        <div class="actions full">
          <button type="submit">
            {{ editingId ? "Spremi izmjene" : "Spremi pretplatnika" }}
          </button>
          <button v-if="editingId" type="button" class="secondary" @click="resetForm">
            Odustani
          </button>
        </div>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </section>

    <section class="panel">
      <div class="filters">
        <div class="field search">
          <label>Pretraga</label>
          <input
            v-model="search"
            type="text"
            placeholder="Ime, firma, JMBG..."
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
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Popis pretplatnika</h2>
        <span class="muted">Ukupno: {{ filteredSubscribers.length }}</span>
      </div>

      <div v-if="loading" class="loading">Učitavanje...</div>

      <table v-else>
        <thead>
          <tr>
            <th>Naziv</th>
            <th>Tip</th>
            <th>JMBG</th>
            <th>Kontakt</th>
            <th>Adresa</th>
            <th>Akcije</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="subscriber in filteredSubscribers" :key="subscriber.id">
            <td>
              <strong>{{ displayName(subscriber) }}</strong>
              <div class="muted">ID: {{ subscriber.id }}</div>
            </td>

            <td>
              <span class="badge" :class="subscriber.subscriber_type === 'legal_entity' ? 'badge-blue' : 'badge-red'">
                {{ subscriber.subscriber_type === "legal_entity" ? "Pravna osoba" : "Fizička osoba" }}
              </span>
            </td>

            <td>{{ subscriber.jmbg || "-" }}</td>

            <td>
              <div>{{ subscriber.contact_phone || "-" }}</div>
              <div class="muted">{{ subscriber.email || "" }}</div>
            </td>

            <td>{{ subscriber.address || "-" }}</td>

            <td class="table-actions">
              <button class="small-btn" @click="startEdit(subscriber)">Edit</button>
              <button class="small-btn danger" @click="deleteSubscriber(subscriber)">Delete</button>
            </td>
          </tr>

          <tr v-if="filteredSubscribers.length === 0">
            <td colspan="6" class="empty">Nema pretplatnika za prikaz.</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import api from "../api/client";

const subscribers = ref([]);
const entities = ref([]);
const regions = ref([]);
const cities = ref([]);
const postalCodes = ref([]);

const search = ref("");
const typeFilter = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");
const editingId = ref(null);

const form = reactive({
  subscriber_type: "physical_person",
  first_name: "",
  last_name: "",
  company_name: "",
  jmbg: "",
  entity_id: "",
  region_id: "",
  city_id: "",
  postal_code_id: "",
  address: "",
  contact_phone: "",
  email: "",
  note: "",
});

const filteredSubscribers = computed(() => {
  if (!typeFilter.value) return subscribers.value;
  return subscribers.value.filter(
    (subscriber) => subscriber.subscriber_type === typeFilter.value
  );
});

function displayName(subscriber) {
  if (subscriber.subscriber_type === "legal_entity") {
    return subscriber.company_name || "-";
  }
  return `${subscriber.first_name || ""} ${subscriber.last_name || ""}`.trim() || "-";
}

function buildPayload() {
  return {
    subscriber_type: form.subscriber_type,
    first_name: form.subscriber_type === "physical_person" ? form.first_name || null : null,
    last_name: form.subscriber_type === "physical_person" ? form.last_name || null : null,
    company_name: form.subscriber_type === "legal_entity" ? form.company_name || null : null,
    jmbg: form.jmbg || null,
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

async function onEntityChange() {
  form.region_id = "";
  form.city_id = "";
  form.postal_code_id = "";
  regions.value = [];
  cities.value = [];
  postalCodes.value = [];
  if (!form.entity_id) return;
  const response = await api.get(`/regions?entity_id=${form.entity_id}`);
  regions.value = response.data;
}

async function onRegionChange() {
  form.city_id = "";
  form.postal_code_id = "";
  cities.value = [];
  postalCodes.value = [];
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

async function loadSubscribers() {
  loading.value = true;
  try {
    const query = search.value ? `?search=${encodeURIComponent(search.value)}` : "";
    const response = await api.get(`/subscribers${query}`);
    subscribers.value = response.data;
  } finally {
    loading.value = false;
  }
}

async function saveSubscriber() {
  error.value = "";
  success.value = "";
  try {
    const payload = buildPayload();
    if (editingId.value) {
      await api.put(`/subscribers/${editingId.value}`, payload);
      success.value = "Pretplatnik je uspješno izmijenjen.";
    } else {
      await api.post("/subscribers", payload);
      success.value = "Pretplatnik je uspješno spremljen.";
    }
    resetForm();
    await loadSubscribers();
  } catch (err) {
    error.value = err.response?.data?.detail || "Greška pri spremanju pretplatnika.";
  }
}

async function startEdit(subscriber) {
  editingId.value = subscriber.id;

  form.subscriber_type = subscriber.subscriber_type;
  form.first_name = subscriber.first_name || "";
  form.last_name = subscriber.last_name || "";
  form.company_name = subscriber.company_name || "";
  form.jmbg = subscriber.jmbg || "";
  form.address = subscriber.address || "";
  form.contact_phone = subscriber.contact_phone || "";
  form.email = subscriber.email || "";
  form.note = subscriber.note || "";

  form.entity_id = "";
  form.region_id = "";
  form.city_id = subscriber.city_id || "";
  form.postal_code_id = subscriber.postal_code_id || "";

  regions.value = [];
  cities.value = [];
  postalCodes.value = [];

  if (subscriber.city_id) {
    const citiesResponse = await api.get("/cities");
    const city = citiesResponse.data.find((item) => Number(item.id) === Number(subscriber.city_id));

    if (city) {
      const regionsResponse = await api.get("/regions");
      const region = regionsResponse.data.find((item) => Number(item.id) === Number(city.region_id));

      if (region) {
        form.entity_id = region.entity_id;
        await onEntityChange();
        form.region_id = region.id;
        await onRegionChange();
        form.city_id = city.id;
        await onCityChange();
        form.postal_code_id = subscriber.postal_code_id || "";
      }
    }
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  editingId.value = null;
  form.subscriber_type = "physical_person";
  form.first_name = "";
  form.last_name = "";
  form.company_name = "";
  form.jmbg = "";
  form.entity_id = "";
  form.region_id = "";
  form.city_id = "";
  form.postal_code_id = "";
  form.address = "";
  form.contact_phone = "";
  form.email = "";
  form.note = "";
  regions.value = [];
  cities.value = [];
  postalCodes.value = [];
}

async function deleteSubscriber(subscriber) {
  const confirmed = confirm(`Obrisati pretplatnika "${displayName(subscriber)}"?`);
  if (!confirmed) return;
  error.value = "";
  success.value = "";
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
  await loadSubscribers();
});
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 30px; color: #111827; }
.page-header p { margin-top: 6px; color: #6b7280; }

.panel {
  background: rgba(255,255,255,0.9);
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 18px 40px rgba(15,23,42,0.06);
}
.panel h2 { margin-top: 0; margin-bottom: 18px; color: #111827; }

.form-grid,
.filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.filters { grid-template-columns: 2fr 1fr; }

.field { display: flex; flex-direction: column; }
.field.full, .actions.full { grid-column: span 2; }

label {
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 700;
}
.optional { font-weight: 400; color: #9ca3af; font-size: 13px; }

.section-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #9ca3af;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 8px;
  margin-top: 4px;
  display: flex;
  align-items: center;
}

.type-toggle {
  display: flex;
  gap: 10px;
}
.toggle-btn {
  flex: 1;
  background: #f9fafb;
  color: #374151;
  border: 1.5px solid #e5e7eb;
  padding: 11px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.15s;
}
.toggle-btn.active {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border-color: transparent;
}

input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 12px 13px;
  font-size: 14px;
  background: white;
  color: #111827;
}
textarea { min-height: 80px; }
select:disabled { background: #f9fafb; color: #9ca3af; cursor: not-allowed; }
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220,38,38,0.12);
}

.actions.full { display: flex; gap: 10px; }

button {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  border: none;
  padding: 13px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
}
button.secondary { background: #6b7280; }
.small-btn { padding: 8px 11px; border-radius: 9px; font-size: 12px; }
.small-btn.danger { background: #dc2626; }

.error { color: #dc2626; margin-top: 12px; }
.success { color: #16a34a; margin-top: 12px; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.panel-header h2 { margin: 0; }
.muted { color: #6b7280; font-size: 13px; }
.loading, .empty { text-align: center; color: #6b7280; padding: 28px; }

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
  vertical-align: top;
}
.table-actions { display: flex; gap: 8px; }

.badge {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}
.badge-red { background: rgba(220,38,38,0.12); color: #dc2626; }
.badge-blue { background: rgba(37,99,235,0.12); color: #2563eb; }

@media (max-width: 760px) {
  .form-grid, .filters { grid-template-columns: 1fr; }
  .field.full, .actions.full { grid-column: span 1; }
  .type-toggle { flex-direction: column; }
}
</style>