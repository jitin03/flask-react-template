import ApiService from './api.service';
import { getAccessTokenFromStorage } from '../utils/storage-util';

export interface Task {
  id: string;
  title: string;
  description?: string;
  account_id: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
}

export interface TasksResponse {
  items: Task[];
  pagination_params: {
    page: number;
    size: number;
    offset: number;
  };
  total_count: number;
  total_pages: number;
}

export class TasksService {
  private static apiService = new ApiService();

  private static getAuthHeaders() {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      throw new Error('Access token not found');
    }
    return {
      Authorization: `Bearer ${accessToken.token}`,
    };
  }

  static async getTasks(
    accountId: string,
    params?: {
      page?: number;
      per_page?: number;
    },
  ): Promise<TasksResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.per_page)
      queryParams.append('size', params.per_page.toString());

    const url = `/accounts/${accountId}/tasks${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

    const response = await this.apiService.apiClient.get<TasksResponse>(url, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  static async getTask(accountId: string, taskId: string): Promise<Task> {
    const response = await this.apiService.apiClient.get<Task>(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        headers: this.getAuthHeaders(),
      },
    );
    return response.data;
  }

  static async createTask(
    accountId: string,
    taskData: CreateTaskRequest,
  ): Promise<Task> {
    const response = await this.apiService.apiClient.post<Task>(
      `/accounts/${accountId}/tasks`,
      taskData,
      {
        headers: this.getAuthHeaders(),
      },
    );
    return response.data;
  }

  static async updateTask(
    accountId: string,
    taskId: string,
    taskData: UpdateTaskRequest,
  ): Promise<Task> {
    const response = await this.apiService.apiClient.put<Task>(
      `/accounts/${accountId}/tasks/${taskId}`,
      taskData,
      {
        headers: this.getAuthHeaders(),
      },
    );
    return response.data;
  }

  static async deleteTask(accountId: string, taskId: string): Promise<void> {
    await this.apiService.apiClient.delete(
      `/accounts/${accountId}/tasks/${taskId}`,
      {
        headers: this.getAuthHeaders(),
      },
    );
  }
}
