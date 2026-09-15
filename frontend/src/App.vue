<script setup>
import { computed, onMounted, ref } from 'vue'
import api from './services/api'
import { getAnalysisCount } from './services/api'

const activeMenu = ref('dashboard')

const recentDatasets = ref([])
const analysisCount = ref(0)
const qualityScore = ref(0)

const stats = computed(() => [
  {
    title: '数据集',
    value: recentDatasets.value.length,
    description: '已上传数据集',
    icon: '▣',
  },
  {
    title: '数据记录',
    value: recentDatasets.value.reduce(
  (total, dataset) => total + dataset.row_count,
  0
),
    description: '累计分析数据',
    icon: '⌁',
  },
  {
    title: '分析次数',
    value: analysisCount.value,
    description: 'AI 分析已完成',
    icon: '◈',
  },
  {
    title: '数据质量',
  value: `${qualityScore.value}%`,
    description: '整体数据质量',
    icon: '✓',
  },
])



onMounted(async () => {
  try {
    const response = await api.get('/api/data/datasets')

    recentDatasets.value = response.data

    const analysisResponse = await getAnalysisCount()
    analysisCount.value = analysisResponse.data.count

    const qualityResponse = await api.get('/api/data/quality')
    qualityScore.value = qualityResponse.data.quality_score
  } catch (error) {
    console.error('获取数据失败：', error)
  }
})

</script>

<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">D</div>
        <div>
          <div class="brand-name">DataInsightAI</div>
          <div class="brand-subtitle">智能数据分析平台</div>
        </div>
      </div>

      <nav class="nav-menu">
        <div class="nav-section-title">工作台</div>

        <button
          class="nav-item"
          :class="{ active: activeMenu === 'dashboard' }"
          @click="activeMenu = 'dashboard'"
        >
          <span class="nav-icon">⌂</span>
          <span>数据总览</span>
        </button>

        <button
          class="nav-item"
          :class="{ active: activeMenu === 'datasets' }"
          @click="activeMenu = 'datasets'"
        >
          <span class="nav-icon">▣</span>
          <span>数据集</span>
        </button>

        <button
          class="nav-item"
          :class="{ active: activeMenu === 'history' }"
          @click="activeMenu = 'history'"
        >
          <span class="nav-icon">◷</span>
          <span>分析历史</span>
        </button>

        <div class="nav-section-title second">系统</div>

        <button class="nav-item">
          <span class="nav-icon">⚙</span>
          <span>设置</span>
        </button>
      </nav>

      <div class="sidebar-bottom">
        <div class="status-dot"></div>
        <div>
          <div class="system-status">系统运行正常</div>
          <div class="system-version">DataInsightAI v1.0</div>
        </div>
      </div>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div>
          <div class="breadcrumb">工作台 / 数据总览</div>
          <h1>数据分析工作台</h1>
          <p>欢迎回来，开始探索你的数据吧。</p>
        </div>

        <div class="topbar-actions">
          <button class="icon-button">⌕</button>
          <button class="icon-button">♢</button>

          <div class="user-profile">
            <div class="avatar">D</div>
            <div class="user-info">
              <div class="user-name">Data User</div>
              <div class="user-role">分析员</div>
            </div>
          </div>
        </div>
      </header>

      <!-- 核心统计卡片 -->
      <section class="stats-grid">
        <div v-for="stat in stats" :key="stat.title" class="stat-card">
          <div class="stat-top">
            <div class="stat-icon">{{ stat.icon }}</div>
            <span class="stat-trend">+12.5%</span>
          </div>

          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-description">{{ stat.description }}</div>
        </div>
      </section>

      <!-- 上传区域 -->
      <section class="upload-card">
        <div class="upload-content">
          <div class="upload-icon">↑</div>

          <div>
            <h2>开始新的数据分析</h2>
            <p>上传 CSV 文件，让 DataInsightAI 帮你发现数据中的价值。</p>
          </div>
        </div>

        <button class="primary-button">
          <span>＋</span>
          上传数据
        </button>
      </section>

      <!-- 中间区域 -->
      <section class="dashboard-grid">
        <!-- 数据概览 -->
        <div class="panel chart-panel">
          <div class="panel-header">
            <div>
              <h2>数据分析趋势</h2>
              <p>最近 7 天的数据分析情况</p>
            </div>

            <button class="period-button">最近 7 天⌄</button>
          </div>

          <div class="chart">
            <div class="chart-y">
              <span>40</span>
              <span>30</span>
              <span>20</span>
              <span>10</span>
              <span>0</span>
            </div>

            <div class="chart-area">
              <div class="grid-line line-1"></div>
              <div class="grid-line line-2"></div>
              <div class="grid-line line-3"></div>
              <div class="grid-line line-4"></div>

              <div class="fake-chart">
                <div class="bar" style="height: 42%"></div>
                <div class="bar" style="height: 55%"></div>
                <div class="bar" style="height: 48%"></div>
                <div class="bar" style="height: 70%"></div>
                <div class="bar" style="height: 62%"></div>
                <div class="bar" style="height: 82%"></div>
                <div class="bar active-bar" style="height: 92%"></div>
              </div>

              <div class="chart-x">
                <span>09/09</span>
                <span>09/10</span>
                <span>09/11</span>
                <span>09/12</span>
                <span>09/13</span>
                <span>09/14</span>
                <span>09/15</span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI 洞察 -->
        <div class="panel ai-panel">
          <div class="panel-header">
            <div>
              <h2>AI 智能洞察</h2>
              <p>最近一次分析结果</p>
            </div>

            <div class="ai-badge">AI</div>
          </div>

          <div class="ai-content">
            <div class="ai-title">
              <span class="ai-star">✦</span>
              数据分析完成
            </div>

            <p>
              当前数据集整体质量较好，检测到少量缺失值。
              建议重点关注销售金额字段，并进一步分析异常数据。
            </p>

            <div class="insight-list">
              <div class="insight-item">
                <span class="insight-number">01</span>
                <span>数据完整性达到 94%</span>
              </div>

              <div class="insight-item">
                <span class="insight-number">02</span>
                <span>发现 23 条潜在异常记录</span>
              </div>

              <div class="insight-item">
                <span class="insight-number">03</span>
                <span>销售金额呈现增长趋势</span>
              </div>
            </div>
          </div>

          <button class="text-button">
            查看完整 AI 分析 →
          </button>
        </div>
      </section>

      <!-- 最近数据集 -->
      <section class="panel datasets-panel">
        <div class="panel-header">
          <div>
            <h2>最近数据集</h2>
            <p>你最近分析过的数据文件</p>
          </div>

          <button class="text-button">查看全部 →</button>
        </div>

        <div class="dataset-table">
          <div class="table-header">
            <span>数据集名称</span>
            <span>数据量</span>
            <span>字段数</span>
            <span>状态</span>
          </div>

          <div
  v-for="dataset in recentDatasets"
  :key="dataset.id"
  class="table-row"
>
  <span class="dataset-name">
    <span class="file-icon">CSV</span>
    <span>{{ dataset.filename }}</span>
  </span>

  <span>{{ dataset.row_count }}</span>

  <span>{{ dataset.column_count }}</span>

  <span class="status-tag">
    <span class="small-dot"></span>
    <span>分析完成</span>
  </span>
</div>
        </div>
      </section>

      <footer class="footer">
        DataInsightAI · Intelligent Data Analysis Platform
      </footer>
    </main>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  min-height: 100%;
  width: 100%;
}

body {
  font-family:
    Inter,
    "PingFang SC",
    "Microsoft YaHei",
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  background: #f5f7fb;
  color: #172033;
}

button {
  font-family: inherit;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  background: #f5f7fb;
}

/* Sidebar */

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 248px;
  padding: 28px 18px;
  background: #101827;
  color: white;
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 10px 32px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5b5df0, #8b5cf6);
  font-size: 20px;
  font-weight: 800;
  box-shadow: 0 8px 22px rgba(91, 93, 240, 0.35);
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.brand-subtitle {
  margin-top: 4px;
  color: #8994a8;
  font-size: 11px;
}

.nav-menu {
  flex: 1;
}

.nav-section-title {
  padding: 0 12px 10px;
  color: #69758a;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.nav-section-title.second {
  margin-top: 30px;
}

.nav-item {
  width: 100%;
  border: none;
  background: transparent;
  color: #9ba6b8;
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 13px 14px;
  margin-bottom: 5px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: #1a2537;
  color: white;
}

.nav-item.active {
  color: white;
  background: linear-gradient(90deg, #292f54, #222a43);
  box-shadow: inset 3px 0 0 #756cf6;
}

.nav-icon {
  width: 22px;
  text-align: center;
  font-size: 16px;
}

.sidebar-bottom {
  border-top: 1px solid #222c3d;
  padding: 20px 10px 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot,
.small-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #35c98b;
  box-shadow: 0 0 8px rgba(53, 201, 139, 0.6);
}

.system-status {
  font-size: 12px;
  color: #d8deea;
}

.system-version {
  margin-top: 3px;
  font-size: 10px;
  color: #69758a;
}

/* Main */

.main-content {
  margin-left: 248px;
  width: calc(100% - 248px);
  min-height: 100vh;
  padding: 34px 42px;
}

.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 30px;
}

.breadcrumb {
  color: #8b95a7;
  font-size: 12px;
  margin-bottom: 8px;
}

h1 {
  margin: 0;
  font-size: 28px;
  letter-spacing: -0.8px;
}

.topbar p {
  margin: 7px 0 0;
  color: #8b95a7;
  font-size: 13px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-button {
  width: 38px;
  height: 38px;
  border: 1px solid #e5e8ef;
  background: white;
  color: #657087;
  border-radius: 10px;
  cursor: pointer;
  font-size: 17px;
}

.user-profile {
  margin-left: 8px;
  padding-left: 16px;
  border-left: 1px solid #e1e5ec;
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.user-name {
  font-size: 12px;
  font-weight: 700;
}

.user-role {
  margin-top: 2px;
  color: #9099aa;
  font-size: 10px;
}

/* Stats */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.stat-card {
  background: white;
  border: 1px solid #e9ecf2;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 5px 18px rgba(25, 35, 55, 0.035);
}

.stat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #f0efff;
  color: #655eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
}

.stat-trend {
  color: #2caf78;
  background: #eafaf3;
  border-radius: 20px;
  padding: 4px 8px;
  font-size: 10px;
}

.stat-title {
  margin-top: 18px;
  color: #7d8799;
  font-size: 12px;
}

.stat-value {
  margin-top: 4px;
  font-size: 26px;
  font-weight: 750;
  letter-spacing: -0.5px;
}

.stat-description {
  margin-top: 4px;
  color: #a0a8b6;
  font-size: 11px;
}

/* Upload */

.upload-card {
  margin-top: 20px;
  padding: 20px 24px;
  border: 1px dashed #bbb9f6;
  border-radius: 15px;
  background: linear-gradient(100deg, #f7f6ff, #ffffff);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.upload-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: #e9e7ff;
  color: #625bea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23px;
  font-weight: 700;
}

.upload-card h2 {
  margin: 0;
  font-size: 15px;
}

.upload-card p {
  margin: 5px 0 0;
  color: #8b95a7;
  font-size: 12px;
}

.primary-button {
  border: none;
  padding: 11px 17px;
  border-radius: 9px;
  background: #625bea;
  color: white;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  box-shadow: 0 6px 15px rgba(98, 91, 234, 0.25);
  transition: transform 0.2s ease;
}

.primary-button:hover {
  transform: translateY(-1px);
}

/* Panels */

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.55fr 1fr;
  gap: 18px;
  margin-top: 20px;
}

.panel {
  background: white;
  border: 1px solid #e9ecf2;
  border-radius: 15px;
  box-shadow: 0 5px 18px rgba(25, 35, 55, 0.035);
}

.chart-panel,
.ai-panel,
.datasets-panel {
  padding: 22px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.panel-header h2 {
  margin: 0;
  font-size: 15px;
}

.panel-header p {
  margin: 5px 0 0;
  color: #969faf;
  font-size: 11px;
}

.period-button {
  border: 1px solid #e6e9ef;
  background: white;
  color: #687287;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 10px;
}

/* Chart */

.chart {
  height: 245px;
  display: flex;
  margin-top: 20px;
}

.chart-y {
  width: 30px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 25px;
  color: #a3aab7;
  font-size: 9px;
}

.chart-area {
  position: relative;
  flex: 1;
}

.grid-line {
  position: absolute;
  left: 0;
  right: 0;
  border-top: 1px dashed #e9ecf1;
}

.line-1 {
  top: 0;
}

.line-2 {
  top: 25%;
}

.line-3 {
  top: 50%;
}

.line-4 {
  top: 75%;
}

.fake-chart {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 25px;
  top: 10px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: 12px;
}

.bar {
  width: 30px;
  max-width: 12%;
  border-radius: 7px 7px 2px 2px;
  background: #dcd9ff;
  transition: height 0.3s ease;
}

.active-bar {
  background: #6b63ed;
  box-shadow: 0 7px 15px rgba(107, 99, 237, 0.22);
}

.chart-x {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  color: #a3aab7;
  font-size: 8px;
}

/* AI */

.ai-panel {
  display: flex;
  flex-direction: column;
}

.ai-badge {
  padding: 5px 8px;
  border-radius: 7px;
  color: #665eed;
  background: #eeecff;
  font-size: 10px;
  font-weight: 700;
}

.ai-content {
  margin-top: 24px;
  padding: 17px;
  border-radius: 12px;
  background: #f8f7ff;
}

.ai-title {
  font-size: 13px;
  font-weight: 700;
}

.ai-star {
  margin-right: 5px;
  color: #6b63ed;
}

.ai-content > p {
  margin: 10px 0 16px;
  color: #737e91;
  font-size: 11px;
  line-height: 1.8;
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.insight-item {
  display: flex;
  gap: 9px;
  align-items: center;
  font-size: 10px;
  color: #586276;
}

.insight-number {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: white;
  color: #6b63ed;
  font-size: 9px;
  font-weight: 700;
}

.text-button {
  margin-top: auto;
  padding-top: 17px;
  border: none;
  background: transparent;
  color: #625bea;
  font-size: 11px;
  cursor: pointer;
  text-align: left;
}

/* Dataset */

.datasets-panel {
  margin-top: 20px;
}

.dataset-table {
  margin-top: 18px;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr;
  align-items: center;
  padding: 13px 10px;
}

.table-header {
  color: #9ba3b1;
  font-size: 10px;
  border-bottom: 1px solid #edf0f4;
}

.table-row {
  color: #697387;
  font-size: 11px;
  border-bottom: 1px solid #f1f3f6;
}

.table-row:last-child {
  border-bottom: none;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #354055 !important;
  font-weight: 600;
}

.file-icon {
  padding: 5px 6px;
  border-radius: 5px;
  background: #eaf8f1;
  color: #2caf78;
  font-size: 8px;
  font-weight: 800;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2caf78 !important;
  font-weight: 600;
}

.footer {
  padding: 24px 0 8px;
  text-align: center;
  color: #a0a8b6;
  font-size: 9px;
}

/* Responsive */

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 800px) {
  .sidebar {
    width: 70px;
    padding: 20px 10px;
  }

  .brand-name,
  .brand-subtitle,
  .nav-section-title,
  .nav-item span:last-child,
  .system-status,
  .system-version {
    display: none;
  }

  .brand {
    justify-content: center;
    padding: 0 0 30px;
  }

  .nav-item {
    justify-content: center;
  }

  .sidebar-bottom {
    justify-content: center;
  }

  .main-content {
    margin-left: 70px;
    width: calc(100% - 70px);
    padding: 25px 20px;
  }

  .topbar {
    gap: 20px;
  }

  .user-info {
    display: none;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 550px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .upload-card {
    align-items: flex-start;
    flex-direction: column;
    gap: 15px;
  }

  .table-header,
  .table-row {
    grid-template-columns: 2fr 1fr 1fr;
  }

  .table-header span:last-child,
  .table-row span:last-child {
    display: none;
  }
}
</style>