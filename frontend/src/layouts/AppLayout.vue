<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-glow glow-red"></div>
      <div class="sidebar-glow glow-blue"></div>

      <div class="brand">
        <div class="logo">HT</div>
        <div>
          <h2>HT Mostar</h2>
          <p>Upravljanje numeracijom</p>
        </div>
      </div>

      <nav class="nav">
        <RouterLink to="/dashboard">Pregled sustava</RouterLink>
        <RouterLink to="/cities">Gradovi/općine</RouterLink>
        <RouterLink to="/locations">Lokacije</RouterLink>
        <RouterLink to="/devices">Uređaji</RouterLink>
        <RouterLink to="/number-ranges">Rasponi</RouterLink>
        <RouterLink to="/phone-numbers">Brojevi</RouterLink>
        <RouterLink to="/subscribers">Pretplatnici</RouterLink>
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
            <p> {{ authStore.user?.full_name || authStore.user?.email || "IME/EMAIL" }}</p>
            <span>{{ authStore.user?.role ?? 'a' }}</span>
          </div>
        </div>
        <button class="logout" @click="logout">Odjava</button>
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
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  font-family: Arial, sans-serif;
}

/* SIDEBAR */
.sidebar {
  position: relative;
  width: 270px;
  min-width: 270px;
  padding: 26px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;
}

.sidebar-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(50px);
  opacity: 0.18;
  pointer-events: none;
}
.glow-red {
  width: 220px;
  height: 220px;
  background: #ef4444;
  top: -50px;
  left: -60px;
}
.glow-blue {
  width: 220px;
  height: 220px;
  background: #2563eb;
  bottom: -60px;
  right: -80px;
}

/* BRAND */
.brand {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 38px;
  z-index: 2;
  flex-shrink: 0;
}
.logo {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  font-weight: 900;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.18);
  flex-shrink: 0;
}
.brand h2 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}
.brand p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280;
}

/* NAV */
.nav {
  position: relative;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 2;
  flex-shrink: 0;
}
.nav a {
  text-decoration: none;
  color: #374151;
  padding: 12px 16px;
  border-radius: 14px;
  font-weight: 600;
  transition: 0.2s;
}
.nav a:hover {
  background: #f3f4f6;
}
.nav a.router-link-active {
  background: linear-gradient(140deg,rgb(37, 99, 235), rgb(205, 38, 38,0.9));
  color: white;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
}

/* ── Bottom section ──────────────────────────────────── */
.sb-bottom {
  position: relative;
  z-index: 2;
  margin-top: auto;
  padding-bottom: 35px;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 4px 12px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #e0e7ff, #dbeafe);
  border: 1px solid #c7d2fe;
  color: #3730a3;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.5px;
}

.user-info p {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #111827;
}

.user-info span {
  font-size: 11px;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.logout {
  width: 100%;
  border: 1px solid rgba(220,38,38,0.2);
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  color: #f7f7fa;
  background: linear-gradient(135deg, #8726cd, #2563eb);
  transition: background 0.15s;
}
.logout:hover {
  background: linear-gradient(135deg, #8726cd, #cd2626);
  transform: none;
  box-shadow: none;
}

/* MAIN */
.main {
  flex: 1;
  padding: 34px;
  overflow-y: auto;
  height: 100vh;
}
</style>