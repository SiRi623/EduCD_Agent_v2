<template>
  <div>
    <div class="panel-header">
      <div>
        <h1 class="page-title">学生个体诊断</h1>
        <p class="page-desc">选择学生后发起完整分析，系统会展示知识点掌握度、错因解释和个性化学情报告。</p>
      </div>
      <div class="toolbar">
        <el-select v-model="selectedStudent" placeholder="选择学生" filterable style="width: 180px">
          <el-option v-for="student in students" :key="student" :label="student" :value="student" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="runDiagnosis">开始诊断</el-button>
        <el-button @click="handleClearCache">清除缓存</el-button>
      </div>
    </div>

    <el-alert
      v-if="serviceError"
      class="section"
      :title="serviceErrorTitle"
      :description="serviceError"
      type="error"
      show-icon
      :closable="false"
    />

    <el-card v-if="!analysis" class="section panel" shadow="never">
      <div class="empty-state">请选择学生并点击“开始诊断”</div>
    </el-card>

    <template v-if="analysis">
      <section class="section metric-grid">
        <div class="metric-card">
          <div class="metric-value">{{ analysis.student_id }}</div>
          <div class="metric-label">学生 ID</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ masteryCount }}</div>
          <div class="metric-label">知识点数量</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ weakPoints.length }}</div>
          <div class="metric-label">薄弱知识点数量</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ analysis.wrong_questions.length }}</div>
          <div class="metric-label">错题数量</div>
        </div>
      </section>

      <section class="section two-column">
        <MasteryChart :mastery="analysis.mastery" title="知识点掌握度" />
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-title">薄弱知识点列表</div>
          </template>
          <div v-if="weakPoints.length" class="weak-list">
            <el-tag v-for="item in weakPoints" :key="item.name" type="danger" effect="plain">
              {{ item.name }}：{{ item.score.toFixed(2) }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无薄弱知识点" />
        </el-card>
      </section>

      <section class="section">
        <div class="panel-header">
          <h2 class="panel-title">错因分析</h2>
        </div>
        <div v-if="analysis.error_analysis.length" class="error-list">
          <ErrorAnalysisCard
            v-for="error in analysis.error_analysis"
            :key="`${error.question_id}-${error.error_type}`"
            :error="error"
          />
        </div>
        <el-card v-else shadow="never" class="panel">
          <el-empty description="该学生暂无错题分析" />
        </el-card>
      </section>

      <section class="section">
        <ReportPanel :report="analysis.report" />
      </section>
    </template>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { clearCache, getApiErrorMessage, getFullAnalysis, getStudents } from '../api'
import ErrorAnalysisCard from '../components/ErrorAnalysisCard.vue'
import MasteryChart from '../components/MasteryChart.vue'
import ReportPanel from '../components/ReportPanel.vue'

const students = ref([])
const selectedStudent = ref('S001')
const analysis = ref(null)
const loading = ref(false)
const serviceError = ref('')
const serviceErrorTitle = ref('')

const masteryCount = computed(() => Object.keys(analysis.value?.mastery || {}).length)
const weakPoints = computed(() =>
  Object.entries(analysis.value?.mastery || {})
    .filter(([, score]) => Number(score) < 0.6)
    .map(([name, score]) => ({ name, score: Number(score) })),
)

async function loadStudents() {
  try {
    serviceError.value = ''
    const response = await getStudents()
    if (!response.success) {
      ElMessage.error(response.message || '获取学生列表失败')
      return
    }
    students.value = response.data || []
    if (!students.value.includes(selectedStudent.value)) {
      selectedStudent.value = students.value[0] || ''
    }
  } catch (error) {
    const message = getApiErrorMessage(error)
    serviceErrorTitle.value = message
    serviceError.value = error.message || message
    ElMessage.error(message)
  }
}

async function runDiagnosis() {
  if (!selectedStudent.value) {
    ElMessage.warning('请先选择学生')
    return
  }
  loading.value = true
  serviceError.value = ''
  try {
    const response = await getFullAnalysis(selectedStudent.value)
    if (!response.success) {
      ElMessage.error(response.message || '诊断失败')
      return
    }
    analysis.value = response.data
    ElMessage.success('诊断完成')
  } catch (error) {
    const message = getApiErrorMessage(error)
    serviceErrorTitle.value = message
    serviceError.value = error.message || message
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

async function handleClearCache() {
  try {
    const response = await clearCache()
    if (!response.success) {
      ElMessage.error(response.message || '清除缓存失败')
      return
    }
    ElMessage.success('缓存已清空')
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error))
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.weak-list,
.error-list {
  display: grid;
  gap: 12px;
}

.weak-list {
  grid-template-columns: 1fr;
  align-items: start;
}
</style>
