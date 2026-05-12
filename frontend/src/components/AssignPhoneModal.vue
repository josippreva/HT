<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">

      <!-- HEADER -->
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="modal-phone-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.35 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 5.45 5.45l.96-.96a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21 16.92z"/></svg>
            {{ formatPhoneNumber(phone?.number_value) }}
          </div>
          <h3>Dodjela broja pretplatniku</h3>
          <p class="modal-subtitle">
            {{ phone?.entity_name }} / {{ phone?.region_name }} / {{ phone?.city_name }} / {{ phone?.location_name }}
          </p>
        </div>
        <button class="close-btn" @click="close">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <!-- BODY -->
      <div class="modal-body">

        <!-- LIJEVA KOLONA — lista pretplatnika -->
        <div class="modal-col modal-col-list">
          <div class="search-bar-wrapper">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              ref="subscriberSearchInput"
              v-model="subscriberFilters.search"
              type="text"
              class="search-bar"
              placeholder="Ime, OIB, JMBG, interni ID..."
            />
            <button v-if="subscriberFilters.search" class="search-clear" @click="subscriberFilters.search = ''">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <div class="type-tabs">
            <button class="type-tab" :class="{ active: subscriberFilters.type === '' }" @click="subscriberFilters.type = ''">Svi</button>
            <button class="type-tab" :class="{ active: subscriberFilters.type === 'physical_person' }" @click="subscriberFilters.type = 'physical_person'">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              Fizička osoba
            </button>
            <button class="type-tab" :class="{ active: subscriberFilters.type === 'legal_entity' }" @click="subscriberFilters.type = 'legal_entity'">
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
                  <strong>{{ subscriberDisplayName(subscriber) }}</strong>
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
                <p>Nema rezultata</p>
                <button class="switch-to-new-btn" @click="assignMode = 'new'">
                  + Kreiraj novog pretplatnika
                </button>
              </div>
            </template>
          </div>
        </div>

        <!-- DESNA KOLONA — detalji / forma -->
        <div class="modal-col modal-col-detail">

          <!-- SWITCH: postojeći / novi -->
          <div class="assign-mode-switch">
            <button
              type="button"
              class="type-tab"
              :class="{ active: assignMode === 'existing' }"
              @click="assignMode = 'existing'"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              Postojeći pretplatnik
            </button>
            <button
              type="button"
              class="type-tab"
              :class="{ active: assignMode === 'new' }"
              @click="assignMode = 'new'"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Novi pretplatnik
            </button>
          </div>

          <!-- POSTOJEĆI PRETPLATNIK -->
          <template v-if="assignMode === 'existing'">
            <div v-if="selectedSubscriber" class="selected-subscriber-card">
              <div class="selected-header">
                <span class="selected-label">Odabrani pretplatnik</span>
                <button class="deselect-btn" @click="deselectSubscriber">Poništi</button>
              </div>
              <div class="selected-name">{{ subscriberDisplayName(selectedSubscriber) }}</div>
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
          </template>

          <!-- NOVI PRETPLATNIK -->
          <template v-else>
            <div class="new-subscriber-form">
              <div class="field">
                <label>Tip pretplatnika</label>
                <select v-model="newSubscriberForm.subscriber_type">
                  <option value="physical_person">Fizička osoba</option>
                  <option value="legal_entity">Pravna osoba</option>
                </select>
              </div>

              <template v-if="newSubscriberForm.subscriber_type === 'physical_person'">
                <div class="field-row">
                  <div class="field">
                    <label>Ime</label>
                    <input v-model="newSubscriberForm.first_name" type="text" placeholder="Ime" />
                  </div>
                  <div class="field">
                    <label>Prezime</label>
                    <input v-model="newSubscriberForm.last_name" type="text" placeholder="Prezime" />
                  </div>
                </div>
                <div class="field">
                  <label>JMBG</label>
                  <input v-model="newSubscriberForm.jmbg" type="text" maxlength="13" placeholder="13 znamenki" />
                </div>
              </template>

              <template v-else>
                <div class="field">
                  <label>Naziv firme</label>
                  <input v-model="newSubscriberForm.company_name" type="text" placeholder="Naziv pravne osobe" />
                </div>
                <div class="field">
                  <label>ID broj firme</label>
                  <input v-model="newSubscriberForm.company_id_number" type="text" maxlength="12" placeholder="12 znamenki" />
                </div>
              </template>

              <div class="field">
                <label>Grad/općina</label>
                <input :value="phone?.city_name || ''" type="text" disabled class="input-disabled" />
              </div>

                <div class="field">
                <label>Poštanski broj</label>
                <select v-model="newSubscriberForm.postal_code_id">
                    <option :value="null" disabled>Odaberi poštanski broj</option>
                    <option v-for="pc in postalCodes" :key="pc.id" :value="pc.id">
                    {{ pc.postal_code }} – {{ pc.postal_name }}
                    </option>
                </select>
                </div>


              <div class="field">
                <label>Adresa</label>
                <input v-model="newSubscriberForm.address" type="text" placeholder="Ulica i broj" />
              </div>

              <div class="field-row">
                <div class="field">
                  <label>Kontakt telefon</label>
                  <input v-model="newSubscriberForm.contact_phone" type="text" placeholder="+387 xx xxx xxx" />
                </div>
                <div class="field">
                  <label>Email</label>
                  <input v-model="newSubscriberForm.email" type="email" placeholder="email@primjer.ba" />
                </div>
              </div>
            </div>
          </template>

          <!-- NAPOMENA -->
          <div class="note-field">
            <label>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Napomena <span class="optional">(opcionalno)</span>
            </label>
            <textarea v-model="assignForm.note" placeholder="Npr. ugovor br. 1234, zamjena uređaja..."></textarea>
          </div>
        </div>
      </div>

      <!-- FOOTER -->
      <div class="modal-footer">
        <p v-if="error" class="error">{{ error }}</p>
        <div class="footer-actions">
          <button class="btn-secondary" @click="close">Odustani</button>
          <button
            class="btn-primary"
            :disabled="assignMode === 'existing' && !assignForm.subscriber_id"
            @click="submit"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Dodijeli broj
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from "vue";
import api from "../api/client";

const props = defineProps({
  phone: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "assigned"]);

// =====================
// STATE
// =====================

const subscribers = ref([]);
const subscribersLoading = ref(false);
const selectedSubscriber = ref(null);
const subscriberSearchInput = ref(null);
const error = ref("");
const assignMode = ref("existing");
const postalCodes = ref([]);

const subscriberFilters = reactive({
  search: "",
  type: "",
  city_id: "",
});

const assignForm = reactive({
  subscriber_id: "",
  note: "",
});

const newSubscriberForm = reactive({
  subscriber_type: "physical_person",
  first_name: "",
  last_name: "",
  company_name: "",
  jmbg: "",
  company_id_number: "",
  address: "",
  city_id: "",
  postal_code_id: null,
  contact_phone: "",
  email: "",
  note: "",
});

// =====================
// COMPUTED
// =====================

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

// =====================
// WATCHERS
// =====================

let subSearchTimer = null;
watch(
  () => subscriberFilters.search,
  () => {
    clearTimeout(subSearchTimer);
    subSearchTimer = setTimeout(() => loadSubscribers(), 350);
  }
);

// =====================
// HELPERI
// =====================

function formatPhoneNumber(value) {
  if (!value) return "";
  const digits = String(value).replace(/\D/g, "");
  if (digits.length === 8) return `+387 ${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  if (digits.length === 9) return `+387 ${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  return value;
}

function subscriberDisplayName(subscriber) {
  if (!subscriber) return "—";
  if (subscriber.subscriber_type === "legal_entity") return subscriber.company_name || "—";
  return `${subscriber.first_name || ""} ${subscriber.last_name || ""}`.trim() || "—";
}

function selectSubscriber(subscriber) {
  assignMode.value = "existing";
  assignForm.subscriber_id = subscriber.id;
  selectedSubscriber.value = subscriber;
}

function deselectSubscriber() {
  assignForm.subscriber_id = "";
  selectedSubscriber.value = null;
}

function close() {
  emit("close");
}

// =====================
// API POZIVI
// =====================

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

async function assignExistingSubscriber() {
  if (!assignForm.subscriber_id) {
    error.value = "Odaberi pretplatnika s popisa.";
    return;
  }
  await api.post(`/phone-numbers/${props.phone.id}/assign`, {
    subscriber_id: Number(assignForm.subscriber_id),
    note: assignForm.note || null,
  });
}

async function assignNewSubscriber() {
console.log("postal_code_id:", newSubscriberForm.postal_code_id)
  await api.post(`/phone-numbers/${props.phone.id}/assign-with-new-subscriber`, {
    subscriber: {
      subscriber_type: newSubscriberForm.subscriber_type,

      first_name:
        newSubscriberForm.subscriber_type === "physical_person"
          ? newSubscriberForm.first_name || null
          : null,

      last_name:
        newSubscriberForm.subscriber_type === "physical_person"
          ? newSubscriberForm.last_name || null
          : null,

      company_name:
        newSubscriberForm.subscriber_type === "legal_entity"
          ? newSubscriberForm.company_name || null
          : null,

      jmbg:
        newSubscriberForm.subscriber_type === "physical_person"
          ? newSubscriberForm.jmbg || null
          : null,

      company_id_number:
        newSubscriberForm.subscriber_type === "legal_entity"
          ? newSubscriberForm.company_id_number || null
          : null,

      address: newSubscriberForm.address || null,
      city_id: props.phone.city_id ? Number(props.phone.city_id) : null,
      postal_code_id: newSubscriberForm.postal_code_id ? Number(newSubscriberForm.postal_code_id) : null,
      contact_phone: newSubscriberForm.contact_phone || null,
      email: newSubscriberForm.email || null,
      note: null,
    },
    note: assignForm.note || null,
  });
}

async function submit() {
  error.value = "";
  try {
    if (assignMode.value === "existing") {
      await assignExistingSubscriber();
    } else {
      await assignNewSubscriber();
    }
    emit("assigned");
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      "Greška pri dodjeli broja.";
  }
}


async function loadPostalCodes(cityId) {
  if (!cityId) return;
  const response = await api.get(`/postal-codes?city_id=${cityId}`);
  postalCodes.value = response.data;
}

// =====================
// INIT
// =====================

onMounted(async () => {
  subscriberFilters.city_id = props.phone?.city_id || "";
  await loadSubscribers();
  await loadPostalCodes(props.phone?.city_id);  // ← dodaj ovo
  await nextTick();
  subscriberSearchInput.value?.focus();
});
</script>

<style scoped>

* {
  font-family: 'Geist', sans-serif;
}
button,
input,
select,
textarea {
  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s,
    box-shadow 0.15s,
    transform 0.12s;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
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

  background: rgba(255,255,255,0.96);

  border: 1px solid #e5e7eb;
  border-radius: 22px;

  box-shadow:
    0 18px 40px rgba(15,23,42,0.08),
    0 4px 12px rgba(15,23,42,0.04);

  display: flex;
  flex-direction: column;
  overflow: hidden;

  backdrop-filter: blur(12px);
}


.modal-phone-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;

  background: #ECFDF3;
  border: 1px solid #BBF7D0;

  color: #15803D;

  font-family: monospace;
  font-size: 14px;
  font-weight: 700;

  padding: 6px 11px;

  border-radius: 9px;

  width: fit-content;
  margin-bottom: 4px;
}
/* HEADER */
.modal-header {
  padding: 18px 22px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
}
.modal-title-group { display: flex; flex-direction: column; gap: 4px; }

.modal-title-group h3 { margin: 0; font-size: 16px; color: #111827; }
.modal-subtitle { margin: 0; color: #6b7280; font-size: 12px; }
.close-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 7px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.close-btn:hover { background: #e5e7eb; }

/* BODY */
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
  padding: 18px 20px;
  overflow-y: auto;
}
.modal-col-list { border-right: 1px solid #e5e7eb; overflow-y: hidden; }

/* SEARCH BAR */
.search-bar-wrapper { position: relative; margin-bottom: 10px; }
.search-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
}
.search-bar {
  width: 100%;
  padding: 9px 34px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 13px;
  background: #f9fafb;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-bar:focus,
input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #1B4FD8;
  box-shadow: 0 0 0 3px rgba(27, 79, 216, 0.08);
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
  cursor: pointer;
  border: none;
}
.search-clear:hover { background: #d1d5db; }

/* TABS */
.type-tabs,
.assign-mode-switch {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}
.type-tab {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s;
}
.type-tab:hover {
  background: #EDF4FF;
  border-color: #BFDBFE;
  color: #1B4FD8;
}
.type-tab.active {
  background: #EFF6FF;
  color: #1B4FD8;
  border-color: #93C5FD;
}

/* SUBSCRIBER LIST */
.subscriber-list-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;

  border: 1px solid #E5E7EB;
  border-radius: 14px;

  background: #FFFFFF;
}
.subscriber-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.12s;
}
.subscriber-row:last-child { border-bottom: none; }
.subscriber-row:hover {
  background: #F9FAFB;
}.subscriber-row.selected {
  background: #F8FAFF;
  border-left: 3px solid #1B4FD8;
}
.subscriber-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar-blue {
  background: #E5E7EB;
  color: #374151;
}
.avatar-red {
  background: #EDF4FF;
  color: #1B4FD8;
}

.subscriber-info { flex: 1; min-width: 0; }
.subscriber-info strong {
  font-size: 13px;
  color: #111827;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.subscriber-meta {
  color: #9ca3af;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}
.meta-sep { color: #d1d5db; }
.subscriber-check {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
  flex-shrink: 0;
}

.sub-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 36px 20px;
  gap: 10px;
  color: #9ca3af;
  font-size: 13px;
}
.spinner {
  width: 22px;
  height: 22px;
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
  padding: 36px 20px;
  gap: 8px;
  color: #9ca3af;
  text-align: center;
}
.sub-empty p { margin: 0; font-size: 13px; line-height: 1.5; }
.switch-to-new-btn {
  margin-top: 6px;
  background: none;
  border: 1px dashed rgba(220, 38, 38, 0.4);
  color: #dc2626;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.13s;
}
.switch-to-new-btn:hover { background: rgba(220, 38, 38, 0.06); }

/* DESNA KOLONA */
.selected-subscriber-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 16px;

  margin-bottom: 14px;

  box-shadow: 0 2px 6px rgba(15,23,42,0.03);
}
.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.selected-label {
  font-size: 10px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.deselect-btn {
  background: none;
  color: #dc2626;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid rgba(220, 38, 38, 0.3);
  cursor: pointer;
}
.deselect-btn:hover { background: rgba(220, 38, 38, 0.06); }
.selected-name { font-size: 15px; font-weight: 700; color: #111827; margin-bottom: 10px; }
.selected-meta-grid { display: flex; flex-direction: column; gap: 7px; }
.selected-meta-item { display: flex; justify-content: space-between; align-items: center; }
.meta-key { font-size: 11px; color: #9ca3af; font-weight: 600; }
.meta-val { font-size: 12px; color: #374151; font-weight: 600; }

.no-selection-placeholder {
  flex: 1;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  color: #9CA3AF;

  text-align: center;
  gap: 10px;

  border: 1px dashed #D1D5DB;
  border-radius: 16px;

  background: #FAFBFC;

  padding: 28px;
  margin-bottom: 14px;
  min-height: 120px;
}
.no-selection-placeholder p { margin: 0; font-size: 13px; color: #9ca3af; line-height: 1.6; }

/* NOVA FORMA */
.new-subscriber-form { display: flex; flex-direction: column; gap: 0; margin-bottom: 10px; }

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

label {
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 5px;
}
input, select, textarea {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 12px;
  background: white;
  color: #111827;
  transition: border-color 0.15s, box-shadow 0.15s;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}
.input-disabled {
  background: #f9fafb !important;
  color: #9ca3af;
  cursor: not-allowed;
}

/* NAPOMENA */
.note-field { margin-top: auto; padding-top: 6px; }
.note-field textarea {
  width: 100%;
  min-height: 68px;
  resize: vertical;
  box-sizing: border-box;
}
.optional { font-weight: 400; color: #9ca3af; text-transform: none; letter-spacing: 0; }

/* FOOTER */
.modal-footer {
  padding: 16px 22px;

  border-top: 1px solid #F1F5F9;

  background: #FCFCFD;

  display: flex;
  justify-content: space-between;
  align-items: center;

  flex-shrink: 0;
  gap: 10px;
}
.footer-actions { display: flex; gap: 8px; margin-left: auto; }
.error { color: #dc2626; font-size: 13px; margin: 0; }

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


.badge {
  display: inline-flex;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.badge-red  { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.badge-blue { background: rgba(37, 99, 235, 0.1); color: #2563eb; }


.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;

  background: #FFFFFF;
  color: #374151;

  border: 1px solid #E5E7EB;
  border-radius: 9px;

  padding: 8px 14px;

  cursor: pointer;

  font-weight: 600;
  font-size: 12.5px;
  line-height: 1;

  font-family: 'Geist', sans-serif;

  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s,
    transform 0.12s;
}

.btn-secondary:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}

.btn-secondary:active {
  transform: scale(0.98);
}

@media (max-width: 800px) {
  .modal-body { grid-template-columns: 1fr; overflow-y: auto; }
  .modal-col-list { border-right: none; border-bottom: 1px solid #e5e7eb; max-height: 320px; }
}
</style>