<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const datasets = ref([])
const loading = ref(true)
const error = ref('')

const fetchDatasets = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await api.get('/api/data/datasets')
    datasets.value = response.data
  } catch (err) {
    console.error('获取数据集失败：', err)
    error.value = '获取数据集失败，请检查后端服务是否正常运行。'
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/datasets/${id}`)
}

onMounted(fetchDatasets)
</script>

<template>
  <div class="datasets-page">
    <div class="page-header">
      <div>
        <div class="breadcrumb">工作台 / 数据集</div>

        <h1>数据集</h1>

        <p>管理和查看你上传的所有数据集。</p>
      </div>

      <button class="primary-button">
        ＋ 上传数据
      </button>
    </div>

    <div v-if="loading" class="state-card">
      正在加载数据集...
    </div>

    <div v-else-if="error" class="state-card error">
      {{ error }}
    </div>

    <div v-else class="dataset-card">
      <div class="card-header">
        <div>
          <h2>全部数据集</h2>
          <p>共 {{ datasets.length }} 个数据集</p>
        </div>
      </div>

      <div v-if="datasets.length === 0" class="empty-state">
        暂无数据集
      </div>

      <div v-else class="dataset-list">
        <div
          v-for="dataset in datasets"
          :key="dataset.id"
          class="dataset-row"
        >
          <div
            class="dataset-info clickable"
            @click="goToDetail(dataset.id)"
          >
            <div class="file-icon">
              CSV
            </div>

            <div>
              <div class="dataset-name">
                {{ dataset.filename }}
              </div>

              <div class="dataset-meta">
                ID {{ dataset.id }} · 上传时间 {{ dataset.uploaded_at }}
              </div>
            </div>
          </div>

          <div class="dataset-stat">
            <span>数据量</span>
            <strong>{{ dataset.row_count }}</strong>
          </div>

          <div class="dataset-stat">
            <span>字段数</span>
            <strong>{{ dataset.column_count }}</strong>
          </div>

          <div class="status-tag">
            <span class="small-dot"></span>
            分析完成
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.datasets-page {
  min-height: 100vh;
  padding: 34px 42px;
  background: #f5f7fb;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
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

.page-header p {
  margin: 7px 0 0;
  color: #8b95a7;
  font-size: 13px;
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
}

.dataset-card,
.state-card {
  background: white;
  border: 1px solid #e9ecf2;
  border-radius: 15px;
  box-shadow: 0 5px 18px rgba(25, 35, 55, 0.035);
}

.dataset-card {
  padding: 22px;
}

.state-card {
  padding: 40px;
  text-align: center;
  color: #7d8799;
}

.error {
  color: #d9534f;
}

.card-header {
  padding-bottom: 18px;
  border-bottom: 1px solid #edf0f4;
}

.card-header h2 {
  margin: 0;
  font-size: 16px;
}

.card-header p {
  margin: 5px 0 0;
  color: #969faf;
  font-size: 11px;
}

.dataset-list {
  margin-top: 8px;
}

.dataset-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr;
  align-items: center;
  gap: 20px;
  padding: 18px 10px;
  border-bottom: 1px solid #f1f3f6;
}

.dataset-row:last-child {
  border-bottom: none;
}

.dataset-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dataset-info.clickable {
  cursor: pointer;
}

.file-icon {
  padding: 6px 7px;
  border-radius: 6px;
  background: #eaf8f1;
  color: #2caf78;
  font-size: 8px;
  font-weight: 800;
}

.dataset-name {
  color: #354055;
  font-size: 13px;
  font-weight: 600;
  transition: color 0.2s ease;
}

.dataset-info.clickable:hover .dataset-name {
  color: #756cf6;
}

.dataset-meta {
  margin-top: 4px;
  color: #a0a8b6;
  font-size: 10px;
}

.dataset-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dataset-stat span {
  color: #9ba3b1;
  font-size: 10px;
}

.dataset-stat strong {
  color: #354055;
  font-size: 14px;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2caf78;
  font-size: 11px;
  font-weight: 600;
}

.small-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #35c98b;
  box-shadow: 0 0 8px rgba(53, 201, 139, 0.6);
}

.empty-state {
  padding: 50px 0;
  text-align: center;
  color: #a0a8b6;
}
</style>