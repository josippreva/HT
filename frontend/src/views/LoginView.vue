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

        <button type="submit" :disabled="loading">
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
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background:
    radial-gradient(circle at top left, rgba(220,38,38,0.28) 0, transparent 32%),
    radial-gradient(circle at bottom right, rgba(37,99,235,0.22) 0, transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f8fafc 45%, #eef2ff 100%);
  position: relative;
  overflow: hidden;
  font-family: Arial, sans-serif;
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
  background: #ef4444;
  top: 8%;
  left: 12%;
}

.glow-2 {
  width: 320px;
  height: 320px;
  background: #3b82f6;
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
  background: linear-gradient(135deg, #dc2626, #2563eb);
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
}

input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}

button {
  width: 100%;
  margin-top: 8px;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #dc2626, #2563eb);
  color: white;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
  transition: 0.2s;
}

button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(37,99,235,0.16);
}

button:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.error {
  margin-top: 16px;
  text-align: center;
  color: #dc2626;
}
</style>