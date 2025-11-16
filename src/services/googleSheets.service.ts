/**
 * Google Sheets Integration Service
 */

import { google, sheets_v4 } from 'googleapis';
import { JWT } from 'google-auth-library';
import { config } from '../config';
import { logger } from '../utils/logger';
import {
  AllAgentsData,
  Lead,
  QualifiedLead,
  Competitor,
  MarketSegment,
  ContentPiece,
  SocialPost,
  EmailCampaign,
  Campaign,
  Report
} from '../types';

export class GoogleSheetsService {
  private sheets: sheets_v4.Sheets | null = null;
  private auth: JWT | null = null;
  private spreadsheetId: string;

  constructor() {
    this.spreadsheetId = config.googleSheets.spreadsheetId;
  }

  /**
   * Initialize Google Sheets API client
   */
  async initialize(): Promise<void> {
    try {
      // In production, load credentials from file
      // For now, we'll use a placeholder
      logger.info('Google Sheets Service: Initialization (credentials required for production)');

      // Uncomment this when credentials are available:
      /*
      const credentials = require(config.googleSheets.credentialsPath);
      this.auth = new google.auth.JWT(
        credentials.client_email,
        undefined,
        credentials.private_key,
        ['https://www.googleapis.com/auth/spreadsheets']
      );

      await this.auth.authorize();
      this.sheets = google.sheets({ version: 'v4', auth: this.auth });
      logger.info('Google Sheets Service: Initialized successfully');
      */
    } catch (error) {
      logger.error('Google Sheets Service: Initialization failed', { error });
      throw error;
    }
  }

  /**
   * Sync all agent data to Google Sheets
   */
  async syncAllAgents(data: AllAgentsData): Promise<void> {
    try {
      logger.info('Google Sheets Service: Starting full sync');

      await Promise.all([
        this.syncAgent1Data(data.agent1.leads),
        this.syncAgent2Data(data.agent2.qualifiedLeads),
        this.syncAgent3Data(data.agent3.competitors),
        this.syncAgent4Data(data.agent4.segments),
        this.syncAgent5Data(data.agent5.contentPieces),
        this.syncAgent6Data(data.agent6.keywords),
        this.syncAgent7Data(data.agent7.posts),
        this.syncAgent8Data(data.agent8.campaigns),
        this.syncAgent9Data(data.agent9.currentReport),
        this.syncAgent10Data(data.agent10.campaigns),
        this.syncAgent11Data(data.agent11.reports)
      ]);

      logger.info('Google Sheets Service: Full sync completed');
    } catch (error) {
      logger.error('Google Sheets Service: Sync failed', { error });
      throw error;
    }
  }

  /**
   * Sync Agent 1 (Lead Generation) data
   */
  private async syncAgent1Data(leads: Lead[]): Promise<void> {
    const sheetName = 'Agent 1 - Leads';
    const headers = ['ID', 'First Name', 'Last Name', 'Email', 'Company', 'Source', 'Score', 'Created At'];
    const rows = leads.map(lead => [
      lead.id,
      lead.firstName,
      lead.lastName,
      lead.email,
      lead.company || '',
      lead.source.name,
      lead.score || 0,
      lead.createdAt.toISOString()
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 2 (Lead Qualification) data
   */
  private async syncAgent2Data(leads: QualifiedLead[]): Promise<void> {
    const sheetName = 'Agent 2 - Qualified Leads';
    const headers = ['ID', 'Email', 'Status', 'Score', 'Assigned To', 'Next Action', 'Qualified At'];
    const rows = leads.map(lead => [
      lead.id,
      lead.email,
      lead.qualificationStatus,
      lead.qualificationScore,
      lead.assignedTo || '',
      lead.nextAction || '',
      lead.qualifiedAt?.toISOString() || ''
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 3 (Competitor Analysis) data
   */
  private async syncAgent3Data(competitors: Competitor[]): Promise<void> {
    const sheetName = 'Agent 3 - Competitors';
    const headers = ['ID', 'Name', 'Website', 'Industry', 'Market Share', 'Products', 'Last Updated'];
    const rows = competitors.map(comp => [
      comp.id,
      comp.name,
      comp.website,
      comp.industry,
      comp.marketShare || 0,
      comp.products.join(', '),
      comp.lastUpdated.toISOString()
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 4 (Market Research) data
   */
  private async syncAgent4Data(segments: MarketSegment[]): Promise<void> {
    const sheetName = 'Agent 4 - Market Segments';
    const headers = ['ID', 'Name', 'Size', 'Growth Rate', 'Pain Points'];
    const rows = segments.map(seg => [
      seg.id,
      seg.name,
      seg.size,
      seg.growthRate,
      seg.painPoints.join(', ')
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 5 (Content Strategy) data
   */
  private async syncAgent5Data(content: ContentPiece[]): Promise<void> {
    const sheetName = 'Agent 5 - Content';
    const headers = ['ID', 'Title', 'Type', 'Status', 'Author', 'Publish Date', 'Views'];
    const rows = content.map(c => [
      c.id,
      c.title,
      c.type,
      c.status,
      c.author || '',
      c.publishDate?.toISOString() || '',
      c.performance?.views || 0
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 6 (SEO) data
   */
  private async syncAgent6Data(keywords: any[]): Promise<void> {
    const sheetName = 'Agent 6 - SEO Keywords';
    const headers = ['Keyword', 'Search Volume', 'Difficulty', 'Ranking', 'Last Checked'];
    const rows = keywords.map(k => [
      k.keyword,
      k.searchVolume,
      k.difficulty,
      k.ranking || '-',
      k.lastChecked.toISOString()
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 7 (Social Media) data
   */
  private async syncAgent7Data(posts: SocialPost[]): Promise<void> {
    const sheetName = 'Agent 7 - Social Posts';
    const headers = ['ID', 'Platform', 'Content', 'Status', 'Scheduled Date', 'Likes', 'Shares'];
    const rows = posts.map(p => [
      p.id,
      p.platform,
      p.content.substring(0, 50) + '...',
      p.status,
      p.scheduledDate.toISOString(),
      p.engagement?.likes || 0,
      p.engagement?.shares || 0
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 8 (Email Marketing) data
   */
  private async syncAgent8Data(campaigns: EmailCampaign[]): Promise<void> {
    const sheetName = 'Agent 8 - Email Campaigns';
    const headers = ['ID', 'Name', 'Type', 'Status', 'Sent', 'Open Rate', 'Click Rate'];
    const rows = campaigns.map(c => [
      c.id,
      c.name,
      c.type,
      c.status,
      c.metrics?.sent || 0,
      c.metrics?.openRate || 0,
      c.metrics?.clickRate || 0
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 9 (Analytics) data
   */
  private async syncAgent9Data(report: any): Promise<void> {
    const sheetName = 'Agent 9 - Analytics';
    const headers = ['Metric', 'Value', 'Trend'];
    const rows = report.metrics?.map((m: any) => [
      m.name,
      m.value,
      m.trend
    ]) || [];

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 10 (Campaign Management) data
   */
  private async syncAgent10Data(campaigns: Campaign[]): Promise<void> {
    const sheetName = 'Agent 10 - Campaigns';
    const headers = ['ID', 'Name', 'Type', 'Status', 'Budget', 'Spent', 'ROI'];
    const rows = campaigns.map(c => [
      c.id,
      c.name,
      c.type,
      c.status,
      c.budget.total,
      c.budget.spent,
      c.performance?.roi || 0
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Sync Agent 11 (Reports) data
   */
  private async syncAgent11Data(reports: Report[]): Promise<void> {
    const sheetName = 'Agent 11 - Reports';
    const headers = ['ID', 'Name', 'Type', 'Format', 'Generated At', 'Recipients'];
    const rows = reports.map(r => [
      r.id,
      r.name,
      r.type,
      r.format,
      r.generatedAt.toISOString(),
      r.recipients.join(', ')
    ]);

    await this.writeToSheet(sheetName, headers, rows);
  }

  /**
   * Write data to a specific sheet
   */
  private async writeToSheet(sheetName: string, headers: string[], rows: any[][]): Promise<void> {
    try {
      if (!this.sheets) {
        logger.warn(`Google Sheets Service: Not initialized, skipping write to ${sheetName}`);
        return;
      }

      const values = [headers, ...rows];

      await this.sheets.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!A1`,
        valueInputOption: 'RAW',
        requestBody: { values }
      });

      logger.info(`Google Sheets Service: Updated ${sheetName} with ${rows.length} rows`);
    } catch (error) {
      logger.error(`Google Sheets Service: Failed to write to ${sheetName}`, { error });
      // Don't throw - allow other syncs to continue
    }
  }

  /**
   * Create all required sheets
   */
  async setupSheets(): Promise<void> {
    const sheetNames = [
      'Agent 1 - Leads',
      'Agent 2 - Qualified Leads',
      'Agent 3 - Competitors',
      'Agent 4 - Market Segments',
      'Agent 5 - Content',
      'Agent 6 - SEO Keywords',
      'Agent 7 - Social Posts',
      'Agent 8 - Email Campaigns',
      'Agent 9 - Analytics',
      'Agent 10 - Campaigns',
      'Agent 11 - Reports'
    ];

    logger.info('Google Sheets Service: Setup instructions');
    logger.info('Create the following sheets in your spreadsheet:');
    sheetNames.forEach(name => logger.info(`  - ${name}`));
  }
}

export const googleSheetsService = new GoogleSheetsService();
