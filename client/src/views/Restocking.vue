<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t("restocking.title") }}</h2>
      <p>{{ t("restocking.description") }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t("common.loading") }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Budget control card -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t("restocking.budgetLabel") }}</h3>
          <span class="budget-display">${{ budget.toLocaleString() }}</span>
        </div>
        <div class="budget-control">
          <input
            type="range"
            min="10000"
            max="500000"
            step="1000"
            v-model.number="budget"
          />
        </div>
        <div class="budget-markers">
          <span>$10K</span>
          <span>$100K</span>
          <span>$250K</span>
          <span>$500K</span>
        </div>
      </div>

      <!-- Stats row -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t("restocking.itemsSelected") }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t("restocking.totalCost") }}</div>
          <div class="stat-value">${{ totalCost.toLocaleString() }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t("restocking.remainingBudget") }}</div>
          <div class="stat-value">${{ remainingBudget.toLocaleString() }}</div>
        </div>
      </div>

      <!-- Recommendations card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("restocking.recommendations") }}</h3>
          <button
            class="place-order-btn"
            :disabled="submitting || recommendations.length === 0"
            @click="placeOrder"
          >
            {{
              submitting
                ? t("restocking.submitting")
                : t("restocking.placeOrder")
            }}
          </button>
        </div>

        <div v-if="successMessage" class="success-banner">
          {{ successMessage }}
        </div>
        <div v-if="orderError" class="error-banner">{{ orderError }}</div>

        <div v-if="recommendations.length === 0" class="empty-state">
          {{ t("restocking.noItems") }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("restocking.table.sku") }}</th>
                <th>{{ t("restocking.table.itemName") }}</th>
                <th>{{ t("restocking.table.trend") }}</th>
                <th>{{ t("restocking.table.forecastedDemand") }}</th>
                <th>{{ t("restocking.table.unitCost") }}</th>
                <th>{{ t("restocking.table.recommendedQty") }}</th>
                <th>{{ t("restocking.table.totalCost") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.id">
                <td>
                  <strong>{{ item.item_sku }}</strong>
                </td>
                <td>{{ item.item_name }}</td>
                <td>
                  <span :class="trendBadgeClass(item.trend)">{{
                    item.trend
                  }}</span>
                </td>
                <td>{{ item.forecasted_demand.toLocaleString() }}</td>
                <td>${{ item.unit_cost.toFixed(2) }}</td>
                <td>{{ item.recommended_qty.toLocaleString() }}</td>
                <td>
                  <strong>${{ item.item_total.toLocaleString() }}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { api } from "../api";
import { useI18n } from "../composables/useI18n";

export default {
  name: "Restocking",
  setup() {
    const { t } = useI18n();

    const demandItems = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const budget = ref(100000);
    const submitting = ref(false);
    const successMessage = ref("");
    const orderError = ref("");

    const recommendations = computed(() => {
      const eligible = demandItems.value.filter((item) => item.unit_cost > 0);

      const sorted = [...eligible].sort((a, b) => {
        const aIncreasing = a.trend === "increasing" ? 0 : 1;
        const bIncreasing = b.trend === "increasing" ? 0 : 1;
        if (aIncreasing !== bIncreasing) return aIncreasing - bIncreasing;
        return b.forecasted_demand - a.forecasted_demand;
      });

      let remaining = budget.value;
      const result = [];
      for (const item of sorted) {
        if (remaining <= 0) break;
        if (item.unit_cost > remaining) continue;
        const qty = Math.min(
          Math.floor(remaining / item.unit_cost),
          item.forecasted_demand,
        );
        if (qty <= 0) continue;
        const itemTotal = Math.round(qty * item.unit_cost * 100) / 100;
        result.push({ ...item, recommended_qty: qty, item_total: itemTotal });
        remaining -= itemTotal;
      }
      return result;
    });

    const totalCost = computed(
      () =>
        Math.round(
          recommendations.value.reduce((sum, r) => sum + r.item_total, 0) * 100,
        ) / 100,
    );

    const remainingBudget = computed(
      () => Math.round((budget.value - totalCost.value) * 100) / 100,
    );

    const trendBadgeClass = (trend) => {
      if (trend === "increasing") return "badge danger";
      if (trend === "stable") return "badge info";
      return "badge";
    };

    const loadData = async () => {
      loading.value = true;
      error.value = null;
      try {
        demandItems.value = await api.getDemandForecasts();
      } catch (err) {
        error.value = "Failed to load demand forecast data";
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const placeOrder = async () => {
      if (recommendations.value.length === 0 || submitting.value) return;
      submitting.value = true;
      successMessage.value = "";
      orderError.value = "";
      try {
        await api.createOrder({
          budget: budget.value,
          items: recommendations.value.map((r) => ({
            sku: r.item_sku,
            name: r.item_name,
            quantity: r.recommended_qty,
            unit_price: r.unit_cost,
          })),
        });
        successMessage.value = t("restocking.orderSuccess");
      } catch (err) {
        orderError.value =
          t("restocking.orderError") + " " + (err.message || err);
      } finally {
        submitting.value = false;
      }
    };

    onMounted(() => loadData());

    return {
      t,
      demandItems,
      loading,
      error,
      budget,
      submitting,
      successMessage,
      orderError,
      recommendations,
      totalCost,
      remainingBudget,
      trendBadgeClass,
      placeOrder,
    };
  },
};
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.25rem;
}

.budget-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-display {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2563eb;
  white-space: nowrap;
}

input[type="range"] {
  flex: 1;
  accent-color: #2563eb;
  cursor: pointer;
  height: 6px;
}

.budget-markers {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.375rem;
}

.place-order-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.625rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success-banner {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.error-banner {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-size: 0.938rem;
}

.stats-grid {
  margin-bottom: 1.25rem;
}
</style>
