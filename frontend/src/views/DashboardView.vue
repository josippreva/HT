<template>
  <div class="dash">
    <div class="page-header">
      <div class="header-left">
        <h1><i class="ti ti-layout-dashboard"></i> Pregled sustava</h1>
        <p>Analitički i operativni pregled numeracijskih resursa HT Mostar.</p>
      </div>
      <div class="live-clock">
        <div class="clock-date">{{ clockDate }}</div>
        <div class="clock-time">{{ clockTime }}</div>
      </div>
    </div>

    <template v-if="loading && !data">
      <div class="skeleton-grid g6">
        <div class="skeleton sh-metric" v-for="i in 6" :key="i"></div>
      </div>
      <div class="skeleton-grid g3 mt">
        <div class="skeleton sh-tall" v-for="i in 3" :key="i"></div>
      </div>
    </template>

    <template v-else-if="data">
      <div class="metrics-row mb">
        <div class="metric-card mc-blue" @click="go('/number-ranges')">
          <div class="mc-icon"><i class="ti ti-database"></i></div>
          <div class="mc-body">
            <div class="mc-label">RAK Kapacitet</div>
            <div class="mc-val">{{ fmt(s.rak_total_capacity) }}</div>
            <div class="mc-sub">ukupno u blokovima</div>
          </div>
        </div>

        <div class="metric-card mc-cyan" @click="go('/number-ranges')">
          <div class="mc-icon"><i class="ti ti-list-numbers"></i></div>
          <div class="mc-body">
            <div class="mc-label">Rasponi</div>
            <div class="mc-val">{{ fmt(s.ranges_total) }}</div>
            <div class="mc-sub-dual">
              <span class="sub-green"><i class="ti ti-check"></i> {{ fmt(s.ranges_generated) }} gen.</span>
              <span class="sub-muted"><i class="ti ti-clock"></i> {{ fmt(s.ranges_not_generated) }} negen.</span>
            </div>
          </div>
        </div>

        <div class="metric-card mc-indigo" @click="go('/phone-numbers')">
          <div class="mc-icon"><i class="ti ti-phone"></i></div>
          <div class="mc-body">
            <div class="mc-label">Brojevi</div>
            <div class="mc-val">{{ fmt(s.generated_total) }}</div>
            <div class="mc-sub">{{ s.gen_pct }}% od RAK kapaciteta</div>
          </div>
        </div>

        <div class="metric-card mc-teal" @click="go('/subscribers')">
          <div class="mc-icon"><i class="ti ti-users"></i></div>
          <div class="mc-body">
            <div class="mc-label">Pretplatnici</div>
            <div class="mc-val">{{ fmt(s.subscribers_total) }}</div>
            <div class="mc-sub-dual">
              <span class="sub-muted"><i class="ti ti-user"></i> {{ fmt(s.subscribers_physical) }} fizičkih</span>
              <span class="sub-muted"><i class="ti ti-building"></i> {{ fmt(s.subscribers_legal) }} pravnih</span>
            </div>
          </div>
        </div>

        <div class="metric-card mc-slate" @click="go('/cities')">
          <div class="mc-icon"><i class="ti ti-building-community"></i></div>
          <div class="mc-body">
            <div class="mc-label">Gradovi</div>
            <div class="mc-val">{{ fmt(s.cities_count) }}</div>
            <div class="mc-sub-dual">
              <span class="sub-muted"><i class="ti ti-mail"></i> {{ fmt(s.postal_codes_count) }} post. br.</span>
            </div>
          </div>
        </div>

        <div class="metric-card mc-rose" @click="go('/locations')">
          <div class="mc-icon"><i class="ti ti-map-pin"></i></div>
          <div class="mc-body">
            <div class="mc-label">Lokacije</div>
            <div class="mc-val">{{ fmt(s.locations) }}</div>
          </div>
        </div>

        <div class="metric-card mc-violet" @click="go('/devices')">
          <div class="mc-icon"><i class="ti ti-cpu"></i></div>
          <div class="mc-body">
            <div class="mc-label">Uređaji</div>
            <div class="mc-val">{{ fmt(s.devices) }}</div>
            <div class="mc-sub-dual">
              <span class="sub-green"><i class="ti ti-check"></i> {{ fmt(s.devices_active) }} aktiv.</span>
              <span class="sub-red"><i class="ti ti-x"></i> {{ fmt(s.devices_inactive) }} neaktiv.</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="data.warnings?.length" class="warnings-row mb">
        <div class="warnings-title"><i class="ti ti-alert-triangle"></i> Upozorenja</div>
        <div v-for="(w, i) in data.warnings.slice(0, 5)" :key="i" class="warn-pill" :class="`warn-${w.severity}`">
          <i :class="warningIcon(w.severity)"></i>
          <span>{{ w.message }}</span>
        </div>
      </div>

      <div class="dashboard-grid mb">
        <div class="panel span-8">
          <div class="panel-head">
            <span class="panel-title"><i class="ti ti-chart-donut-3"></i> Distribucija brojeva po statusu i kategoriji</span>
          </div>

          <div class="dist-body">
            <div class="dist-left">
              <div class="donut-wrap">
                <svg width="170" height="170" viewBox="0 0 170 170" aria-hidden="true">
                  <circle cx="85" cy="85" r="64" fill="none" stroke="#F3F4F6" stroke-width="20"/>
                  <circle cx="85" cy="85" r="64" fill="none" stroke="#16A34A" stroke-width="20" transform="rotate(-90 85 85)" :stroke-dasharray="`${donut.free} 402.12`"/>
                  <circle cx="85" cy="85" r="64" fill="none" stroke="#DC2626" stroke-width="20" transform="rotate(-90 85 85)" :stroke-dasharray="`${donut.busy} 402.12`" :stroke-dashoffset="`${-donut.free}`"/>
                  <circle cx="85" cy="85" r="64" fill="none" stroke="#F59E0B" stroke-width="20" transform="rotate(-90 85 85)" :stroke-dasharray="`${donut.quarantine} 402.12`" :stroke-dashoffset="`${-(donut.free + donut.busy )}`"/>
                  <text x="85" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827">{{ s.busy_pct }}%</text>
                  <text x="85" y="98" text-anchor="middle" font-size="12" fill="#6B7280">zauzeto</text>
                </svg>
              </div>

              <div class="status-legend">
                <div class="legend-item" @click="go('/phone-numbers?status=slobodan')">
                  <div class="li-dot green"></div>
                  <div class="li-body">
                    <span>Slobodni</span>
                    <strong>{{ fmt(s.free) }}</strong>
                  </div>
                  <div class="li-pct" style="color:#16A34A">{{ s.free_pct }}%</div>
                </div>
                <div class="legend-item" @click="go('/phone-numbers?status=zauzet')">
                  <div class="li-dot red"></div>
                  <div class="li-body">
                    <span>Zauzeti</span>
                    <strong>{{ fmt(s.busy) }}</strong>
                  </div>
                  <div class="li-pct" style="color:#DC2626">{{ s.busy_pct }}%</div>
                </div>
                
                <div class="legend-item" @click="go('/phone-numbers?status=karantena')">
                  <div class="li-dot amber"></div>
                  <div class="li-body">
                    <span>Karantena</span>
                    <strong>{{ fmt(s.quarantine) }}</strong>
                  </div>
                  <div class="li-pct" style="color:#F59E0B">{{ s.quarantine_pct }}%</div>
                </div>
              </div>
            </div>

            <div class="dist-right">
              <div class="cat-title"><i class="ti ti-tag"></i> Po kategorijama</div>
              <div class="category-list">
                <div v-for="cat in data.categories" :key="cat.category" class="category-row">
                  <div class="category-head">
                    <strong>{{ catLabel(cat.category) }}</strong>
                    <div class="cat-stats">
                      <span class="cs-total">{{ fmt(cat.total) }}</span>
                      <span class="cs-free clr-green">{{ fmt(cat.free) }} slob.</span>
                      <span class="cs-busy clr-red">{{ fmt(cat.busy) }} zauz.</span>
                    </div>
                  </div>
                  <div class="stacked">
                    <div class="seg green" :style="{ width: pctOf(cat.free, cat.total) + '%' }"></div>
                    <div class="seg red" :style="{ width: pctOf(cat.busy, cat.total) + '%' }"></div>
                    <div class="seg amber" :style="{ width: pctOf(cat.quarantine, cat.total) + '%' }"></div>
                  </div>
                  <div class="cat-meta">
                    <span>{{ cat.usage_pct }}% iskorištenost</span>
                    <span> {{ fmt(cat.quarantine) }} kar.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel span-4">
          <div class="panel-head">
            <span class="panel-title"><i class="ti ti-phone-call"></i> Prvi slobodni broj</span>
          </div>

          <div class="first-free-box">
            <div class="filters-grid">
              <select v-model="firstFreeFilters.entity_id" @change="onFirstEntityChange">
                <option :value="null">Svi entiteti</option>
                <option v-for="e in firstEntities" :key="e.id" :value="e.id">{{ e.name }}</option>
              </select>
              <select v-model="firstFreeFilters.region_id" @change="onFirstRegionChange">
                <option :value="null">Sve regije</option>
                <option v-for="r in firstRegions" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
              <select v-model="firstFreeFilters.city_id" @change="onFirstCityChange">
                <option :value="null">Svi gradovi</option>
                <option v-for="c in firstCities" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <select v-model="firstFreeFilters.location_id" @change="onFirstLocationChange">
                <option :value="null">Sve lokacije</option>
                <option v-for="l in firstLocations" :key="l.id" :value="l.id">{{ l.name }}</option>
              </select>
              <select v-model="firstFreeFilters.device_id" @change="loadFirstFree">
                <option :value="null">Svi uređaji</option>
                <option v-for="d in firstDevices" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
              <select v-model="firstFreeFilters.number_category" @change="loadFirstFree">
                <option :value="null">Sve kategorije</option>
                <option value="premium">Premium</option>
                <option value="gold">Gold</option>
                <option value="silver">Silver</option>
                <option value="bronze">Bronze</option>
                <option value="standard">Standard</option>
              </select>
            </div>

            <template v-if="firstFreeNumber">
              <div class="ff-number-display">
                <div class="ff-label">Sljedeći slobodan broj</div>
                <div class="ff-number">{{ prettyNumber(firstFreeNumber.number_value) }}</div>
                <div class="ff-meta">
                  <span><i class="ti ti-building-community"></i> {{ firstFreeNumber.city_name }}</span>
                  <span><i class="ti ti-map-pin"></i> {{ firstFreeNumber.location_name }}</span>
                  <span v-if="firstFreeNumber.number_category" class="cat-badge">{{ catLabel(firstFreeNumber.number_category) }}</span>
                </div>
              </div>
              <div class="ff-actions">
                <button class="btn btn-primary" @click="openAssign(firstFreeNumber)">
                  <i class="ti ti-phone-plus"></i> Dodijeli broj
                </button>
                <button class="btn btn-ghost" @click="go('/phone-numbers')">
                  <i class="ti ti-list"></i> Svi brojevi
                </button>
              </div>
            </template>

            <div v-else class="empty-soft">
              <i class="ti ti-phone-off"></i>
              <span>Nema slobodnog broja za odabrane filtere.</span>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-grid mb">
        <div class="panel span-6">
          <div class="panel-head">
            <span class="panel-title"><i class="ti ti-activity"></i> Nedavne aktivnosti</span>
          </div>

          <div class="activity-list">
            <div v-for="(a, i) in data.recent_activities?.slice(0, 8)" :key="i" class="activity-row">
              <div class="activity-icon" :class="a.tone"><i :class="a.icon"></i></div>
              <div class="activity-body">
                <strong>{{ a.title }}</strong>
                <span class="activity-meta">
                  <span v-if="a.user_name" class="act-user">
                    <i class="ti ti-user"></i> {{ a.user_name }}
                  </span>
                  <span v-if="a.entity_type" class="act-entity">
                    <i class="ti ti-tag"></i> {{ a.entity_type }}
                    <template v-if="a.entity_id">#{{ a.entity_id }}</template>
                  </span>
                </span>
              </div>
              <time>{{ timeShort(a.time) }}</time>
            </div>
            <div v-if="!data.recent_activities?.length" class="empty-soft">
              <i class="ti ti-history"></i><span>Nema zabilježenih aktivnosti.</span>
            </div>
          </div>
        </div>

        <div class="panel span-6">
          <div class="panel-head">
            <span class="panel-title"><i class="ti ti-trending-up"></i> Trend dodjele — zadnjih 6 mj.</span>
          </div>

          <div class="trend-kpis">
            <div class="tkpi">
              <div class="tkpi-icon blue"><i class="ti ti-phone-plus"></i></div>
              <div>
                <span>Dodijeljeno</span>
                <strong class="clr-blue">+{{ fmt(trendTotals.assigned) }}</strong>
              </div>
            </div>
            <div class="tkpi">
              <div class="tkpi-icon amber"><i class="ti ti-clock"></i></div>
              <div>
                <span>U karantenu</span>
                <strong class="clr-amber">{{ fmt(trendTotals.released) }}</strong>
              </div>
            </div>
            <div class="tkpi">
              <div class="tkpi-icon" :class="trendTotals.net >= 0 ? 'green' : 'red'"><i class="ti ti-arrows-diff"></i></div>
              <div>
                <span>Neto</span>
                <strong :class="trendTotals.net >= 0 ? 'clr-green' : 'clr-red'">{{ trendTotals.net >= 0 ? '+' : '' }}{{ fmt(trendTotals.net) }}</strong>
              </div>
            </div>
          </div>

          <div class="bar-chart">
            <div v-for="m in data.monthly_trend" :key="m.month_iso" class="bc-col">
              <div class="bc-top">
                <div class="bc-val clr-blue">{{ fmt(m.assigned) }}</div>
                <div class="bc-val clr-amber">{{ fmt(m.released) }}</div>
              </div>
              <div class="bc-bars">
                <div class="bc-bar blue" :style="{ height: trendBarH(m.assigned) + 'px' }" :title="`Dodijeljeni: ${m.assigned}`"></div>
                <div class="bc-bar amber" :style="{ height: trendBarH(m.released) + 'px' }" :title="`Karantena: ${m.released}`"></div>
              </div>
              <div class="bc-label">{{ shortMonth(m.month) }}</div>
              <div class="bc-net" :class="m.net >= 0 ? 'clr-green' : 'clr-red'">{{ m.net >= 0 ? '+' : '' }}{{ m.net }}</div>
            </div>
          </div>

          <div class="trend-legend">
            <span><i class="dot-inline blue"></i> Dodijeljeno</span>
            <span><i class="dot-inline amber"></i> U karantenu</span>
            <span class="trend-note">Neto = Dodijeljeno − Karantena po mjesecu</span>
          </div>
        </div>
      </div>

      <div ref="rangesPanel" class="panel mb">
        <div class="panel-head">
          <span class="panel-title"><i class="ti ti-list-numbers"></i> Rasponi numeracije</span>
          <div class="range-head-right">
            <div class="range-pills">
              <span><i class="ti ti-check clr-green"></i> Generirani: <strong>{{ s.ranges_generated }}</strong></span>
              <span><i class="ti ti-clock"></i> Negenerirani: <strong>{{ s.ranges_not_generated }}</strong></span>
            </div>
            <button class="btn btn-warning-soft" :class="{ active: sortByCritical }" @click="toggleCritical">
              <i class="ti ti-alert-triangle"></i>
              {{ sortByCritical ? 'Poredano po kritičnosti' : 'Prikaži najkritičnije' }}
            </button>
          </div>
        </div>

        <div class="filters">
          <div class="field search-field">
            <label>Pretraga</label>
            <div class="search-wrap">
              <i class="ti ti-search"></i>
              <input v-model="rangeSearch" type="text" placeholder="Naziv, početak ili kraj raspona..." @input="debouncedLoadRanges" />
            </div>
          </div>
          <div class="field">
            <label>Grad</label>
            <select v-model="rangeFilters.city_id" @change="loadRanges(1)">
              <option :value="null">Svi gradovi</option>
              <option v-for="c in rangeFilterCities" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="field">
            <label>RAK blok</label>
            <select v-model="rangeFilters.rak_block_id" @change="loadRanges(1)">
              <option :value="null">Svi RAK blokovi</option>
              <option v-for="r in rangeFilterRaks" :key="r.id" :value="r.id">{{ r.label }}</option>
            </select>
          </div>
          <div class="field">
            <label>Generiranost</label>
            <select v-model="rangeFilters.generated" @change="loadRanges(1)">
              <option :value="null">Svi rasponi</option>
              <option :value="true">Samo generirani</option>
              <option :value="false">Samo negenerirani</option>
            </select>
          </div>
          <button v-if="hasActiveFilters" class="btn btn-danger-soft" @click="clearRangeFilters">
            <i class="ti ti-x"></i> Očisti
          </button>
        </div>

        <div v-if="!rangesLoading && rangesData" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Naziv / Raspon</th>
                <th>Grad / Lokacija</th>
                <th>RAK blok</th>
                <th>Veličina</th>
                <th>Status</th>
                <th>Slobodni</th>
                <th>Zauzeti</th>
                <th>Karantena</th>
                <th>Iskorištenost</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rangesData.ranges" :key="r.id">
                <td>
                  <strong>{{ r.name }}</strong>
                  <span class="sub-mono">{{ r.range_start }} – {{ r.range_end }}</span>
                </td>
                <td>
                  <strong>{{ r.city_name }}</strong>
                  <span class="sub-text">{{ r.location_name }}</span>
                </td>
                <td>
                  <strong class="mono-range">{{ r.rak_block_start }} – {{ r.rak_block_end }}</strong>
                  <span class="sub-text">{{ r.operator_name }} · {{ r.area_code }}</span>
                </td>
                <td><strong>{{ fmt(r.range_size) }}</strong></td>
                <td>
                  <span v-if="r.generated" class="badge badge-green"><i class="ti ti-check"></i> Generiran</span>
                  <span v-else class="badge badge-muted"><i class="ti ti-clock"></i> Nije generiran</span>
                </td>
                <template v-if="r.generated">
                  <td class="clr-green fw6">{{ fmt(r.free) }}</td>
                  <td class="clr-red fw6">{{ fmt(r.busy) }}</td>
                  <td class="clr-amber fw6">{{ fmt(r.quarantine) }}</td>
                  <td>
                    <div class="usage-cell">
                      <div class="bar-track"><div class="bar-fill" :style="{ width: r.usage_pct + '%', background: usageColor(r.usage_pct) }"></div></div>
                      <span :style="{ color: usageColor(r.usage_pct) }">{{ r.usage_pct }}%</span>
                    </div>
                  </td>
                </template>
                <template v-else>
                  <td colspan="4" class="not-gen-msg">Raspon nije generiran</td>
                </template>
              </tr>
              <tr v-if="!rangesData.ranges.length">
                <td colspan="9" class="empty">Nema pronađenih raspona za zadane filtere.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="range-skel">
          <div class="skeleton" v-for="i in 8" :key="i"></div>
        </div>

        <div v-if="rangesData" class="load-more-row">
          <span class="pg-info">
            Prikazano {{ rangesData.ranges.length }} od {{ fmt(rangesData.total) }} raspona
          </span>
          <button
            v-if="rangesData.ranges.length < rangesData.total"
            class="btn btn-ghost load-more-btn"
            :disabled="rangesLoading"
            @click="loadMore"
          >
            <i class="ti ti-loader" v-if="rangesLoading"></i>
            <i class="ti ti-chevrons-down" v-else></i>
            Učitaj više
          </button>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <span class="panel-title"><i class="ti ti-table"></i> RAK blokovi — kapacitet i iskorištenost</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
          <tr>
            <th>Operator</th>
            <th>Pozivni / Regija</th>
            <th>Raspon bloka</th>
            <th>Kapacitet</th>
            <th>Rasponi</th>
            <th>Iskorištenost RAK bloka</th>
          </tr>
            </thead>
            <tbody>
              <tr v-for="rb in data.rak_blocks" :key="rb.id">
                <td><strong>{{ rb.operator_name }}</strong></td>
                <td>
                  <strong class="plain-code">{{ rb.area_code }}</strong>
                  <span class="sub-text">{{ rb.region_name }}</span>
                </td>
                <td><span class="mono-range">{{ rb.block_start }} – {{ rb.block_end }}</span></td>
                <td><strong>{{ fmt(rb.block_size) }}</strong></td>
                <td>
                  <strong>{{ rb.ranges_generated }} / {{ rb.ranges_total }}</strong>
                  <span class="sub-text">generirani / ukupno</span>
                  <span v-if="rb.ranges_not_generated" class="pct-tag">{{ rb.ranges_not_generated }} neg.</span>
                </td>
                <td>
                  <div class="usage-cell">
                    <div class="bar-track"><div class="bar-fill" :style="{ width: rb.gen_pct + '%', background: usageColor(rb.gen_pct) }"></div></div>
                    <span :style="{ color: usageColor(rb.gen_pct) }">{{ rb.gen_pct }}%</span>
                  </div>
                  <span class="sub-text">{{ fmt(rb.generated_numbers) }} / {{ fmt(rb.block_size) }}</span>
                </td>
              </tr>
          
              <tr v-if="!data.rak_blocks?.length">
                <td colspan="9" class="empty">Nema RAK blokova.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-else-if="loadError" class="error-state">
      <i class="ti ti-alert-circle"></i>
      <p>Greška pri učitavanju dashboard podataka.</p>
      <button class="btn btn-primary" @click="load">Pokušaj ponovo</button>
    </div>

    <AssignModal
      v-if="assignModalOpen"
      :phone="selectedPhone"
      @close="closeAssign"
      @assigned="onAssigned"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import AssignModal from "../components/AssignPhoneModal.vue";

const router = useRouter();

const loading = ref(false);
const loadError = ref(false);
const data = ref(null);

const clockDate = ref("");
const clockTime = ref("");
let clockInterval = null;

function updateClock() {
  const now = new Date();
  clockDate.value = now.toLocaleDateString("hr-HR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" });
  clockTime.value = now.toLocaleTimeString("hr-HR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

const rangesPanel = ref(null);
const rangesLoading = ref(false);
const rangesData = ref(null);
const rangeSearch = ref("");
const rangeFilters = ref({ city_id: null, rak_block_id: null, generated: null });
const rangeFilterCities = ref([]);
const rangeFilterRaks = ref([]);
const sortByCritical = ref(false);
const rangesPage = ref(1);
const rangesPageSize = 15;

const firstFreeFilters = reactive({
  entity_id: null,
  region_id: null,
  city_id: null,
  location_id: null,
  device_id: null,
  number_category: null,
});
const firstFreeNumber = ref(null);
const firstEntities = ref([]);
const firstRegions = ref([]);
const firstCities = ref([]);
const firstLocations = ref([]);
const firstDevices = ref([]);
const assignModalOpen = ref(false);
const selectedPhone = ref(null);

const s = computed(() => data.value?.summary ?? {});

const donut = computed(() => {
  const total = s.value.generated_total || 1;
  const circumference = 402.12;
  const arc = (val) => +((val / total) * circumference).toFixed(2);
  return {
    free: arc(s.value.free),
    busy: arc(s.value.busy),
    quarantine: arc(s.value.quarantine),
  };
});

const trendMax = computed(() => {
  if (!data.value?.monthly_trend?.length) return 1;
  return Math.max(...data.value.monthly_trend.flatMap((m) => [m.assigned, m.released]), 1);
});

const trendTotals = computed(() => {
  const t = data.value?.monthly_trend ?? [];
  return {
    assigned: t.reduce((a, m) => a + m.assigned, 0),
    released: t.reduce((a, m) => a + m.released, 0),
    net: t.reduce((a, m) => a + m.net, 0),
  };
});

const hasActiveFilters = computed(() =>
  rangeSearch.value ||
  rangeFilters.value.city_id ||
  rangeFilters.value.rak_block_id ||
  rangeFilters.value.generated !== null
);

const fmt = (n) => (n ?? 0).toLocaleString("hr-HR");
const pctOf = (a, b) => (b ? Math.min(100, Math.round((a / b) * 100)) : 0);
const shortMonth = (l) => l?.split(" ")[0] ?? l;
const catLabel = (c) => ({ standard: "Standard", premium: "Premium", gold: "Gold", silver: "Silver", bronze: "Bronze", special: "Posebni / VIP", short: "Kratki" }[c] ?? c ?? "—");
const usageColor = (p) => (p >= 85 ? "#DC2626" : p >= 65 ? "#D97706" : "#16A34A");
const usageBadge = (p) => (p >= 85 ? "badge-red" : p >= 65 ? "badge-amber" : "badge-green");
const warningIcon = (sev) => (sev === "danger" ? "ti ti-alert-triangle" : sev === "warning" ? "ti ti-alert-circle" : "ti ti-info-circle");
const trendBarH = (val) => Math.max(3, Math.round((val / trendMax.value) * 100));

function prettyNumber(n) {
  if (!n) return "—";
  const raw = String(n).replace(/\s+/g, "");
  if (raw.length === 9) return `+387 ${raw.slice(0, 2)} ${raw.slice(2, 5)} ${raw.slice(5)}`;
  if (raw.length === 8) return `+387 ${raw.slice(0, 2)} ${raw.slice(2, 5)} ${raw.slice(5)}`;
  return raw;
}

function timeShort(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const today = new Date();
  const isToday = d.toDateString() === today.toDateString();
  const time = d.toLocaleTimeString("hr-HR", { hour: "2-digit", minute: "2-digit" });
  if (isToday) return time;
  return d.toLocaleDateString("hr-HR", { day: "2-digit", month: "2-digit" }) + " " + time;
}

function go(path) {
  router.push(path);
}

function toggleCritical() {
  sortByCritical.value = !sortByCritical.value;
  rangesPage.value = 1;
  loadRanges(1, false);
}

let debounceTimer = null;
function debouncedLoadRanges() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    rangesPage.value = 1;
    loadRanges(1, false);
  }, 350);
}

async function load() {
  loading.value = true;
  loadError.value = false;

  try {
    const res = await api.get("/dashboard/analytics");
    data.value = res.data;
    firstFreeNumber.value = res.data.first_free;
    rangesPage.value = 1;
    await loadRanges(1, false);
  } catch (e) {
    console.error(e);
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}

async function loadFirstEntities() {
  try {
    const res = await api.get("/entities");
    firstEntities.value = res.data || [];
  } catch (e) {
    console.error(e);
  }
}

async function onFirstEntityChange() {
  firstFreeFilters.region_id = null;
  firstFreeFilters.city_id = null;
  firstFreeFilters.location_id = null;
  firstFreeFilters.device_id = null;
  firstRegions.value = [];
  firstCities.value = [];
  firstLocations.value = [];
  firstDevices.value = [];
  if (firstFreeFilters.entity_id) {
    const res = await api.get(`/regions?entity_id=${firstFreeFilters.entity_id}`);
    firstRegions.value = res.data || [];
  }
  await loadFirstFree();
}

async function onFirstRegionChange() {
  firstFreeFilters.city_id = null;
  firstFreeFilters.location_id = null;
  firstFreeFilters.device_id = null;
  firstCities.value = [];
  firstLocations.value = [];
  firstDevices.value = [];
  if (firstFreeFilters.region_id) {
    const res = await api.get(`/cities?region_id=${firstFreeFilters.region_id}`);
    firstCities.value = res.data || [];
  }
  await loadFirstFree();
}

async function onFirstCityChange() {
  firstFreeFilters.location_id = null;
  firstFreeFilters.device_id = null;
  firstLocations.value = [];
  firstDevices.value = [];
  if (firstFreeFilters.city_id) {
    const res = await api.get("/locations");
    firstLocations.value = (res.data || []).filter((l) => Number(l.city_id) === Number(firstFreeFilters.city_id));
  }
  await loadFirstFree();
}

async function onFirstLocationChange() {
  firstFreeFilters.device_id = null;
  firstDevices.value = [];
  if (firstFreeFilters.location_id) {
    const res = await api.get(`/devices?location_id=${firstFreeFilters.location_id}`);
    firstDevices.value = res.data || [];
  }
  await loadFirstFree();
}

async function loadFirstFree() {
  try {
    const params = {};
    if (firstFreeFilters.entity_id) params.entity_id = firstFreeFilters.entity_id;
    if (firstFreeFilters.region_id) params.region_id = firstFreeFilters.region_id;
    if (firstFreeFilters.city_id) params.city_id = firstFreeFilters.city_id;
    if (firstFreeFilters.location_id) params.location_id = firstFreeFilters.location_id;
    if (firstFreeFilters.device_id) params.device_id = firstFreeFilters.device_id;
    if (firstFreeFilters.number_category) params.number_category = firstFreeFilters.number_category;

    const res = await api.get("/dashboard/first-free", { params });
    firstFreeNumber.value = res.data?.found ? res.data.number : null;
  } catch (e) {
    console.error(e);
  }
}

function openAssign(phone) {
  selectedPhone.value = phone;
  assignModalOpen.value = true;
}

function closeAssign() {
  assignModalOpen.value = false;
  selectedPhone.value = null;
}

async function onAssigned() {
  closeAssign();
  await load();
}

async function loadRanges(page = 1, append = false) {
  rangesLoading.value = true;

  try {
    const params = { page, page_size: rangesPageSize };
    if (rangeSearch.value) params.search = rangeSearch.value;
    if (rangeFilters.value.city_id) params.city_id = rangeFilters.value.city_id;
    if (rangeFilters.value.rak_block_id) params.rak_block_id = rangeFilters.value.rak_block_id;
    if (rangeFilters.value.generated !== null) params.generated = rangeFilters.value.generated;
    if (sortByCritical.value) params.sort_critical = true;

    const res = await api.get("/dashboard/ranges", { params });

    if (append && rangesData.value) {
      rangesData.value = {
        ...res.data,
        ranges: [...rangesData.value.ranges, ...res.data.ranges],
      };
    } else {
      rangesData.value = res.data;
    }

    if (res.data.filter_cities?.length && !rangeFilterCities.value.length) {
      rangeFilterCities.value = res.data.filter_cities;
    }
    if (res.data.filter_rak_blocks?.length && !rangeFilterRaks.value.length) {
      rangeFilterRaks.value = res.data.filter_rak_blocks;
    }

    rangesPage.value = page;
  } catch (e) {
    console.error(e);
  } finally {
    rangesLoading.value = false;
  }
}

async function loadMore() {
  await loadRanges(rangesPage.value + 1, true);
}

function clearRangeFilters() {
  rangeSearch.value = "";
  rangeFilters.value = { city_id: null, rak_block_id: null, generated: null };
  sortByCritical.value = false;
  rangesPage.value = 1;
  loadRanges(1, false);
}

onMounted(async () => {
  updateClock();
  clockInterval = setInterval(updateClock, 1000);
  await loadFirstEntities();
  await load();
});

onUnmounted(() => {
  clearInterval(clockInterval);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

* { box-sizing: border-box; font-family: 'Geist', sans-serif; }
.dash { padding-bottom: 40px; color: #111827; }
.mb { margin-bottom: 16px; }
.mt { margin-top: 14px; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.4px;
}
.header-left h1 i { color: #1B4FD8; font-size: 27px; }
.header-left p { margin: 5px 0 0; color: #6B7280; font-size: 14px; }

.live-clock {
  background: linear-gradient(135deg, #1B4FD8 0%, #3B82F6 100%);
  border-radius: 14px;
  padding: 12px 20px;
  text-align: right;
  box-shadow: 0 8px 24px rgba(27,79,216,.22);
  min-width: 220px;
}
.clock-date {
  color: rgba(255,255,255,.75);
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: .02em;
}
.clock-time {
  color: #fff;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: .04em;
  margin-top: 2px;
  font-variant-numeric: tabular-nums;
}

.btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  transition: transform .12s, box-shadow .12s, background .12s;
}
.btn:hover { transform: translateY(-1px); }
.btn:disabled { opacity: .5; cursor: not-allowed; transform: none; }
.btn-primary { background: #1B4FD8; color: #fff; box-shadow: 0 8px 18px rgba(27,79,216,.18); }
.btn-ghost { background: #fff; color: #1B4FD8; border: 1px solid #BFDBFE; }
.btn-danger-soft { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; align-self: end; }
.btn-warning-soft { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; font-size: 12px; padding: 8px 12px; }
.btn-warning-soft.active { background: #D97706; color: #fff; border-color: #D97706; }

.metrics-row { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 12px; }
.metric-card {
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 17px;
  padding: 16px 17px;
  display: flex;
  gap: 12px;
  min-height: 108px;
  box-shadow: 0 1px 4px rgba(15,23,42,.04);
  cursor: pointer;
  transition: transform .14s, box-shadow .14s, border-color .14s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(15,23,42,.08); border-color: #D1D5DB; }
.mc-icon {
  width: 40px;
  height: 40px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex: 0 0 auto;
}
.mc-blue .mc-icon { background: #EFF6FF; color: #1B4FD8; }
.mc-cyan .mc-icon { background: #ECFEFF; color: #0891B2; }
.mc-indigo .mc-icon { background: #EEF2FF; color: #4F46E5; }
.mc-teal .mc-icon { background: #F0FDFA; color: #0D9488; }
.mc-slate .mc-icon { background: #F8FAFC; color: #475569; }
.mc-rose .mc-icon { background: #FFF1F2; color: #E11D48; }
.mc-violet .mc-icon { background: #F5F3FF; color: #7C3AED; }
.mc-body { min-width: 0; flex: 1; }
.mc-label { color: #6B7280; font-size: 11px; font-weight: 700; white-space: nowrap; }
.mc-val { color: #111827; font-size: 22px; font-weight: 800; line-height: 1.35; margin-top: 3px; }
.mc-sub { color: #374151; font-size: 11px; font-weight: 600; margin-top: 2px; }
.mc-sub-dual { display: flex; flex-direction: column; gap: 2px; margin-top: 3px; }
.mc-sub-dual .sub-muted { color: #374151; font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 3px; }
.mc-sub-dual .sub-green { color: #15803D; font-size: 11px; font-weight: 700; display: flex; align-items: center; gap: 3px; }
.mc-sub-dual .sub-red { color: #B91C1C; font-size: 11px; font-weight: 700; display: flex; align-items: center; gap: 3px; }

.warnings-row {
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 15px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.warnings-title { color: #D97706; font-size: 12px; font-weight: 800; display: flex; align-items: center; gap: 5px; padding-right: 4px; }
.warn-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 700;
}
.warn-danger { color: #DC2626; background: #FEF2F2; border: 1px solid #FECACA; }
.warn-warning { color: #D97706; background: #FFFBEB; border: 1px solid #FDE68A; }
.warn-info { color: #1B4FD8; background: #EFF6FF; border: 1px solid #BFDBFE; }

.dashboard-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 12px; }
.span-4 { grid-column: span 4; }
.span-5 { grid-column: span 5; }
.span-6 { grid-column: span 6; }
.span-7 { grid-column: span 7; }
.span-8 { grid-column: span 8; }

.panel {
  background: #fff;
  border: 1px solid #E5E7EB;
  border-radius: 17px;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(15,23,42,.04);
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 800;
  color: #111827;
}
.panel-title i { color: #1B4FD8; font-size: 17px; }

.dist-body { display: grid; grid-template-columns: 220px 1fr; gap: 24px; }
.dist-left { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.donut-wrap { display: flex; justify-content: center; }

.status-legend { width: 100%; display: flex; flex-direction: column; gap: 6px; }
.legend-item {
  display: grid;
  grid-template-columns: 10px 1fr 42px;
  gap: 8px;
  align-items: center;
  padding: 7px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background .12s;
}
.legend-item:hover { background: #F9FAFB; }
.li-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.li-body { display: flex; flex-direction: column; min-width: 0; }
.li-body span { color: #6B7280; font-size: 11px; }
.li-body strong { color: #111827; font-size: 13px; font-weight: 800; }
.li-pct { text-align: right; font-size: 12px; font-weight: 800; }

.li-dot.green { background: #16A34A; }
.li-dot.red { background: #DC2626; }
.li-dot.purple { background: #7C3AED; }
.li-dot.amber { background: #F59E0B; }

.dist-right { display: flex; flex-direction: column; gap: 12px; }
.cat-title { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 800; color: #111827; padding-bottom: 8px; border-bottom: 1px solid #F3F4F6; }
.cat-title i { color: #1B4FD8; }
.category-list { display: flex; flex-direction: column; gap: 12px; }
.category-row { display: flex; flex-direction: column; gap: 6px; }
.category-head { display: flex; justify-content: space-between; align-items: center; }
.category-head strong { font-size: 13px; color: #111827; font-weight: 800; }
.cat-stats { display: flex; gap: 10px; align-items: center; }
.cs-total { color: #6B7280; font-size: 12px; font-weight: 700; }
.cs-free { font-size: 11px; font-weight: 700; }
.cs-busy { font-size: 11px; font-weight: 700; }
.stacked { height: 8px; background: #F3F4F6; border-radius: 999px; overflow: hidden; display: flex; }
.seg { height: 100%; min-width: 1px; }
.seg.green { background: #16A34A; }
.seg.red { background: #DC2626; }
.seg.purple { background: #7C3AED; }
.seg.amber { background: #F59E0B; }
.cat-meta { display: flex; justify-content: space-between; }
.cat-meta span { color: #9CA3AF; font-size: 11px; font-weight: 600; }

.first-free-box { display: flex; flex-direction: column; gap: 14px; }
.filters-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.ff-number-display {
  background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%);
  border: 1px solid #BBF7D0;
  border-radius: 14px;
  padding: 16px;
  text-align: center;
}
.ff-label { color: #6B7280; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.ff-number { color: #15803D; font-size: 26px; font-weight: 800; letter-spacing: .5px; margin: 6px 0; font-variant-numeric: tabular-nums; }
.ff-meta { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
.ff-meta span { color: #6B7280; font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
.cat-badge { background: #EFF6FF; color: #1B4FD8; border-radius: 6px; padding: 2px 7px; font-size: 11px; font-weight: 700; }
.ff-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

.activity-list { display: flex; flex-direction: column; gap: 0; }
.activity-row {
  display: grid;
  grid-template-columns: 34px 1fr 48px;
  gap: 10px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #F3F4F6;
}
.activity-row:last-child { border-bottom: 0; }
.activity-icon {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.activity-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 2px;
}
.act-user, .act-entity {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: #9CA3AF;
  font-size: 11px;
  font-weight: 600;
}
.act-user i, .act-entity i {
  font-size: 11px;
}



.activity-icon.blue { color: #1B4FD8; background: #EFF6FF; }
.activity-icon.amber { color: #D97706; background: #FFFBEB; }
.activity-icon.gray { color: #6B7280; background: #F3F4F6; }
.activity-body strong { display: block; color: #111827; font-size: 13px; font-weight: 700; }
.activity-body span { display: block; color: #9CA3AF; font-size: 11px; margin-top: 2px; }
.activity-row time { color: #9CA3AF; font-size: 11px; text-align: right; }

.trend-kpis { display: flex; gap: 10px; margin-bottom: 18px; }
.tkpi {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F9FAFB;
  border-radius: 12px;
  padding: 10px 12px;
}
.tkpi-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.tkpi-icon.blue { background: #EFF6FF; color: #1B4FD8; }
.tkpi-icon.amber { background: #FFFBEB; color: #D97706; }
.tkpi-icon.green { background: #F0FDF4; color: #16A34A; }
.tkpi-icon.red { background: #FEF2F2; color: #DC2626; }
.tkpi div:last-child span { display: block; color: #9CA3AF; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.tkpi div:last-child strong { display: block; font-size: 20px; font-weight: 800; margin-top: 2px; }

.bar-chart { display: flex; align-items: flex-end; justify-content: space-between; gap: 6px; padding: 4px 0 0; }
.bc-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; }
.bc-top { height: 36px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 1px; }
.bc-val { font-size: 10px; font-weight: 700; line-height: 1; }
.bc-bars { height: 100px; display: flex; align-items: flex-end; gap: 4px; }
.bc-bar { width: 16px; border-radius: 5px 5px 0 0; min-height: 3px; transition: height .5s; }
.bc-bar.blue { background: #1B4FD8; }
.bc-bar.amber { background: #F59E0B; }
.bc-label { color: #6B7280; font-size: 10px; font-weight: 700; margin-top: 4px; }
.bc-net { font-size: 10px; font-weight: 800; }

.trend-legend { display: flex; align-items: center; gap: 14px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #F3F4F6; flex-wrap: wrap; }
.trend-legend span { color: #6B7280; font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 5px; }
.trend-note { margin-left: auto; color: #9CA3AF; font-style: italic; }
.dot-inline { display: inline-block; width: 10px; height: 10px; border-radius: 3px; }
.dot-inline.blue { background: #1B4FD8; }
.dot-inline.amber { background: #F59E0B; }

.range-head-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.range-pills { display: flex; gap: 12px; flex-wrap: wrap; color: #6B7280; font-size: 12px; }
.range-pills span { display: inline-flex; align-items: center; gap: 5px; }
.range-pills strong { color: #111827; }

.filters { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr auto; gap: 10px; align-items: end; margin-bottom: 14px; }
.field { display: flex; flex-direction: column; min-width: 0; }
.field label { color: #374151; font-size: 12px; font-weight: 800; margin-bottom: 5px; }
.search-wrap { position: relative; }
.search-wrap i { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9CA3AF; pointer-events: none; }
.search-wrap input { width: 100%; padding-left: 32px; }

input, select {
  border: 1px solid #E5E7EB;
  background: #FAFAFA;
  color: #111827;
  border-radius: 10px;
  padding: 9px 11px;
  font-size: 13px;
  min-width: 0;
  outline: none;
}
input:focus, select:focus { border-color: #1B4FD8; box-shadow: 0 0 0 3px rgba(27,79,216,.08); background: #fff; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 920px; }
th {
  text-align: left;
  background: #F9FAFB;
  color: #9CA3AF;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  padding: 11px 12px;
  border-bottom: 1px solid #F3F4F6;
  white-space: nowrap;
}
td { padding: 11px 12px; border-bottom: 1px solid #F9FAFB; color: #374151; font-size: 13px; vertical-align: middle; }
tr:hover td { background: #FAFAFA; }
td strong { display: block; color: #111827; font-weight: 800; }
.sub-text { display: block; color: #9CA3AF; font-size: 11px; margin-top: 3px; }
.sub-mono, .mono-range { font-family: "Courier New", monospace; color: #6B7280; font-size: 11px; }
.plain-code { font-family: 'Courier New', monospace; font-size: 13px; color: #111827; }
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 7px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
}
.badge-green { background: #F0FDF4; color: #16A34A; }
.badge-red { background: #FEF2F2; color: #DC2626; }
.badge-amber { background: #FFFBEB; color: #D97706; }
.badge-muted { background: #F3F4F6; color: #6B7280; }
.pct-tag { display: inline-block; margin-top: 3px; color: #9CA3AF; font-size: 11px; font-weight: 700; }
.usage-cell { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; min-width: 130px; }
.usage-cell span { font-size: 12px; font-weight: 800; }
.not-gen-msg { color: #9CA3AF; font-weight: 700; text-align: center; }
.empty, .empty-soft { color: #9CA3AF; text-align: center; padding: 20px; font-size: 13px; }
.empty-soft {
  background: #F9FAFB;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.empty-soft i { font-size: 22px; }

.load-more-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #F3F4F6;
  gap: 12px;
}
.pg-info { color: #6B7280; font-size: 12px; font-weight: 700; }
.load-more-btn { min-width: 130px; }

.bar-track { width: 100%; height: 7px; background: #EEF2F7; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; min-width: 2px; transition: width .5s ease; }

.clr-blue { color: #1B4FD8 !important; }
.clr-green { color: #16A34A !important; }
.clr-red { color: #DC2626 !important; }
.clr-amber { color: #D97706 !important; }
.clr-purple { color: #7C3AED !important; }
.fw6 { font-weight: 800; }

.skeleton-grid { display: grid; gap: 12px; }
.skeleton-grid.g6 { grid-template-columns: repeat(6, 1fr); }
.skeleton-grid.g3 { grid-template-columns: repeat(3, 1fr); }
.skeleton {
  background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 37%, #F3F4F6 63%);
  background-size: 400% 100%;
  animation: shimmer 1.2s infinite;
  border-radius: 16px;
}
.sh-metric { height: 108px; }
.sh-tall { height: 300px; }
.range-skel { display: flex; flex-direction: column; gap: 8px; }
.range-skel .skeleton { height: 38px; border-radius: 9px; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: 0 0; } }

.error-state {
  background: #fff;
  border: 1px solid #FECACA;
  color: #DC2626;
  border-radius: 16px;
  padding: 30px;
  text-align: center;
}
.error-state i { font-size: 32px; }
.error-state p { margin: 10px 0 16px; font-weight: 800; }

@media (max-width: 1400px) {
  .metrics-row { grid-template-columns: repeat(4, 1fr); }
  .span-4, .span-5, .span-6, .span-7, .span-8 { grid-column: span 6; }
  .dist-body { grid-template-columns: 1fr; }
}

@media (max-width: 980px) {
  .page-header { flex-direction: column; }
  .live-clock { min-width: 0; width: 100%; text-align: left; }
  .metrics-row { grid-template-columns: repeat(2, 1fr); }
  .span-4, .span-5, .span-6, .span-7, .span-8 { grid-column: span 12; }
  .filters { grid-template-columns: 1fr; }
  .dist-body { grid-template-columns: 1fr; }
  .trend-kpis { flex-direction: column; }
}

@media (max-width: 640px) {
  .metrics-row { grid-template-columns: 1fr; }
  .filters-grid { grid-template-columns: 1fr; }
  .ff-actions { grid-template-columns: 1fr; }
}
</style>