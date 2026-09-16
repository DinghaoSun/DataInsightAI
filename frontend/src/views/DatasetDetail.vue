<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()

const dataset = ref(null)
const analysis = ref(null)

const loading = ref(true)
const error = ref('')

const fetchDataset = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await api.get(
      `/api/data/datasets/${route.params.id}`
    )

    dataset.value = response.data

    try {
      const analysisResponse = await api.get(
        `/api/data/datasets/${route.params.id}/analysis`
      )

      analysis.value = analysisResponse.data
    } catch (err) {
      console.warn('该数据集暂无分析结果：', err)
      analysis.value = null
    }
  } catch (err) {
    console.error('获取数据集详情失败：', err)

    if (err.response?.status === 404) {
      error.value = '数据集不存在。'
    } else {
      error.value =
        '获取数据集详情失败，请检查后端服务是否正常运行。'
    }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/datasets')
}

/* =========================
   数据分析数据
========================= */

const qualityScore = computed(() => {
  const score = analysis.value?.analysis?.quality_score

  if (score === undefined || score === null) {
    return '--'
  }

  return Number(score).toFixed(0)
})

const analysisSummary = computed(() => {
  return analysis.value?.analysis?.summary || ''
})

const missingValues = computed(() => {
  return analysis.value?.analysis?.missing_values || {}
})

const uniqueValues = computed(() => {
  return analysis.value?.analysis?.unique_counts || {}
})

const numericSummary = computed(() => {
  return analysis.value?.analysis?.numeric_summary || {}
})

const ruleSummary = computed(() => {
  return analysis.value?.insights?.summary || ''
})

const warnings = computed(() => {
  return analysis.value?.insights?.warnings || []
})

const recommendations = computed(() => {
  return analysis.value?.insights?.recommendations || []
})

const columns = computed(() => {
  return analysis.value?.analysis?.columns || []
})

const dtypes = computed(() => {
  return analysis.value?.analysis?.dtypes || {}
})

/* =========================
   AI 洞察 Markdown 格式处理
========================= */

const formattedAiInsight = computed(() => {
  if (!analysis.value?.ai_insight) {
    return []
  }

  return analysis.value.ai_insight
    .split('\n')
    .map(line => line.trim())
    .filter(line => line !== '')
})

const getAiLineClass = (line) => {
  const trimmed = line.trim()

  if (/^#{1,6}\s/.test(trimmed)) {
    return 'ai-line-title'
  }

  if (/^\d+\.\s/.test(trimmed)) {
    return 'ai-line-number'
  }

  if (/^[-*]\s/.test(trimmed)) {
    return 'ai-line-item'
  }

  return 'ai-line-text'
}

const cleanAiLine = (line) => {
  return line
    .replace(/^#{1,6}\s*/, '')
    .replace(/\*\*/g, '')
    .replace(/^[-*]\s*/, '')
    .replace(/^\d+\.\s*/, '')
}

onMounted(fetchDataset)
</script>

<template>
  <div class="detail-page">

    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <div class="breadcrumb">
          工作台 / 数据集 / 详情
        </div>

        <h1>数据集详情</h1>

        <p>
          查看数据集信息、数据质量与智能分析结果。
        </p>
      </div>

      <button
        class="back-button"
        @click="goBack"
      >
        ← 返回数据集
      </button>
    </header>

    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="state-card"
    >
      正在加载数据集详情...
    </div>

    <!-- 错误状态 -->
    <div
      v-else-if="error"
      class="state-card error"
    >
      {{ error }}
    </div>

    <!-- 页面主体 -->
    <div
      v-else-if="dataset"
      class="content"
    >

      <!-- 数据集基本信息 -->
      <section class="hero-card">

        <div class="file-icon">
          CSV
        </div>

        <div class="file-info">

          <div class="file-name">
            {{ dataset.filename }}
          </div>

          <div class="file-meta">
            <span>
              数据集 ID：{{ dataset.id }}
            </span>

            <span>·</span>

            <span>
              上传于 {{ dataset.uploaded_at }}
            </span>
          </div>

        </div>

        <div class="status">
          <span class="status-dot"></span>
          分析完成
        </div>

      </section>

      <!-- 核心指标 -->
      <section class="stats-grid">

        <!-- 数据量 -->
        <div class="stat-card">

          <div class="stat-top">
            <div class="stat-icon purple">
              ≋
            </div>

            <span class="stat-label">
              数据量
            </span>
          </div>

          <div class="stat-value">
            {{ dataset.row_count }}
          </div>

          <div class="stat-desc">
            条数据记录
          </div>

        </div>

        <!-- 字段数 -->
        <div class="stat-card">

          <div class="stat-top">
            <div class="stat-icon blue">
              ▦
            </div>

            <span class="stat-label">
              字段数
            </span>
          </div>

          <div class="stat-value">
            {{ dataset.column_count }}
          </div>

          <div class="stat-desc">
            个数据字段
          </div>

        </div>

        <!-- 数据质量 -->
        <div class="stat-card">

          <div class="stat-top">
            <div class="stat-icon green">
              ✓
            </div>

            <span class="stat-label">
              数据质量
            </span>
          </div>

          <div class="stat-value">
            {{ qualityScore }}

            <span
              v-if="qualityScore !== '--'"
              class="percent"
            >
              %
            </span>
          </div>

          <div class="stat-desc">
            综合数据质量评分
          </div>

        </div>

        <!-- 分析状态 -->
        <div class="stat-card">

          <div class="stat-top">
            <div class="stat-icon orange">
              ✦
            </div>

            <span class="stat-label">
              分析状态
            </span>
          </div>

          <div class="stat-value status-value">
            已完成
          </div>

          <div class="stat-desc">
            AI 分析结果可用
          </div>

        </div>

      </section>

      <!-- 数据概览 -->
      <section
        v-if="analysis"
        class="overview-grid"
      >

        <!-- 数据质量 -->
        <div class="panel quality-panel">

          <div class="panel-header">
            <div>
              <h2>数据质量</h2>

              <p>
                当前数据集的数据质量概览
              </p>
            </div>
          </div>

          <div class="quality-content">

            <div class="quality-score">

              <div class="score-number">
                {{ qualityScore }}

                <span>
                  %
                </span>
              </div>

              <div class="score-label">
                数据质量评分
              </div>

            </div>

            <div class="quality-info">

              <div class="quality-item">
                <span>
                  数据记录
                </span>

                <strong>
                  {{ dataset.row_count }}
                </strong>
              </div>

              <div class="quality-item">
                <span>
                  字段数量
                </span>

                <strong>
                  {{ dataset.column_count }}
                </strong>
              </div>

              <div class="quality-item">
                <span>
                  缺失字段
                </span>

                <strong>
                  {{ Object.keys(missingValues).length }}
                </strong>
              </div>

            </div>

          </div>

          <div class="quality-bar">
            <div
              class="quality-progress"
              :style="{
                width: `${qualityScore === '--' ? 0 : qualityScore}%`
              }"
            ></div>
          </div>

        </div>

        <!-- 分析摘要 -->
        <div class="panel">

          <div class="panel-header">
            <div>
              <h2>分析摘要</h2>

              <p>
                系统对当前数据集的初步分析
              </p>
            </div>
          </div>

          <div class="summary-content">
            {{ analysisSummary || '暂无分析摘要。' }}
          </div>

        </div>

      </section>

      <!-- 字段概览 -->
      <section
        v-if="analysis && columns.length"
        class="panel"
      >

        <div class="panel-header">

          <div>
            <h2>字段概览</h2>

            <p>
              当前数据集包含
              {{ columns.length }}
              个字段
            </p>
          </div>

        </div>

        <div class="column-list">

          <div
            v-for="column in columns"
            :key="column"
            class="column-item"
          >

            <div class="column-name">
              {{ column }}
            </div>

            <div class="column-type">
              {{ dtypes[column] || 'unknown' }}
            </div>

            <div class="column-missing">
              缺失值：
              {{ missingValues[column] ?? 0 }}
            </div>

            <div class="column-unique">
              唯一值：
              {{ uniqueValues[column] ?? '--' }}
            </div>

          </div>

        </div>

      </section>

      <!-- 数值统计 -->
      <section
        v-if="Object.keys(numericSummary).length"
        class="panel"
      >

        <div class="panel-header">

          <div>
            <h2>数值统计</h2>

            <p>
              数值字段的统计分析结果
            </p>
          </div>

        </div>

        <div class="numeric-grid">

          <div
            v-for="(stats, column) in numericSummary"
            :key="column"
            class="numeric-card"
          >

            <div class="numeric-name">
              {{ column }}
            </div>

            <div class="numeric-main">

              <span>
                平均值
              </span>

              <strong>
                {{ Number(stats.mean).toFixed(2) }}
              </strong>

            </div>

            <div class="numeric-row">
              <span>最大值</span>

              <strong>
                {{ stats.max }}
              </strong>
            </div>

            <div class="numeric-row">
              <span>最小值</span>

              <strong>
                {{ stats.min }}
              </strong>
            </div>

            <div class="numeric-row">
              <span>总和</span>

              <strong>
                {{ stats.sum }}
              </strong>
            </div>

            <div class="numeric-row">
              <span>标准差</span>

              <strong>
                {{ Number(stats.std).toFixed(2) }}
              </strong>
            </div>

          </div>

        </div>

      </section>

      <!-- 智能洞察 -->
      <section
        v-if="analysis"
        class="panel insight-panel"
      >

        <div class="panel-header">

          <div>
            <h2>智能数据洞察</h2>

            <p>
              基于规则分析对数据集进行质量诊断。
            </p>
          </div>

          <div class="insight-badge">
            ✦ Smart Insight
          </div>

        </div>

        <!-- 规则分析摘要 -->
        <div
          v-if="ruleSummary"
          class="rule-summary"
        >
          {{ ruleSummary }}
        </div>

        <!-- 问题 -->
        <div
          v-if="warnings.length"
          class="insight-block warning-block"
        >

          <div class="insight-block-title">

            <span class="block-icon">
              !
            </span>

            发现的问题

          </div>

          <div
            v-for="(warning, index) in warnings"
            :key="index"
            class="insight-item"
          >
            {{ warning }}
          </div>

        </div>

        <!-- 建议 -->
        <div
          v-if="recommendations.length"
          class="insight-block recommendation-block"
        >

          <div class="insight-block-title">

            <span class="block-icon">
              ✓
            </span>

            优化建议

          </div>

          <div
            v-for="(recommendation, index) in recommendations"
            :key="index"
            class="insight-item"
          >
            {{ recommendation }}
          </div>

        </div>

      </section>

      <!-- AI 数据洞察 -->
      <section
        v-if="analysis?.ai_insight"
        class="ai-panel"
      >

        <div class="ai-header">

          <div class="ai-icon">
            ✦
          </div>

          <div>

            <h2>
              AI 数据洞察
            </h2>

            <p>
              基于数据分析结果生成的智能分析报告
            </p>

          </div>

          <div class="ai-badge">
            DeepSeek AI
          </div>

        </div>

        <!-- AI 正文 -->
        <div class="ai-content">

          <div
            v-for="(line, index) in formattedAiInsight"
            :key="index"
            :class="getAiLineClass(line)"
          >
            {{ cleanAiLine(line) }}
          </div>

        </div>

      </section>

      <!-- 没有分析结果 -->
      <section
        v-else
        class="panel empty-analysis"
      >

        <div class="empty-icon">
          ✦
        </div>

        <h3>
          暂无分析结果
        </h3>

        <p>
          当前数据集还没有生成分析结果。
        </p>

        <button class="primary-button">
          开始分析
        </button>

      </section>

    </div>

  </div>
</template>

<style scoped>
.detail-page {
  min-height: 100vh;
  padding: 34px 42px 60px;
  background: #f5f7fb;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 26px;
}

.breadcrumb {
  margin-bottom: 9px;
  color: #8a94a8;
  font-size: 13px;
}

h1 {
  margin: 0;
  color: #172033;
  font-size: 29px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.page-header p {
  margin: 8px 0 0;
  color: #8a94a8;
  font-size: 13px;
}

.back-button {
  border: 1px solid #e2e6ef;
  border-radius: 10px;
  padding: 10px 17px;
  background: white;
  color: #59657d;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  border-color: #756cf6;
  color: #756cf6;
  transform: translateY(-1px);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-card,
.panel,
.stat-card,
.ai-panel,
.state-card {
  border: 1px solid #e7eaf1;
  background: white;
  box-shadow: 0 7px 24px rgba(31, 41, 67, 0.035);
}

.hero-card {
  display: flex;
  align-items: center;
  padding: 23px 27px;
  border-radius: 16px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-right: 17px;
  border-radius: 13px;
  background: #eaf8f2;
  color: #22ae78;
  font-size: 13px;
  font-weight: 800;
}

.file-info {
  min-width: 0;
}

.file-name {
  color: #182238;
  font-size: 19px;
  font-weight: 700;
}

.file-meta {
  display: flex;
  gap: 7px;
  margin-top: 6px;
  color: #929caf;
  font-size: 12px;
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  color: #20b77a;
  font-size: 13px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2bc58a;
  box-shadow: 0 0 0 4px #e8f8f1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.stat-card {
  padding: 19px 20px;
  border-radius: 14px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-top {
  display: flex;
  align-items: center;
  gap: 9px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  font-size: 16px;
  font-weight: 700;
}

.stat-icon.purple {
  background: #f0efff;
  color: #7168f4;
}

.stat-icon.blue {
  background: #edf5ff;
  color: #528be8;
}

.stat-icon.green {
  background: #eaf8f2;
  color: #22ae78;
}

.stat-icon.orange {
  background: #fff4e9;
  color: #ed9a48;
}

.stat-label {
  color: #8c96a9;
  font-size: 12px;
}

.stat-value {
  margin-top: 14px;
  color: #182238;
  font-size: 27px;
  font-weight: 700;
}

.percent {
  font-size: 15px;
  font-weight: 600;
}

.stat-value.status-value {
  color: #20b77a;
  font-size: 20px;
}

.stat-desc {
  margin-top: 5px;
  color: #a1a9b7;
  font-size: 11px;
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.panel {
  padding: 23px 25px;
  border-radius: 15px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-header h2 {
  margin: 0;
  color: #202a40;
  font-size: 17px;
}

.panel-header p {
  margin: 5px 0 0;
  color: #929bad;
  font-size: 11px;
}

.quality-content {
  display: flex;
  align-items: center;
  gap: 38px;
  margin-top: 24px;
}

.quality-score {
  min-width: 120px;
  text-align: center;
}

.score-number {
  color: #7168f4;
  font-size: 38px;
  font-weight: 750;
}

.score-number span {
  font-size: 18px;
}

.score-label {
  margin-top: 3px;
  color: #929bad;
  font-size: 11px;
}

.quality-info {
  flex: 1;
}

.quality-item {
  display: flex;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid #f0f2f6;
}

.quality-item:last-child {
  border-bottom: none;
}

.quality-item span {
  color: #929bad;
  font-size: 11px;
}

.quality-item strong {
  color: #354055;
  font-size: 12px;
}

.quality-bar {
  height: 7px;
  margin-top: 23px;
  overflow: hidden;
  border-radius: 10px;
  background: #edf0f5;
}

.quality-progress {
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(90deg, #756cf6, #8c85ff);
}

.summary-content {
  min-height: 120px;
  margin-top: 23px;
  padding: 17px;
  border-radius: 10px;
  background: #f7f8fb;
  color: #59657d;
  font-size: 12px;
  line-height: 1.8;
}

.column-list {
  margin-top: 19px;
  overflow: hidden;
  border: 1px solid #edf0f4;
  border-radius: 10px;
}

.column-item {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  align-items: center;
  padding: 13px 15px;
  border-bottom: 1px solid #edf0f4;
}

.column-item:last-child {
  border-bottom: none;
}

.column-name {
  color: #354055;
  font-size: 12px;
  font-weight: 600;
}

.column-type,
.column-missing,
.column-unique {
  color: #929bad;
  font-size: 11px;
}

.numeric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 13px;
  margin-top: 20px;
}

.numeric-card {
  padding: 17px;
  border: 1px solid #edf0f4;
  border-radius: 11px;
  background: #fafbfc;
}

.numeric-name {
  margin-bottom: 14px;
  color: #354055;
  font-size: 13px;
  font-weight: 700;
}

.numeric-main {
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecf1;
}

.numeric-main span,
.numeric-row span {
  color: #929bad;
  font-size: 10px;
}

.numeric-main strong {
  display: block;
  margin-top: 4px;
  color: #7168f4;
  font-size: 20px;
}

.numeric-row {
  display: flex;
  justify-content: space-between;
  padding-top: 9px;
}

.numeric-row strong {
  color: #4b566c;
  font-size: 11px;
}

.insight-panel {
  padding-bottom: 25px;
}

.insight-badge {
  padding: 7px 10px;
  border-radius: 8px;
  background: #f0efff;
  color: #7168f4;
  font-size: 10px;
  font-weight: 700;
}

.rule-summary {
  margin-top: 20px;
  padding: 15px 17px;
  border-radius: 10px;
  background: #f7f8fb;
  color: #59657d;
  font-size: 12px;
  line-height: 1.8;
}

.insight-block {
  margin-top: 16px;
  padding: 15px 17px;
  border-radius: 10px;
}

.warning-block {
  background: #fff8ef;
  border: 1px solid #f8e5ca;
}

.recommendation-block {
  background: #f1fbf6;
  border: 1px solid #d9f1e5;
}

.insight-block-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #3e485d;
  font-size: 12px;
  font-weight: 700;
}

.block-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 19px;
  height: 19px;
  border-radius: 50%;
  background: white;
  font-size: 10px;
}

.insight-item {
  margin-top: 9px;
  padding-left: 27px;
  color: #68738a;
  font-size: 11px;
  line-height: 1.7;
}

/* =========================
   AI 洞察区域
========================= */

.ai-panel {
  padding: 24px 25px;
  border: 1px solid #dfdbff;
  border-radius: 15px;
  background: linear-gradient(
    135deg,
    #faf9ff,
    #ffffff
  );
  box-shadow:
    0 8px 28px rgba(104, 91, 235, 0.07);
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 43px;
  height: 43px;
  border-radius: 11px;
  background: linear-gradient(
    135deg,
    #8178fa,
    #6258e8
  );
  color: white;
  font-size: 20px;
  box-shadow:
    0 6px 14px rgba(105, 94, 232, 0.22);
}

.ai-header h2 {
  margin: 0;
  color: #242d43;
  font-size: 16px;
}

.ai-header p {
  margin: 4px 0 0;
  color: #929bad;
  font-size: 11px;
}

.ai-badge {
  margin-left: auto;
  padding: 7px 11px;
  border-radius: 8px;
  background: #f0efff;
  color: #7168f4;
  font-size: 10px;
  font-weight: 700;
}

.ai-content {
  max-width: 1050px;
  margin: 22px auto 0;
  padding: 28px 34px;
  border: 1px solid #ece9ff;
  border-radius: 12px;
  background: white;
  color: #59657d;
  font-size: 13px;
  line-height: 1.9;
}

/* AI 标题 */
.ai-line-title {
  margin-top: 22px;
  margin-bottom: 10px;
  color: #292f45;
  font-size: 15px;
  font-weight: 700;
}

.ai-line-title:first-child {
  margin-top: 0;
}

/* AI 编号 */
.ai-line-number {
  margin-top: 10px;
  padding-left: 8px;
  color: #4d5870;
  font-weight: 600;
}

/* AI 项目符号 */
.ai-line-item {
  position: relative;
  margin-top: 8px;
  padding-left: 20px;
  color: #68738a;
}

.ai-line-item::before {
  content: '•';
  position: absolute;
  left: 5px;
  color: #756cf6;
  font-weight: 700;
}

/* AI 普通文本 */
.ai-line-text {
  margin-top: 7px;
  color: #68738a;
}

/* 没有分析结果 */
.empty-analysis {
  padding: 55px 20px;
  text-align: center;
}

.empty-icon {
  color: #756cf6;
  font-size: 30px;
}

.empty-analysis h3 {
  margin: 10px 0 0;
  color: #354055;
  font-size: 16px;
}

.empty-analysis p {
  margin: 7px 0 18px;
  color: #929bad;
  font-size: 12px;
}

.primary-button {
  border: none;
  border-radius: 9px;
  padding: 10px 18px;
  background: linear-gradient(
    135deg,
    #756cf6,
    #6258e8
  );
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow:
    0 7px 16px rgba(108, 97, 236, 0.2);
}

.state-card {
  padding: 50px;
  border-radius: 15px;
  color: #7d879b;
  text-align: center;
}

.state-card.error {
  color: #e45d67;
}

/* =========================
   响应式
========================= */

@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .numeric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 650px) {
  .detail-page {
    padding: 24px 18px 40px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .numeric-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .status {
    width: 100%;
    margin-left: 0;
    margin-top: 8px;
  }

  .column-item {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .ai-badge {
    display: none;
  }

  .quality-content {
    flex-direction: column;
    align-items: stretch;
    gap: 18px;
  }

  .ai-content {
    padding: 22px 20px;
  }
}
</style>