```vue
<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const datasets = ref([])
const loading = ref(true)
const error = ref('')

const showUploadModal = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadError = ref('')

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
</style>
```
