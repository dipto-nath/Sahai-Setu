/**
 * TypeScript types for SIH26093 Frontend
 */

// User types
export interface User {
  id: number;
  name: string;
  identifier: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'ADMIN' | 'COUNSELLOR' | 'LEGAL_OFFICER' | 'AUTHORIZED_STAFF';

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Case types
export interface Case {
  id: number;
  anonymous_case_id: string;
  language: string;
  status: CaseStatus;
  risk_level: RiskLevel;
  svi: number;
  confidence: number;
  assigned_user_id?: number;
  created_at: string;
  updated_at: string;
}

export type CaseStatus = 'PENDING' | 'ASSESSED' | 'PENDING_REVIEW' | 'REVIEWED' | 'CLOSED';

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'INCONCLUSIVE';

export interface CaseCreate {
  language: string;
}

export interface CaseUpdate {
  status?: CaseStatus;
  risk_level?: RiskLevel;
  svi?: number;
  confidence?: number;
  assigned_user_id?: number;
}

// Interaction types
export interface Interaction {
  id: number;
  case_id: number;
  input_type: InteractionType;
  language: string;
  content: string;
  created_at: string;
}

export type InteractionType = 'TEXT' | 'AUDIO' | 'MULTIMODAL';

// Assessment types
export interface Assessment {
  id: number;
  case_id: number;
  text_score: number;
  audio_score: number;
  context_score: number;
  threat_score: number;
  distress_score: number;
  final_svi: number;
  risk_level: RiskLevel;
  confidence: number;
  assessment_status: AssessmentStatus;
  // Backend stores these as JSON-encoded strings; the frontend parses
  // them on demand (see parseExplanation).
  explanation_json?: string | null;
  analysis_json?: string | null;
  created_at: string;
}

// Structured shape of the Gemini explanation JSON that the backend
// stores in assessments.explanation_json.
export interface AssessmentExplanation {
  summary?: string;
  care?: string;
  action?: string;
}

// Safely parse an Assessment.explanation_json field, returning an empty
// object if it's missing, null, or malformed JSON. Never throws.
export function parseExplanation(
  raw?: string | null,
): AssessmentExplanation {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      return {
        summary:
          typeof parsed.summary === 'string' ? parsed.summary : undefined,
        care: typeof parsed.care === 'string' ? parsed.care : undefined,
        action: typeof parsed.action === 'string' ? parsed.action : undefined,
      };
    }
  } catch {
    // Fall through to return empty object.
  }
  return {};
}

export type AssessmentStatus = 'COMPLETED' | 'REVIEW_RECOMMENDED' | 'INCONCLUSIVE';

// Indicator types
export interface Indicator {
  id: number;
  assessment_id: number;
  name: string;
  severity: IndicatorSeverity;
  confidence: number;
  source: IndicatorSource;
}

export type IndicatorSeverity = 'low' | 'moderate' | 'high' | 'severe';
export type IndicatorSource = 'text' | 'audio' | 'context';

// Recommendation types
export interface Recommendation {
  id: number;
  case_id: number;
  type: RecommendationType;
  priority: RecommendationPriority;
  reason: string;
  status: RecommendationStatus;
  created_at: string;
}

export type RecommendationType =
  | 'GENERAL_SUPPORT'
  | 'COUNSELLING_REFERRAL'
  | 'FOLLOW_UP'
  | 'PRIORITY_HUMAN_REVIEW'
  | 'LEGAL_SUPPORT'
  | 'SAFETY_ASSESSMENT'
  | 'EMERGENCY_PROTOCOL'
  | 'HUMAN_REVIEW_REQUIRED';

export type RecommendationPriority = 'ROUTINE' | 'ELEVATED' | 'URGENT' | 'IMMEDIATE';
export type RecommendationStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'DECLINED';

// Review types
export interface Review {
  id: number;
  case_id: number;
  reviewer_id: number;
  ai_risk: RiskLevel;
  human_risk: RiskLevel;
  decision: ReviewDecision;
  notes?: string;
  created_at: string;
}

export type ReviewDecision =
  | 'CONFIRMED'
  | 'MODIFIED'
  | 'FALSE_POSITIVE'
  | 'FALSE_NEGATIVE'
  | 'REASSESS_REQUESTED'
  | 'ESCALATED';

export interface ReviewCreate {
  human_risk: RiskLevel;
  decision: ReviewDecision;
  notes?: string;
}

// Analysis types
export interface AnalysisResult {
  case_id: string;
  transcript?: string;
  svi: number;
  risk_level: RiskLevel;
  confidence: number;
  audio_quality?: string;
  assessment_status: AssessmentStatus;
  indicators: IndicatorResult[];
  recommendations: RecommendationResult[];
  explanation: string[];
  nlp_analysis?: any;
  audio_analysis?: any;
  fusion_analysis?: any;
  analysis_mode: 'DEMO' | 'REAL';
}

export interface AssessmentResult {
  id: number;
  case_id: number;
  text_score: number;
  audio_score: number;
  context_score: number;
  threat_score: number;
  distress_score: number;
  final_svi: number;
  risk_level: RiskLevel;
  confidence: number;
  assessment_status: AssessmentStatus;
  created_at: string;
}

export interface IndicatorResult {
  name: string;
  severity: IndicatorSeverity;
  confidence: number;
  source: IndicatorSource;
}

export interface RecommendationResult {
  type: RecommendationType;
  priority: RecommendationPriority;
  title: string;
  description: string;
  reasoning: string;
  applicable_roles: string[];
}

// Dashboard types
export interface DashboardData {
  summary: DashboardSummary;
  risk_distribution: RiskDistribution[];
  language_distribution: LanguageDistribution[];
  cases_over_time: CasesOverTime[];
  average_processing_time: number;
  human_review_outcomes: HumanReviewOutcome[];
  ai_vs_human_comparison: AiVsHumanComparison[];
  confidence_distribution: ConfidenceDistribution[];
}

export interface DashboardSummary {
  total_cases: number;
  low: number;
  moderate: number;
  high: number;
  critical: number;
  pending_human_review: number;
}

export interface RiskDistribution {
  risk_level: string;
  count: number;
}

export interface LanguageDistribution {
  language: string;
  count: number;
}

export interface CasesOverTime {
  date: string;
  count: number;
}

export interface HumanReviewOutcome {
  decision: string;
  count: number;
}

export interface AiVsHumanComparison {
  comparison: string;
  count: number;
}

export interface ConfidenceDistribution {
  range: string;
  count: number;
}

// Language types
export interface LanguageOption {
  code: string;
  name: string;
  native_name: string;
}

// Demo case types
export interface DemoCase {
  id: string;
  title: string;
  description: string;
  risk_level: RiskLevel;
  svi: number;
  language: string;
  input_type: InteractionType;
  text?: string;
  audio_url?: string;
}
