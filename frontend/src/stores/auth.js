import { defineStore } from "pinia";
import api from "../api/client";
import router from "../router";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token"),
    user: null,
  }),

  actions: {
    async login(email, password) {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      this.token = response.data.access_token;
      localStorage.setItem("token", this.token);

      await this.fetchMe();

      router.push("/dashboard");
    },

    async fetchMe() {
      const response = await api.get("/auth/me");
      this.user = response.data;
    },

    async initAuth() {
      if (this.token && !this.user) {
        try {
          await this.fetchMe();
        } catch (err) {
          this.logout();
        }
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      router.push("/login");
    },
  },
});