/**
 * Agent 5: Content Strategy Service
 * Manages content planning and calendar
 */

import {
  Agent5Data,
  ContentPiece,
  ContentCalendar,
  ContentType,
  ContentStatus,
  AgentStatus,
  ProcessingResult
} from '../../types';
import { logger } from '../../utils/logger';

export class Agent5Service {
  private data: Agent5Data;

  constructor() {
    this.data = {
      id: 'agent-5',
      name: 'Content Strategy Agent',
      status: AgentStatus.IDLE,
      createdAt: new Date(),
      updatedAt: new Date(),
      contentPieces: [],
      calendar: [],
      totalPublished: 0,
      totalPlanned: 0,
      topPerformingContent: [],
      contentGaps: []
    };
  }

  async createContent(content: Omit<ContentPiece, 'id'>): Promise<ProcessingResult<ContentPiece>> {
    const startTime = Date.now();
    try {
      const newContent: ContentPiece = {
        ...content,
        id: `content-${Date.now()}`
      };

      this.data.contentPieces.push(newContent);

      if (content.status === ContentStatus.PUBLISHED) {
        this.data.totalPublished++;
      } else if (content.status === ContentStatus.PLANNED) {
        this.data.totalPlanned++;
      }

      this.updateCalendar(newContent);
      this.updateTopPerforming();
      this.data.updatedAt = new Date();

      logger.info(`Agent 5: Created content piece ${content.title}`);

      return {
        success: true,
        data: newContent,
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

  async updateContentStatus(id: string, status: ContentStatus): Promise<ProcessingResult<ContentPiece>> {
    try {
      const index = this.data.contentPieces.findIndex(c => c.id === id);
      if (index === -1) throw new Error(`Content with ID ${id} not found`);

      const oldStatus = this.data.contentPieces[index].status;
      this.data.contentPieces[index].status = status;

      // Update counts
      if (oldStatus === ContentStatus.PUBLISHED && status !== ContentStatus.PUBLISHED) {
        this.data.totalPublished--;
      } else if (status === ContentStatus.PUBLISHED && oldStatus !== ContentStatus.PUBLISHED) {
        this.data.totalPublished++;
      }

      if (oldStatus === ContentStatus.PLANNED && status !== ContentStatus.PLANNED) {
        this.data.totalPlanned--;
      } else if (status === ContentStatus.PLANNED && oldStatus !== ContentStatus.PLANNED) {
        this.data.totalPlanned++;
      }

      this.data.updatedAt = new Date();

      return {
        success: true,
        data: this.data.contentPieces[index],
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

  private updateCalendar(content: ContentPiece): void {
    if (!content.publishDate) return;

    const date = new Date(content.publishDate);
    const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

    let calendarEntry = this.data.calendar.find(
      c => `${c.year}-${String(c.month).padStart(2, '0')}` === monthYear
    );

    if (!calendarEntry) {
      calendarEntry = {
        month: date.toLocaleString('default', { month: 'long' }),
        year: date.getFullYear(),
        content: [],
        themes: []
      };
      this.data.calendar.push(calendarEntry);
    }

    if (!calendarEntry.content.find(c => c.id === content.id)) {
      calendarEntry.content.push(content);
    }
  }

  private updateTopPerforming(): void {
    this.data.topPerformingContent = [...this.data.contentPieces]
      .filter(c => c.status === ContentStatus.PUBLISHED && c.performance)
      .sort((a, b) => {
        const aScore = (a.performance?.views || 0) + (a.performance?.engagement || 0);
        const bScore = (b.performance?.views || 0) + (b.performance?.engagement || 0);
        return bScore - aScore;
      })
      .slice(0, 10);
  }

  async analyzeContentGaps(): Promise<ProcessingResult<string[]>> {
    const startTime = Date.now();
    try {
      const gaps: string[] = [];
      const contentTypes = Object.values(ContentType);
      const existingTypes = new Set(this.data.contentPieces.map(c => c.type));

      contentTypes.forEach(type => {
        if (!existingTypes.has(type)) {
          gaps.push(`Missing content type: ${type}`);
        }
      });

      this.data.contentGaps = gaps;
      this.data.updatedAt = new Date();

      return {
        success: true,
        data: gaps,
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

  getContent(filters?: { type?: ContentType; status?: ContentStatus }): ContentPiece[] {
    let content = [...this.data.contentPieces];

    if (filters) {
      if (filters.type) {
        content = content.filter(c => c.type === filters.type);
      }
      if (filters.status) {
        content = content.filter(c => c.status === filters.status);
      }
    }

    return content;
  }

  getData(): Agent5Data {
    return { ...this.data };
  }

  getStatistics() {
    return {
      totalContent: this.data.contentPieces.length,
      totalPublished: this.data.totalPublished,
      totalPlanned: this.data.totalPlanned,
      topPerforming: this.data.topPerformingContent.slice(0, 5),
      contentGaps: this.data.contentGaps,
      calendarMonths: this.data.calendar.length,
      avgPerformance: this.calculateAveragePerformance()
    };
  }

  private calculateAveragePerformance(): number {
    const published = this.data.contentPieces.filter(
      c => c.status === ContentStatus.PUBLISHED && c.performance
    );

    if (published.length === 0) return 0;

    const totalViews = published.reduce((sum, c) => sum + (c.performance?.views || 0), 0);
    return totalViews / published.length;
  }
}

export const agent5Service = new Agent5Service();
