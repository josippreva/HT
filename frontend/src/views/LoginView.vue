<template>
  <div class="login-page">
    <div class="glow glow-1"></div>
    <div class="glow glow-2"></div>

    <div class="login-card">
      <div class="brand">
        <div class="logo">HT</div>

        <div>
          <h1>HT Mostar</h1>
          <p>Interni sustav za upravljanje numeracijom</p>
        </div>
      </div>

      <form @submit.prevent="submitLogin">
        <label>Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="admin@htmostar.ba"
          required
        />

        <label>Lozinka</label>
        <input
          v-model="password"
          type="password"
          placeholder="••••••••"
          required
        />

        <button
          class="btn-192"
          type="submit"
          :disabled="loading"
        >
          <i class="ti ti-login"></i>
          {{ loading ? "Prijava..." : "Prijavi se" }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submitLogin() {
  error.value = "";
  loading.value = true;

  try {
    await authStore.login(email.value, password.value);
    router.push("/dashboard");
  } catch (err) {
    error.value = "Neispravni podaci za prijavu.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background:
    radial-gradient(circle at top left, rgba(27, 79, 216, 0.34), transparent 32%),
    radial-gradient(circle at bottom right, rgba(37,99,235,0.22) 0, transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f8fafc 45%, #eef2ff 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Geist', sans-serif;
}

.glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(60px);
  opacity: 0.45;
}

.glow-1 {
  width: 280px;
  height: 280px;
  background: #1B4FD8;
  top: 8%;
  left: 12%;
}

.glow-2 {
  width: 320px;
  height: 320px;
  background: #7C3AED;
  bottom: 8%;
  right: 12%;
}

.login-card {
  position: relative;
  width: 430px;
  padding: 36px;
  border-radius: 26px;
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(255,255,255,0.75);
  backdrop-filter: blur(18px);
  box-shadow: 0 30px 80px rgba(15,23,42,0.16);
  color: #111827;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 30px;
}

.logo {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: #1B4FD8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 18px;
  color: white;
  box-shadow: 0 12px 28px rgba(37,99,235,0.18);
}

h1 {
  margin: 0;
  font-size: 26px;
  color: #111827;
}

.brand p {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 14px;
}

label {
  display: block;
  margin-bottom: 7px;
  font-size: 14px;
  color: #374151;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 13px 14px;
  margin-bottom: 18px;
  border-radius: 12px;
  border: 1px solid #d1d5db;
  background: white;
  color: #111827;
  outline: none;
  font-size: 15px;
  transition: 0.2s;
  box-sizing: border-box;
  font-family: 'Geist', sans-serif;
}

input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}

/* LOGIN BUTTON */
.btn-192 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  width: 100%;
  padding: 12px 14px;
  background: #EDF4FF;
  color: #1B4FD8;

  border: 1px solid #7FB3FF;
  border-radius: 12px;

  font-size: 14px;
  font-weight: 600;

  cursor: pointer;
  font-family: 'Geist', sans-serif;

  transition:
    background 0.12s,
    color 0.12s,
    border-color 0.12s,
    transform 0.12s;
}

.btn-192 i {
  font-size: 17px;
}

.btn-192:hover {
  background: #1B4FD8;
  color: #FFFF;
  border-color: #7FB3FF;
}

.btn-192:active {
  transform: scale(0.98);
}

.btn-192:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 16px;
  text-align: center;
  color: #dc2626;
  font-size: 14px;
}
</style>