<script setup>
import { useRoute } from "vue-router";
import { useI18n } from "../composables/useI18n";
import LanguageSwitcher from "./LanguageSwitcher.vue";
import ProfileMenu from "./ProfileMenu.vue";

const route = useRoute();
const { t } = useI18n();
const emit = defineEmits(["show-profile-details", "show-tasks"]);

const isActive = (path) => {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
};
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-brand">
      <h2 class="brand-name">{{ t("nav.companyName") }}</h2>
      <p class="brand-subtitle">{{ t("nav.subtitle") }}</p>
    </div>
    <div class="sidebar-divider"></div>

    <nav class="sidebar-nav">
      <router-link class="nav-link" :class="{ active: isActive('/') }" to="/">
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M3 3h7v7H3zM13 3h7v7h-7zM3 13h7v7H3zM13 13h7v7h-7z" />
        </svg>
        <span>{{ t("nav.overview") }}</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/inventory') }"
        to="/inventory"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M20 7L12 3L4 7M20 7v10l-8 4M20 7l-8 4M4 7v10l8 4M4 7l8 4M12 11v10"
          />
        </svg>
        <span>{{ t("nav.inventory") }}</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/orders') }"
        to="/orders"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9h6m-6 4h6m-6-8h6"
          />
        </svg>
        <span>{{ t("nav.orders") }}</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/spending') }"
        to="/spending"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
        </svg>
        <span>{{ t("nav.finance") }}</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/demand') }"
        to="/demand"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M23 6l-9.5 9.5-5-5L1 18M17 6h6v6" />
        </svg>
        <span>{{ t("nav.demandForecast") }}</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/reports') }"
        to="/reports"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 20V10M18 20V4M6 20v-6" />
        </svg>
        <span>Reports</span>
      </router-link>

      <router-link
        class="nav-link"
        :class="{ active: isActive('/restocking') }"
        to="/restocking"
      >
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
        <span>{{ t("nav.restocking") }}</span>
      </router-link>
    </nav>

    <div class="sidebar-divider"></div>
    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="emit('show-profile-details')"
        @show-tasks="emit('show-tasks')"
      />
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  box-shadow: 1px 0 3px 0 rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  z-index: 100;
  overflow-y: auto;
}

.sidebar-brand {
  padding: 1.25rem 1rem 1rem;
  flex-shrink: 0;
}

.brand-name {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.3;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
  line-height: 1.4;
}

.sidebar-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 0 1rem;
  flex-shrink: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  overflow-y: auto;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 1rem;
  margin: 0 0.5rem;
  border-radius: 6px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  padding-left: calc(1rem - 3px);
}

.nav-link:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.nav-link.active {
  background: #eff6ff;
  color: #2563eb;
  border-left-color: #2563eb;
}

.nav-link svg {
  flex-shrink: 0;
  opacity: 0.8;
}

.nav-link.active svg {
  opacity: 1;
}

.sidebar-footer {
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Stretch both buttons to fill the sidebar width */
.sidebar-footer :deep(.language-button),
.sidebar-footer :deep(.profile-button) {
  width: 100%;
  justify-content: flex-start;
}

/* Open dropdowns upward so they aren't clipped at the bottom */
.sidebar-footer :deep(.dropdown-menu) {
  top: auto !important;
  bottom: calc(100% + 0.5rem) !important;
  left: 0 !important;
  right: 0 !important;
  min-width: unset !important;
}
</style>
