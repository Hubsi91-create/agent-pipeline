/**
 * API Routes for all 11 Agents
 */

import express, { Router, Request, Response } from 'express';
import { agent1Service } from '../../services/agents/agent1.service';
import { agent2Service } from '../../services/agents/agent2.service';
import { agent3Service } from '../../services/agents/agent3.service';
import { agent4Service } from '../../services/agents/agent4.service';
import { agent5Service } from '../../services/agents/agent5.service';
import { agent6Service } from '../../services/agents/agent6.service';
import { agent7Service } from '../../services/agents/agent7.service';
import { agent8Service } from '../../services/agents/agent8.service';
import { agent9Service } from '../../services/agents/agent9.service';
import { agent10Service } from '../../services/agents/agent10.service';
import { agent11Service } from '../../services/agents/agent11.service';
import { googleSheetsService } from '../../services/googleSheets.service';
import { logger } from '../../utils/logger';

const router: Router = express.Router();

// ==================== Agent 1: Lead Generation ====================

router.get('/agent1/data', (req: Request, res: Response) => {
  try {
    const data = agent1Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 1 data' });
  }
});

router.get('/agent1/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent1Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent1/leads', async (req: Request, res: Response) => {
  try {
    const result = await agent1Service.addLead(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to add lead' });
  }
});

router.post('/agent1/generate', async (req: Request, res: Response) => {
  try {
    const { sources } = req.body;
    const result = await agent1Service.generateLeads(sources);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to generate leads' });
  }
});

// ==================== Agent 2: Lead Qualification ====================

router.get('/agent2/data', (req: Request, res: Response) => {
  try {
    const data = agent2Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 2 data' });
  }
});

router.get('/agent2/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent2Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent2/qualify', async (req: Request, res: Response) => {
  try {
    const { lead, criteria } = req.body;
    const result = await agent2Service.qualifyLead(lead, criteria);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to qualify lead' });
  }
});

// ==================== Agent 3: Competitor Analysis ====================

router.get('/agent3/data', (req: Request, res: Response) => {
  try {
    const data = agent3Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 3 data' });
  }
});

router.get('/agent3/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent3Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent3/competitors', async (req: Request, res: Response) => {
  try {
    const result = await agent3Service.addCompetitor(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to add competitor' });
  }
});

router.post('/agent3/analyze/:id', async (req: Request, res: Response) => {
  try {
    const result = await agent3Service.analyzeCompetitor(req.params.id);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to analyze competitor' });
  }
});

// ==================== Agent 4: Market Research ====================

router.get('/agent4/data', (req: Request, res: Response) => {
  try {
    const data = agent4Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 4 data' });
  }
});

router.get('/agent4/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent4Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent4/segments', async (req: Request, res: Response) => {
  try {
    const result = await agent4Service.addSegment(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to add segment' });
  }
});

router.post('/agent4/research', async (req: Request, res: Response) => {
  try {
    const result = await agent4Service.conductResearch();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to conduct research' });
  }
});

// ==================== Agent 5: Content Strategy ====================

router.get('/agent5/data', (req: Request, res: Response) => {
  try {
    const data = agent5Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 5 data' });
  }
});

router.get('/agent5/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent5Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent5/content', async (req: Request, res: Response) => {
  try {
    const result = await agent5Service.createContent(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to create content' });
  }
});

// ==================== Agent 6: SEO Optimization ====================

router.get('/agent6/data', (req: Request, res: Response) => {
  try {
    const data = agent6Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 6 data' });
  }
});

router.get('/agent6/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent6Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent6/keywords', async (req: Request, res: Response) => {
  try {
    const result = await agent6Service.addKeyword(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to add keyword' });
  }
});

// ==================== Agent 7: Social Media ====================

router.get('/agent7/data', (req: Request, res: Response) => {
  try {
    const data = agent7Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 7 data' });
  }
});

router.get('/agent7/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent7Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent7/posts', async (req: Request, res: Response) => {
  try {
    const result = await agent7Service.createPost(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to create post' });
  }
});

// ==================== Agent 8: Email Marketing ====================

router.get('/agent8/data', (req: Request, res: Response) => {
  try {
    const data = agent8Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 8 data' });
  }
});

router.get('/agent8/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent8Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent8/campaigns', async (req: Request, res: Response) => {
  try {
    const result = await agent8Service.createCampaign(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to create campaign' });
  }
});

// ==================== Agent 9: Analytics ====================

router.get('/agent9/data', (req: Request, res: Response) => {
  try {
    const data = agent9Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 9 data' });
  }
});

router.get('/agent9/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent9Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent9/reports', async (req: Request, res: Response) => {
  try {
    const result = await agent9Service.generateReport(req.body.period);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to generate report' });
  }
});

// ==================== Agent 10: Campaign Management ====================

router.get('/agent10/data', (req: Request, res: Response) => {
  try {
    const data = agent10Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 10 data' });
  }
});

router.get('/agent10/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent10Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent10/campaigns', async (req: Request, res: Response) => {
  try {
    const result = await agent10Service.createCampaign(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to create campaign' });
  }
});

// ==================== Agent 11: Report Generation ====================

router.get('/agent11/data', (req: Request, res: Response) => {
  try {
    const data = agent11Service.getData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get agent 11 data' });
  }
});

router.get('/agent11/statistics', (req: Request, res: Response) => {
  try {
    const stats = agent11Service.getStatistics();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get statistics' });
  }
});

router.post('/agent11/reports', async (req: Request, res: Response) => {
  try {
    const result = await agent11Service.generateReport(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to generate report' });
  }
});

// ==================== System Routes ====================

router.get('/all', (req: Request, res: Response) => {
  try {
    const allData = {
      agent1: agent1Service.getData(),
      agent2: agent2Service.getData(),
      agent3: agent3Service.getData(),
      agent4: agent4Service.getData(),
      agent5: agent5Service.getData(),
      agent6: agent6Service.getData(),
      agent7: agent7Service.getData(),
      agent8: agent8Service.getData(),
      agent9: agent9Service.getData(),
      agent10: agent10Service.getData(),
      agent11: agent11Service.getData()
    };
    res.json({ success: true, data: allData });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to get all agents data' });
  }
});

router.post('/sync-sheets', async (req: Request, res: Response) => {
  try {
    const allData = {
      agent1: agent1Service.getData(),
      agent2: agent2Service.getData(),
      agent3: agent3Service.getData(),
      agent4: agent4Service.getData(),
      agent5: agent5Service.getData(),
      agent6: agent6Service.getData(),
      agent7: agent7Service.getData(),
      agent8: agent8Service.getData(),
      agent9: agent9Service.getData(),
      agent10: agent10Service.getData(),
      agent11: agent11Service.getData()
    };

    await googleSheetsService.syncAllAgents(allData);
    res.json({ success: true, message: 'Data synced to Google Sheets' });
  } catch (error) {
    logger.error('Failed to sync to Google Sheets', { error });
    res.status(500).json({ success: false, error: 'Failed to sync to Google Sheets' });
  }
});

export default router;
