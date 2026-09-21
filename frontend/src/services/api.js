import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,
})

export const getAnalysisCount = () => {
  return api.get('/api/data/analysis/count')
}

export default api