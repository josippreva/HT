import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

// Povuci korisnika pri svakom refreshu ako token postoji
const authStore = useAuthStore();
if (authStore.token) {
  authStore.fetchMe();
}

app.use(router);
app.mount("#app");