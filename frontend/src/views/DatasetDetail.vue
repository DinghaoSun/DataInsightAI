<template>

  <div class="detail-page">

    <!-- 顶部 -->

    <header class="page-header">

      <div class="breadcrumb">

        <span>工作台</span>

        <span>/</span>

        <span>数据集</span>

        <span>/</span>

        <span class="current">

          {{ dataset?.filename || '详情' }}

        </span>

      </div>

      <div class="header-main">

        <div>

          <h1>数据集详情</h1>

          <p>查看当前数据集的详细分析结果与数据质量信息</p>

        </div>

        <button class="back-button" @click="goBack">

          ← 返回数据集

        </button>

      </div>

    </header>

    <!-- 加载 -->

    <div v-if="loading" class="state-card">

      <div class="state-icon loading">⟳</div>

      <div>

        <h3>正在加载数据集</h3>

        <p>正在获取数据分析结果，请稍候...</p>

      </div>

    </div>

    <!-- 错误 -->

    <div v-else-if="error" class="state-card error-state">

      <div class="state-icon">!</div>

      <div>

        <h3>{{ error }}</h3>

        <p>请检查后端服务是否正常运行。</p>

      </div>

    </div>

    <!-- 内容 -->

    <main v-else-if="dataset" class="content">

      <!-- 数据集信息 -->

      <section class="hero-card">

        <div class="file-info">

          <div class="file-icon">

            📄

          </div>

          <div class="file-text">

            <h2>{{ dataset.filename }}</h2>

            <div class="file-meta">

              <span>CSV 数据集</span>

              <span>·</span>

              <span>ID {{ dataset.id }}</span>

              <span>·</span>

              <span>{{ formatDate(dataset.uploaded_at) }}</span>

            </div>

          </div>

        </div>

        <div

          class="analysis-status"

          :class="dataset.status"

        >

          <span class="status-dot"></span>

          {{ getStatusText(dataset.status) }}

        </div>

      </section>

      <!-- 核心数据 -->

      <section class="stats-grid">

        <!-- 数据量 -->

        <div class="stat-card">

          <div class="stat-icon blue">≋</div>

          <div class="stat-label">

            数据量

          </div>

          <div class="stat-value">

            {{ dataset.row_count ?? '--' }}

          </div>

          <div class="stat-desc">

            条数据记录

          </div>

          <div class="stat-decoration"></div>

        </div>

        <!-- 字段数 -->

        <div class="stat-card">

          <div class="stat-icon purple">▦</div>

          <div class="stat-label">

            字段数

          </div>

          <div class="stat-value">

            {{ dataset.column_count ?? '--' }}

          </div>

          <div class="stat-desc">

            个数据字段

          </div>

          <div class="stat-decoration"></div>

        </div>

        <!-- 数据质量 -->

        <div class="stat-card">

          <div class="stat-icon green">✓</div>

          <div class="stat-label">

            数据质量

          </div>

          <div class="stat-value quality-value">

            {{ qualityScore }}

            <small v-if="qualityScore !== '--'">

              %

            </small>

          </div>

          <div class="stat-desc">

            综合数据质量评分

          </div>

          <div class="stat-decoration"></div>

        </div>

        <!-- 分析状态 -->

        <div class="stat-card">

          <div class="stat-icon orange">✦</div>

          <div class="stat-label">

            分析状态

          </div>

          <div

            class="status-value"

            :class="dataset.status"

          >

            {{ getStatusText(dataset.status) }}

          </div>

          <div class="stat-desc">

            {{ getStatusDescription(dataset.status) }}

          </div>

          <div class="stat-decoration"></div>

        </div>

      </section>

      <template v-if="dataset.status === 'completed' && analysis">

      <!-- 数据质量 + 分析摘要 -->

      <section class="two-column-grid">

        <!-- 数据质量 -->

        <div class="panel-card">

          <div class="panel-header">

            <div>

              <div class="panel-eyebrow">

                QUALITY

              </div>

              <h2>数据质量</h2>

              <p>

                当前数据集的数据质量概览

              </p>

            </div>

            <div class="panel-icon green-icon">

              ✓

            </div>

          </div>

          <div class="quality-content">

            <div class="quality-circle">

              <div

                class="circle-progress"

                :style="{

                  '--progress': `${qualityScore === '--' ? 0 : qualityScore}%`

                }"

              >

                <div class="circle-inner">

                  <strong>

                    {{ qualityScore }}

                  </strong>

                  <span v-if="qualityScore !== '--'">

                    %

                  </span>

                </div>

              </div>

              <div class="circle-label">

                数据质量评分

              </div>

            </div>

            <div class="quality-details">

              <div class="quality-row">

                <span>数据记录</span>

                <strong>

                  {{ dataset.row_count ?? '--' }}

                </strong>

              </div>

              <div class="quality-row">

                <span>字段数量</span>

                <strong>

                  {{ dataset.column_count ?? '--' }}

                </strong>

              </div>

              <div class="quality-row">

                <span>缺失字段</span>

                <strong>

                  {{ missingFieldCount }}

                </strong>

              </div>

            </div>

          </div>

          <div class="quality-progress">

            <div

              class="quality-progress-inner"

              :style="{

                width: `${qualityScore === '--' ? 0 : qualityScore}%`

              }"

            ></div>

          </div>

        </div>

        <!-- 分析摘要 -->

        <div class="panel-card">

          <div class="panel-header">

            <div>

              <div class="panel-eyebrow">

                SUMMARY

              </div>

              <h2>分析摘要</h2>

              <p>

                当前数据集的整体分析概览

              </p>

            </div>

            <div class="panel-icon purple-icon">

              ≋

            </div>

          </div>

          <div class="summary-content">

            <div class="summary-highlight">

              <span class="summary-highlight-icon">

                ✦

              </span>

              <span>

                数据集概览

              </span>

            </div>

            <p>

              {{ analysisSummary }}

            </p>

            <div class="summary-tags">

              <span>

                {{ dataset?.row_count ?? '--' }} 条记录

              </span>

              <span>

                {{ dataset?.column_count ?? '--' }} 个字段

              </span>

              <span v-if="qualityScore !== '--'">

                质量 {{ qualityScore }}%

              </span>

              <span v-if="missingFieldCount > 0">

                {{ missingFieldCount }} 个字段有缺失

              </span>

            </div>

          </div>

        </div>

      </section>

      <!-- 缺失值图表 -->

      <section class="panel-card">

        <div class="panel-header">

          <div>

            <div class="panel-eyebrow">

              DATA QUALITY

            </div>

            <h2>字段缺失值统计</h2>

            <p>

              查看当前数据集中各字段的缺失数据情况

            </p>

          </div>

          <div class="panel-icon blue-icon">

            #

          </div>

        </div>

        <div class="chart-wrapper">

          <div

            ref="missingChartRef"

            class="missing-chart"

          ></div>

          <div

            v-if="!hasMissingData"

            class="chart-empty"

          >

            暂无缺失值统计数据

          </div>

        </div>

      </section>

      <!-- 字段概览 -->

      <section

        v-if="columns.length"

        class="panel-card"

      >

        <div class="panel-header">

          <div>

            <div class="panel-eyebrow">

              FIELDS

            </div>

            <h2>字段概览</h2>

            <p>

              当前数据集包含的字段及数据类型

            </p>

          </div>

          <div class="panel-icon blue-icon">

            #

          </div>

        </div>

        <div class="field-table-wrapper">

          <table class="field-table">

            <thead>

              <tr>

                <th>#</th>

                <th>字段名称</th>

                <th>数据类型</th>

                <th>缺失值</th>

                <th>唯一值</th>

              </tr>

            </thead>

            <tbody>

              <tr

                v-for="(column, index) in columns"

                :key="column"

              >

                <td class="index-cell">

                  {{ index + 1 }}

                </td>

                <td class="column-name">

                  {{ column }}

                </td>

                <td>

                  <span class="type-tag">

                    {{ dtypes[column] || '--' }}

                  </span>

                </td>

                <td>

                  <span

                    :class="[

                      'missing-value',

                      {

                        danger:

                          Number(missingValues[column] || 0) > 0

                      }

                    ]"

                  >

                    {{ missingValues[column] ?? 0 }}

                  </span>

                </td>

                <td>

                  {{ uniqueValues[column] ?? '--' }}

                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </section>

      <!-- 数值统计 -->

      <section

        v-if="Object.keys(numericSummary).length"

        class="panel-card"

      >

        <div class="panel-header">

          <div>

            <div class="panel-eyebrow">

              STATISTICS

            </div>

            <h2>数值统计</h2>

            <p>

              数值字段的统计分析结果

            </p>

          </div>

          <div class="panel-icon blue-icon">

            #

          </div>

        </div>

        <div class="numeric-grid">

          <div

            v-for="(stats, column) in numericSummary"

            :key="column"

            class="numeric-card"

          >

            <div class="numeric-card-header">

              <strong>

                {{ column }}

              </strong>

              <span class="numeric-tag">

                NUMERIC

              </span>

            </div>

            <div class="average-label">

              平均值

            </div>

            <div class="average-value">

              {{ formatNumber(stats.mean) }}

            </div>

            <div class="numeric-divider"></div>

            <div class="numeric-row">

              <span>最大值</span>

              <strong>

                {{ formatNumber(stats.max) }}

              </strong>

            </div>

            <div class="numeric-row">

              <span>最小值</span>

              <strong>

                {{ formatNumber(stats.min) }}

              </strong>

            </div>

            <div class="numeric-row">

              <span>总和</span>

              <strong>

                {{ formatNumber(stats.sum) }}

              </strong>

            </div>

            <div class="numeric-row">

              <span>标准差</span>

              <strong>

                {{ formatNumber(stats.std) }}

              </strong>

            </div>

          </div>

        </div>

      </section>

      <!-- 数值字段均值对比图 -->

      <section
        v-if="Object.keys(numericSummary).length"
        class="panel-card"
      >
        <div class="panel-header">
          <div>
            <div class="panel-eyebrow">
              VISUAL ANALYSIS
            </div>
            <h2>数值字段均值对比</h2>
            <p>
              基于后端真实 numeric_summary 展示各数值字段的平均值
            </p>
          </div>

          <div class="panel-icon purple-icon">
            ≈
          </div>
        </div>

        <div class="chart-wrapper">
          <div
            ref="numericChartRef"
            class="numeric-chart"
          ></div>
        </div>
      </section>

      <!-- 规则型洞察 -->

      <section

        v-if="ruleSummary || warnings.length || recommendations.length"

        class="panel-card"

      >

        <div class="panel-header">

          <div>

            <div class="panel-eyebrow">

              INSIGHTS

            </div>

            <h2>数据洞察</h2>

            <p>

              基于规则分析生成的数据质量洞察

            </p>

          </div>

          <div class="panel-icon orange-icon">

            ✦

          </div>

        </div>

        <div class="insight-content">

          <div

            v-if="ruleSummary"

            class="insight-summary"

          >

            {{ ruleSummary }}

          </div>

          <div

            v-if="warnings.length"

            class="insight-block warning-block"

          >

            <div class="insight-title">

              <span>⚠</span>

              数据问题

            </div>

            <ul>

              <li

                v-for="(warning, index) in warnings"

                :key="index"

              >

                {{ warning }}

              </li>

            </ul>

          </div>

          <div

            v-if="recommendations.length"

            class="insight-block recommendation-block"

          >

            <div class="insight-title">

              <span>✦</span>

              分析建议

            </div>

            <ul>

              <li

                v-for="(recommendation, index) in recommendations"

                :key="index"

              >

                {{ recommendation }}

              </li>

            </ul>

          </div>

        </div>

      </section>

      <!-- AI 智能洞察 -->

      <section

        v-if="formattedAiInsight.length"

        class="panel-card ai-panel"

      >

        <div class="ai-header">

          <div class="ai-title-area">

            <div class="ai-main-icon">

              ✦

            </div>

            <div>

              <div class="panel-eyebrow">

                AI INSIGHT

              </div>

              <h2>

                AI 智能洞察

              </h2>

              <p>

                基于当前数据集生成的智能分析报告

              </p>

            </div>

          </div>

          <div class="ai-badge">

            AI ANALYSIS

          </div>

        </div>

        <div class="ai-report">

          <div

            v-for="(line, index) in formattedAiInsight"

            :key="index"

            :class="getAiLineClass(line)"

          >

            <!-- AI 标题 -->

            <template

              v-if="getAiLineClass(line) === 'ai-line-title'"

            >

              <div class="ai-section-title">

                <span class="ai-section-icon">

                  ✦

                </span>

                <span>

                  {{ cleanAiLine(line) }}

                </span>

              </div>

            </template>

            <!-- AI 数字列表 -->

            <template

              v-else-if="getAiLineClass(line) === 'ai-line-number'"

            >

              <div class="ai-number-item">

                <div class="ai-number">

                  {{ extractNumber(line) }}

                </div>

                <div class="ai-number-content">

                  {{ cleanAiLine(line) }}

                </div>

              </div>

            </template>

            <!-- AI 普通列表 -->

            <template

              v-else-if="getAiLineClass(line) === 'ai-line-item'"

            >

              <div class="ai-bullet-item">

                <span class="ai-bullet">

                  •

                </span>

                <span>

                  {{ cleanAiLine(line) }}

                </span>

              </div>

            </template>

            <!-- AI 普通文本 -->

            <template v-else>

              <p class="ai-paragraph">

                {{ cleanAiLine(line) }}

              </p>

            </template>

          </div>

        </div>

        <div class="ai-footer">

          <span>✦</span>

          AI 分析结果仅供数据分析参考

        </div>

      </section>

      </template>

      <!-- 没有分析结果 -->

      <section

        v-if="dataset.status === 'pending'"

        class="panel-card empty-analysis"

      >

        <div class="empty-analysis-icon">

          ✦

        </div>

        <h3>

          正在分析

        </h3>

        <p>

          当前数据集正在生成分析结果，请稍后刷新状态。

        </p>

        <button

          class="state-action-button"

          @click="fetchDataset"

        >

          刷新状态

        </button>

      </section>

      <section

        v-else-if="dataset.status === 'failed'"

        class="panel-card empty-analysis failed-analysis"

      >

        <div class="empty-analysis-icon">!</div>

        <h3>分析失败</h3>

        <p>
          {{ dataset.error_message || '数据分析失败，请重新上传文件。' }}
        </p>

        <button
          class="state-action-button failed-button"
          @click="goToUpload"
        >
          重新上传
        </button>

      </section>

      <section

        v-else-if="dataset.status === 'completed' && analysisError"

        class="panel-card empty-analysis failed-analysis"

      >

        <div class="empty-analysis-icon">!</div>

        <h3>分析记录异常，请重新上传数据</h3>

        <p>数据集状态已完成，但没有找到对应的分析记录。</p>

        <button
          class="state-action-button failed-button"
          @click="goToUpload"
        >
          重新上传
        </button>

      </section>

    </main>

  </div>

</template>

<script setup>

import {

  computed,

  nextTick,

  onBeforeUnmount,

  onMounted,

  ref,

  watch,

} from 'vue'

import { useRoute, useRouter } from 'vue-router'

import * as echarts from 'echarts'

import api from '../services/api'

const route = useRoute()

const router = useRouter()

const dataset = ref(null)

const analysis = ref(null)

const loading = ref(true)

const error = ref('')

const analysisError = ref(false)

const missingChartRef = ref(null)
const numericChartRef = ref(null)

let missingChart = null
let numericChart = null

/* =========================

   获取数据

========================= */

const fetchDataset = async () => {

  try {

    loading.value = true

    error.value = ''

    analysisError.value = false

    const response = await api.get(

      `/api/data/datasets/${route.params.id}`

    )

    dataset.value = response.data

    analysis.value = null

    if (dataset.value.status === 'completed') {

      try {

        const analysisResponse = await api.get(

          `/api/data/datasets/${route.params.id}/analysis`

        )

        analysis.value = analysisResponse.data

      } catch (err) {

        console.warn(

          '已完成的数据集缺少分析记录：',

          err

        )

        analysisError.value = true

      }

    }

  } catch (err) {

    console.error(

      '获取数据集详情失败：',

      err

    )

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

/* 返回数据集 */

const goBack = () => {

  router.push('/datasets')

}

const goToUpload = () => {

  router.push('/datasets')

}

const getStatusText = (status) => {

  const statusText = {
    pending: '正在分析',
    completed: '分析完成',
    failed: '分析失败',
  }

  return statusText[status] || '状态未知'

}

const getStatusDescription = (status) => {

  const descriptions = {
    pending: '正在生成分析结果',
    completed: 'AI 分析结果可用',
    failed: '请重新上传数据文件',
  }

  return descriptions[status] || '暂无状态信息'

}

/* =========================

   数据计算

========================= */

const qualityScore = computed(() => {

  const score =

    analysis.value?.analysis?.quality_score

  if (

    score === undefined ||

    score === null

  ) {

    return '--'

  }

  return Number(score).toFixed(0)

})

/*

 * 分析摘要

 *

 * 不再依赖后端必须返回 summary。

 * 根据当前真实数据自动生成。

 */

const analysisSummary = computed(() => {

  const rowCount =

    dataset.value?.row_count ?? '--'

  const columnCount =

    dataset.value?.column_count ?? '--'

  const score =

    analysis.value?.analysis?.quality_score

  const qualityText =

    score !== undefined &&

    score !== null

      ? `当前数据质量评分为 ${Number(score).toFixed(0)}%`

      : '当前数据质量评分暂不可用'

  const missingValuesData =

    analysis.value?.analysis?.missing_values || {}

  const missingCount =

    Object.values(

      missingValuesData

    ).filter(

      value => Number(value || 0) > 0

    ).length

  const numericData =

    analysis.value?.analysis?.numeric_summary || {}

  const numericCount =

    Object.keys(numericData).length

  let text =

    `该数据集共包含 ${rowCount} 条记录、${columnCount} 个字段。${qualityText}。`

  if (missingCount > 0) {

    text +=

      ` 当前检测到 ${missingCount} 个字段存在缺失数据，需要重点关注数据完整性。`

  } else {

    text +=

      ' 当前未检测到字段缺失数据，数据完整性较好。'

  }

  if (numericCount > 0) {

    text +=

      ` 系统已完成 ${numericCount} 个数值字段的统计分析，可进一步结合业务场景进行分析。`

  }

  return text

})

const missingValues = computed(() => {

  return (

    analysis.value?.analysis?.missing_values || {}

  )

})

const uniqueValues = computed(() => {

  return (

    analysis.value?.analysis?.unique_counts || {}

  )

})

const numericSummary = computed(() => {

  return (

    analysis.value?.analysis?.numeric_summary || {}

  )

})

const ruleSummary = computed(() => {

  return (

    analysis.value?.insights?.summary || ''

  )

})

const warnings = computed(() => {

  return (

    analysis.value?.insights?.warnings || []

  )

})

const recommendations = computed(() => {

  return (

    analysis.value?.insights?.recommendations || []

  )

})

const columns = computed(() => {
  const analysisData = analysis.value?.analysis || {}

  if (
    Array.isArray(analysisData.columns) &&
    analysisData.columns.length
  ) {
    return analysisData.columns
  }

  const fieldSet = new Set([
    ...Object.keys(analysisData.dtypes || {}),
    ...Object.keys(analysisData.missing_values || {}),
    ...Object.keys(analysisData.unique_counts || {}),
    ...Object.keys(analysisData.numeric_summary || {}),
  ])

  return Array.from(fieldSet)
})

const dtypes = computed(() => {
  const analysisData = analysis.value?.analysis || {}

  // 优先使用后端返回的真实数据类型。
  const backendTypes =
    analysisData.dtypes ||
    analysisData.data_types ||
    analysisData.types ||
    {}

  const result = { ...backendTypes }

  // 如果当前分析结果没有单独返回 dtypes，
  // 就根据 numeric_summary 判断数值字段，其余字段按文本字段展示。
  // 这样不会再出现所有字段都是 "--" 的情况。
  const numericFields = Object.keys(
    analysisData.numeric_summary || {}
  )

  const allFields = new Set([
    ...Object.keys(analysisData.missing_values || {}),
    ...Object.keys(analysisData.unique_counts || {}),
    ...numericFields,
  ])

  allFields.forEach((field) => {
    if (result[field]) {
      return
    }

    if (numericFields.includes(field)) {
      result[field] = 'number'
    } else {
      result[field] = 'text'
    }
  })

  return result
})

const missingFieldCount = computed(() => {

  return Object.values(

    missingValues.value

  ).filter(

    value => Number(value || 0) > 0

  ).length

})

const hasMissingData = computed(() => {

  return (

    Object.keys(

      missingValues.value

    ).length > 0

  )

})

/* =========================

   AI Markdown

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

const extractNumber = (line) => {
  const match = line.trim().match(/^(\d+)\.\s/)

  return match
    ? match[1].padStart(2, '0')
    : '•'
}

const cleanAiLine = (line) => {
  return line
    .replace(/^#{1,6}\s*/, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/^[-*]\s*/, '')
    .replace(/^\d+\.\s*/, '')
    .replace(/`(.*?)`/g, '$1')
    .trim()
}

/* =========================

   工具函数

========================= */

const formatDate = (value) => {

  if (!value) {

    return '--'

  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {

    return value

  }

  return date.toLocaleString(

    'zh-CN',

    {

      year: 'numeric',

      month: '2-digit',

      day: '2-digit',

      hour: '2-digit',

      minute: '2-digit',

    }

  )

}

const formatNumber = (value) => {

  if (

    value === undefined ||

    value === null

  ) {

    return '--'

  }

  const number = Number(value)

  if (Number.isNaN(number)) {

    return value

  }

  return number.toFixed(2)

}

/* =========================

   ECharts

========================= */

const renderMissingChart = async () => {

  await nextTick()

  if (!missingChartRef.value) {

    return

  }

  if (!hasMissingData.value) {

    return

  }

  if (!missingChart) {

    missingChart = echarts.init(

      missingChartRef.value

    )

  }

  const data = Object.entries(

    missingValues.value

  ).map(([name, value]) => ({

    name,

    value: Number(value || 0),

  }))

  const option = {

    tooltip: {

      trigger: 'axis',

      axisPointer: {

        type: 'shadow',

      },

      formatter: params => {

        const item = params[0]

        return `

          <div style="font-weight:600;margin-bottom:4px;">

            ${item.name}

          </div>

          <div>

            缺失值：${item.value}

          </div>

        `

      },

    },

    grid: {

      left: 45,

      right: 25,

      top: 25,

      bottom: 45,

      containLabel: true,

    },

    xAxis: {

      type: 'category',

      data: data.map(

        item => item.name

      ),

      axisTick: {

        show: false,

      },

      axisLine: {

        lineStyle: {

          color: '#e5e7eb',

        },

      },

      axisLabel: {

        color: '#64748b',

        fontSize: 12,

      },

    },

    yAxis: {

      type: 'value',

      minInterval: 1,

      name: '缺失数量',

      nameTextStyle: {

        color: '#94a3b8',

        fontSize: 12,

      },

      splitLine: {

        lineStyle: {

          color: '#eef0f5',

          type: 'dashed',

        },

      },

      axisLabel: {

        color: '#94a3b8',

        fontSize: 12,

      },

    },

    series: [

      {

        name: '缺失值',

        type: 'bar',

        data: data.map(

          item => item.value

        ),

        barMaxWidth: 46,

        itemStyle: {

          borderRadius: [

            8,

            8,

            2,

            2,

          ],

          color: '#8b5cf6',

        },

      },

    ],

  }

  missingChart.setOption(option)

}

const renderNumericChart = async () => {
  await nextTick()

  if (!numericChartRef.value) {
    return
  }

  const entries = Object.entries(
    numericSummary.value
  )

  if (!entries.length) {
    return
  }

  if (!numericChart) {
    numericChart = echarts.init(
      numericChartRef.value
    )
  }

  const data = entries.map(([name, stats]) => ({
    name,
    value:
      stats?.mean === null ||
      stats?.mean === undefined
        ? 0
        : Number(stats.mean),
  }))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: params => {
        const item = params[0]

        return `
          <div style="font-weight:600;margin-bottom:4px;">
            ${item.name}
          </div>
          <div>
            平均值：${Number(item.value).toFixed(2)}
          </div>
        `
      },
    },

    grid: {
      left: 45,
      right: 25,
      top: 25,
      bottom: 55,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: data.map(
        item => item.name
      ),
      axisTick: {
        show: false,
      },
      axisLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 12,
        interval: 0,
        rotate:
          data.length > 5
            ? 25
            : 0,
      },
    },

    yAxis: {
      type: 'value',
      name: '平均值',
      nameTextStyle: {
        color: '#94a3b8',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: '#eef0f5',
          type: 'dashed',
        },
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12,
      },
    },

    series: [
      {
        name: '平均值',
        type: 'bar',
        data: data.map(
          item => item.value
        ),
        barMaxWidth: 52,
        itemStyle: {
          color: '#8b5cf6',
          borderRadius: [
            6,
            6,
            0,
            0,
          ],
        },
      },
    ],
  }

  numericChart.setOption(option)
}

const handleResize = () => {

  if (missingChart) {

    missingChart.resize()

  }

  if (numericChart) {

    numericChart.resize()

  }

}

watch(

  () =>

    analysis.value?.analysis

      ?.missing_values,

  () => {

    renderMissingChart()

  },

  {

    deep: true,

  }

)

watch(

  () =>

    analysis.value?.analysis

      ?.numeric_summary,

  () => {

    renderNumericChart()

  },

  {

    deep: true,

  }

)

/* =========================

   生命周期

========================= */

onMounted(async () => {

  await fetchDataset()

  await renderMissingChart()
  await renderNumericChart()

  window.addEventListener(

    'resize',

    handleResize

  )

})

onBeforeUnmount(() => {

  window.removeEventListener(

    'resize',

    handleResize

  )

  if (missingChart) {

    missingChart.dispose()

    missingChart = null

  }

  if (numericChart) {

    numericChart.dispose()

    numericChart = null

  }

})

</script>

<style scoped>

.detail-page {

  min-height: 100vh;

  padding: 34px 42px 60px;

  background: #f7f7fb;

  color: #172033;

}

/* =========================

   Header

========================= */

.page-header {

  margin-bottom: 26px;

}

.breadcrumb {

  display: flex;

  align-items: center;

  gap: 9px;

  margin-bottom: 13px;

  font-size: 12px;

  color: #94a3b8;

}

.breadcrumb .current {

  max-width: 320px;

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

  color: #64748b;

}

.header-main {

  display: flex;

  align-items: flex-end;

  justify-content: space-between;

  gap: 20px;

}

.header-main h1 {

  margin: 0;

  font-size: 28px;

  line-height: 1.25;

  color: #172033;

}

.header-main p {

  margin: 9px 0 0;

  color: #94a3b8;

  font-size: 13px;

}

.back-button {

  border: 1px solid #e2e8f0;

  background: #ffffff;

  color: #475569;

  padding: 10px 17px;

  border-radius: 10px;

  font-size: 13px;

  cursor: pointer;

  transition: all 0.2s ease;

}

.back-button:hover {

  color: #7c3aed;

  border-color: #d8c5ff;

  background: #faf7ff;

}

/* =========================

   Content

========================= */

.content {

  display: flex;

  flex-direction: column;

  gap: 18px;

}

/* =========================

   Hero

========================= */

.hero-card {

  background: #ffffff;

  border: 1px solid #e7eaf0;

  border-radius: 16px;

  padding: 22px 24px;

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 20px;

  box-shadow: 0 3px 12px rgba(31, 41, 55, 0.03);

}

.file-info {

  display: flex;

  align-items: center;

  min-width: 0;

}

.file-icon {

  width: 52px;

  height: 52px;

  border-radius: 14px;

  background: #f1eaff;

  display: flex;

  align-items: center;

  justify-content: center;

  font-size: 25px;

  margin-right: 15px;

  flex-shrink: 0;

}

.file-text {

  min-width: 0;

}

.file-text h2 {

  margin: 0;

  font-size: 18px;

  color: #172033;

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

}

.file-meta {

  display: flex;

  flex-wrap: wrap;

  gap: 7px;

  margin-top: 7px;

  color: #94a3b8;

  font-size: 12px;

}

.analysis-status {

  display: flex;

  align-items: center;

  gap: 7px;

  padding: 7px 11px;

  border-radius: 999px;

  background: #ecfdf5;

  color: #16a34a;

  font-size: 12px;

  font-weight: 600;

  flex-shrink: 0;

}

.analysis-status.pending {

  background: #fff7ed;

  color: #ea580c;

}

.analysis-status.failed {

  background: #fef2f2;

  color: #dc2626;

}

.status-dot {

  width: 7px;

  height: 7px;

  border-radius: 50%;

  background: #22c55e;

}

.analysis-status.pending .status-dot {

  background: #f97316;

}

.analysis-status.failed .status-dot {

  background: #ef4444;

}

/* =========================

   Stats

========================= */

.stats-grid {

  display: grid;

  grid-template-columns: repeat(4, minmax(0, 1fr));

  gap: 16px;

}

.stat-card {

  position: relative;

  overflow: hidden;

  min-height: 150px;

  padding: 18px 20px;

  background: #ffffff;

  border: 1px solid #e7eaf0;

  border-radius: 15px;

  box-shadow: 0 3px 12px rgba(31, 41, 55, 0.03);

}

.stat-icon {

  width: 38px;

  height: 38px;

  margin-bottom: 13px;

  border-radius: 11px;

  display: flex;

  align-items: center;

  justify-content: center;

  font-size: 18px;

  font-weight: 600;

}

.stat-icon.blue {

  background: #eef2ff;

  color: #6366f1;

}

.stat-icon.purple {

  background: #f3e8ff;

  color: #8b5cf6;

}

.stat-icon.green {

  background: #ecfdf5;

  color: #10b981;

}

.stat-icon.orange {

  background: #fff7ed;

  color: #f97316;

}

.stat-label {

  color: #64748b;

  font-size: 12px;

  margin-bottom: 6px;

}

.stat-value {

  position: relative;

  z-index: 1;

  font-size: 28px;

  font-weight: 700;

  line-height: 1.15;

  color: #172033;

}

.quality-value {

  color: #7657f6;

}

.quality-value small {

  margin-left: 3px;

  font-size: 14px;

}

.status-value {

  position: relative;

  z-index: 1;

  margin-top: 4px;

  color: #10b981;

  font-size: 19px;

  font-weight: 700;

}

.status-value.pending {

  color: #f97316;

}

.status-value.failed {

  color: #dc2626;

}

.stat-desc {

  position: relative;

  z-index: 1;

  margin-top: 6px;

  color: #a0aec0;

  font-size: 11px;

}

.stat-decoration {

  position: absolute;

  right: -15px;

  bottom: -20px;

  width: 82px;

  height: 82px;

  border-radius: 50%;

  background: #faf9ff;

}

/* =========================

   Panel

========================= */

.panel-card {

  background: #ffffff;

  border: 1px solid #e7eaf0;

  border-radius: 16px;

  padding: 23px 25px;

  box-shadow: 0 3px 12px rgba(31, 41, 55, 0.03);

}

.two-column-grid {

  display: grid;

  grid-template-columns: 1fr 1fr;

  gap: 18px;

}

.panel-header {

  display: flex;

  align-items: flex-start;

  justify-content: space-between;

  gap: 20px;

}

.panel-eyebrow {

  margin-bottom: 5px;

  color: #94a3b8;

  font-size: 9px;

  font-weight: 700;

  letter-spacing: 1.4px;

}

.panel-header h2 {

  margin: 0;

  color: #172033;

  font-size: 19px;

}

.panel-header p {

  margin: 5px 0 0;

  color: #94a3b8;

  font-size: 11px;

}

.panel-icon {

  width: 34px;

  height: 34px;

  border-radius: 10px;

  display: flex;

  align-items: center;

  justify-content: center;

  font-weight: 700;

}

.green-icon {

  background: #ecfdf5;

  color: #10b981;

}

.purple-icon {

  background: #f3e8ff;

  color: #7c3aed;

}

.blue-icon {

  background: #eef2ff;

  color: #6366f1;

}

.orange-icon {

  background: #fff7ed;

  color: #f97316;

}

/* =========================

   Quality

========================= */

.quality-content {

  display: flex;

  align-items: center;

  gap: 38px;

  margin-top: 25px;

}

.quality-circle {

  text-align: center;

  flex-shrink: 0;

}

.circle-progress {

  width: 98px;

  height: 98px;

  border-radius: 50%;

  background:

    conic-gradient(

      #7662f6 var(--progress),

      #eef0f8 var(--progress)

    );

  display: flex;

  align-items: center;

  justify-content: center;

}

.circle-inner {

  width: 78px;

  height: 78px;

  border-radius: 50%;

  background: #ffffff;

  display: flex;

  align-items: baseline;

  justify-content: center;

  gap: 2px;

  padding-top: 25px;

}

.circle-inner strong {

  color: #7657f6;

  font-size: 25px;

}

.circle-inner span {

  color: #7657f6;

  font-size: 11px;

  font-weight: 600;

}

.circle-label {

  margin-top: 8px;

  color: #94a3b8;

  font-size: 10px;

}

.quality-details {

  flex: 1;

}

.quality-row {

  display: flex;

  justify-content: space-between;

  padding: 10px 0;

  border-bottom: 1px solid #f1f5f9;

  color: #64748b;

  font-size: 12px;

}

.quality-row:last-child {

  border-bottom: 0;

}

.quality-row strong {

  color: #172033;

}

.quality-progress {

  height: 7px;

  margin-top: 20px;

  overflow: hidden;

  border-radius: 999px;

  background: #edf0f6;

}

.quality-progress-inner {

  height: 100%;

  border-radius: inherit;

  background: linear-gradient(

    90deg,

    #7561f5,

    #967cff

  );

}

/* =========================

   Summary

========================= */

.summary-content {

  min-height: 160px;

  margin-top: 24px;

  padding: 17px;

  border: 1px solid #edf0f5;

  border-radius: 12px;

  background: #fafbfe;

  color: #64748b;

  font-size: 12px;

  line-height: 1.9;

}

.summary-content p {

  margin: 0;

}

.summary-highlight {

  display: flex;

  align-items: center;

  gap: 7px;

  margin-bottom: 9px;

  color: #5b4aa8;

  font-size: 12px;

  font-weight: 700;

}

.summary-highlight-icon {

  width: 20px;

  height: 20px;

  border-radius: 6px;

  background: #eee8ff;

  color: #7657f6;

  display: inline-flex;

  align-items: center;

  justify-content: center;

  font-size: 10px;

}

.summary-tags {

  display: flex;

  flex-wrap: wrap;

  gap: 7px;

  margin-top: 15px;

}

.summary-tags span {

  padding: 5px 9px;

  border-radius: 7px;

  background: #f1efff;

  color: #7657f6;

  font-size: 10px;

  font-weight: 600;

}

/* =========================

   Chart

========================= */

.chart-wrapper {

  position: relative;

  width: 100%;

  height: 320px;

  margin-top: 15px;

}

.missing-chart {

  width: 100%;

  height: 100%;

}

.numeric-chart {

  width: 100%;

  height: 100%;

}

.chart-empty {

  position: absolute;

  inset: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  color: #94a3b8;

  font-size: 13px;

}

/* =========================

   Fields

========================= */

.field-table-wrapper {

  margin-top: 20px;

  overflow-x: auto;

}

.field-table {

  width: 100%;

  min-width: 620px;

  border-collapse: collapse;

}

.field-table th {

  padding: 11px 13px;

  text-align: left;

  background: #fafbfe;

  color: #94a3b8;

  font-size: 11px;

}

.field-table td {

  padding: 13px;

  border-bottom: 1px solid #f1f5f9;

  color: #64748b;

  font-size: 12px;

}

.index-cell {

  width: 45px;

  color: #cbd5e1 !important;

}

.column-name {

  color: #172033 !important;

  font-weight: 600;

}

.type-tag,

.numeric-tag {

  display: inline-flex;

  padding: 4px 7px;

  border-radius: 5px;

  background: #f1efff;

  color: #7657f6;

  font-size: 9px;

  font-weight: 700;

}

.missing-value {

  color: #64748b;

  font-weight: 600;

}

.missing-value.danger {

  color: #ef4444;

}

/* =========================

   Numeric

========================= */

.numeric-grid {

  display: grid;

  grid-template-columns: repeat(

    auto-fit,

    minmax(280px, 1fr)

  );

  gap: 14px;

  margin-top: 20px;

}

.numeric-card {

  padding: 17px;

  border: 1px solid #e8ebf1;

  border-radius: 12px;

  background: #fbfcfe;

}

.numeric-card-header {

  display: flex;

  justify-content: space-between;

}

.numeric-card-header strong {

  color: #172033;

  font-size: 13px;

}

.average-label {

  margin-top: 20px;

  color: #94a3b8;

  font-size: 10px;

}

.average-value {

  margin-top: 5px;

  color: #7657f6;

  font-size: 21px;

  font-weight: 700;

}

.numeric-divider {

  height: 1px;

  margin: 12px 0 8px;

  background: #e8ebf1;

}

.numeric-row {

  display: flex;

  justify-content: space-between;

  padding: 5px 0;

  color: #94a3b8;

  font-size: 10px;

}

.numeric-row strong {

  color: #334155;

}

/* =========================

   Insights

========================= */

.insight-content {

  margin-top: 20px;

}

.insight-summary {

  padding: 15px 17px;

  border-radius: 10px;

  background: #faf8ff;

  color: #475569;

  font-size: 12px;

  line-height: 1.8;

}

.insight-block {

  margin-top: 14px;

  padding: 15px 17px;

  border-radius: 10px;

  background: #fafbfe;

}

.insight-title {

  display: flex;

  gap: 7px;

  color: #334155;

  font-size: 12px;

  font-weight: 700;

}

.insight-block ul {

  margin: 10px 0 0;

  padding-left: 20px;

}

.insight-block li {

  margin: 6px 0;

  color: #64748b;

  font-size: 11px;

  line-height: 1.7;

}

.warning-block {

  background: #fffaf5;

}

.warning-block .insight-title {

  color: #ea580c;

}

.recommendation-block {

  background: #f8f7ff;

}

.recommendation-block .insight-title {

  color: #7c3aed;

}

/* =========================

   AI Report

========================= */

.ai-panel {

  overflow: hidden;

}

.ai-header {

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 20px;

}

.ai-title-area {

  display: flex;

  align-items: center;

  gap: 13px;

}

.ai-main-icon {

  width: 42px;

  height: 42px;

  border-radius: 13px;

  background: linear-gradient(

    135deg,

    #f0e8ff,

    #e9ddff

  );

  color: #7657f6;

  display: flex;

  align-items: center;

  justify-content: center;

  font-size: 19px;

}

.ai-title-area h2 {

  margin: 0;

  color: #172033;

  font-size: 19px;

}

.ai-title-area p {

  margin: 5px 0 0;

  color: #94a3b8;

  font-size: 11px;

}

.ai-badge {

  padding: 7px 11px;

  border-radius: 8px;

  background: #f1eaff;

  color: #7c3aed;

  font-size: 9px;

  font-weight: 700;

  letter-spacing: 0.4px;

}

.ai-report {

  margin-top: 20px;

  padding: 22px;

  border: 1px solid #eee9ff;

  border-radius: 14px;

  background:

    linear-gradient(

      135deg,

      #fbfaff,

      #f8f6ff

    );

}

.ai-line-title {

  margin-bottom: 14px;

}

.ai-section-title {

  display: flex;

  align-items: center;

  gap: 9px;

  padding-bottom: 11px;

  border-bottom: 1px solid #ebe5ff;

  color: #3f3277;

  font-size: 14px;

  font-weight: 700;

}

.ai-section-icon {

  width: 23px;

  height: 23px;

  border-radius: 7px;

  background: #eee7ff;

  color: #7657f6;

  display: flex;

  align-items: center;

  justify-content: center;

  font-size: 11px;

}

.ai-number-item {

  display: flex;

  align-items: flex-start;

  gap: 11px;

  margin: 11px 0;

  padding: 11px 12px;

  border-radius: 9px;

  background: rgba(255, 255, 255, 0.72);

  border: 1px solid #f0ecfa;

}

.ai-number {

  width: 25px;

  height: 25px;

  border-radius: 7px;

  background: #eee9ff;

  color: #7657f6;

  display: flex;

  align-items: center;

  justify-content: center;

  flex-shrink: 0;

  font-size: 9px;

  font-weight: 700;

}

.ai-number-content {

  color: #475569;

  font-size: 12px;

  line-height: 1.8;

  padding-top: 1px;

}

.ai-bullet-item {

  display: flex;

  align-items: flex-start;

  gap: 9px;

  margin: 9px 0;

  color: #64748b;

  font-size: 12px;

  line-height: 1.8;

}

.ai-bullet {

  color: #7657f6;

  font-size: 17px;

  line-height: 1.2;

}

.ai-paragraph {

  margin: 9px 0;

  color: #64748b;

  font-size: 12px;

  line-height: 1.9;

}

.ai-footer {

  display: flex;

  align-items: center;

  gap: 6px;

  margin-top: 13px;

  color: #a1a1aa;

  font-size: 10px;

}

/* =========================

   State

========================= */

.state-card {

  display: flex;

  align-items: center;

  gap: 16px;

  padding: 28px;

  background: #ffffff;

  border: 1px solid #e7eaf0;

  border-radius: 16px;

}

.state-icon {

  width: 40px;

  height: 40px;

  border-radius: 11px;

  background: #fef2f2;

  color: #ef4444;

  display: flex;

  align-items: center;

  justify-content: center;

  font-size: 20px;

  font-weight: 700;

}

.state-icon.loading {

  background: #f1eaff;

  color: #7657f6;

}

.state-card h3 {

  margin: 0;

  color: #172033;

  font-size: 15px;

}

.state-card p {

  margin: 5px 0 0;

  color: #94a3b8;

  font-size: 12px;

}

/* =========================

   Empty

========================= */

.empty-analysis {

  text-align: center;

  padding: 42px 20px;

}

.empty-analysis-icon {

  width: 48px;

  height: 48px;

  margin: 0 auto 13px;

  border-radius: 14px;

  background: #f3e8ff;

  color: #7c3aed;

  display: flex;

  align-items: center;

  justify-content: center;

}

.empty-analysis h3 {

  margin: 0;

  color: #172033;

  font-size: 16px;

}

.empty-analysis p {

  margin: 7px 0 17px;

  color: #94a3b8;

  font-size: 12px;

}

.state-action-button {

  border: none;

  padding: 9px 15px;

  border-radius: 9px;

  background: #f1eaff;

  color: #7c3aed;

  font-size: 11px;

  cursor: pointer;

}

.failed-analysis .empty-analysis-icon {

  background: #fef2f2;

  color: #dc2626;

}

.failed-button {

  background: #fef2f2;

  color: #dc2626;

}

/* =========================

   Responsive

========================= */

@media (max-width: 1100px) {

  .detail-page {

    padding: 28px 24px 50px;

  }

  .stats-grid {

    grid-template-columns: repeat(2, 1fr);

  }

  .two-column-grid {

    grid-template-columns: 1fr;

  }

}

@media (max-width: 700px) {

  .detail-page {

    padding: 20px 15px 40px;

  }

  .header-main {

    align-items: flex-start;

    flex-direction: column;

  }

  .hero-card {

    align-items: flex-start;

    flex-direction: column;

  }

  .stats-grid {

    grid-template-columns: 1fr;

  }

  .quality-content {

    gap: 20px;

  }

  .panel-card {

    padding: 18px;

  }

  .chart-wrapper {

    height: 270px;

  }

  .ai-header {

    align-items: flex-start;

    flex-direction: column;

  }

}

</style>
