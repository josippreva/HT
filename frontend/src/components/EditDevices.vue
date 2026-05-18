<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <h2><i class="ti ti-pencil"></i> Uredi uređaj</h2>

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
          <label>Lokacija</label>
          <select v-model="editForm.location_id" :disabled="!editForm.city_id" required>
            <option value="">Odaberi lokaciju</option>
            <option v-for="location in editLocations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label>Tip uređaja</label>
          <select v-model="editForm.device_type" required>
            <option value="MSAN">MSAN</option>
            <option value="GPON_OLT">GPON OLT</option>
          </select>
        </div>

        <div class="field">
          <label>Naziv uređaja</label>
          <input v-model="editForm.name" type="text" required />
        </div>

        <div class="field">
          <label>Serijski broj</label>
          <input v-model="editForm.serial_number" type="text" placeholder="Opcionalno" />
        </div>

        <div class="field checkbox-field">
          <label class="checkbox-label">
            <input v-model="editForm.active" type="checkbox" />
            Aktivan uređaj
          </label>
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
  device: Object,
  entities: Array,
  allLocations: Array,
});

const emit = defineEmits(["close", "saved"]);

const editRegions   = ref([]);
const editCities    = ref([]);
const editLocations = ref([]);
const editSubmitting = ref(false);
const editError      = ref("");

const editForm = reactive({
  entity_id: "", region_id: "", city_id: "", location_id: "",
  name: "", device_type: "MSAN", serial_number: "", active: true,
});

watch(() => props.device, async (device) => {
  if (!device) return;
  editError.value = "";

  // Load regions for entity
  const regionsResp = await api.get(`/regions?entity_id=${device.entity_id}`);
  editRegions.value = regionsResp.data;

  // Load cities for region
  const citiesResp = await api.get(`/cities?region_id=${device.region_id}`);
  editCities.value = citiesResp.data;

  // Filter locations by city from allLocations prop
  editLocations.value = props.allLocations.filter(
    (l) => Number(l.city_id) === Number(device.city_id)
  );

  Object.assign(editForm, {
    entity_id: device.entity_id,
    region_id: device.region_id,
    city_id: device.city_id,
    location_id: device.location_id,
    name: device.name,
    device_type: device.device_type,
    serial_number: device.serial_number || "",
    active: device.active,
  });
});

async function onEditEntityChange() {
  editForm.region_id = editForm.city_id = editForm.location_id = "";
  editRegions.value = editCities.value = editLocations.value = [];
  if (!editForm.entity_id) return;
  const { data } = await api.get(`/regions?entity_id=${editForm.entity_id}`);
  editRegions.value = data;
}

async function onEditRegionChange() {
  editForm.city_id = editForm.location_id = "";
  editCities.value = editLocations.value = [];
  if (!editForm.region_id) return;
  const { data } = await api.get(`/cities?region_id=${editForm.region_id}`);
  editCities.value = data;
}

function onEditCityChange() {
  editForm.location_id = "";
  editLocations.value = [];
  if (!editForm.city_id) return;
  editLocations.value = props.allLocations.filter(
    (l) => Number(l.city_id) === Number(editForm.city_id)
  );
}

async function saveEdit() {
  editError.value = "";
  editSubmitting.value = true;
  try {
    await api.put(`/devices/${props.device.id}`, {
      location_id: Number(editForm.location_id),
      name: editForm.name,
      device_type: editForm.device_type,
      serial_number: editForm.serial_number || null,
      active: editForm.active,
    });
    emit("saved");
    emit("close");
  } catch {
    editError.value = "Greška pri ažuriranju uređaja.";
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
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.field { display: flex; flex-direction: column; }
.field.full { grid-column: span 2; }
.actions.full {
  grid-column: span 2;
  display: flex;
  gap: 8px;
  padding-top: 6px;
}

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
  border-color: #1B4FD8;
  box-shadow: 0 0 0 3px rgba(27, 79, 216, 0.08);
  background: white;
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

.error { color: #DC2626; margin-top: 10px; font-size: 13px; }

@media (max-width: 600px) {
  .modal { padding: 20px 16px; }
  .form-grid { grid-template-columns: 1fr; }
  .field.full, .actions.full { grid-column: span 1; }
}
</style>