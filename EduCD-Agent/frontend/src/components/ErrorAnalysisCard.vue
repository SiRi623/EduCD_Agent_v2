<template>
  <el-card class="error-card" shadow="never">
    <template #header>
      <div class="error-header">
        <div>
          <span class="question-id">{{ error.question_id || '未知题号' }}</span>
          <el-tag class="type-tag" size="small" type="warning">{{ error.error_type || 'Unknown' }}</el-tag>
        </div>
        <el-tag size="small" type="success">置信度 {{ confidenceText }}</el-tag>
      </div>
    </template>

    <div class="tag-row">
      <span class="field-label">薄弱知识点</span>
      <el-tag v-for="item in weakKnowledge" :key="item" effect="plain">{{ item }}</el-tag>
    </div>

    <el-descriptions :column="1" border class="analysis-desc">
      <el-descriptions-item label="思维断点">{{ error.thinking_breakpoint || '暂无' }}</el-descriptions-item>
      <el-descriptions-item label="错误原因">{{ error.reason || '暂无' }}</el-descriptions-item>
      <el-descriptions-item label="学习建议">{{ suggestionText }}</el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  error: {
    type: Object,
    required: true,
  },
})

const weakKnowledge = computed(() => {
  const value = props.error.weak_knowledge
  if (Array.isArray(value)) return value.filter(Boolean)
  if (typeof value === 'string' && value.trim()) {
    return value.split(/[,，、;；]/).map((item) => item.trim()).filter(Boolean)
  }
  return ['未知知识点']
})

const confidenceText = computed(() => {
  const value = Number(props.error.confidence ?? 0)
  return Number.isFinite(value) ? value.toFixed(2) : '0.00'
})

const suggestionText = computed(() => {
  const suggestion = props.error.suggestion
  if (Array.isArray(suggestion)) return suggestion.join('；')
  return suggestion || '暂无'
})
</script>

<style scoped>
.error-card {
  border-radius: 8px;
  border-color: #e3ecf7;
}

.error-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.question-id {
  font-weight: 760;
  color: #173454;
  margin-right: 8px;
}

.type-tag {
  vertical-align: middle;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.field-label {
  color: #64758b;
  font-size: 13px;
}

.analysis-desc {
  --el-descriptions-table-border: 1px solid #e7eef7;
}
</style>
