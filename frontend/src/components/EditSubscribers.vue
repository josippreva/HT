<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <h2><i class="ti ti-pencil"></i> Uredi pretplatnika</h2>

      <form class="form-grid" @submit.prevent="saveEdit">

        <div class="field full">
          <label>Tip pretplatnika</label>
          <div class="type-toggle">
            <button type="button" :class="['toggle-btn', editForm.subscriber_type === 'physical_person' ? 'active' : '']" @click="editForm.subscriber_type = 'physical_person'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Fizička osoba
            </button>
            <button type="button" :class="['toggle-btn', editForm.subscriber_type === 'legal_entity' ? 'active' : '']" @click="editForm.subscriber_type = 'legal_entity'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              Pravna osoba
            </button>
          </div>
        </div>

        <template v-if="editForm.subscriber_type === 'physical_person'">
          <div class="field">
            <label>Ime</label>
            <input v-model="editForm.first_name" type="text" placeholder="Ime" />
          </div>
          <div class="field">
            <label>Prezime</label>
            <input v-model="editForm.last_name" type="text" placeholder="Prezime" />
          </div>
        </template>

        <template v-else>
          <div class="field half">
            <label>Naziv firme</label>
            <input v-model="editForm.company_name" type="text" placeholder="Naziv pravne osobe" />
          </div>
        </template>

        <div v-if="editForm.subscriber_type === 'physical_person'" class="field">
          <label>JMBG</label>
          <input v-model="editForm.jmbg" type="text" maxlength="13" placeholder="13 znamenki" />
        </div>
        <div v-else class="field">
          <label>ID broj firme</label>
          <input v-model="editForm.company_id_number" type="text" placeholder="ID / porezni broj firme" />
        </div>

        <div class="field">
          <label>Kontakt telefon</label>
          <input v-model="editForm.contact_phone" type="text" placeholder="+387 xx xxx xxx" />
        </div>

        <div class="field half">
          <label>Email</label>
          <input v-model="editForm.email" type="email" placeholder="email@primjer.ba" />
        </div>

        <div class="section-label">Adresa</div>

        <div class="field">
          <label>Entitet</label>
          <select v-model="editForm.entity_id" @change="onEditEntityChange">
            <option value="">Odaberi entitet</option>
            <option v-for="entity in entities" :key="entity.id" :value="entity.id">{{ entity.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Županija</label>
          <select v-model="editForm.region_id" @change="onEditRegionChange" :disabled="!editForm.entity_id">
            <option value="">Odaberi županiju</option>
            <option v-for="region in editRegions" :key="region.id" :value="region.id">{{ region.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Grad / općina</label>
          <select v-model="editForm.city_id" @change="onEditCityChange" :disabled="!editForm.region_id">
            <option value="">Odaberi grad/općinu</option>
            <option v-for="city in editCities" :key="city.id" :value="city.id">{{ city.name }}</option>
          </select>
        </div>

        <div class="field">
          <label>Poštanski broj</label>
          <select v-model="editForm.postal_code_id" :disabled="!editForm.city_id">
            <option value="">Odaberi poštanski broj</option>
            <option v-for="postal in editPostalCodes" :key="postal.id" :value="postal.id">
              {{ postal.postal_code }} — {{ postal.postal_name }}
            </option>
          </select>
        </div>

        <div class="field half">
          <label>Ulica i broj</label>
          <input v-model="editForm.address" type="text" placeholder="npr. Ulica bb" />
        </div>

        <div class="field full">
          <label>Napomena <span class="optional">(opcionalno)</span></label>
          <textarea v-model="editForm.note" placeholder="Dodatne napomene..."></textarea>
        </div>

        <div class="actions full">
          <button type="submit" class="btn-primary" :disabled="editSubmitting">
            <i class="ti ti-device-floppy"></i>
            {{ editSubmitting ? "Spremanje..." : "Spremi izmjene" }}
          </button>
          <button type="button" class="btn-secondary" @click="$emit('close')">Odustani</button>
        </div>
      </form>

      <p v-if="editError" class="error">{{ editError }}</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import api from "../api/client";

const props = defineProps({
  open: Boolean,
  subscriber: Object,
  entities: Array,
});

const emit = defineEmits(["close", "saved"]);

const editRegions     = ref([]);
const editCities      = ref([]);
const editPostalCodes = ref([]);
const editSubmitting  = ref(false);
const editError       = ref("");

const editForm = reactive({
  subscriber_type: "physical_person",
  first_name: "", last_name: "", company_name: "",
  jmbg: "", company_id_number: "",
  entity_id: "", region_id: "", city_id: "", postal_code_id: "",
  address: "", contact_phone: "", email: "", note: "",
});

watch(() => props.subscriber, async (subscriber) => {
  if (!subscriber) return;
  editError.value = "";

  // Reset cascades
  editRegions.value = editCities.value = editPostalCodes.value = [];

  Object.assign(editForm, {
    subscriber_type: subscriber.subscriber_type,
    first_name: subscriber.first_name || "",
    last_name: subscriber.last_name || "",
    company_name: subscriber.company_name || "",
    jmbg: subscriber.jmbg || "",
    company_id_number: subscriber.company_id_number || "",
    address: subscriber.address || "",
    contact_phone: subscriber.contact_phone || "",
    email: subscriber.email || "",
    note: subscriber.note || "",
    entity_id: "",
    region_id: "",
    city_id: subscriber.city_id || "",
    postal_code_id: subscriber.postal_code_id || "",
  });

  if (!subscriber.city_id) return;

  // Resolve region and entity from city
  const cityResp   = await api.get(`/cities/${subscriber.city_id}`);
  const regionId   = cityResp.data.region_id;
  const regionResp = await api.get(`/regions/${regionId}`);
  const entityId   = regionResp.data.entity_id;

  const [regionsResp, citiesResp, postalsResp] = await Promise.all([
    api.get(`/regions?entity_id=${entityId}`),
    api.get(`/cities?region_id=${regionId}`),
    api.get(`/postal-codes?city_id=${subscriber.city_id}`),
  ]);

  editRegions.value     = regionsResp.data;
  editCities.value      = citiesResp.data;
  editPostalCodes.value = postalsResp.data;

  editForm.entity_id = entityId;
  editForm.region_id = regionId;
});

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
    const payload = {
      subscriber_type: editForm.subscriber_type,
      first_name: editForm.subscriber_type === "physical_person" ? editForm.first_name || null : null,
      last_name: editForm.subscriber_type === "physical_person" ? editForm.last_name || null : null,
      company_name: editForm.subscriber_type === "legal_entity" ? editForm.company_name || null : null,
      jmbg: editForm.subscriber_type === "physical_person" ? editForm.jmbg || null : null,
      company_id_number: editForm.subscriber_type === "legal_entity" ? editForm.company_id_number || null : null,
      city_id: editForm.city_id ? Number(editForm.city_id) : null,
      postal_code_id: editForm.postal_code_id ? Number(editForm.postal_code_id) : null,
      address: editForm.address || null,
      contact_phone: editForm.contact_phone || null,
      email: editForm.email || null,
      note: editForm.note || null,
    };
    await api.put(`/subscribers/${props.subscriber.id}`, payload);
    emit("saved");
    emit("close");
  } catch (err) {
    editError.value = err.response?.data?.detail || "Greška pri ažuriranju pretplatnika.";
  } finally {
    editSubmitting.value = false;
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { font-family: 'Geist', sans-serif; }

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
  padding: 28px 32px;
  width: 860px;
  max-width: 96vw;
  max-height: 92vh;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  border: 1px solid #E5E7EB;
}

.modal h2 {
  margin: 0 0 20px;
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}
.modal h2 i { color: #1B4FD8; font-size: 18px; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.field { display: flex; flex-direction: column; }
.field.full { grid-column: span 3; }
.field.half { grid-column: span 2; }
.actions.full {
  grid-column: span 3;
  display: flex;
  gap: 8px;
  padding-top: 6px;
}

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

.type-toggle {
  display: flex;
  gap: 8px;
}

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
.toggle-btn:hover {
  background: #EDF4FF;
  color: #1B4FD8;
  border-color: #7FB3FF;
}
.toggle-btn.active {
  background: #EFF6FF;
  color: #1B4FD8;
  border-color: #93C5FD;
}
.toggle-btn:active { transform: scale(0.98); }

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
  font-family: 'Geist', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
textarea { min-height: 68px; resize: vertical; }
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

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  background: #FFFFFF;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  font-family: 'Geist', sans-serif;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.btn-secondary:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}

.error { color: #dc2626; margin-top: 10px; font-size: 13px; }

@media (max-width: 760px) {
  .modal { padding: 20px 16px; }
  .form-grid { grid-template-columns: 1fr 1fr; }
  .field.full, .field.half, .actions.full, .section-label { grid-column: span 2; }
  .type-toggle { flex-direction: column; }
}
@media (max-width: 500px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .field.half, .actions.full, .section-label { grid-column: span 1; }
}
</style>