/**
 * Application Configuration
 */

import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config();

export const config = {
  // Server Configuration
  port: parseInt(process.env.PORT || '3000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',

  // Google Sheets Configuration
  googleSheets: {
    credentialsPath: process.env.GOOGLE_SHEETS_CREDENTIALS_PATH || './credentials/google-sheets-credentials.json',
    spreadsheetId: process.env.GOOGLE_SHEETS_SPREADSHEET_ID || ''
  },

  // API Configuration
  api: {
    rateLimitWindowMs: parseInt(process.env.API_RATE_LIMIT_WINDOW_MS || '900000', 10),
    rateLimitMaxRequests: parseInt(process.env.API_RATE_LIMIT_MAX_REQUESTS || '100', 10)
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    filePath: process.env.LOG_FILE_PATH || './logs/app.log'
  },

  // Agent Configuration
  agents: {
    timeoutMs: parseInt(process.env.AGENT_TIMEOUT_MS || '30000', 10),
    maxRetryAttempts: parseInt(process.env.MAX_RETRY_ATTEMPTS || '3', 10),
    retryDelayMs: parseInt(process.env.RETRY_DELAY_MS || '1000', 10)
  }
};

export default config;
