<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import diaNormal from '../assets/dia/dia-normal.webp'
import diaThinking from '../assets/dia/dia-thinking.webp'
import diaAnalyzing from '../assets/dia/dia-analyzing.webp'
import diaIssue from '../assets/dia/dia-issue.webp'

const router = useRouter()

const datasets = ref([])
const loading = ref(true)
const error = ref('')

const showUploadModal = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadError = ref('')


const diaState = computed(() => {
  if (uploadError.value || error.value) {
    return 'issue'
  }

  if (uploading.value || datasets.value.some((dataset) => dataset.status === 'pending')) {
    return 'analyzing'
  }

  if (loading.value) {
    return 'thinking'
  }

  if (datasets.value[0]?.status === 'failed') {
    return 'issue'
  }

  return 'normal'
})

const diaStateMap = {
  normal: {
    image: diaNormal,
    title: '数据都在这里，需要我帮你看看吗？',
    message: '从最近的一份开始，或者上传新的 CSV。',
  },
  thinking: {
    image: diaThinking,
    title: 'DIA 正在整理',
    message: '我先看一下你已有的数据集。',
  },
  analyzing: {
    image: diaAnalyzing,
    title: 'DIA 正在分析',
    message: '数据收到，我开始检查啦。',
  },
  issue: {
    image: diaIssue,
    title: '有一份数据需要再看一眼。',
    message: '上传或分析没有顺利完成，可以检查后重试。',
  },
}

const currentDia = computed(() => diaStateMap[diaState.value])

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
  router.push('/datasets/' + id)
}

const openUploadModal = () => {
  showUploadModal.value = true
  selectedFile.value = null
  uploadError.value = ''
}

const getStatusText = (status) => {
  const statusText = {
    pending: '分析中',
    completed: '分析完成',
    failed: '分析失败',
  }

  return statusText[status] || '状态未知'
}

const reopenUploadModal = () => {
  openUploadModal()
}

const closeUploadModal = () => {
  if (uploading.value) {
    return
  }

  showUploadModal.value = false
  selectedFile.value = null
  uploadError.value = ''
}

const handleFileChange = (event) => {
  const file = event.target.files[0]

  if (!file) {
    return
  }

  uploadError.value = ''

  if (!file.name.toLowerCase().endsWith('.csv')) {
    selectedFile.value = null
    uploadError.value = '请选择 CSV 格式的文件。'
    return
  }

  if (file.size > 20 * 1024 * 1024) {
    selectedFile.value = null
    uploadError.value = '文件大小不能超过 20MB。'
    return
  }

  selectedFile.value = file
  console.log('选择的文件：', file.name, '文件大小：', file.size, 'bytes')
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    uploadError.value = '请先选择一个 CSV 文件。'
    return
  }

  try {
    uploading.value = true
    uploadError.value = ''

    const formData = new FormData()
    formData.append('file', selectedFile.value)

    await api.post(
      '/api/data/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    console.log('上传并分析成功')

    showUploadModal.value = false

    await fetchDatasets()

    if (datasets.value.length > 0) {
      const latestDataset = datasets.value[0]

      console.log('最新数据集：', latestDataset)

      const detailPath = '/datasets/' + latestDataset.id

      router.push(detailPath)
    }
  } catch (err) {
    console.error('上传数据失败：', err)

    if (
      err.response &&
      err.response.data &&
      err.response.data.detail
    ) {
      uploadError.value = err.response.data.detail
    } else {
      uploadError.value = '上传失败，请检查后端服务是否正常运行。'
    }

    await fetchDatasets()
  } finally {
    uploading.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(2)} KB`
  }

  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
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

      <button
        class="primary-button"
        @click="openUploadModal"
      >
        ＋ 上传数据
      </button>
    </div>

    <section class="dia-workspace" :class="`dia-workspace-${diaState}`" aria-live="polite">
      <div class="dia-workspace-copy">
        <span class="dia-eyebrow">DIA · 数据工作空间</span>
        <strong>{{ currentDia.title }}</strong>
        <p>{{ currentDia.message }}</p>
      </div>
      <img class="dia-workspace-image" :src="currentDia.image" :alt="`DIA ${diaState}`" />
    </section>

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

          <div
            class="status-tag"
            :class="dataset.status"
          >
            <span class="small-dot"></span>
            {{ getStatusText(dataset.status) }}

            <button
              v-if="dataset.status === 'failed'"
              class="retry-upload-button"
              @click.stop="reopenUploadModal"
            >
              重新上传
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <div
      v-if="showUploadModal"
      class="modal-overlay"
      @click.self="closeUploadModal"
    >
      <div class="upload-modal">
        <div class="modal-header">
          <div>
            <h2>上传数据集</h2>
            <p>上传 CSV 文件，系统将自动进行数据分析。</p>
          </div>

          <button
            class="close-button"
            @click="closeUploadModal"
            :disabled="uploading"
          >
            ×
          </button>
        </div>

        <div class="upload-area">
          <div v-if="uploading" class="upload-dia-feedback">
            <img :src="diaAnalyzing" alt="DIA 正在分析" />
            <span>数据收到，我开始检查啦。</span>
          </div>
          <div v-else-if="selectedFile" class="upload-dia-feedback">
            <img :src="diaThinking" alt="DIA 正在思考" />
            <span>让我先看看这份数据……</span>
          </div>
          <div class="upload-icon">
            CSV
          </div>

          <h3>选择 CSV 文件</h3>

          <p>
            支持 CSV 格式，文件大小不超过 20MB
          </p>

          <label class="file-select-button">
            选择文件

            <input
              type="file"
              accept=".csv,text/csv"
              @change="handleFileChange"
              :disabled="uploading"
            />
          </label>

          <div
            v-if="selectedFile"
            class="selected-file"
          >
            <span>📄</span>

            <div>
              <strong>{{ selectedFile.name }}</strong>

              <small>
                {{ formatFileSize(selectedFile.size) }}
              </small>
            </div>
          </div>

          <div
            v-if="uploadError"
            class="upload-error"
          >
            {{ uploadError }}
          </div>
        </div>

        <div class="modal-footer">
          <button
            class="cancel-button"
            @click="closeUploadModal"
            :disabled="uploading"
          >
            取消
          </button>

          <button
            class="upload-button"
            @click="uploadFile"
            :disabled="!selectedFile || uploading"
          >
            <span v-if="uploading">
              正在分析...
            </span>

            <span v-else>
              开始分析
            </span>
          </button>
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

.dia-workspace {
  position: relative;
  display: flex;
  align-items: flex-end;
  min-height: 176px;
  margin: -6px 0 20px;
  padding: 22px 220px 20px 22px;
  overflow: hidden;
  border: 1px solid #e2e8f5;
  border-radius: 16px;
  background: linear-gradient(110deg, #ffffff 0%, #f5f7ff 70%, #eef0ff 100%);
}

.dia-workspace-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.dia-eyebrow {
  color: #756cf6;
  font-size: 10px;
  font-weight: 700;
}

.dia-workspace-copy strong {
  color: #273b75;
  font-size: 15px;
}

.dia-workspace-copy p {
  margin: 0;
  color: #7d8ca6;
  font-size: 12px;
  line-height: 1.6;
}

.dia-workspace-image {
  position: absolute;
  right: 24px;
  bottom: -8px;
  width: 150px;
  height: 160px;
  object-fit: contain;
  object-position: center bottom;
  filter: drop-shadow(0 8px 14px rgba(67, 73, 145, 0.08));
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
  transition: all 0.2s ease;
}

.primary-button:hover {
  transform: translateY(-1px);
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

.status-tag.pending {
  color: #d97706;
}

.status-tag.failed {
  color: #dc2626;
}

.small-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #35c98b;
  box-shadow: 0 0 8px rgba(53, 201, 139, 0.6);
}

.status-tag.pending .small-dot {
  background: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
}

.status-tag.failed .small-dot {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.45);
}

.retry-upload-button {
  margin-left: 4px;
  padding: 4px 8px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background: #fff;
  color: #dc2626;
  font-size: 10px;
  cursor: pointer;
}

.empty-state {
  padding: 50px 0;
  text-align: center;
  color: #a0a8b6;
}

/* 上传弹窗 */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(25, 30, 45, 0.42);
  backdrop-filter: blur(3px);
}

.upload-modal {
  width: 500px;
  max-width: calc(100vw - 40px);

  background: white;
  border-radius: 18px;

  box-shadow: 0 20px 60px rgba(20, 25, 40, 0.18);

  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  padding: 24px 26px 18px;

  border-bottom: 1px solid #edf0f4;
}

.modal-header h2 {
  margin: 0;
  color: #273044;
  font-size: 18px;
}

.modal-header p {
  margin: 6px 0 0;
  color: #929bab;
  font-size: 11px;
}

.close-button {
  width: 30px;
  height: 30px;

  border: none;
  border-radius: 8px;

  background: #f4f5f8;
  color: #8c95a5;

  font-size: 20px;
  line-height: 1;

  cursor: pointer;
}

.upload-area {
  margin: 22px 26px;
  padding: 34px 24px;

  text-align: center;

  border: 1.5px dashed #d9ddea;
  border-radius: 14px;

  background: #fafbfe;
}

.upload-dia-feedback {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: -8px auto 16px;
  color: #625bea;
  font-size: 11px;
}

.upload-dia-feedback img {
  width: 54px;
  height: 64px;
  object-fit: contain;
}

.upload-icon {
  width: 52px;
  height: 52px;

  display: flex;
  align-items: center;
  justify-content: center;

  margin: 0 auto 14px;

  border-radius: 13px;

  background: #eeeaff;
  color: #625bea;

  font-size: 11px;
  font-weight: 800;
}

.upload-area h3 {
  margin: 0;
  color: #354055;
  font-size: 15px;
}

.upload-area > p {
  margin: 7px 0 18px;
  color: #9aa3b2;
  font-size: 11px;
}

.file-select-button {
  display: inline-flex;

  padding: 9px 15px;

  border-radius: 8px;

  background: #625bea;
  color: white;

  font-size: 11px;
  font-weight: 600;

  cursor: pointer;
}

.file-select-button input {
  display: none;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 10px;

  margin-top: 18px;
  padding: 11px 13px;

  text-align: left;

  border: 1px solid #e6e9f0;
  border-radius: 9px;

  background: white;
}

.selected-file > span {
  font-size: 17px;
}

.selected-file div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.selected-file strong {
  color: #465065;
  font-size: 11px;
}

.selected-file small {
  color: #a0a8b6;
  font-size: 9px;
}

.upload-error {
  margin-top: 14px;
  padding: 9px 12px;

  border-radius: 8px;

  background: #fff1f0;
  color: #d9534f;

  font-size: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;

  padding: 16px 26px 22px;

  border-top: 1px solid #edf0f4;
}

.cancel-button,
.upload-button {
  padding: 10px 16px;

  border-radius: 8px;

  font-size: 11px;
  font-weight: 600;

  cursor: pointer;
}

.cancel-button {
  border: 1px solid #e2e5eb;
  background: white;
  color: #7e8797;
}

.upload-button {
  border: none;
  background: #625bea;
  color: white;

  box-shadow: 0 5px 12px rgba(98, 91, 234, 0.22);
}

.upload-button:disabled,
.cancel-button:disabled,
.close-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 700px) {
  .dia-workspace {
    min-height: 142px;
    padding-right: 145px;
  }

  .dia-workspace-image {
    right: 8px;
    width: 118px;
    height: 128px;
  }
}
</style>
