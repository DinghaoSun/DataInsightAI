<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api, { getAnalysisCount } from "../services/api";
import diaNormalHalf from "../assets/dia/dia-normal-half.png";
import diaHeroPointing from "../assets/dia/dia-hero-pointing-transparent.png";

const router = useRouter();
const datasets = ref([]);
const analysisCount = ref(null);
const qualityScore = ref(null);
const loading = ref(true);
const datasetsError = ref("");
const analysisCountError = ref("");
const qualityError = ref("");

const go = (path) => router.push(path);

const formatNumber = (value) => {
  if (value === null || value === undefined) return "--";
  return new Intl.NumberFormat("zh-CN").format(value);
};

const formatDate = (value) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";

  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${month}-${day} ${hours}:${minutes}`;
};

const formatStatus = (status) =>
  ({
    pending: "分析中",
    completed: "分析完成",
    failed: "分析失败",
  })[status] || "状态未知";

const totalRows = computed(() =>
  datasets.value.reduce(
    (total, dataset) => total + (Number(dataset.row_count) || 0),
    0,
  ),
);
const recentDatasets = computed(() => datasets.value.slice(0, 4));

const qualityValue = computed(() => {
  if (qualityError.value) return "--";
  if (analysisCount.value === 0) return "暂无数据";
  if (qualityScore.value === null) return "--";
  return `${formatNumber(qualityScore.value)}%`;
});

const stats = computed(() => [
  {
    title: "数据集总数",
    value: datasetsError.value ? "--" : formatNumber(datasets.value.length),
    description: datasetsError.value ? "加载失败" : "已上传的数据集",
    icon: "▱",
    available: !datasetsError.value,
  },
  {
    title: "数据记录",
    value: datasetsError.value ? "--" : formatNumber(totalRows.value),
    description: datasetsError.value ? "加载失败" : "累计数据行数",
    icon: "▤",
    available: !datasetsError.value,
  },
  {
    title: "分析次数",
    value: analysisCountError.value ? "--" : formatNumber(analysisCount.value),
    description: analysisCountError.value ? "加载失败" : "已保存的分析结果",
    icon: "⌁",
    available: !analysisCountError.value,
  },
  {
    title: "平均数据质量",
    value: qualityValue.value,
    description: qualityError.value
      ? "加载失败"
      : analysisCount.value === 0
        ? "暂无分析结果"
        : "所有分析结果平均值",
    icon: "✓",
    available: !qualityError.value && analysisCount.value !== 0,
  },
]);

const uploadTrend = computed(() => {
  const countsByDay = new Map();

  for (const dataset of datasets.value) {
    const uploadedAt = new Date(dataset.uploaded_at);
    if (Number.isNaN(uploadedAt.getTime())) continue;

    const key = [
      uploadedAt.getFullYear(),
      String(uploadedAt.getMonth() + 1).padStart(2, "0"),
      String(uploadedAt.getDate()).padStart(2, "0"),
    ].join("-");
    countsByDay.set(key, (countsByDay.get(key) || 0) + 1);
  }

  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - (6 - index));
    const key = [
      date.getFullYear(),
      String(date.getMonth() + 1).padStart(2, "0"),
      String(date.getDate()).padStart(2, "0"),
    ].join("-");

    return {
      key,
      label: `${String(date.getMonth() + 1).padStart(2, "0")}/${String(date.getDate()).padStart(2, "0")}`,
      count: countsByDay.get(key) || 0,
    };
  });
});

const hasUploadTrend = computed(() =>
  uploadTrend.value.some((item) => item.count > 0),
);
const trendMax = computed(() =>
  Math.max(...uploadTrend.value.map((item) => item.count), 1),
);
const trendY = (count) => 155 - (count / trendMax.value) * 115;
const trendX = (index) => 35 + index * 70;
const trendPoints = computed(() =>
  uploadTrend.value
    .map((item, index) => `${trendX(index)},${trendY(item.count)}`)
    .join(" "),
);

const loadErrors = computed(() =>
  [datasetsError.value, analysisCountError.value, qualityError.value].filter(
    Boolean,
  ),
);

const diaMessage = computed(() => {
  if (loading.value) return "我正在整理最新的数据，请稍等一下。";
  if (loadErrors.value.length) return "部分数据暂时无法加载，可以稍后重试。";
  if (datasets.value.length === 0)
    return "还没有数据集，上传一份 CSV 开始分析吧。";
  return `目前共有 ${formatNumber(datasets.value.length)} 个数据集，包含 ${formatNumber(totalRows.value)} 条数据记录。`;
});

const loadDashboard = async () => {
  loading.value = true;
  datasetsError.value = "";
  analysisCountError.value = "";
  qualityError.value = "";

  const [datasetsResult, countResult, qualityResult] = await Promise.allSettled(
    [
      api.get("/api/data/datasets"),
      getAnalysisCount(),
      api.get("/api/data/quality"),
    ],
  );

  if (datasetsResult.status === "fulfilled") {
    datasets.value = Array.isArray(datasetsResult.value.data)
      ? datasetsResult.value.data
      : [];
  } else {
    datasets.value = [];
    datasetsError.value = "数据集列表加载失败";
  }

  if (countResult.status === "fulfilled") {
    const count = countResult.value.data?.count;
    analysisCount.value = Number.isFinite(Number(count)) ? Number(count) : null;
  } else {
    analysisCount.value = null;
    analysisCountError.value = "分析次数加载失败";
  }

  if (qualityResult.status === "fulfilled") {
    const score = qualityResult.value.data?.quality_score;
    qualityScore.value = Number.isFinite(Number(score)) ? Number(score) : null;
  } else {
    qualityScore.value = null;
    qualityError.value = "数据质量加载失败";
  }

  loading.value = false;
};

onMounted(loadDashboard);
</script>

<template>
  <div class="dashboard-page">
    <header class="top">
      <h1>数据总览</h1>
      <div class="account">
        <span class="bell">♧</span>
        <span class="avatar">D</span>
        <div><b>DataInsightAI</b><small>分析员</small></div>
        <span>⌄</span>
      </div>
    </header>

    <section class="banner">
      <div>
        <h2>欢迎回来，鼎皓! 👋</h2>
        <p>DIA 已经准备好帮你探索数据世界了</p>
        <div class="pills">
          <span>◈ 数据驱动决策</span><span>◌ 智能分析</span>
          <span>⌁ 洞察未来</span><span>✣ 简单高效</span>
        </div>
      </div>
      <div class="speech">数据都在这里，<br />需要我帮你看看吗？</div>
      <img class="hero-pointing" :src="diaHeroPointing" alt="DIA" />
    </section>

    <div v-if="loadErrors.length" class="error" role="alert">
      {{ loadErrors.join("；") }}
      <button @click="loadDashboard">重试</button>
    </div>

    <section class="stats">
      <div v-for="stat in stats" :key="stat.title" class="metric">
        <i>{{ stat.icon }}</i>
        <div>
          <small>{{ stat.title }}</small>
          <strong>{{ loading ? "--" : stat.value }}</strong>
          <em>{{ loading ? "正在加载" : stat.description }}</em>
        </div>
        <label v-if="!loading && stat.available">实时数据</label>
      </div>
    </section>

    <section class="grid">
      <article class="panel trend">
        <header>
          <h3>数据趋势</h3>
          <span class="period">近 7 天</span>
        </header>
        <div class="legend">● 数据集上传数量</div>
        <div v-if="loading" class="panel-state">正在加载趋势数据...</div>
        <div v-else-if="datasetsError" class="panel-state error-state">
          趋势数据加载失败
        </div>
        <div v-else-if="!hasUploadTrend" class="panel-state">
          最近 7 天暂无数据集上传
        </div>
        <svg
          v-else
          viewBox="0 0 500 205"
          preserveAspectRatio="none"
          aria-label="最近 7 天数据集上传趋势"
        >
          <path class="grid-line" d="M35 40H455M35 95H455M35 150H455" />
          <polyline class="trend-line" :points="trendPoints" />
          <g v-for="(item, index) in uploadTrend" :key="item.key">
            <circle
              class="trend-point"
              :cx="trendX(index)"
              :cy="trendY(item.count)"
              r="4"
            />
            <text
              class="trend-count"
              :x="trendX(index)"
              :y="trendY(item.count) - 10"
            >
              {{ item.count }}
            </text>
            <text class="trend-label" :x="trendX(index)" y="190">
              {{ item.label }}
            </text>
          </g>
        </svg>
      </article>

      <article class="panel recent">
        <header>
          <h3>最近数据集</h3>
          <button class="link" @click="go('/datasets')">查看全部 →</button>
        </header>
        <div v-if="loading" class="empty">正在加载数据集...</div>
        <div v-else-if="datasetsError" class="empty error-state">
          最近数据集加载失败
        </div>
        <template v-else>
          <button
            v-for="dataset in recentDatasets"
            :key="dataset.id"
            class="row"
            @click="go(`/datasets/${dataset.id}`)"
          >
            <i>▤</i>
            <span
              ><b>{{ dataset.filename }}</b
              ><small
                >{{ formatNumber(dataset.row_count) }} 行 ·
                {{ formatDate(dataset.uploaded_at) }}</small
              ></span
            >
            <label :class="dataset.status">{{
              formatStatus(dataset.status)
            }}</label
            >›
          </button>
          <div v-if="recentDatasets.length === 0" class="empty">暂无数据集</div>
        </template>
      </article>

      <article class="panel quality">
        <h3>数据质量分布</h3>
        <div class="quality-empty">
          <div class="quality-placeholder">--</div>
          <div>
            <strong>暂无分布数据</strong>
            <p>当前仅提供平均数据质量，尚无各评分区间的分布统计。</p>
          </div>
        </div>
      </article>
    </section>

    <section class="bottom">
      <article class="dia">
        <img :src="diaNormalHalf" alt="DIA" />
        <div>
          <h3>DIA 想对你说</h3>
          <p>{{ diaMessage }}</p>
          <button @click="go('/datasets')">查看数据集 ↗</button>
        </div>
      </article>
      <article class="quick">
        <h3>快速开始</h3>
        <div>
          <button @click="go('/datasets')">
            ↥ <b>上传数据<small>支持 CSV 文件</small></b>
          </button>
          <button>
            ◉ <b>智能分析<small>AI 驱动分析</small></b>
          </button>
          <button>
            ◉ <b>数据洞察<small>发现数据价值</small></b>
          </button>
          <button>
            ▤ <b>报告生成<small>导出分析报告</small></b>
          </button>
        </div>
      </article>
    </section>
  </div>
</template>

<style>
.dashboard-page {
  display: block;
  width: 100%;
  max-width: none;
  min-width: 0;
  min-height: 100vh;
  padding: 25px 34px 36px;
  background: linear-gradient(135deg, #f7f9ff, #f5f6ff);
  color: #13234f;
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}
.top h1 {
  margin: 0;
  font-size: 28px;
}
.account {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}
.account small {
  display: block;
  color: #9aa3bf;
  font-size: 10px;
}
.bell {
  margin-right: 15px;
  font-size: 24px;
}
.avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: #265ce8;
  color: #fff;
  font-size: 18px;
}
.banner {
  position: relative;
  height: 320px;
  overflow: visible;
  padding: 40px 46% 24px 46px;
  border: 1px solid #edf0ff;
  border-radius: 16px;
  background: linear-gradient(110deg, #fff, #f5f4ff 70%, #ede9ff);
}
.banner h2 {
  margin: 0 0 7px;
  font-size: 30px;
  line-height: 1.25;
}
.banner p {
  margin: 0 0 26px;
  color: #53618d;
  font-size: 17px;
}
.pills {
  display: flex;
  gap: 15px;
}
.pills span {
  padding: 8px 14px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 3px 12px #4b4da711;
  color: #5863a1;
  font-size: 11px;
}
.banner .hero-pointing {
  position: absolute;
  top: 0;
  right: -8px;
  width: 520px;
  height: auto;
  max-width: none;
  object-fit: contain;
  object-position: center top;
  filter: drop-shadow(0 12px 16px #3c398922);
}
.speech {
  position: absolute;
  top: 52px;
  right: 440px;
  z-index: 2;
  padding: 20px 22px;
  border: 1px solid #e8e6ff;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 8px 18px #4c49ad1a;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.8;
}
.error {
  margin: 12px 0;
  padding: 9px 14px;
  border-radius: 8px;
  background: #fff1f2;
  color: #db4562;
}
.error button {
  float: right;
  border: 0;
  background: none;
  color: inherit;
  cursor: pointer;
}
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  margin: 14px 0;
  border: 1px solid #e8eafe;
  border-radius: 15px;
  background: #fff;
}
.metric {
  position: relative;
  display: flex;
  align-items: center;
  gap: 15px;
  min-height: 118px;
  padding: 26px 25px;
  border-right: 1px solid #edf0fa;
}
.metric:last-child {
  border: 0;
}
.metric i {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  border-radius: 17px;
  background: #eeebff;
  color: #5948f2;
  font-size: 34px;
  font-style: normal;
}
.metric small,
.metric em {
  display: block;
  color: #667294;
  font-size: 13px;
  font-style: normal;
}
.metric strong {
  display: block;
  margin: 5px 0;
  font-size: 31px;
}
.metric em {
  color: #8e98b7;
  font-size: 11px;
}
.metric label {
  position: absolute;
  right: 20px;
  bottom: 17px;
  color: #22ad75;
  font-size: 11px;
}
.grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr 1.1fr;
  gap: 14px;
}
.panel {
  min-height: 300px;
  padding: 20px 22px;
  border: 1px solid #e8eafe;
  border-radius: 15px;
  background: #fff;
}
.panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.panel h3,
.quick h3 {
  margin: 0;
  font-size: 17px;
}
.period,
.panel header button {
  padding: 7px 11px;
  border: 1px solid #e1e4f4;
  border-radius: 8px;
  background: #fff;
  color: #51618c;
  font-size: 11px;
}
.link {
  border: 0 !important;
  color: #4f6ef5 !important;
  cursor: pointer;
}
.legend {
  margin: 20px 0;
  color: #6654f4;
  font-size: 11px;
}
.trend svg {
  width: 100%;
  height: 205px;
}
.grid-line {
  fill: none;
  stroke: #eff1fb;
  stroke-dasharray: 4 4;
}
.trend-line {
  fill: none;
  stroke: #7c56ed;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.trend-point {
  fill: #fff;
  stroke: #7c56ed;
  stroke-width: 3;
}
.trend-count,
.trend-label {
  fill: #7480a3;
  font-size: 10px;
  text-anchor: middle;
}
.trend-count {
  fill: #5a48d8;
  font-weight: 700;
}
.panel-state {
  min-height: 205px;
  display: grid;
  place-items: center;
  color: #8a95b2;
  font-size: 12px;
}
.error-state {
  color: #db4562;
}
.row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
  border: 0;
  border-bottom: 1px solid #f0f1f8;
  background: none;
  color: inherit;
  text-align: left;
  cursor: pointer;
}
.row i {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: #eee9ff;
  color: #704ff0;
  font-style: normal;
}
.row span {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.row b {
  overflow: hidden;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row small {
  color: #8994b0;
  font-size: 10px;
}
.row label {
  padding: 5px 9px;
  border-radius: 11px;
  background: #eaf8f1;
  color: #21aa76;
  font-size: 10px;
}
.row label.pending {
  background: #fff6e3;
  color: #d78315;
}
.row label.failed {
  background: #fff0f0;
  color: #ef5d64;
}
.empty {
  padding: 60px 0;
  color: #8a95b2;
  text-align: center;
}
.quality-empty {
  height: 220px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.quality-placeholder {
  width: 132px;
  height: 132px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border: 14px solid #eef0f8;
  border-radius: 50%;
  color: #9aa3bf;
  font-size: 24px;
  font-weight: 700;
}
.quality-empty strong {
  color: #394873;
  font-size: 13px;
}
.quality-empty p {
  margin: 10px 0 0;
  color: #8a95b2;
  font-size: 11px;
  line-height: 1.7;
}
.bottom {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 14px;
  margin-top: 14px;
}
.dia {
  position: relative;
  min-height: 160px;
  overflow: hidden;
  padding: 24px 28px;
  border: 1px solid #e5e2ff;
  border-radius: 15px;
  background: linear-gradient(100deg, #f4f1ff, #f8f9ff);
}
.dia img {
  position: absolute;
  right: -4px;
  bottom: -70px;
  width: 150px;
  opacity: 0.8;
}
.dia div {
  position: relative;
  width: 70%;
}
.dia h3 {
  margin: 0 0 9px;
  font-size: 18px;
}
.dia p {
  min-height: 40px;
  color: #60709a;
  font-size: 11px;
  line-height: 1.8;
}
.dia button {
  padding: 8px 12px;
  border: 0;
  border-radius: 7px;
  background: #7256ee;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
}
.quick {
  padding: 13px 20px;
  border: 1px solid #e8eafe;
  border-radius: 15px;
  background: #fff;
}
.quick > div {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 13px;
  margin-top: 15px;
}
.quick button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 13px;
  border: 1px solid #edf0fa;
  border-radius: 11px;
  background: #fff;
  color: inherit;
  font-size: 20px;
  text-align: left;
  cursor: pointer;
}
.quick b {
  font-size: 12px;
}
.quick small {
  display: block;
  margin-top: 4px;
  color: #8b96b4;
  font-size: 10px;
  font-weight: 400;
}
@media (max-width: 1200px) {
  .dashboard-page {
    padding: 20px;
  }
  .banner {
    height: 300px;
  }
  .banner .hero-pointing {
    top: 0;
    right: -10px;
    width: 470px;
  }
  .speech {
    right: 390px;
  }
  .grid {
    grid-template-columns: 1fr 1fr;
  }
  .quality {
    grid-column: span 2;
  }
  .bottom {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 700px) {
  .banner {
    height: 300px;
    padding: 25px 20px;
    overflow: hidden;
  }
  .banner h2 {
    max-width: 62%;
    font-size: 24px;
  }
  .banner p {
    max-width: 55%;
    font-size: 14px;
  }
  .pills {
    display: none;
  }
  .banner .hero-pointing {
    top: 6px;
    right: -16px;
    width: 360px;
  }
  .speech {
    top: 145px;
    right: auto;
    left: 20px;
    max-width: 180px;
    padding: 10px;
    font-size: 11px;
  }
  .stats,
  .grid {
    grid-template-columns: 1fr;
  }
  .metric {
    border-right: 0;
    border-bottom: 1px solid #edf0fa;
  }
  .quality {
    grid-column: auto;
  }
  .quality-empty {
    gap: 16px;
  }
  .quality-placeholder {
    width: 100px;
    height: 100px;
  }
  .quick > div {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
