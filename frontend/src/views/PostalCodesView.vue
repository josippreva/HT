<template>
  <div>
    <h1>Poštanski brojevi</h1>
    <p>Pregled poštanskih brojeva iz baze.</p>

    <div v-if="loading">Učitavanje...</div>

    <div v-else-if="error" style="color: red;">
      {{ error }}
    </div>

    <table v-else border="1" cellpadding="8" cellspacing="0" style="margin-top: 20px; width: 100%;">
      <thead>
        <tr>
          <th>ID</th>
          <th>Poštanski broj</th>
          <th>Naziv</th>
          <th>City ID</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="item in postalCodes" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.postal_code }}</td>
          <td>{{ item.postal_name }}</td>
          <td>{{ item.city_id }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api/client";

const postalCodes = ref([]);
const loading = ref(false);
const error = ref("");

async function loadPostalCodes() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/postal-codes");
    postalCodes.value = response.data;
  } catch (err) {
    error.value = "Greška pri učitavanju poštanskih brojeva.";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadPostalCodes();
});
</script>