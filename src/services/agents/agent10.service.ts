/**
 * Agent 10: Campaign Management Service
 */

import { Agent10Data, Campaign, CampaignType, CampaignStatus, AgentStatus, ProcessingResult } from '../../types';
import { logger } from '../../utils/logger';

export class Agent10Service {
  private data: Agent10Data;

  constructor() {
    this.data = {
      id: 'agent-10',
      name: 'Campaign Management Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      campaigns: [],
      activeCampaigns: 0,
      totalBudget: 0,
      totalSpent: 0,
      avgROI: 0,
      upcomingMilestones: [],
      campaignPerformance: []
    };
  }

  async createCampaign(campaign: Omit<Campaign, 'id'>): Promise<ProcessingResult<Campaign>> {
    const startTime = Date.now();
    try {
      const newCampaign: Campaign = { ...campaign, id: `campaign-${Date.now()}` };
      this.data.campaigns.push(newCampaign);
      this.data.totalBudget += campaign.budget.total;

      if (campaign.status === CampaignStatus.ACTIVE) {
        this.data.activeCampaigns++;
      }

      this.updateMilestones();
      this.data.updatedAt = new Date();

      logger.info(`Agent 10: Created campaign ${campaign.name}`);
      return {
        success: true,
        data: newCampaign,
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
        processingTime: Date.now() - startTime
      };
    }
  }

  async updateCampaignStatus(campaignId: string, status: CampaignStatus): Promise<ProcessingResult<Campaign>> {
    try {
      const index = this.data.campaigns.findIndex(c => c.id === campaignId);
      if (index === -1) throw new Error('Campaign not found');

      const oldStatus = this.data.campaigns[index].status;
      this.data.campaigns[index].status = status;

      if (oldStatus === CampaignStatus.ACTIVE && status !== CampaignStatus.ACTIVE) {
        this.data.activeCampaigns--;
      } else if (status === CampaignStatus.ACTIVE && oldStatus !== CampaignStatus.ACTIVE) {
        this.data.activeCampaigns++;
      }

      this.data.updatedAt = new Date();

      logger.info(`Agent 10: Updated campaign ${campaignId} status to ${status}`);
      return { success: true, data: this.data.campaigns[index], timestamp: new Date() };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  async updateCampaignBudget(campaignId: string, spent: number): Promise<ProcessingResult<Campaign>> {
    try {
      const index = this.data.campaigns.findIndex(c => c.id === campaignId);
      if (index === -1) throw new Error('Campaign not found');

      const previousSpent = this.data.campaigns[index].budget.spent;
      this.data.campaigns[index].budget.spent = spent;
      this.data.totalSpent += (spent - previousSpent);

      this.updateROI();
      this.data.updatedAt = new Date();

      return { success: true, data: this.data.campaigns[index], timestamp: new Date() };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  async completeMilestone(campaignId: string, milestoneName: string): Promise<ProcessingResult<Campaign>> {
    try {
      const campaign = this.data.campaigns.find(c => c.id === campaignId);
      if (!campaign) throw new Error('Campaign not found');

      const milestone = campaign.milestones.find(m => m.name === milestoneName);
      if (!milestone) throw new Error('Milestone not found');

      milestone.completed = true;
      this.updateMilestones();
      this.data.updatedAt = new Date();

      logger.info(`Agent 10: Completed milestone ${milestoneName} for campaign ${campaignId}`);
      return { success: true, data: campaign, timestamp: new Date() };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      };
    }
  }

  private updateMilestones(): void {
    this.data.upcomingMilestones = [];

    this.data.campaigns.forEach(campaign => {
      campaign.milestones
        .filter(m => !m.completed && new Date(m.date) > new Date())
        .forEach(m => {
          this.data.upcomingMilestones.push({
            campaign: campaign.name,
            milestone: m.name,
            date: m.date
          });
        });
    });

    this.data.upcomingMilestones.sort((a, b) => a.date.getTime() - b.date.getTime());
    this.data.upcomingMilestones = this.data.upcomingMilestones.slice(0, 20);
  }

  private updateROI(): void {
    const campaignsWithPerformance = this.data.campaigns.filter(c => c.performance);

    if (campaignsWithPerformance.length > 0) {
      const totalROI = campaignsWithPerformance.reduce((sum, c) => sum + (c.performance?.roi || 0), 0);
      this.data.avgROI = totalROI / campaignsWithPerformance.length;

      this.data.campaignPerformance = campaignsWithPerformance.map(c => ({
        campaignId: c.id,
        score: this.calculateCampaignScore(c)
      }));
    }
  }

  private calculateCampaignScore(campaign: Campaign): number {
    if (!campaign.performance) return 0;

    const roi = campaign.performance.roi || 0;
    const budgetUtilization = (campaign.budget.spent / campaign.budget.total) * 100;
    const kpiProgress = this.calculateKPIProgress(campaign);

    return (roi * 0.5) + (budgetUtilization * 0.2) + (kpiProgress * 0.3);
  }

  private calculateKPIProgress(campaign: Campaign): number {
    if (campaign.kpis.length === 0) return 0;

    const progress = campaign.kpis.reduce((sum, kpi) => {
      const actual = kpi.actual || 0;
      const achievement = (actual / kpi.target) * 100;
      return sum + Math.min(achievement, 100);
    }, 0);

    return progress / campaign.kpis.length;
  }

  getCampaigns(filters?: { type?: CampaignType; status?: CampaignStatus }): Campaign[] {
    let campaigns = [...this.data.campaigns];

    if (filters) {
      if (filters.type) campaigns = campaigns.filter(c => c.type === filters.type);
      if (filters.status) campaigns = campaigns.filter(c => c.status === filters.status);
    }

    return campaigns;
  }

  getData(): Agent10Data {
    return { ...this.data };
  }

  getStatistics() {
    this.updateROI();
    return {
      totalCampaigns: this.data.campaigns.length,
      activeCampaigns: this.data.activeCampaigns,
      totalBudget: this.data.totalBudget,
      totalSpent: this.data.totalSpent,
      budgetUtilization: this.data.totalBudget > 0 ? (this.data.totalSpent / this.data.totalBudget) * 100 : 0,
      avgROI: this.data.avgROI,
      upcomingMilestones: this.data.upcomingMilestones.slice(0, 5),
      topPerformingCampaigns: this.getTopPerformingCampaigns(5)
    };
  }

  private getTopPerformingCampaigns(limit: number): Campaign[] {
    return [...this.data.campaigns]
      .filter(c => c.performance)
      .sort((a, b) => (b.performance?.roi || 0) - (a.performance?.roi || 0))
      .slice(0, limit);
  }
}

export const agent10Service = new Agent10Service();
