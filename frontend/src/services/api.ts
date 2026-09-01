/**
 * API Service for SIH26093 Frontend
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type {
  TokenResponse, User, Case, CaseCreate, CaseUpdate,
  AssessmentResult, DashboardData, ReviewCreate, LanguageOption
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      if (this.token && config.headers) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          if (typeof window !== 'undefined') {
            const path = window.location.pathname;
            if (!path.startsWith('/victim') && !path.startsWith('/login')) {
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  loadTokenFromStorage() {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        this.token = token;
      }
    }
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<TokenResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post<TokenResponse>('/auth/login', formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async register(userData: { name: string; identifier: string; password: string; role: string }): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Case endpoints
  async createCase(caseData: CaseCreate): Promise<Case> {
    const response = await this.client.post<Case>('/cases', caseData);
    return response.data;
  }

  async createAnonymousCase(caseData: CaseCreate): Promise<Case> {
    const response = await this.client.post<Case>('/cases/anonymous', caseData);
    return response.data;
  }

  async getCases(skip = 0, limit = 100, riskLevel?: string): Promise<Case[]> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (riskLevel) params.append('risk_level', riskLevel);

    const response = await this.client.get<Case[]>(`/cases?${params.toString()}`);
    return response.data;
  }

  async getPriorityCases(limit = 50): Promise<Case[]> {
    const response = await this.client.get<Case[]>(`/cases/priority?limit=${limit}`);
    return response.data;
  }

  async getCase(caseId: number) {
    const response = await this.client.get(`/cases/${caseId}`);
    return response.data;
  }

  async getCaseByAnonymousId(anonymousId: string) {
    const response = await this.client.get(`/cases/anonymous/${anonymousId}`);
    return response.data;
  }

  async updateCase(caseId: number, caseData: CaseUpdate): Promise<Case> {
    const response = await this.client.put<Case>(`/cases/${caseId}`, caseData);
    return response.data;
  }

  async analyzeText(caseId: number, text: string, language: string): Promise<AssessmentResult> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('language', language);

    const response = await this.client.post<AssessmentResult>(`/cases/${caseId}/analyze/text`, formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async analyzeAudio(caseId: number, audioFile: File, language: string): Promise<AssessmentResult> {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('language', language);

    const response = await this.client.post<AssessmentResult>(`/cases/${caseId}/analyze/audio`, formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async analyzeMultimodal(caseId: number, text: string | null, audioFile: File | null, language: string): Promise<AssessmentResult> {
    const formData = new FormData();
    if (text) formData.append('text', text);
    if (audioFile) formData.append('audio', audioFile);
    formData.append('language', language);

    const response = await this.client.post<AssessmentResult>(`/cases/${caseId}/analyze`, formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async addReview(caseId: number, reviewData: ReviewCreate) {
    const response = await this.client.post(`/cases/${caseId}/review`, reviewData);
    return response.data;
  }

  async assignCase(caseId: number, assignedUserId: number) {
    const response = await this.client.post(`/cases/${caseId}/assign`, null, {
      params: { assigned_user_id: assignedUserId },
    });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboard(): Promise<DashboardData> {
    const response = await this.client.get<DashboardData>('/dashboard');
    return response.data;
  }

  async getSummary() {
    const response = await this.client.get('/dashboard/summary');
    return response.data;
  }

  // Analysis endpoints (standalone)
  async analyzeTextStandalone(text: string, language: string, caseId?: string): Promise<AssessmentResult> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('language', language);
    if (caseId) formData.append('case_id', caseId);

    const response = await this.client.post<AssessmentResult>('/analyze/text', formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async analyzeAudioStandalone(audioFile: File, language: string, caseId?: string): Promise<AssessmentResult> {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('language', language);
    if (caseId) formData.append('case_id', caseId);

    const response = await this.client.post<AssessmentResult>('/analyze/audio', formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async analyzeMultimodalStandalone(text: string | null, audioFile: File | null, language: string, caseId?: string): Promise<AssessmentResult> {
    const formData = new FormData();
    if (text) formData.append('text', text);
    if (audioFile) formData.append('audio', audioFile);
    formData.append('language', language);
    if (caseId) formData.append('case_id', caseId);

    const response = await this.client.post<AssessmentResult>('/analyze', formData, { headers: { 'Content-Type': undefined } });
    return response.data;
  }

  async getServiceInfo() {
    const response = await this.client.get('/analyze/services/info');
    return response.data;
  }

  // Recommendations
  async getRecommendations(caseId: number) {
    const response = await this.client.get(`/recommendations/${caseId}`);
    return response.data;
  }

  // Audit log
  async getAuditLog(params?: { skip?: number; limit?: number; user_id?: number; case_id?: number; action?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString());
    if (params?.case_id) queryParams.append('case_id', params.case_id.toString());
    if (params?.action) queryParams.append('action', params.action);

    const response = await this.client.get(`/audit-log?${queryParams.toString()}`);
    return response.data;
  }

  // Users
  async getUsers(): Promise<User[]> {
    const response = await this.client.get<User[]>('/users');
    return response.data;
  }

  async getRoles(): Promise<{ value: string; label: string }[]> {
    const response = await this.client.get('/users/roles/list');
    return response.data;
  }
}

export const apiService = new ApiService();

// Initialize token from localStorage on client side
if (typeof window !== 'undefined') {
  apiService.loadTokenFromStorage();
}
