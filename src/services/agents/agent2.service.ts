/**
 * Agent 2: Lead Qualification Service
 * Qualifies leads based on defined criteria and scoring
 */

import {
  Agent2Data,
  QualifiedLead,
  Lead,
  QualificationStatus,
  QualificationCriteria,
  AgentStatus,
  ProcessingResult
} from '../../types';
import { logger } from '../../utils/logger';

export class Agent2Service {
  private data: Agent2Data;

  constructor() {
    this.data = this.initializeData();
  }

  private initializeData(): Agent2Data {
    return {
      id: 'agent-2',
      name: 'Lead Qualification Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      qualifiedLeads: [],
      totalQualified: 0,
      totalUnqualified: 0,
      totalNurture: 0,
      qualificationRate: 0,
      averageScore: 0
    };
  }

  /**
   * Qualify a lead based on criteria
   */
  async qualifyLead(
    lead: Lead,
    criteria: QualificationCriteria
  ): Promise<ProcessingResult<QualifiedLead>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 2: Qualifying lead ${lead.email}`);

      // Calculate qualification score
      const score = this.calculateQualificationScore(lead, criteria);
      const status = this.determineQualificationStatus(score);

      const qualifiedLead: QualifiedLead = {
        ...lead,
        qualificationStatus: status,
        qualificationScore: score,
        criteria,
        qualifiedAt: new Date()
      };

      // Add recommendations
      qualifiedLead.notes = this.generateNotes(qualifiedLead);
      qualifiedLead.nextAction = this.determineNextAction(status);

      // Update data
      this.data.qualifiedLeads.push(qualifiedLead);

      switch (status) {
        case QualificationStatus.QUALIFIED:
          this.data.totalQualified++;
          break;
        case QualificationStatus.UNQUALIFIED:
          this.data.totalUnqualified++;
          break;
        case QualificationStatus.NURTURE:
          this.data.totalNurture++;
          break;
      }

      this.updateStatistics();
      this.data.status = AgentStatus.COMPLETED;
      this.data.updatedAt = new Date();

      const processingTime = Date.now() - startTime;

      logger.info(`Agent 2: Qualified lead ${lead.email} with score ${score} (${status})`);

      return {
        success: true,
        data: qualifiedLead,
        timestamp: new Date(),
        processingTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      logger.error(`Agent 2: Error qualifying lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Qualify multiple leads in batch
   */
  async qualifyLeads(
    leads: Lead[],
    criteria: QualificationCriteria
  ): Promise<ProcessingResult<QualifiedLead[]>> {
    const startTime = Date.now();
    this.data.status = AgentStatus.PROCESSING;

    try {
      logger.info(`Agent 2: Qualifying ${leads.length} leads in batch`);

      const qualifiedLeads: QualifiedLead[] = [];

      for (const lead of leads) {
        const result = await this.qualifyLead(lead, criteria);
        if (result.success && result.data) {
          qualifiedLeads.push(result.data);
        }
      }

      this.data.status = AgentStatus.COMPLETED;

      const processingTime = Date.now() - startTime;

      logger.info(`Agent 2: Qualified ${qualifiedLeads.length} leads in ${processingTime}ms`);

      return {
        success: true,
        data: qualifiedLeads,
        timestamp: new Date(),
        processingTime
      };
    } catch (error) {
      this.data.status = AgentStatus.ERROR;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      logger.error(`Agent 2: Error qualifying leads in batch: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Calculate qualification score based on criteria
   */
  private calculateQualificationScore(lead: Lead, criteria: QualificationCriteria): number {
    let score = lead.score || 50; // Base score

    // Budget criteria
    if (criteria.budget) {
      score += 15;
    }

    // Authority criteria
    if (criteria.authority) {
      if (lead.jobTitle?.toLowerCase().includes('director') ||
          lead.jobTitle?.toLowerCase().includes('manager') ||
          lead.jobTitle?.toLowerCase().includes('ceo') ||
          lead.jobTitle?.toLowerCase().includes('cto')) {
        score += 20;
      }
    }

    // Need criteria
    if (criteria.need) {
      score += 15;
    }

    // Timeline criteria
    if (criteria.timeline) {
      if (criteria.timeline.includes('immediate') || criteria.timeline.includes('urgent')) {
        score += 20;
      } else if (criteria.timeline.includes('month')) {
        score += 10;
      }
    }

    // Company size criteria
    if (criteria.companySize) {
      score += 10;
    }

    // Industry match
    if (criteria.industry && criteria.industry.length > 0) {
      score += 10;
    }

    // Normalize score to 0-100
    return Math.min(Math.max(score, 0), 100);
  }

  /**
   * Determine qualification status based on score
   */
  private determineQualificationStatus(score: number): QualificationStatus {
    if (score >= 75) {
      return QualificationStatus.QUALIFIED;
    } else if (score >= 50) {
      return QualificationStatus.NURTURE;
    } else {
      return QualificationStatus.UNQUALIFIED;
    }
  }

  /**
   * Generate qualification notes
   */
  private generateNotes(lead: QualifiedLead): string {
    const notes: string[] = [];

    notes.push(`Qualification score: ${lead.qualificationScore}/100`);

    if (lead.qualificationScore >= 75) {
      notes.push('High-priority lead, recommended for immediate follow-up');
    } else if (lead.qualificationScore >= 50) {
      notes.push('Moderate potential, suitable for nurture campaign');
    } else {
      notes.push('Low qualification score, consider re-qualification later');
    }

    if (lead.company) {
      notes.push(`Company: ${lead.company}`);
    }

    if (lead.jobTitle) {
      notes.push(`Role: ${lead.jobTitle}`);
    }

    return notes.join('. ');
  }

  /**
   * Determine next action based on status
   */
  private determineNextAction(status: QualificationStatus): string {
    switch (status) {
      case QualificationStatus.QUALIFIED:
        return 'Schedule discovery call within 24 hours';
      case QualificationStatus.NURTURE:
        return 'Add to nurture campaign, follow up in 1 week';
      case QualificationStatus.UNQUALIFIED:
        return 'Archive or re-qualify in 3 months';
      default:
        return 'Review manually';
    }
  }

  /**
   * Get qualified leads with optional filtering
   */
  getQualifiedLeads(filters?: {
    status?: QualificationStatus;
    minScore?: number;
    assignedTo?: string;
  }): QualifiedLead[] {
    let leads = [...this.data.qualifiedLeads];

    if (filters) {
      if (filters.status) {
        leads = leads.filter(lead => lead.qualificationStatus === filters.status);
      }
      if (filters.minScore !== undefined) {
        leads = leads.filter(lead => lead.qualificationScore >= filters.minScore!);
      }
      if (filters.assignedTo) {
        leads = leads.filter(lead => lead.assignedTo === filters.assignedTo);
      }
    }

    return leads;
  }

  /**
   * Update lead qualification
   */
  async requalifyLead(
    leadId: string,
    newCriteria: QualificationCriteria
  ): Promise<ProcessingResult<QualifiedLead>> {
    try {
      const leadIndex = this.data.qualifiedLeads.findIndex(lead => lead.id === leadId);

      if (leadIndex === -1) {
        throw new Error(`Qualified lead with ID ${leadId} not found`);
      }

      const lead = this.data.qualifiedLeads[leadIndex];
      const newScore = this.calculateQualificationScore(lead, newCriteria);
      const newStatus = this.determineQualificationStatus(newScore);

      // Update counts
      this.decrementStatusCount(lead.qualificationStatus);
      this.incrementStatusCount(newStatus);

      // Update lead
      this.data.qualifiedLeads[leadIndex] = {
        ...lead,
        qualificationScore: newScore,
        qualificationStatus: newStatus,
        criteria: newCriteria,
        notes: this.generateNotes({ ...lead, qualificationScore: newScore, qualificationStatus: newStatus }),
        nextAction: this.determineNextAction(newStatus),
        updatedAt: new Date()
      };

      this.updateStatistics();
      this.data.updatedAt = new Date();

      logger.info(`Agent 2: Requalified lead ${leadId} with new score ${newScore}`);

      return {
        success: true,
        data: this.data.qualifiedLeads[leadIndex],
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 2: Error requalifying lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Assign lead to sales rep
   */
  async assignLead(leadId: string, assignedTo: string): Promise<ProcessingResult<QualifiedLead>> {
    try {
      const leadIndex = this.data.qualifiedLeads.findIndex(lead => lead.id === leadId);

      if (leadIndex === -1) {
        throw new Error(`Qualified lead with ID ${leadId} not found`);
      }

      this.data.qualifiedLeads[leadIndex].assignedTo = assignedTo;
      this.data.qualifiedLeads[leadIndex].updatedAt = new Date();
      this.data.updatedAt = new Date();

      logger.info(`Agent 2: Assigned lead ${leadId} to ${assignedTo}`);

      return {
        success: true,
        data: this.data.qualifiedLeads[leadIndex],
        timestamp: new Date()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error(`Agent 2: Error assigning lead: ${errorMessage}`);

      return {
        success: false,
        error: errorMessage,
        timestamp: new Date()
      };
    }
  }

  /**
   * Update statistics
   */
  private updateStatistics(): void {
    const totalLeads = this.data.qualifiedLeads.length;

    if (totalLeads > 0) {
      this.data.qualificationRate = (this.data.totalQualified / totalLeads) * 100;

      const totalScore = this.data.qualifiedLeads.reduce(
        (sum, lead) => sum + lead.qualificationScore,
        0
      );
      this.data.averageScore = totalScore / totalLeads;
    }
  }

  /**
   * Helper: Decrement status count
   */
  private decrementStatusCount(status: QualificationStatus): void {
    switch (status) {
      case QualificationStatus.QUALIFIED:
        this.data.totalQualified = Math.max(0, this.data.totalQualified - 1);
        break;
      case QualificationStatus.UNQUALIFIED:
        this.data.totalUnqualified = Math.max(0, this.data.totalUnqualified - 1);
        break;
      case QualificationStatus.NURTURE:
        this.data.totalNurture = Math.max(0, this.data.totalNurture - 1);
        break;
    }
  }

  /**
   * Helper: Increment status count
   */
  private incrementStatusCount(status: QualificationStatus): void {
    switch (status) {
      case QualificationStatus.QUALIFIED:
        this.data.totalQualified++;
        break;
      case QualificationStatus.UNQUALIFIED:
        this.data.totalUnqualified++;
        break;
      case QualificationStatus.NURTURE:
        this.data.totalNurture++;
        break;
    }
  }

  /**
   * Get agent data
   */
  getData(): Agent2Data {
    return { ...this.data };
  }

  /**
   * Get agent statistics
   */
  getStatistics() {
    return {
      totalQualified: this.data.totalQualified,
      totalUnqualified: this.data.totalUnqualified,
      totalNurture: this.data.totalNurture,
      qualificationRate: this.data.qualificationRate,
      averageScore: this.data.averageScore,
      topQualifiedLeads: this.getTopQualifiedLeads(5),
      recentQualifications: this.data.qualifiedLeads.slice(-10).reverse()
    };
  }

  /**
   * Get top qualified leads
   */
  private getTopQualifiedLeads(limit: number): QualifiedLead[] {
    return [...this.data.qualifiedLeads]
      .filter(lead => lead.qualificationStatus === QualificationStatus.QUALIFIED)
      .sort((a, b) => b.qualificationScore - a.qualificationScore)
      .slice(0, limit);
  }
}

export const agent2Service = new Agent2Service();
