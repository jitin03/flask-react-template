import ApiService from './api.service';
import { getAccessTokenFromStorage } from '../utils/storage-util';

export interface TaskComment {
  id: string;
  task_id: string;
  account_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentRequest {
  content: string;
}

export interface UpdateCommentRequest {
  content: string;
}

export interface TaskCommentsResponse {
  comments: TaskComment[];
  task_id: string;
  total_count: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export class TaskCommentsService {
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

  static async getTaskComments(
    taskId: string,
    params?: {
      page?: number;
      limit?: number;
    }
  ): Promise<TaskCommentsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const url = `/tasks/${taskId}/comments${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    
    const response = await this.apiService.apiClient.get<TaskCommentsResponse>(url, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  static async createComment(taskId: string, commentData: CreateCommentRequest): Promise<TaskComment> {
    const response = await this.apiService.apiClient.post<TaskComment>(`/tasks/${taskId}/comments`, commentData, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  static async updateComment(
    taskId: string,
    commentId: string,
    commentData: UpdateCommentRequest
  ): Promise<TaskComment> {
    const response = await this.apiService.apiClient.put<TaskComment>(
      `/tasks/${taskId}/comments/${commentId}`,
      commentData,
      {
        headers: this.getAuthHeaders(),
      }
    );
    return response.data;
  }

  static async deleteComment(taskId: string, commentId: string): Promise<void> {
    await this.apiService.apiClient.delete(`/tasks/${taskId}/comments/${commentId}`, {
      headers: this.getAuthHeaders(),
    });
  }
}