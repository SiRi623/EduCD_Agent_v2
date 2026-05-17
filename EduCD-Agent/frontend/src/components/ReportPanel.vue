<template>
  <el-card class="report-panel" shadow="never">
    <template #header>
      <div class="report-title">个性化学情报告</div>
    </template>
    <div v-if="report" class="report-content">{{ report }}</div>
    <div v-else class="empty-state">暂无报告</div>
  </el-card>
</template>

<script setup>
defineProps({
  report: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.report-panel {
  border-radius: 8px;
  border-color: #e3ecf7;
}

.report-title {
  font-size: 18px;
  font-weight: 700;
  color: #132948;
}

.report-content {
  white-space: pre-wrap;
  line-height: 1.9;
  color: #253a54;
  font-size: 15px;
}
</style>
