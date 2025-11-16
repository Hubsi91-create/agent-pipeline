/**
 * Data Models for 11-Agent Marketing Pipeline System
 */

// ==================== Common Types ====================

export enum AgentStatus {
  IDLE = 'idle',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  ERROR = 'error',
  WAITING = 'waiting'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export interface BaseAgent {
  id: string;
  name: string;
  status: AgentStatus;
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, unknown>;
}

export interface ProcessingResult<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: Date;
  processingTime?: number;
}

// ==================== Agent 1: Lead Generation ====================

export interface LeadSource {
  name: string;
  type: 'website' | 'social_media' | 'referral' | 'advertising' | 'event' | 'other';
  url?: string;
  campaignId?: string;
}

export interface Lead {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  company?: string;
  jobTitle?: string;
  source: LeadSource;
  score?: number;
  tags?: string[];
  customFields?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

export interface Agent1Data extends BaseAgent {
  leads: Lead[];
  totalLeadsGenerated: number;
  leadsToday: number;
  topSources: LeadSource[];
  conversionRate?: number;
}

// ==================== Agent 2: Lead Qualification ====================

export enum QualificationStatus {
  QUALIFIED = 'qualified',
  UNQUALIFIED = 'unqualified',
  NURTURE = 'nurture',
  PENDING = 'pending'
}

export interface QualificationCriteria {
  budget?: { min: number; max: number; currency: string };
  authority?: boolean;
  need?: boolean;
  timeline?: string;
  companySize?: { min: number; max: number };
  industry?: string[];
}

export interface QualifiedLead extends Lead {
  qualificationStatus: QualificationStatus;
  qualificationScore: number;
  criteria: QualificationCriteria;
  notes?: string;
  nextAction?: string;
  assignedTo?: string;
  qualifiedAt?: Date;
}

export interface Agent2Data extends BaseAgent {
  qualifiedLeads: QualifiedLead[];
  totalQualified: number;
  totalUnqualified: number;
  totalNurture: number;
  qualificationRate: number;
  averageScore: number;
}

// ==================== Agent 3: Competitor Analysis ====================

export interface Competitor {
  id: string;
  name: string;
  website: string;
  industry: string;
  marketShare?: number;
  strengths: string[];
  weaknesses: string[];
  pricing?: {
    model: string;
    range: { min: number; max: number; currency: string };
  };
  products: string[];
  targetAudience: string[];
  marketingChannels: string[];
  lastUpdated: Date;
}

export interface CompetitorAnalysis {
  competitor: Competitor;
  swotAnalysis: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  marketPosition: 'leader' | 'challenger' | 'follower' | 'nicher';
  competitiveAdvantages: string[];
  recommendations: string[];
}

export interface Agent3Data extends BaseAgent {
  competitors: Competitor[];
  analyses: CompetitorAnalysis[];
  totalCompetitorsTracked: number;
  marketInsights: string[];
  lastAnalysisDate?: Date;
}

// ==================== Agent 4: Market Research ====================

export interface MarketSegment {
  id: string;
  name: string;
  size: number;
  growthRate: number;
  demographics: {
    ageRange?: { min: number; max: number };
    gender?: string[];
    income?: { min: number; max: number; currency: string };
    education?: string[];
    location?: string[];
  };
  psychographics: {
    interests?: string[];
    values?: string[];
    lifestyle?: string[];
  };
  painPoints: string[];
  needs: string[];
}

export interface MarketTrend {
  id: string;
  title: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
  timeframe: string;
  relatedSegments: string[];
  sources: string[];
  confidence: number;
}

export interface Agent4Data extends BaseAgent {
  segments: MarketSegment[];
  trends: MarketTrend[];
  totalMarketSize: number;
  targetSegments: string[];
  marketOpportunities: string[];
  researchDate?: Date;
}

// ==================== Agent 5: Content Strategy ====================

export enum ContentType {
  BLOG_POST = 'blog_post',
  VIDEO = 'video',
  INFOGRAPHIC = 'infographic',
  EBOOK = 'ebook',
  WHITEPAPER = 'whitepaper',
  CASE_STUDY = 'case_study',
  PODCAST = 'podcast',
  SOCIAL_POST = 'social_post',
  EMAIL = 'email',
  WEBINAR = 'webinar'
}

export enum ContentStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  APPROVED = 'approved',
  PUBLISHED = 'published',
  ARCHIVED = 'archived'
}

export interface ContentPiece {
  id: string;
  title: string;
  type: ContentType;
  status: ContentStatus;
  topic: string;
  keywords: string[];
  targetAudience: string[];
  channels: string[];
  author?: string;
  publishDate?: Date;
  url?: string;
  performance?: {
    views?: number;
    engagement?: number;
    conversions?: number;
    shares?: number;
  };
}

export interface ContentCalendar {
  month: string;
  year: number;
  content: ContentPiece[];
  themes: string[];
}

export interface Agent5Data extends BaseAgent {
  contentPieces: ContentPiece[];
  calendar: ContentCalendar[];
  totalPublished: number;
  totalPlanned: number;
  topPerformingContent: ContentPiece[];
  contentGaps: string[];
}

// ==================== Agent 6: SEO Optimization ====================

export interface SEOKeyword {
  keyword: string;
  searchVolume: number;
  difficulty: number;
  cpc?: number;
  ranking?: number;
  url?: string;
  lastChecked: Date;
}

export interface SEOPage {
  url: string;
  title: string;
  metaDescription: string;
  keywords: string[];
  backlinks: number;
  pageAuthority: number;
  loadTime: number;
  mobileOptimized: boolean;
  issues: string[];
  recommendations: string[];
}

export interface SEOMetrics {
  organicTraffic: number;
  averagePosition: number;
  totalKeywords: number;
  topRankingKeywords: number;
  domainAuthority: number;
  totalBacklinks: number;
  technicalScore: number;
}

export interface Agent6Data extends BaseAgent {
  keywords: SEOKeyword[];
  pages: SEOPage[];
  metrics: SEOMetrics;
  competitorKeywords: SEOKeyword[];
  optimizationTasks: string[];
}

// ==================== Agent 7: Social Media Management ====================

export enum SocialPlatform {
  FACEBOOK = 'facebook',
  INSTAGRAM = 'instagram',
  TWITTER = 'twitter',
  LINKEDIN = 'linkedin',
  YOUTUBE = 'youtube',
  TIKTOK = 'tiktok',
  PINTEREST = 'pinterest'
}

export interface SocialPost {
  id: string;
  platform: SocialPlatform;
  content: string;
  media?: {
    type: 'image' | 'video' | 'carousel';
    urls: string[];
  };
  scheduledDate: Date;
  publishedDate?: Date;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  engagement?: {
    likes: number;
    comments: number;
    shares: number;
    clicks: number;
    reach: number;
    impressions: number;
  };
  hashtags?: string[];
  mentions?: string[];
}

export interface SocialAccount {
  platform: SocialPlatform;
  handle: string;
  followers: number;
  following: number;
  verified: boolean;
  metrics: {
    engagementRate: number;
    averageLikes: number;
    averageComments: number;
    totalPosts: number;
  };
}

export interface Agent7Data extends BaseAgent {
  posts: SocialPost[];
  accounts: SocialAccount[];
  totalPosts: number;
  scheduledPosts: number;
  averageEngagement: number;
  bestPerformingPosts: SocialPost[];
  contentCalendar: { date: Date; posts: SocialPost[] }[];
}

// ==================== Agent 8: Email Marketing ====================

export enum EmailCampaignType {
  NEWSLETTER = 'newsletter',
  PROMOTIONAL = 'promotional',
  TRANSACTIONAL = 'transactional',
  DRIP = 'drip',
  WELCOME = 'welcome',
  RE_ENGAGEMENT = 're_engagement'
}

export interface EmailCampaign {
  id: string;
  name: string;
  type: EmailCampaignType;
  subject: string;
  preheader?: string;
  content: string;
  segments: string[];
  status: 'draft' | 'scheduled' | 'sent' | 'paused';
  scheduledDate?: Date;
  sentDate?: Date;
  metrics?: {
    sent: number;
    delivered: number;
    opens: number;
    clicks: number;
    conversions: number;
    bounces: number;
    unsubscribes: number;
    openRate: number;
    clickRate: number;
    conversionRate: number;
  };
  abTest?: {
    variant: 'A' | 'B';
    testElement: 'subject' | 'content' | 'sender';
    winner?: 'A' | 'B';
  };
}

export interface EmailList {
  id: string;
  name: string;
  subscribers: number;
  activeSubscribers: number;
  growthRate: number;
  segments: {
    name: string;
    criteria: Record<string, unknown>;
    count: number;
  }[];
}

export interface Agent8Data extends BaseAgent {
  campaigns: EmailCampaign[];
  lists: EmailList[];
  totalCampaigns: number;
  activeCampaigns: number;
  averageOpenRate: number;
  averageClickRate: number;
  totalSubscribers: number;
  bestPerformingCampaigns: EmailCampaign[];
}

// ==================== Agent 9: Analytics & Reporting ====================

export interface AnalyticsMetric {
  name: string;
  value: number;
  previousValue?: number;
  change?: number;
  changePercentage?: number;
  trend: 'up' | 'down' | 'stable';
  unit?: string;
}

export interface TrafficSource {
  source: string;
  medium: string;
  sessions: number;
  users: number;
  bounceRate: number;
  avgSessionDuration: number;
  conversions: number;
  revenue?: number;
}

export interface ConversionFunnel {
  stage: string;
  visitors: number;
  conversions: number;
  conversionRate: number;
  dropOff: number;
}

export interface AnalyticsReport {
  id: string;
  period: { start: Date; end: Date };
  metrics: AnalyticsMetric[];
  trafficSources: TrafficSource[];
  funnels: ConversionFunnel[];
  topPages: { url: string; pageviews: number; uniquePageviews: number }[];
  goals: { name: string; completions: number; value: number }[];
}

export interface Agent9Data extends BaseAgent {
  currentReport: AnalyticsReport;
  historicalReports: AnalyticsReport[];
  kpis: AnalyticsMetric[];
  insights: string[];
  recommendations: string[];
  dashboardUrl?: string;
}

// ==================== Agent 10: Campaign Management ====================

export enum CampaignType {
  BRAND_AWARENESS = 'brand_awareness',
  LEAD_GENERATION = 'lead_generation',
  PRODUCT_LAUNCH = 'product_launch',
  SALES = 'sales',
  RETENTION = 'retention',
  EVENT = 'event'
}

export enum CampaignStatus {
  PLANNING = 'planning',
  READY = 'ready',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export interface Campaign {
  id: string;
  name: string;
  type: CampaignType;
  status: CampaignStatus;
  objective: string;
  budget: {
    total: number;
    spent: number;
    currency: string;
  };
  duration: {
    startDate: Date;
    endDate: Date;
  };
  channels: string[];
  targetAudience: string[];
  kpis: {
    name: string;
    target: number;
    actual?: number;
    unit: string;
  }[];
  assets: {
    type: string;
    url: string;
    description?: string;
  }[];
  team: {
    role: string;
    name: string;
    email: string;
  }[];
  milestones: {
    name: string;
    date: Date;
    completed: boolean;
  }[];
  performance?: {
    impressions: number;
    clicks: number;
    conversions: number;
    roi: number;
    cpa: number;
  };
}

export interface Agent10Data extends BaseAgent {
  campaigns: Campaign[];
  activeCampaigns: number;
  totalBudget: number;
  totalSpent: number;
  avgROI: number;
  upcomingMilestones: { campaign: string; milestone: string; date: Date }[];
  campaignPerformance: { campaignId: string; score: number }[];
}

// ==================== Agent 11: Report Generation ====================

export enum ReportType {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  CUSTOM = 'custom',
  EXECUTIVE = 'executive',
  TECHNICAL = 'technical'
}

export enum ReportFormat {
  PDF = 'pdf',
  HTML = 'html',
  EXCEL = 'excel',
  CSV = 'csv',
  JSON = 'json'
}

export interface ReportSection {
  title: string;
  type: 'text' | 'chart' | 'table' | 'metrics';
  content: unknown;
  insights?: string[];
}

export interface Report {
  id: string;
  name: string;
  type: ReportType;
  format: ReportFormat;
  period: { start: Date; end: Date };
  sections: ReportSection[];
  recipients: string[];
  generatedAt: Date;
  generatedBy: string;
  url?: string;
  summary: string;
  highlights: string[];
  recommendations: string[];
  dataSource: string[];
}

export interface ReportTemplate {
  id: string;
  name: string;
  type: ReportType;
  sections: string[];
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string;
    recipients: string[];
  };
}

export interface Agent11Data extends BaseAgent {
  reports: Report[];
  templates: ReportTemplate[];
  scheduledReports: Report[];
  totalReportsGenerated: number;
  lastReportDate?: Date;
  popularTemplates: ReportTemplate[];
}

// ==================== Pipeline & System Types ====================

export interface PipelineConfig {
  agents: {
    [key: string]: {
      enabled: boolean;
      priority: Priority;
      dependencies: string[];
      config: Record<string, unknown>;
    };
  };
  executionOrder: string[];
  parallelExecution: boolean;
  retryPolicy: {
    maxRetries: number;
    retryDelay: number;
    backoffMultiplier: number;
  };
}

export interface PipelineExecution {
  id: string;
  startedAt: Date;
  completedAt?: Date;
  status: 'running' | 'completed' | 'failed' | 'paused';
  currentAgent?: string;
  completedAgents: string[];
  failedAgents: string[];
  results: {
    [agentId: string]: ProcessingResult;
  };
  logs: {
    timestamp: Date;
    level: 'info' | 'warn' | 'error';
    agent: string;
    message: string;
  }[];
}

export interface GoogleSheetsConfig {
  spreadsheetId: string;
  worksheets: {
    [agentId: string]: {
      sheetName: string;
      range: string;
      headers: string[];
    };
  };
  updateFrequency: number;
  autoSync: boolean;
}

// ==================== API Types ====================

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  timestamp: Date;
  requestId?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// ==================== Exports ====================

export type AgentData =
  | Agent1Data
  | Agent2Data
  | Agent3Data
  | Agent4Data
  | Agent5Data
  | Agent6Data
  | Agent7Data
  | Agent8Data
  | Agent9Data
  | Agent10Data
  | Agent11Data;

export interface AllAgentsData {
  agent1: Agent1Data;
  agent2: Agent2Data;
  agent3: Agent3Data;
  agent4: Agent4Data;
  agent5: Agent5Data;
  agent6: Agent6Data;
  agent7: Agent7Data;
  agent8: Agent8Data;
  agent9: Agent9Data;
  agent10: Agent10Data;
  agent11: Agent11Data;
}
