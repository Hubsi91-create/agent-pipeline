/**
 * Agent 8: Email Marketing Service
 */

import { Agent8Data, EmailCampaign, EmailList, EmailCampaignType, AgentStatus, ProcessingResult } from '../../types';
import { logger } from '../../utils/logger';

export class Agent8Service {
  private data: Agent8Data;

  constructor() {
    this.data = {
      id: 'agent-8',
      name: 'Email Marketing Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      campaigns: [],
      lists: [],
      totalCampaigns: 0,
      activeCampaigns: 0,
      averageOpenRate: 0,
      averageClickRate: 0,
      totalSubscribers: 0,
      bestPerformingCampaigns: []
    };
  }

  async createCampaign(campaign: Omit<EmailCampaign, 'id'>): Promise<ProcessingResult<EmailCampaign>> {
    try {
      const newCampaign: EmailCampaign = { ...campaign, id: `campaign-${Date.now()}` };
      this.data.campaigns.push(newCampaign);
      this.data.totalCampaigns++;
      if (campaign.status === 'sent' || campaign.status === 'scheduled') this.data.activeCampaigns++;
      this.data.updatedAt = new Date();

      logger.info(`Agent 8: Created email campaign ${campaign.name}`);
      return { success: true, data: newCampaign, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  async sendCampaign(campaignId: string): Promise<ProcessingResult<EmailCampaign>> {
    try {
      const index = this.data.campaigns.findIndex(c => c.id === campaignId);
      if (index === -1) throw new Error('Campaign not found');

      this.data.campaigns[index].status = 'sent';
      this.data.campaigns[index].sentDate = new Date();
      this.updateMetrics();
      this.data.updatedAt = new Date();

      logger.info(`Agent 8: Sent campaign ${campaignId}`);
      return { success: true, data: this.data.campaigns[index], timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  async createList(list: Omit<EmailList, 'id'>): Promise<ProcessingResult<EmailList>> {
    try {
      const newList: EmailList = { ...list, id: `list-${Date.now()}` };
      this.data.lists.push(newList);
      this.data.totalSubscribers += list.subscribers;
      this.data.updatedAt = new Date();

      logger.info(`Agent 8: Created email list ${list.name}`);
      return { success: true, data: newList, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  private updateMetrics(): void {
    const sentCampaigns = this.data.campaigns.filter(c => c.status === 'sent' && c.metrics);

    if (sentCampaigns.length > 0) {
      const totalOpenRate = sentCampaigns.reduce((sum, c) => sum + (c.metrics?.openRate || 0), 0);
      const totalClickRate = sentCampaigns.reduce((sum, c) => sum + (c.metrics?.clickRate || 0), 0);

      this.data.averageOpenRate = totalOpenRate / sentCampaigns.length;
      this.data.averageClickRate = totalClickRate / sentCampaigns.length;

      this.data.bestPerformingCampaigns = [...sentCampaigns]
        .sort((a, b) => (b.metrics?.conversionRate || 0) - (a.metrics?.conversionRate || 0))
        .slice(0, 10);
    }
  }

  getData(): Agent8Data {
    return { ...this.data };
  }

  getStatistics() {
    this.updateMetrics();
    return {
      totalCampaigns: this.data.totalCampaigns,
      activeCampaigns: this.data.activeCampaigns,
      averageOpenRate: this.data.averageOpenRate,
      averageClickRate: this.data.averageClickRate,
      totalSubscribers: this.data.totalSubscribers,
      totalLists: this.data.lists.length,
      bestPerforming: this.data.bestPerformingCampaigns.slice(0, 5)
    };
  }
}

export const agent8Service = new Agent8Service();
