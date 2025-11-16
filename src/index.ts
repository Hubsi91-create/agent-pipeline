/**
 * Main Application Entry Point
 * 11-Agent Marketing Pipeline System
 */

import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { config } from './config';
import { logger } from './utils/logger';
import agentsRoutes from './api/routes/agents.routes';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';
import { googleSheetsService } from './services/googleSheets.service';

// Initialize Express app
const app: Application = express();

// ==================== Middleware ====================

// Security
app.use(helmet());

// CORS
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use((req: Request, res: Response, next) => {
  logger.info(`${req.method} ${req.path}`, {
    query: req.query,
    ip: req.ip
  });
  next();
});

// ==================== Routes ====================

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({
    success: true,
    message: '11-Agent Marketing Pipeline System is running',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: config.nodeEnv
  });
});

// API Info
app.get('/', (req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'Welcome to the 11-Agent Marketing Pipeline System API',
    version: '1.0.0',
    agents: [
      'Agent 1: Lead Generation',
      'Agent 2: Lead Qualification',
      'Agent 3: Competitor Analysis',
      'Agent 4: Market Research',
      'Agent 5: Content Strategy',
      'Agent 6: SEO Optimization',
      'Agent 7: Social Media Management',
      'Agent 8: Email Marketing',
      'Agent 9: Analytics & Reporting',
      'Agent 10: Campaign Management',
      'Agent 11: Report Generation'
    ],
    endpoints: {
      health: '/health',
      agents: '/api/agents/*',
      allAgents: '/api/agents/all',
      syncSheets: '/api/agents/sync-sheets'
    },
    documentation: 'See README.md for detailed API documentation'
  });
});

// Agent routes
app.use('/api/agents', agentsRoutes);

// ==================== Error Handling ====================

// 404 handler
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// ==================== Server Initialization ====================

const startServer = async () => {
  try {
    // Initialize Google Sheets (optional - requires credentials)
    try {
      await googleSheetsService.initialize();
      await googleSheetsService.setupSheets();
    } catch (error) {
      logger.warn('Google Sheets Service not initialized. Set up credentials to enable sync.');
    }

    // Start server
    const port = config.port;
    app.listen(port, () => {
      logger.info('='.repeat(60));
      logger.info('11-Agent Marketing Pipeline System');
      logger.info('='.repeat(60));
      logger.info(`Server running on port ${port}`);
      logger.info(`Environment: ${config.nodeEnv}`);
      logger.info(`API URL: http://localhost:${port}`);
      logger.info(`Health check: http://localhost:${port}/health`);
      logger.info('='.repeat(60));
      logger.info('Available Agents:');
      logger.info('  1. Lead Generation');
      logger.info('  2. Lead Qualification');
      logger.info('  3. Competitor Analysis');
      logger.info('  4. Market Research');
      logger.info('  5. Content Strategy');
      logger.info('  6. SEO Optimization');
      logger.info('  7. Social Media Management');
      logger.info('  8. Email Marketing');
      logger.info('  9. Analytics & Reporting');
      logger.info(' 10. Campaign Management');
      logger.info(' 11. Report Generation');
      logger.info('='.repeat(60));
    });
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
};

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error) => {
  logger.error('Uncaught Exception', { error });
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason: unknown) => {
  logger.error('Unhandled Rejection', { reason });
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start the server
startServer();

export default app;
