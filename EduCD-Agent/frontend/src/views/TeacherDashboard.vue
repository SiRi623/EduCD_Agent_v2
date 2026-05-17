<template>
  <div>
    <div class="panel-header">
      <div>
        <h1 class="page-title">教师看板</h1>
        <p class="page-desc">聚合班级知识点掌握情况，辅助教师发现共性薄弱点与高风险学生。</p>
      </div>
      <el-button type="primary" :loading="loading" @click="loadSummary">刷新数据</el-button>
    </div>

    <el-alert
      v-if="serviceError"
      class="section"
      title="后端服务未连接，请先运行 python app.py"
      :description="serviceError"
      type="error"
      show-icon
      :closable="false"
    />

    <div v-if="loading && !summary" class="section panel loading-panel">
      <el-skeleton :rows="8" animated />
    </div>

    <template v-if="summary">
      <section class="section">
        <ClassSummaryPanel :summary="summary" />
      </section>

      <section class="section">
        <MasteryChart :mastery="summary.class_average_mastery" title="班级平均掌握度" />
      </section>
    </template>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { getClassSummary } from '../api'
import ClassSummaryPanel from '../components/ClassSummaryPanel.vue'
import MasteryChart from '../components/MasteryChart.vue'

const summary = ref(null)
const loading = ref(false)
const serviceError = ref('')

async function loadSummary() {
  loading.value = true
  serviceError.value = ''
  try {
    const response = await getClassSummary()
    if (!response.success) {
      ElMessage.error(response.message || '获取班级摘要失败')
      return
    }
    summary.value = response.data
  } catch (error) {
    serviceError.value = error.message
    ElMessage.error('后端服务未连接，请先运行 python app.py')
  } finally {
    loading.value = false
  }
}

onMounted(loadSummary)
</script>

<style scoped>
.loading-panel {
  padding: 24px;
}
</style>
