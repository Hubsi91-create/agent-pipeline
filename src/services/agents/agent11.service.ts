/**
 * Agent 11: Report Generation Service
 */

import { Agent11Data, Report, ReportTemplate, ReportType, ReportFormat, AgentStatus, ProcessingResult } from '../../types';
import { logger } from '../../utils/logger';

export class Agent11Service {
  private data: Agent11Data;

  constructor() {
    this.data = {
      id: 'agent-11',
      name: 'Report Generation Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      reports: [],
      templates: [],
      scheduledReports: [],
      totalReportsGenerated: 0,
      popularTemplates: []
    };
  }

  async generateReport(config: {
    name: string;
    type: ReportType;
    format: ReportFormat;
    period: { start: Date; end: Date };
    dataSource: string[];
    recipients: string[];
  }): Promise<ProcessingResult<Report>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 11: Generating ${config.type} report`);

      const sections = this.generateSections(config.type);
      const summary = this.generateSummary(sections);
      const highlights = this.extractHighlights(sections);
      const recommendations = this.generateRecommendations(sections);

      const report: Report = {
        id: `report-${Date.now()}`,
        name: config.name,
        type: config.type,
        format: config.format,
        period: config.period,
        sections,
        recipients: config.recipients,
        generatedAt: new Date(),
        generatedBy: 'Agent 11',
        summary,
        highlights,
        recommendations,
        dataSource: config.dataSource
      };

      this.data.reports.push(report);
      this.data.totalReportsGenerated++;
      this.data.lastReportDate = new Date();
      this.data.status = AgentStatus.COMPLETED;
      this.data.updatedAt = new Date();

      logger.info(`Agent 11: Report generated successfully (${config.format})`);

      return {
        success: true,
        data: report,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  async createTemplate(template: Omit<ReportTemplate, 'id'>): Promise<ProcessingResult<ReportTemplate>> {
    try {
      const newTemplate: ReportTemplate = {
        ...template,
        id: `template-${Date.now()}`
      };

      this.data.templates.push(newTemplate);
      this.updatePopularTemplates();
      this.data.updatedAt = new Date();

      logger.info(`Agent 11: Created report template ${template.name}`);

      return {
        success: true,
        data: newTemplate,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  async scheduleReport(
    templateId: string,
    config: { period: { start: Date; end: Date }; recipients: string[] }
  ): Promise<ProcessingResult<Report>> {
    try {
      const template = this.data.templates.find(t => t.id === templateId);
      if (!template) throw new Error('Template not found');

      const report = await this.generateReportFromTemplate(template, config);

      if (report.success && report.data) {
        this.data.scheduledReports.push(report.data);
        this.data.updatedAt = new Date();
      }

      return report;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  private async generateReportFromTemplate(
    template: ReportTemplate,
    config: { period: { start: Date; end: Date }; recipients: string[] }
  ): Promise<ProcessingResult<Report>> {
    return this.generateReport({
      name: template.name,
      type: template.type,
      format: ReportFormat.PDF,
      period: config.period,
      dataSource: ['all'],
      recipients: config.recipients
    });
  }

  private generateSections(type: ReportType) {
    const sections = [
      {
        title: 'Executive Summary',
        type: 'text' as const,
        content: 'Overview of key metrics and performance indicators',
        insights: ['Strong growth in key metrics', 'Improved conversion rates']
      },
      {
        title: 'Key Metrics',
        type: 'metrics' as const,
        content: { totalRevenue: 50000, leads: 1000, conversions: 250 }
      },
      {
        title: 'Performance Charts',
        type: 'chart' as const,
        content: { chartType: 'line', data: [/* chart data */] }
      },
      {
        title: 'Detailed Analytics',
        type: 'table' as const,
        content: { headers: ['Metric', 'Value', 'Change'], rows: [] }
      }
    ];

    return type === ReportType.EXECUTIVE ? sections.slice(0, 2) : sections;
  }

  private generateSummary(sections: Report['sections']): string {
    return `This report provides a comprehensive analysis of performance metrics and key insights. The data shows positive trends across multiple indicators with notable improvements in conversion rates and user engagement.`;
  }

  private extractHighlights(sections: Report['sections']): string[] {
    return [
      'Revenue increased by 25% compared to previous period',
      'Lead generation exceeded targets by 15%',
      'Customer engagement improved across all channels',
      'Campaign ROI shows consistent growth',
      'New market segments identified for expansion'
    ];
  }

  private generateRecommendations(sections: Report['sections']): string[] {
    return [
      'Continue investing in high-performing channels',
      'Optimize conversion funnel to reduce drop-off',
      'Expand successful campaigns to new markets',
      'Increase focus on customer retention strategies',
      'Leverage data insights for personalized marketing'
    ];
  }

  private updatePopularTemplates(): void {
    // Track template usage and identify popular ones
    const templateUsage = new Map<string, number>();

    this.data.reports.forEach(report => {
      const matchingTemplate = this.data.templates.find(t =>
        t.type === report.type && t.name === report.name
      );

      if (matchingTemplate) {
        const count = templateUsage.get(matchingTemplate.id) || 0;
        templateUsage.set(matchingTemplate.id, count + 1);
      }
    });

    this.data.popularTemplates = this.data.templates
      .sort((a, b) => (templateUsage.get(b.id) || 0) - (templateUsage.get(a.id) || 0))
      .slice(0, 5);
  }

  getReports(filters?: { type?: ReportType; format?: ReportFormat }): Report[] {
    let reports = [...this.data.reports];

    if (filters) {
      if (filters.type) reports = reports.filter(r => r.type === filters.type);
      if (filters.format) reports = reports.filter(r => r.format === filters.format);
    }

    return reports.sort((a, b) => b.generatedAt.getTime() - a.generatedAt.getTime());
  }

  getTemplates(): ReportTemplate[] {
    return [...this.data.templates];
  }

  getData(): Agent11Data {
    return { ...this.data };
  }

  getStatistics() {
    return {
      totalReports: this.data.totalReportsGenerated,
      recentReports: this.data.reports.slice(-10).reverse(),
      totalTemplates: this.data.templates.length,
      scheduledReports: this.data.scheduledReports.length,
      popularTemplates: this.data.popularTemplates,
      lastReportDate: this.data.lastReportDate,
      reportsByType: this.getReportsByType(),
      reportsByFormat: this.getReportsByFormat()
    };
  }

  private getReportsByType() {
    const counts: Record<string, number> = {};
    this.data.reports.forEach(report => {
      counts[report.type] = (counts[report.type] || 0) + 1;
    });
    return counts;
  }

  private getReportsByFormat() {
    const counts: Record<string, number> = {};
    this.data.reports.forEach(report => {
      counts[report.format] = (counts[report.format] || 0) + 1;
    });
    return counts;
  }
}

export const agent11Service = new Agent11Service();
