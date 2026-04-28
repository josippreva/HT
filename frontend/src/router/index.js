import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/LoginView.vue";
import AppLayout from "../layouts/AppLayout.vue";

import DashboardView from "../views/DashboardView.vue";
import LocationsView from "../views/LocationsView.vue";
import CitiesView from "../views/CitiesView.vue";
import PostalCodesView from "../views/PostalCodesView.vue";
import DevicesView from "../views/DevicesView.vue";
import NumberRangesView from "../views/NumberRangesView.vue";
import SubscribersView from "../views/SubscribersView.vue";

import PhoneNumbersView from "../views/PhoneNumbersView.vue";


const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/",
    component: AppLayout,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: DashboardView,
      },
      {
        path: "locations",
        name: "locations",
        component: LocationsView,
      },
      {
        path: "cities",
        name: "cities",
        component: CitiesView,
      },
      {
        path: "postal-codes",
        name: "postal-codes",
        component: PostalCodesView,
      },

      {
        path: "devices",
        name: "devices",
        component: DevicesView,
      },
      {
        path: "number-ranges",
        name: "number-ranges",
        component: NumberRangesView,
      },
      {
        path: "subscribers",
        name: "subscribers",
        component: SubscribersView,
      },
      {
        path: "phone-numbers",
        name: "phone-numbers",
        component: PhoneNumbersView,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  if (to.path !== "/login" && !token) {
    next("/login");
    return;
  }

  if (to.path === "/login" && token) {
    next("/dashboard");
    return;
  }

  next();
});

export default router;