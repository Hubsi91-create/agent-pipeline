/**
 * Agent 3: Competitor Analysis Service
 * Analyzes competitors and provides market intelligence
 */

import {
  Agent3Data,
  Competitor,
  CompetitorAnalysis,
  AgentStatus,
  ProcessingResult
} from '../../types';
import { logger } from '../../utils/logger';

export class Agent3Service {
  private data: Agent3Data;

  constructor() {
    this.data = this.initializeData();
  }

  private initializeData(): Agent3Data {
    return {
      id: 'agent-3',
      name: 'Competitor Analysis Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      competitors: [],
      analyses: [],
      totalCompetitorsTracked: 0,
      marketInsights: []
    };
  }

  /**
   * Add a new competitor to track
   */
  async addCompetitor(competitor: Omit<Competitor, 'id' | 'lastUpdated'>): Promise<ProcessingResult<Competitor>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 3: Adding competitor ${competitor.name}`);

      const newCompetitor: Competitor = {
        ...competitor,
        id: `competitor-${Date.now()}`,
        lastUpdated: new Date()
      };

      this.data.competitors.push(newCompetitor);
      this.data.totalCompetitorsTracked++;
      this.data.updatedAt = new Date();
      this.data.status = AgentStatus.COMPLETED;

      const processingTime = Date.now() - startTime;

      logger.info(`Agent 3: Added competitor ${competitor.name}`);

      return {
        success: true,
        data: newCompetitor,
        timestamp: new Date(),
        processingTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      logger.error(`Agent 3: Error adding competitor: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Analyze a competitor
   */
  async analyzeCompetitor(competitorId: string): Promise<ProcessingResult<CompetitorAnalysis>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 3: Analyzing competitor ${competitorId}`);

      const competitor = this.data.competitors.find(c => c.id === competitorId);
      if (!competitor) {
        throw new Error(`Competitor with ID ${competitorId} not found`);
      }

      // Perform SWOT analysis
      const swotAnalysis = this.performSWOTAnalysis(competitor);

      // Determine market position
      const marketPosition = this.determineMarketPosition(competitor);

      // Identify competitive advantages
      const competitiveAdvantages = this.identifyCompetitiveAdvantages(competitor);

      // Generate recommendations
      const recommendations = this.generateRecommendations(competitor, swotAnalysis);

      const analysis: CompetitorAnalysis = {
        competitor,
        swotAnalysis,
        marketPosition,
        competitiveAdvantages,
        recommendations
      };

      // Check if analysis already exists for this competitor
      const existingIndex = this.data.analyses.findIndex(
        a => a.competitor.id === competitorId
      );

      if (existingIndex !== -1) {
        this.data.analyses[existingIndex] = analysis;
      } else {
        this.data.analyses.push(analysis);
      }

      // Update market insights
      this.updateMarketInsights();

      this.data.lastAnalysisDate = new Date();
      this.data.updatedAt = new Date();
      this.data.status = AgentStatus.COMPLETED;

      const processingTime = Date.now() - startTime;

      logger.info(`Agent 3: Completed analysis for ${competitor.name} in ${processingTime}ms`);

      return {
        success: true,
        data: analysis,
        timestamp: new Date(),
        processingTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      logger.error(`Agent 3: Error analyzing competitor: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Perform SWOT analysis on competitor
   */
  private performSWOTAnalysis(competitor: Competitor) {
    return {
      strengths: competitor.strengths,
      weaknesses: competitor.weaknesses,
      opportunities: [
        'Market gap identification',
        'Potential partnership opportunities',
        'Emerging market segments'
      ],
      threats: [
        'Aggressive pricing strategies',
        'Strong brand presence',
        'Established customer base'
      ]
    };
  }

  /**
   * Determine market position
   */
  private determineMarketPosition(competitor: Competitor): 'leader' | 'challenger' | 'follower' | 'nicher' {
    const marketShare = competitor.marketShare || 0;

    if (marketShare >= 30) return 'leader';
    if (marketShare >= 15) return 'challenger';
    if (marketShare >= 5) return 'follower';
    return 'nicher';
  }

  /**
   * Identify competitive advantages
   */
  private identifyCompetitiveAdvantages(competitor: Competitor): string[] {
    const advantages: string[] = [];

    if (competitor.strengths.length > 3) {
      advantages.push('Strong capability portfolio');
    }

    if (competitor.marketShare && competitor.marketShare > 20) {
      advantages.push('Significant market share');
    }

    if (competitor.products.length > 5) {
      advantages.push('Diverse product portfolio');
    }

    if (competitor.marketingChannels.length > 4) {
      advantages.push('Multi-channel presence');
    }

    return advantages;
  }

  /**
   * Generate strategic recommendations
   */
  private generateRecommendations(competitor: Competitor, swot: CompetitorAnalysis['swotAnalysis']): string[] {
    const recommendations: string[] = [];

    // Analyze weaknesses
    competitor.weaknesses.forEach(weakness => {
      recommendations.push(`Capitalize on competitor weakness: ${weakness}`);
    });

    // Pricing recommendations
    if (competitor.pricing) {
      recommendations.push(
        `Consider competitive pricing strategy relative to ${competitor.name}'s ${competitor.pricing.model} model`
      );
    }

    // Product recommendations
    if (competitor.products.length > 0) {
      recommendations.push(
        'Develop differentiated features not offered by competitor'
      );
    }

    // Market recommendations
    recommendations.push('Focus on underserved market segments');
    recommendations.push('Strengthen unique value proposition');

    return recommendations;
  }

  /**
   * Update market insights based on all analyses
   */
  private updateMarketInsights(): void {
    const insights: string[] = [];

    // Market position insights
    const leaders = this.data.analyses.filter(a => a.marketPosition === 'leader');
    if (leaders.length > 0) {
      insights.push(`${leaders.length} market leaders identified`);
    }

    // Common strengths
    const allStrengths = this.data.analyses.flatMap(a => a.competitor.strengths);
    const strengthCounts = this.countOccurrences(allStrengths);
    const topStrength = this.getMostCommon(strengthCounts);
    if (topStrength) {
      insights.push(`Most common competitor strength: ${topStrength}`);
    }

    // Market gaps
    insights.push('Identified opportunities in underserved segments');

    this.data.marketInsights = insights;
  }

  /**
   * Get all competitors
   */
  getCompetitors(): Competitor[] {
    return [...this.data.competitors];
  }

  /**
   * Get competitor by ID
   */
  getCompetitorById(id: string): Competitor | undefined {
    return this.data.competitors.find(c => c.id === id);
  }

  /**
   * Get all analyses
   */
  getAnalyses(): CompetitorAnalysis[] {
    return [...this.data.analyses];
  }

  /**
   * Get analysis for specific competitor
   */
  getAnalysisForCompetitor(competitorId: string): CompetitorAnalysis | undefined {
    return this.data.analyses.find(a => a.competitor.id === competitorId);
  }

  /**
   * Update competitor information
   */
  async updateCompetitor(
    id: string,
    updates: Partial<Competitor>
  ): Promise<ProcessingResult<Competitor>> {
    try {
      const index = this.data.competitors.findIndex(c => c.id === id);

      if (index === -1) {
        throw new Error(`Competitor with ID ${id} not found`);
      }

      this.data.competitors[index] = {
        ...this.data.competitors[index],
        ...updates,
        lastUpdated: new Date()
      };

      this.data.updatedAt = new Date();

      logger.info(`Agent 3: Updated competitor ${id}`);

      return {
        success: true,
        data: this.data.competitors[index],
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 3: Error updating competitor: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Delete competitor
   */
  async deleteCompetitor(id: string): Promise<ProcessingResult<void>> {
    try {
      const initialLength = this.data.competitors.length;
      this.data.competitors = this.data.competitors.filter(c => c.id !== id);

      if (this.data.competitors.length === initialLength) {
        throw new Error(`Competitor with ID ${id} not found`);
      }

      // Also remove associated analysis
      this.data.analyses = this.data.analyses.filter(a => a.competitor.id !== id);

      this.data.updatedAt = new Date();

      logger.info(`Agent 3: Deleted competitor ${id}`);

      return {
        success: true,
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 3: Error deleting competitor: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Get agent data
   */
  getData(): Agent3Data {
    return { ...this.data };
  }

  /**
   * Get agent statistics
   */
  getStatistics() {
    return {
      totalCompetitors: this.data.totalCompetitorsTracked,
      totalAnalyses: this.data.analyses.length,
      marketInsights: this.data.marketInsights,
      lastAnalysisDate: this.data.lastAnalysisDate,
      competitorsByPosition: this.getCompetitorsByPosition(),
      topCompetitors: this.getTopCompetitors(5)
    };
  }

  /**
   * Group competitors by market position
   */
  private getCompetitorsByPosition() {
    const positions = {
      leader: 0,
      challenger: 0,
      follower: 0,
      nicher: 0
    };

    this.data.analyses.forEach(analysis => {
      positions[analysis.marketPosition]++;
    });

    return positions;
  }

  /**
   * Get top competitors by market share
   */
  private getTopCompetitors(limit: number): Competitor[] {
    return [...this.data.competitors]
      .sort((a, b) => (b.marketShare || 0) - (a.marketShare || 0))
      .slice(0, limit);
  }

  /**
   * Utility: Count occurrences in array
   */
  private countOccurrences(arr: string[]): Map<string, number> {
    const counts = new Map<string, number>();
    arr.forEach(item => {
      counts.set(item, (counts.get(item) || 0) + 1);
    });
    return counts;
  }

  /**
   * Utility: Get most common item
   */
  private getMostCommon(counts: Map<string, number>): string | null {
    let max = 0;
    let mostCommon: string | null = null;

    counts.forEach((count, item) => {
      if (count > max) {
        max = count;
        mostCommon = item;
      }
    });

    return mostCommon;
  }
}

export const agent3Service = new Agent3Service();
