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

      <button class="logout" @click="logout">Odjava</button>
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
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  font-family: Arial, sans-serif;
}

/* SIDEBAR */

.sidebar {
  position: relative;
  width: 270px;
  padding: 26px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(50px);
  opacity: 0.18;
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
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 2;
}

.nav a {
  text-decoration: none;
  color: #374151;
  padding: 13px 16px;
  border-radius: 14px;
  font-weight: 600;
  transition: 0.2s;
}

.nav a:hover {
  background: #f3f4f6;
}

.nav a.router-link-active {
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
}

/* LOGOUT */

.logout {
  position: relative;
  margin-top: auto;
  z-index: 2;
  border: none;
  border-radius: 14px;
  padding: 13px;
  cursor: pointer;
  font-weight: bold;
  color: white;
  background: linear-gradient(135deg, #dc2626, #991b1b);
  transition: 0.2s;
}

.logout:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 24px rgba(220, 38, 38, 0.18);
}

/* MAIN */

.main {
  flex: 1;
  padding: 34px;
}
</style>