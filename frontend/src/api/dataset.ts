import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export interface Dataset {
  id: number;
  filename: string;
  row_count: number;
  column_count: number;
  uploaded_at: string;
}

export const getDatasets = async (): Promise<Dataset[]> => {
  const response = await api.get<Dataset[]>("/api/data/datasets");
  return response.data;
};