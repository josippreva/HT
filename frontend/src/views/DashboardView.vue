<template>
  <div class="dash">

    <div class="page-header">
      <div>
        <h1>Pregled sustava</h1>
        <p>Centralni pregled lokacija, uređaja, raspona i fiksnih brojeva.</p>
      </div>
      <button class="refresh-btn" @click="load" :disabled="loading">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" :class="{ spinning: loading }">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        Osvježi
      </button>
    </div>

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
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <span class="label">Lokacije</span>
          </div>
          <div class="big">{{ stats.locations }}</div>
          <div class="sub">HT lokacije u sustavu</div>
        </div>

        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-blue">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            </div>
            <span class="label">Uređaji</span>
          </div>
          <div class="big">{{ stats.devices }}</div>
          <div class="sub">MSAN / GPON OLT oprema</div>
        </div>

        <div class="card">
          <div class="icon-row">
            <div class="icon-box ib-gray">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <span class="label">Rasponi</span>
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
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.35 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 5.45 5.45l.96-.96a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21 16.92z"/></svg>
            </div>
            <span class="label">Brojevi ukupno</span>
          </div>
          <div class="big">{{ stats.phone_numbers.total.toLocaleString("hr") }}</div>
          <div class="sub">Generirani fiksni brojevi</div>
        </div>
      </div>

      <!-- Status breakdown -->
      <div class="row r4">
        <div class="card">
          <div class="label">Slobodni</div>
          <div class="big" style="color:#3B6D11">{{ stats.phone_numbers.free.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: freePercent + '%', background: '#639922' }"></div></div>
          <div class="pct-label">{{ freePercent }}% ukupnih</div>
        </div>

        <div class="card">
          <div class="label">Zauzeti</div>
          <div class="big" style="color:#A32D2D">{{ stats.phone_numbers.busy.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: stats.phone_numbers.usage_percent + '%', background: '#E24B4A' }"></div></div>
          <div class="pct-label">{{ stats.phone_numbers.usage_percent }}% iskorištenost</div>
        </div>

        <div class="card">
          <div class="label">Karantena</div>
          <div class="big" style="color:#854F0B">{{ stats.phone_numbers.quarantine.toLocaleString("hr") }}</div>
          <div class="track"><div class="bar" :style="{ width: quarantinePercent + '%', background: '#EF9F27' }"></div></div>
          <div class="pct-label">{{ quarantinePercent }}% ukupnih</div>
        </div>

        <!-- Donut -->
        <div class="card donut-card">
          <div class="donut-wrap">
            <svg width="72" height="72" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="28" fill="none" stroke="#f1efe8" stroke-width="9"/>
              <circle cx="36" cy="36" r="28" fill="none" stroke="#E24B4A" stroke-width="9"
                stroke-linecap="round" transform="rotate(-90 36 36)"
                :stroke-dasharray="`${donutBusy} 175.9`"/>
              <circle cx="36" cy="36" r="28" fill="none" stroke="#EF9F27" stroke-width="9"
                stroke-linecap="round" transform="rotate(-90 36 36)"
                :stroke-dasharray="`${donutQuarantine} 175.9`"
                :stroke-dashoffset="`${-donutBusy}`"/>
              <text x="36" y="33" text-anchor="middle" font-size="11" font-weight="500" fill="#111827">{{ stats.phone_numbers.usage_percent }}%</text>
              <text x="36" y="46" text-anchor="middle" font-size="9" fill="#6b7280">zauzeto</text>
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
            <h2>Zadnje lokacije</h2>
            <RouterLink to="/locations" class="nav-link">Sve lokacije →</RouterLink>
          </div>
          <table>
            <thead>
              <tr><th>Naziv</th><th>Grad</th><th>Ptt</th></tr>
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
            <h2>Zadnji uređaji</h2>
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
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
          </div>
          <div>
            <div class="mini-label">RAK blokovi</div>
            <div class="mini-num">{{ stats.rak_blocks }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-green">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div>
            <div class="mini-label">Generirani rasponi</div>
            <div class="mini-num">{{ stats.ranges.generated }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-gray">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div>
            <div class="mini-label">Negenerirani rasponi</div>
            <div class="mini-num">{{ stats.ranges.not_generated }}</div>
          </div>
        </div>

        <div class="card mini-card">
          <div class="icon-box ib-purple">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div>
            <div class="mini-label">Pretplatnici</div>
            <div class="mini-num">{{ stats.subscribers }}</div>
          </div>
        </div>
      </div>

    </template>

    <div v-else-if="loadError" class="error-state">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
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

// r=28 → circumference = 2π×28 ≈ 175.9
const donutBusy = computed(() => {
  const pct = stats.value?.phone_numbers?.usage_percent || 0;
  return ((pct / 100) * 175.9).toFixed(1);
});

const donutQuarantine = computed(() => {
  return (quarantinePercent.value / 100 * 175.9).toFixed(1);
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
.dash { padding-bottom: 32px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header h1 { margin: 0; font-size: 28px; color: #111827; font-weight: 700; }
.page-header p { margin-top: 5px; color: #6b7280; font-size: 14px; }

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.refresh-btn:hover { background: #f9fafb; }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin 0.8s linear infinite; }

.row { display: grid; gap: 12px; margin-bottom: 12px; }
.r4 { grid-template-columns: repeat(4, minmax(0,1fr)); }
.r2 { grid-template-columns: repeat(2, minmax(0,1fr)); }

.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(15,23,42,0.04);
}

.icon-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.icon-box {
  width: 30px; height: 30px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ib-red    { background: #FAECE7; color: #993C1D; }
.ib-blue   { background: #E6F1FB; color: #185FA5; }
.ib-teal   { background: #E1F5EE; color: #0F6E56; }
.ib-gray   { background: #F1EFE8; color: #5F5E5A; }
.ib-amber  { background: #FAEEDA; color: #854F0B; }
.ib-green  { background: #EAF3DE; color: #3B6D11; }
.ib-purple { background: #EEEDFE; color: #534AB7; }

.label { font-size: 12px; color: #6b7280; font-weight: 600; }
.big   { font-size: 30px; font-weight: 700; color: #111827; line-height: 1.1; margin-bottom: 4px; }
.sub   { font-size: 12px; color: #9ca3af; margin-top: 4px; }

.badge-row { display: flex; gap: 5px; margin-top: 8px; }

.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 600;
  padding: 3px 8px; border-radius: 999px;
}
.badge-green  { background: #EAF3DE; color: #3B6D11; }
.badge-red    { background: #FCEBEB; color: #A32D2D; }
.badge-amber  { background: #FAEEDA; color: #854F0B; }
.badge-gray   { background: #F1EFE8; color: #5F5E5A; }
.badge-blue   { background: #E6F1FB; color: #185FA5; }

.dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-green  { background: #639922; }
.dot-red    { background: #E24B4A; }
.dot-amber  { background: #EF9F27; }
.dot-gray   { background: #888780; }

.track { background: #f3f4f6; border-radius: 999px; height: 5px; margin: 10px 0 5px; overflow: hidden; }
.bar   { height: 100%; border-radius: 999px; transition: width 0.5s ease; }
.pct-label { font-size: 11px; color: #9ca3af; }

.donut-card { display: flex; align-items: center; justify-content: center; }
.donut-wrap { display: flex; align-items: center; gap: 14px; }
.legend { display: flex; flex-direction: column; gap: 6px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6b7280; font-weight: 500; }

.section-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.section-head h2 { font-size: 15px; font-weight: 700; color: #111827; margin: 0; }
.nav-link { font-size: 12px; color: #dc2626; font-weight: 600; text-decoration: none; }
.nav-link:hover { text-decoration: underline; }

table { width: 100%; border-collapse: collapse; }
th {
  font-size: 11px; font-weight: 600; color: #9ca3af;
  text-align: left; padding: 0 0 7px;
  border-bottom: 1px solid #f3f4f6;
  text-transform: uppercase; letter-spacing: 0.04em;
}
td {
  padding: 9px 0;
  border-bottom: 1px solid #f9fafb;
  font-size: 13px;
  color: #374151;
  vertical-align: middle;
}
tr:last-child td { border-bottom: none; }
.td-strong { font-weight: 600; color: #111827; }
.td-muted  { color: #9ca3af; }
.td-mono   { font-family: monospace; font-size: 12px; color: #9ca3af; }

.mini-card { display: flex; align-items: center; gap: 12px; padding: 16px 18px; }
.mini-label { font-size: 12px; color: #9ca3af; font-weight: 500; margin-bottom: 2px; }
.mini-num   { font-size: 22px; font-weight: 700; color: #111827; }

.skeleton-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }
.skeleton {
  height: 120px; border-radius: 18px;
  background: linear-gradient(90deg, #f3f4f6 25%, #eaecee 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
.skeleton.short { height: 80px; }
@keyframes shimmer { to { background-position: -200% 0; } }

.error-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 20px; gap: 10px; color: #9ca3af; text-align: center;
}
.error-state p { margin: 0; font-size: 14px; }
.error-state button {
  margin-top: 8px;
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white; border: none;
  padding: 9px 18px; border-radius: 10px;
  font-weight: 600; cursor: pointer;
}

.empty { text-align: center; color: #9ca3af; padding: 20px; font-size: 13px; }

@media (max-width: 1100px) {
  .r4 { grid-template-columns: repeat(2, minmax(0,1fr)); }
}
@media (max-width: 640px) {
  .r4, .r2 { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; gap: 10px; }
}
</style>