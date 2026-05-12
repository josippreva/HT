<template>
  <div class="layout">
    <aside class="sidebar">

      <div class="brand">
        <div class="logo">HT</div>
        <div class="brand-text">
          <h2>HT Mostar</h2>
          <p>Upravljanje numeracijom</p>
        </div>
      </div>

      <nav class="nav">
        <div class="nav-section">Pregled</div>
        <RouterLink to="/dashboard">
          <i class="ti ti-layout-dashboard"></i>
          Pregled sustava
        </RouterLink>

        <div class="nav-section">Infrastruktura</div>
        <RouterLink to="/cities">
          <i class="ti ti-building"></i>
          Gradovi / općine
        </RouterLink>
        <RouterLink to="/locations">
          <i class="ti ti-map-pin"></i>
          Lokacije
        </RouterLink>
        <RouterLink to="/devices">
          <i class="ti ti-cpu"></i>
          Uređaji
        </RouterLink>

        <div class="nav-section">Numeracija</div>
        <RouterLink to="/number-ranges">
          <i class="ti ti-list-numbers"></i>
          Rasponi
        </RouterLink>
        <RouterLink to="/phone-numbers">
          <i class="ti ti-phone"></i>
          Brojevi
        </RouterLink>
        <RouterLink to="/subscribers">
          <i class="ti ti-users"></i>
          Pretplatnici
        </RouterLink>
      </nav>

      <div class="sb-bottom">
        <div class="user-row">
          <div class="avatar">
            {{
              (authStore.user?.username || authStore.user?.email || "A")
                .charAt(0)
                .toUpperCase()
            }}
          </div>
          <div class="user-info">
            <p>{{ authStore.user?.full_name || authStore.user?.email || "Korisnik" }}</p>
            <span>{{ authStore.user?.role ?? "—" }}</span>
          </div>
        </div>
        <button class="logout" @click="logout">
          <i class="ti ti-logout"></i>
          Odjava
        </button>
      </div>

    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();

function logout() {
  authStore.logout();
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #F3F4F6;
  font-family: 'Geist', sans-serif;
}

/* ── Sidebar ── */
.sidebar {
  width: 268px;
  min-width: 268px;
  height: 100vh;
  background: #FFFFFF;
  border-right: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  box-sizing: border-box;
}

/* ── Brand ── */
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 6px 26px;
  border-bottom: 1px solid #F3F4F6;
  margin-bottom: 6px;
  flex-shrink: 0;
}

.logo {
  width: 54px;
  height: 54px;
  background: #1B4FD8;
  border-radius: 14px;
  color: #fff;
  font-size: 17px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.5px;
}

.brand-text h2 {
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.3px;
}

.brand-text p {
  margin: 5px 0 0;
  font-size: 13px;
  color: #374151;
  font-weight: 400;
}

/* ── Nav ── */
.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
  padding: 4px 0 8px;
}

.nav-section {
  font-size: 10px;
  font-weight: 600;
  color: #9CA3AF;
  letter-spacing: 0.9px;
  text-transform: uppercase;
  padding: 16px 10px 6px;
}

.nav a {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 12px;
  border-radius: 9px;
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  color: #374151;
  transition: background 0.1s, color 0.1s;
}

.nav a i {
  font-size: 18px;
  flex-shrink: 0;
  opacity: 0.85;
}

.nav a:hover {
  background: #F9FAFB;
  color: #374151;
}

.nav a.router-link-active {
  background: #EFF6FF;
  color: #1B4FD8;
  font-weight: 600;
}

.nav a.router-link-active i {
  opacity: 1;
}

/* ── Bottom ── */
.sb-bottom {
  flex-shrink: 0;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 4px 6px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #EFF6FF;
  color: #1B4FD8;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info p {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.user-info span {
  font-size: 11px;
  color: #6B7280;
  text-transform: capitalize;
}

.logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  color: #DC2626;
  cursor: pointer;
  font-family: 'Geist', sans-serif;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.logout i {
  font-size: 17px;
}

.logout:hover {
  background:#DC2626;
  color: #FFFF;
  border-color: #FECACA;
}

/* ── Main ── */
.main {
  flex: 1;
  height: 100vh;
  overflow-y: auto;
  padding: 36px 40px;
  background: #EDF4FF;
}
</style>