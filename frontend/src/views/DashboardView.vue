<template>
  <div class="dash">

    <!-- Page header -->
    <div class="page-header">
      <div class="page-header-left">
  <div>
    <h1><i class="ti ti-layout-dashboard"></i> Pregled sustava</h1>
    <p>Centralni pregled lokacija, uređaja, raspona i fiksnih brojeva.</p>
  </div>
</div>
      <button class="refresh-btn" @click="load" :disabled="loading">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" :class="{ spinning: loading }">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        Osvježi
      </button>
    </div>

    <!-- Skeleton -->
    <template v-if="loading && !stats">
      <div class="skeleton-row">
        <div class="skeleton" v-for="i in 4" :key="i"></div>
      </div>
      <div class="skeleton-row">
        <div class="skeleton short" v-for="i in 4" :key="i"></div>
      </div>
    </template>

    <template v-else-if="stats">

      <!-- Top stat cards -->
      <div class="row r4">
        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-red">
              <i class="ti ti-map-pin"></i>
            </div>
            <span class="card-label">Lokacije</span>
          </div>
          <div class="big">{{ stats.locations }}</div>
          <div class="sub">HT lokacije u sustavu</div>
        </div>

        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-blue">
              <i class="ti ti-cpu"></i>
            </div>
            <span class="card-label">Uređaji</span>
          </div>
          <div class="big">{{ stats.devices }}</div>
          <div class="sub">MSAN / GPON OLT oprema</div>
        </div>

        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-gray">
              <i class="ti ti-list-numbers"></i>
            </div>
            <span class="card-label">Rasponi</span>
          </div>
          <div class="big">{{ stats.ranges.total }}</div>
          <div class="badge-row">
            <span class="badge badge-green">
              <span class="dot dot-green"></span>{{ stats.ranges.generated }} gen.
            </span>
            <span class="badge badge-gray">
              <span class="dot dot-gray"></span>{{ stats.ranges.not_generated }} ne
            </span>
          </div>
        </div>

        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-teal">
              <i class="ti ti-phone"></i>
            </div>
            <span class="card-label">Brojevi ukupno</span>
          </div>
          <div class="big">{{ stats.phone_numbers.total.toLocaleString("hr") }}</div>
          <div class="sub">Generirani fiksni brojevi</div>
        </div>
      </div>

      <!-- Status breakdown -->
      <div class="row r4">
        <div class="card">
          <div class="card-label">Slobodni</div>
          <div class="big" style="color:#3B6D11">{{ stats.phone_numbers.free.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: freePercent + '%', background: '#639922' }"></div></div>
          <div class="pct-label">{{ freePercent }}% ukupnih</div>
        </div>

        <div class="card">
          <div class="card-label">Zauzeti</div>
          <div class="big" style="color:#A32D2D">{{ stats.phone_numbers.busy.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: stats.phone_numbers.usage_percent + '%', background: '#E24B4A' }"></div></div>
          <div class="pct-label">{{ stats.phone_numbers.usage_percent }}% iskorištenost</div>
        </div>

        <div class="card">
          <div class="card-label">Karantena</div>
          <div class="big" style="color:#854F0B">{{ stats.phone_numbers.quarantine.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: quarantinePercent + '%', background: '#EF9F27' }"></div></div>
          <div class="pct-label">{{ quarantinePercent }}% ukupnih</div>
        </div>

        <!-- Donut -->
        <div class="card donut-card">
          <div class="donut-wrap">
            <svg width="72" height="72" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="28" fill="none" stroke="#F3F4F6" stroke-width="9"/>
              <circle cx="36" cy="36" r="28" fill="none" stroke="#E24B4A" stroke-width="9"
                stroke-linecap="round" transform="rotate(-90 36 36)"
                :stroke-dasharray="`${donutBusy} 175.9`"/>
              <circle cx="36" cy="36" r="28" fill="none" stroke="#EF9F27" stroke-width="9"
                stroke-linecap="round" transform="rotate(-90 36 36)"
                :stroke-dasharray="`${donutQuarantine} 175.9`"
                :stroke-dashoffset="`${-donutBusy}`"/>
              <text x="36" y="33" text-anchor="middle" font-size="11" font-weight="600" fill="#111827">{{ stats.phone_numbers.usage_percent }}%</text>
              <text x="36" y="46" text-anchor="middle" font-size="9" fill="#9CA3AF">zauzeto</text>
            </svg>
            <div class="legend">
              <div class="legend-item"><span class="dot dot-red"></span>Zauzeti</div>
              <div class="legend-item"><span class="dot dot-amber"></span>Karantena</div>
              <div class="legend-item"><span class="dot dot-green"></span>Slobodni</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tables -->
      <div class="row r2">
        <div class="card">
          <div class="section-head">
            <div class="section-head-title">
              <i class="ti ti-map-pin section-icon"></i>
              <h2>Zadnje lokacije</h2>
            </div>
            <RouterLink to="/locations" class="nav-link">Sve lokacije →</RouterLink>
          </div>
          <table>
            <thead>
              <tr><th>Naziv</th><th>Grad</th><th>PTT</th></tr>
            </thead>
            <tbody>
              <tr v-for="loc in latestLocations" :key="loc.id">
                <td class="td-strong">{{ loc.name }}</td>
                <td class="td-muted">{{ loc.city_name }}</td>
                <td class="td-mono">{{ loc.postal_code }}</td>
              </tr>
              <tr v-if="latestLocations.length === 0">
                <td colspan="3" class="empty">Nema lokacija.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="section-head">
            <div class="section-head-title">
              <i class="ti ti-cpu section-icon"></i>
              <h2>Zadnji uređaji</h2>
            </div>
            <RouterLink to="/devices" class="nav-link">Svi uređaji →</RouterLink>
          </div>
          <table>
            <thead>
              <tr><th>Uređaj</th><th>Tip</th><th>Lokacija</th></tr>
            </thead>
            <tbody>
              <tr v-for="device in latestDevices" :key="device.id">
                <td class="td-strong">{{ device.name }}</td>
                <td>
                  <span class="badge" :class="device.device_type === 'MSAN' ? 'badge-red' : 'badge-blue'">
                    {{ device.device_type === 'GPON_OLT' ? 'GPON OLT' : 'MSAN' }}
                  </span>
                </td>
                <td class="td-muted">{{ device.location_name }}</td>
              </tr>
              <tr v-if="latestDevices.length === 0">
                <td colspan="3" class="empty">Nema uređaja.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Bottom mini stats -->
      <div class="row r4">
        <div class="card mini-card">
          <div class="icon-box ib-amber">
            <i class="ti ti-table"></i>
          </div>
          <div>
            <div class="mini-label">RAK blokovi</div>
            <div class="mini-num">{{ stats.rak_blocks }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-green">
            <i class="ti ti-circle-check"></i>
          </div>
          <div>
            <div class="mini-label">Generirani rasponi</div>
            <div class="mini-num">{{ stats.ranges.generated }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-gray">
            <i class="ti ti-circle-x"></i>
          </div>
          <div>
            <div class="mini-label">Negenerirani rasponi</div>
            <div class="mini-num">{{ stats.ranges.not_generated }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-purple">
            <i class="ti ti-users"></i>
          </div>
          <div>
            <div class="mini-label">Pretplatnici</div>
            <div class="mini-num">{{ stats.subscribers }}</div>
          </div>
        </div>
      </div>

    </template>

    <div v-else-if="loadError" class="error-state">
      <i class="ti ti-alert-circle" style="font-size:32px; color:#9CA3AF;"></i>
      <p>Greška pri učitavanju podataka.</p>
      <button @click="load">Pokušaj ponovo</button>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import api from "../api/client";

const loading = ref(false);
const loadError = ref(false);
const stats = ref(null);
const latestLocations = ref([]);
const latestDevices = ref([]);

const freePercent = computed(() => {
  const t = stats.value?.phone_numbers?.total;
  const f = stats.value?.phone_numbers?.free;
  return t ? Math.round((f / t) * 100) : 0;
});

const quarantinePercent = computed(() => {
  const t = stats.value?.phone_numbers?.total;
  const q = stats.value?.phone_numbers?.quarantine;
  return t ? Math.round((q / t) * 100) : 0;
});

const donutBusy = computed(() => {
  const pct = stats.value?.phone_numbers?.usage_percent || 0;
  return ((pct / 100) * 175.9).toFixed(1);
});

const donutQuarantine = computed(() => {
  return ((quarantinePercent.value / 100) * 175.9).toFixed(1);
});

async function load() {
  loading.value = true;
  loadError.value = false;
  try {
    const [statsRes, locRes, devRes] = await Promise.all([
      api.get("/dashboard/stats"),
      api.get("/locations"),
      api.get("/devices"),
    ]);

    const d = statsRes.data;
    stats.value = {
      locations:   d.locations,
      devices:     d.devices,
      subscribers: d.subscribers,
      rak_blocks:  d.rak_blocks,
      ranges: {
        total:         d.ranges,
        generated:     d.ranges_generated    ?? "–",
        not_generated: d.ranges_not_generated ?? "–",
      },
      phone_numbers: {
        total:         d.phone_numbers_total,
        free:          d.free,
        busy:          d.busy,
        quarantine:    d.quarantine,
        usage_percent: d.phone_numbers_total
          ? Math.round((d.busy / d.phone_numbers_total) * 100)
          : 0,
      },
    };

    latestLocations.value = locRes.data.slice(0, 5);
    latestDevices.value   = devRes.data.slice(0, 5);
  } catch {
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

.dash {
  padding-bottom: 32px;
  font-family: 'Geist', sans-serif;
}

/* ── Page header ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-icon {
  width: 54px;
  height: 54px;
  background: #EFF6FF;
  border: 1px solid #DBEAFE;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1B4FD8;
  font-size: 28px;
  flex-shrink: 0;
}

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

.page-header h1 i {
  font-size: 26px;
  color: #1B4FD8;
}

.page-header p {
  margin: 4px 0 0;
  color: #6B7280;
  font-size: 13px;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #FFFFFF;
  color: #374151;
  border: 1px solid #E5E7EB;
  padding: 9px 15px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
  transition: background 0.12s;
}
.refresh-btn:hover { background: #F9FAFB; }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin 0.8s linear infinite; }

/* ── Grid ── */
.row { display: grid; gap: 12px; margin-bottom: 12px; }
.r4  { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.r2  { grid-template-columns: repeat(2, minmax(0, 1fr)); }

/* ── Card ── */
.card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  padding: 18px 20px;
}

/* ── Icon boxes ── */
.icon-row {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 10px;
}

.icon-box {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  flex-shrink: 0;
}
.ib-red    { background: #FEF2F2; color: #DC2626; }
.ib-blue   { background: #EFF6FF; color: #1B4FD8; }
.ib-teal   { background: #F0FDF4; color: #059669; }
.ib-gray   { background: #F9FAFB; color: #6B7280; }
.ib-amber  { background: #FFFBEB; color: #D97706; }
.ib-green  { background: #F0FDF4; color: #16A34A; }
.ib-purple { background: #F5F3FF; color: #7C3AED; }

/* ── Card text ── */
.card-label { font-size: 12px; color: #6B7280; font-weight: 600; }
.big        { font-size: 30px; font-weight: 700; color: #111827; line-height: 1.15; margin-bottom: 4px; }
.sub        { font-size: 12px; color: #9CA3AF; margin-top: 4px; }

/* ── Badges ── */
.badge-row { display: flex; gap: 5px; margin-top: 8px; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
}
.badge-green  { background: #F0FDF4; color: #16A34A; }
.badge-red    { background: #FEF2F2; color: #DC2626; }
.badge-amber  { background: #FFFBEB; color: #D97706; }
.badge-gray   { background: #F9FAFB; color: #6B7280; border: 1px solid #E5E7EB; }
.badge-blue   { background: #EFF6FF; color: #1B4FD8; }

/* ── Dots ── */
.dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-green  { background: #16A34A; }
.dot-red    { background: #DC2626; }
.dot-amber  { background: #D97706; }
.dot-gray   { background: #9CA3AF; }

/* ── Progress track ── */
.track { background: #F3F4F6; border-radius: 999px; height: 5px; margin: 10px 0 5px; overflow: hidden; }
.bar   { height: 100%; border-radius: 999px; transition: width 0.5s ease; }
.pct-label { font-size: 11px; color: #9CA3AF; }

/* ── Donut ── */
.donut-card  { display: flex; align-items: center; justify-content: center; }
.donut-wrap  { display: flex; align-items: center; gap: 16px; }
.legend      { display: flex; flex-direction: column; gap: 7px; }
.legend-item { display: flex; align-items: center; gap: 7px; font-size: 12px; color: #6B7280; font-weight: 500; }

/* ── Tables ── */
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-head-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 17px;
  color: #1B4FD8;
}

.section-head h2 {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.nav-link {
  font-size: 12px;
  color: #1B4FD8;
  font-weight: 600;
  text-decoration: none;
}
.nav-link:hover { text-decoration: underline; }

table { width: 100%; border-collapse: collapse; }
th {
  font-size: 10px;
  font-weight: 600;
  color: #9CA3AF;
  text-align: left;
  padding: 0 0 8px;
  border-bottom: 1px solid #F3F4F6;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
td {
  padding: 10px 0;
  border-bottom: 1px solid #F9FAFB;
  font-size: 13px;
  color: #374151;
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
.td-strong { font-weight: 600; color: #111827; }
.td-muted  { color: #9CA3AF; }
.td-mono   { font-family: monospace; font-size: 12px; color: #9CA3AF; }

/* ── Mini cards ── */
.mini-card  { display: flex; align-items: center; gap: 13px; padding: 16px 18px; }
.mini-label { font-size: 12px; color: #6B7280; font-weight: 500; margin-bottom: 2px; }
.mini-num   { font-size: 22px; font-weight: 700; color: #111827; }

/* ── Skeleton ── */
.skeleton-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }
.skeleton {
  height: 120px;
  border-radius: 14px;
  background: linear-gradient(90deg, #F3F4F6 25%, #E9EBEE 50%, #F3F4F6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
.skeleton.short { height: 80px; }
@keyframes shimmer { to { background-position: -200% 0; } }

/* ── Error ── */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 10px;
  color: #9CA3AF;
  text-align: center;
}
.error-state p { margin: 0; font-size: 14px; }
.error-state button {
  margin-top: 8px;
  background: #1B4FD8;
  color: #fff;
  border: none;
  padding: 9px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
}
.error-state button:hover { background: #1640B0; }

.empty { text-align: center; color: #9CA3AF; padding: 20px; font-size: 13px; }

/* ── Responsive ── */
@media (max-width: 1100px) {
  .r4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .r4, .r2 { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; gap: 12px; align-items: flex-start; }
}
</style>