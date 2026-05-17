<template>
  <div class="class-summary">
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-value">{{ knowledgeCount }}</div>
        <div class="metric-label">班级知识点数量</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ weakCount }}</div>
        <div class="metric-label">薄弱知识点 Top3 数量</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ riskCount }}</div>
        <div class="metric-label">高风险学生数量</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ lowestScore }}</div>
        <div class="metric-label">最低平均掌握度</div>
      </div>
    </div>

    <el-card class="section" shadow="never">
      <template #header>
        <div class="panel-title">薄弱知识点 Top3</div>
      </template>
      <el-table :data="weakRows" stripe>
        <el-table-column prop="rank" label="排名" width="90" />
        <el-table-column prop="knowledge" label="知识点" />
        <el-table-column label="平均掌握度" width="130">
          <template #default="{ row }">{{ Number(row.average_mastery).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section" shadow="never">
      <template #header>
        <div class="panel-title">高风险学生列表</div>
      </template>
      <div v-if="riskCount" class="risk-list">
        <el-tag v-for="student in summary.high_risk_students" :key="student" type="danger" effect="plain">
          {{ student }}
        </el-tag>
      </div>
      <el-empty v-else description="暂无高风险学生" />
    </el-card>

    <el-card class="section" shadow="never">
      <template #header>
        <div class="panel-title">教师教学建议</div>
      </template>
      <p class="teacher-suggestion">
        建议教师优先针对{{ weakNames }}开展分层讲解，并结合典型错因组织专项训练。可将学生按掌握度分组，先补齐基础概念和关键步骤，再安排变式题进行巩固。
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  summary: {
    type: Object,
    default: () => ({}),
  },
})

const averageMastery = computed(() => props.summary.class_average_mastery || {})
const weakTop3 = computed(() => props.summary.weak_knowledge_top3 || [])
const knowledgeCount = computed(() => Object.keys(averageMastery.value).length)
const weakCount = computed(() => weakTop3.value.length)
const riskCount = computed(() => (props.summary.high_risk_students || []).length)
const weakRows = computed(() =>
  weakTop3.value.map((item, index) => ({
    rank: index + 1,
    knowledge: item.knowledge,
    average_mastery: item.average_mastery,
  })),
)
const lowestScore = computed(() => {
  const values = Object.values(averageMastery.value)
  if (!values.length) return '0.00'
  return Math.min(...values.map(Number)).toFixed(2)
})
const weakNames = computed(() => {
  const names = weakTop3.value.map((item) => `「${item.knowledge}」`)
  return names.length ? names.join('、') : '班级薄弱知识点'
})
</script>

<style scoped>
.class-summary :deep(.el-card) {
  border-radius: 8px;
  border-color: #e3ecf7;
}

.risk-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.teacher-suggestion {
  margin: 0;
  color: #2d425c;
  line-height: 1.9;
}
</style>
