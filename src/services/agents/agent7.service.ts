/**
 * Agent 7: Social Media Management Service
 */

import { Agent7Data, SocialPost, SocialAccount, SocialPlatform, AgentStatus, ProcessingResult } from '../../types';
import { logger } from '../../utils/logger';

export class Agent7Service {
  private data: Agent7Data;

  constructor() {
    this.data = {
      id: 'agent-7',
      name: 'Social Media Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      posts: [],
      accounts: [],
      totalPosts: 0,
      scheduledPosts: 0,
      averageEngagement: 0,
      bestPerformingPosts: [],
      contentCalendar: []
    };
  }

  async createPost(post: Omit<SocialPost, 'id'>): Promise<ProcessingResult<SocialPost>> {
    try {
      const newPost: SocialPost = { ...post, id: `post-${Date.now()}` };
      this.data.posts.push(newPost);
      this.data.totalPosts++;
      if (post.status === 'scheduled') this.data.scheduledPosts++;
      this.updateCalendar(newPost);
      this.data.updatedAt = new Date();

      logger.info(`Agent 7: Created social post for ${post.platform}`);
      return { success: true, data: newPost, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  async publishPost(postId: string): Promise<ProcessingResult<SocialPost>> {
    try {
      const index = this.data.posts.findIndex(p => p.id === postId);
      if (index === -1) throw new Error('Post not found');

      if (this.data.posts[index].status === 'scheduled') this.data.scheduledPosts--;
      this.data.posts[index].status = 'published';
      this.data.posts[index].publishedDate = new Date();
      this.data.updatedAt = new Date();

      logger.info(`Agent 7: Published post ${postId}`);
      return { success: true, data: this.data.posts[index], timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  async addAccount(account: SocialAccount): Promise<ProcessingResult<SocialAccount>> {
    try {
      this.data.accounts.push(account);
      this.data.updatedAt = new Date();

      logger.info(`Agent 7: Added ${account.platform} account @${account.handle}`);
      return { success: true, data: account, timestamp: new Date() };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error', timestamp: new Date() };
    }
  }

  private updateCalendar(post: SocialPost): void {
    const date = new Date(post.scheduledDate);
    const existing = this.data.contentCalendar.find(
      c => c.date.toDateString() === date.toDateString()
    );

    if (existing) {
      existing.posts.push(post);
    } else {
      this.data.contentCalendar.push({ date, posts: [post] });
    }
  }

  updateBestPerforming(): void {
    this.data.bestPerformingPosts = [...this.data.posts]
      .filter(p => p.engagement)
      .sort((a, b) => {
        const aScore = (a.engagement?.likes || 0) + (a.engagement?.shares || 0) * 2;
        const bScore = (b.engagement?.likes || 0) + (b.engagement?.shares || 0) * 2;
        return bScore - aScore;
      })
      .slice(0, 10);

    if (this.data.posts.length > 0) {
      const totalEngagement = this.data.posts
        .filter(p => p.engagement)
        .reduce((sum, p) => sum + ((p.engagement?.likes || 0) + (p.engagement?.comments || 0)), 0);
      this.data.averageEngagement = totalEngagement / this.data.posts.length;
    }
  }

  getData(): Agent7Data {
    return { ...this.data };
  }

  getStatistics() {
    this.updateBestPerforming();
    return {
      totalPosts: this.data.totalPosts,
      scheduledPosts: this.data.scheduledPosts,
      averageEngagement: this.data.averageEngagement,
      totalAccounts: this.data.accounts.length,
      bestPerforming: this.data.bestPerformingPosts.slice(0, 5),
      upcomingPosts: this.data.posts.filter(p => p.status === 'scheduled').length
    };
  }
}

export const agent7Service = new Agent7Service();
