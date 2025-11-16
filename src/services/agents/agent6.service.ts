/**
 * Agent 6: SEO Optimization Service
 */

import { Agent6Data, SEOKeyword, SEOPage, AgentStatus, ProcessingResult } from '../../types';
import { logger } from '../../utils/logger';

export class Agent6Service {
  private data: Agent6Data;

  constructor() {
    this.data = {
      id: 'agent-6',
      name: 'SEO Optimization Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      keywords: [],
      pages: [],
      metrics: {
        organicTraffic: 0,
        averagePosition: 0,
        totalKeywords: 0,
        topRankingKeywords: 0,
        domainAuthority: 0,
        totalBacklinks: 0,
        technicalScore: 0
      },
      competitorKeywords: [],
      optimizationTasks: []
    };
  }

  async addKeyword(keyword: Omit<SEOKeyword, 'lastChecked'>): Promise<ProcessingResult<SEOKeyword>> {
    try {
      const newKeyword: SEOKeyword = { ...keyword, lastChecked: new Date() };
      this.data.keywords.push(newKeyword);
      this.data.metrics.totalKeywords++;
      if (keyword.ranking && keyword.ranking <= 3) this.data.metrics.topRankingKeywords++;
      this.data.updatedAt = new Date();

      logger.info(`Agent 6: Added keyword ${keyword.keyword}`);
      return { success: true, data: newKeyword, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  async analyzePage(page: Omit<SEOPage, 'recommendations'>): Promise<ProcessingResult<SEOPage>> {
    try {
      const recommendations = this.generateRecommendations(page);
      const newPage: SEOPage = { ...page, recommendations };
      this.data.pages.push(newPage);
      this.updateOptimizationTasks();
      this.data.updatedAt = new Date();

      logger.info(`Agent 6: Analyzed page ${page.url}`);
      return { success: true, data: newPage, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  private generateRecommendations(page: Partial<SEOPage>): string[] {
    const recommendations: string[] = [];
    if (page.loadTime && page.loadTime > 3) recommendations.push('Improve page load time');
    if (!page.mobileOptimized) recommendations.push('Optimize for mobile devices');
    if (page.pageAuthority && page.pageAuthority < 30) recommendations.push('Build more quality backlinks');
    if (page.keywords && page.keywords.length < 3) recommendations.push('Add more relevant keywords');
    return recommendations;
  }

  private updateOptimizationTasks(): void {
    this.data.optimizationTasks = this.data.pages
      .flatMap(p => p.recommendations)
      .filter((task, index, self) => self.indexOf(task) === index)
      .slice(0, 20);
  }

  updateMetrics(metrics: Partial<Agent6Data['metrics']>): void {
    this.data.metrics = { ...this.data.metrics, ...metrics };
    this.data.updatedAt = new Date();
  }

  getData(): Agent6Data {
    return { ...this.data };
  }

  getStatistics() {
    return {
      ...this.data.metrics,
      totalPages: this.data.pages.length,
      avgKeywordDifficulty: this.calculateAvgDifficulty(),
      optimizationTasks: this.data.optimizationTasks.slice(0, 10)
    };
  }

  private calculateAvgDifficulty(): number {
    if (this.data.keywords.length === 0) return 0;
    return this.data.keywords.reduce((sum, k) => sum + k.difficulty, 0) / this.data.keywords.length;
  }
}

export const agent6Service = new Agent6Service();
