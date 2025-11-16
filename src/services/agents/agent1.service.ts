/**
 * Agent 1: Lead Generation Service
 * Handles lead generation, collection, and initial data processing
 */

import {
  Agent1Data,
  Lead,
  LeadSource,
  AgentStatus,
  ProcessingResult
} from '../../types';
import { logger } from '../../utils/logger';

export class Agent1Service {
  private data: Agent1Data;

  constructor() {
    this.data = this.initializeData();
  }

  private initializeData(): Agent1Data {
    return {
      id: 'agent-1',
      name: 'Lead Generation Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      leads: [],
      totalLeadsGenerated: 0,
      leadsToday: 0,
      topSources: [],
      conversionRate: 0
    };
  }

  /**
   * Generate new leads from various sources
   */
  async generateLeads(sources: LeadSource[]): Promise<ProcessingResult<Lead[]>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 1: Generating leads from ${sources.length} sources`);

      const newLeads: Lead[] = [];

      for (const source of sources) {
        // Simulate lead generation (in production, this would call real APIs)
        const generatedLeads = await this.fetchLeadsFromSource(source);
        newLeads.push(...generatedLeads);
      }

      // Update data
      this.data.leads.push(...newLeads);
      this.data.totalLeadsGenerated += newLeads.length;
      this.data.leadsToday += newLeads.length;
      this.data.updatedAt = new Date();
      this.data.status = AgentStatus.COMPLETED;

      // Update top sources
      this.updateTopSources();

      const processingTime = Date.now() - startTime;

      logger.info(`Agent 1: Generated ${newLeads.length} leads in ${processingTime}ms`);

      return {
        success: true,
        data: newLeads,
        timestamp: new Date(),
        processingTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      logger.error(`Agent 1: Error generating leads: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Fetch leads from a specific source
   */
  private async fetchLeadsFromSource(source: LeadSource): Promise<Lead[]> {
    // Simulate API call or data collection
    // In production, this would integrate with actual lead sources

    const mockLeads: Lead[] = [];
    const leadsCount = Math.floor(Math.random() * 10) + 1;

    for (let i = 0; i < leadsCount; i++) {
      mockLeads.push({
        id: `lead-${Date.now()}-${i}`,
        firstName: `FirstName${i}`,
        lastName: `LastName${i}`,
        email: `lead${i}@example.com`,
        phone: `+1-555-${Math.floor(Math.random() * 10000)}`,
        company: `Company ${i}`,
        jobTitle: 'Marketing Manager',
        source,
        score: Math.floor(Math.random() * 100),
        tags: ['new', source.type],
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }

    return mockLeads;
  }

  /**
   * Add a single lead manually
   */
  async addLead(lead: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>): Promise<ProcessingResult<Lead>> {
    try {
      const newLead: Lead = {
        ...lead,
        id: `lead-${Date.now()}`,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      this.data.leads.push(newLead);
      this.data.totalLeadsGenerated++;
      this.data.leadsToday++;
      this.data.updatedAt = new Date();

      logger.info(`Agent 1: Added lead ${newLead.email}`);

      return {
        success: true,
        data: newLead,
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 1: Error adding lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Get all leads with optional filtering
   */
  getLeads(filters?: { source?: string; minScore?: number; tags?: string[] }): Lead[] {
    let leads = [...this.data.leads];

    if (filters) {
      if (filters.source) {
        leads = leads.filter(lead => lead.source.name === filters.source);
      }
      if (filters.minScore !== undefined) {
        leads = leads.filter(lead => (lead.score || 0) >= filters.minScore!);
      }
      if (filters.tags && filters.tags.length > 0) {
        leads = leads.filter(lead =>
          filters.tags!.some(tag => lead.tags?.includes(tag))
        );
      }
    }

    return leads;
  }

  /**
   * Get lead by ID
   */
  getLeadById(id: string): Lead | undefined {
    return this.data.leads.find(lead => lead.id === id);
  }

  /**
   * Update lead information
   */
  async updateLead(id: string, updates: Partial<Lead>): Promise<ProcessingResult<Lead>> {
    try {
      const leadIndex = this.data.leads.findIndex(lead => lead.id === id);

      if (leadIndex === -1) {
        throw new Error(`Lead with ID ${id} not found`);
      }

      this.data.leads[leadIndex] = {
        ...this.data.leads[leadIndex],
        ...updates,
        updatedAt: new Date()
      };

      this.data.updatedAt = new Date();

      logger.info(`Agent 1: Updated lead ${id}`);

      return {
        success: true,
        data: this.data.leads[leadIndex],
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 1: Error updating lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Delete a lead
   */
  async deleteLead(id: string): Promise<ProcessingResult<void>> {
    try {
      const initialLength = this.data.leads.length;
      this.data.leads = this.data.leads.filter(lead => lead.id !== id);

      if (this.data.leads.length === initialLength) {
        throw new Error(`Lead with ID ${id} not found`);
      }

      this.data.updatedAt = new Date();

      logger.info(`Agent 1: Deleted lead ${id}`);

      return {
        success: true,
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 1: Error deleting lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Calculate and update conversion rate
   */
  updateConversionRate(qualifiedLeads: number): void {
    if (this.data.totalLeadsGenerated > 0) {
      this.data.conversionRate = (qualifiedLeads / this.data.totalLeadsGenerated) * 100;
    }
  }

  /**
   * Update top performing sources
   */
  private updateTopSources(): void {
    const sourceCounts = new Map<string, { source: LeadSource; count: number }>();

    this.data.leads.forEach(lead => {
      const sourceKey = lead.source.name;
      const existing = sourceCounts.get(sourceKey);

      if (existing) {
        existing.count++;
      } else {
        sourceCounts.set(sourceKey, { source: lead.source, count: 1 });
      }
    });

    this.data.topSources = Array.from(sourceCounts.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
      .map(item => item.source);
  }

  /**
   * Reset daily lead count (should be called daily)
   */
  resetDailyCount(): void {
    this.data.leadsToday = 0;
    logger.info('Agent 1: Daily lead count reset');
  }

  /**
   * Get agent data
   */
  getData(): Agent1Data {
    return { ...this.data };
  }

  /**
   * Get agent statistics
   */
  getStatistics() {
    return {
      totalLeads: this.data.totalLeadsGenerated,
      leadsToday: this.data.leadsToday,
      averageScore: this.calculateAverageScore(),
      topSources: this.data.topSources,
      conversionRate: this.data.conversionRate,
      leadsBySource: this.getLeadsBySource(),
      recentLeads: this.data.leads.slice(-10).reverse()
    };
  }

  /**
   * Calculate average lead score
   */
  private calculateAverageScore(): number {
    const leadsWithScore = this.data.leads.filter(lead => lead.score !== undefined);
    if (leadsWithScore.length === 0) return 0;

    const totalScore = leadsWithScore.reduce((sum, lead) => sum + (lead.score || 0), 0);
    return totalScore / leadsWithScore.length;
  }

  /**
   * Group leads by source
   */
  private getLeadsBySource(): { source: string; count: number }[] {
    const sourceMap = new Map<string, number>();

    this.data.leads.forEach(lead => {
      const count = sourceMap.get(lead.source.name) || 0;
      sourceMap.set(lead.source.name, count + 1);
    });

    return Array.from(sourceMap.entries())
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count);
  }
}

export const agent1Service = new Agent1Service();
