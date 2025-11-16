# 11-Agent Marketing Pipeline System

A comprehensive marketing automation system powered by 11 specialized AI agents with Google Sheets integration.

## 🚀 Features

This system consists of 11 specialized agents working together to automate your entire marketing pipeline:

### Agent 1: Lead Generation
- Automated lead collection from multiple sources
- Lead scoring and categorization
- Source tracking and analytics

### Agent 2: Lead Qualification
- BANT (Budget, Authority, Need, Timeline) qualification
- Intelligent lead scoring
- Automated routing to sales teams

### Agent 3: Competitor Analysis
- Competitive intelligence gathering
- SWOT analysis automation
- Market positioning insights

### Agent 4: Market Research
- Market segmentation analysis
- Trend identification
- Opportunity mapping

### Agent 5: Content Strategy
- Content planning and calendar management
- Performance tracking
- Gap analysis

### Agent 6: SEO Optimization
- Keyword research and tracking
- Page optimization recommendations
- Technical SEO audits

### Agent 7: Social Media Management
- Multi-platform post scheduling
- Engagement tracking
- Performance analytics

### Agent 8: Email Marketing
- Campaign management
- A/B testing
- Subscriber segmentation

### Agent 9: Analytics & Reporting
- Real-time analytics
- Custom KPI tracking
- Funnel analysis

### Agent 10: Campaign Management
- Multi-channel campaign orchestration
- Budget tracking
- ROI analysis

### Agent 11: Report Generation
- Automated report creation
- Custom templates
- Scheduled delivery

## 📋 Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Google Cloud Platform account (for Sheets integration)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd agent-pipeline
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and configure your settings:
```env
PORT=3000
NODE_ENV=development
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google-sheets-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
```

4. **Set up Google Sheets (Optional):**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create service account credentials
   - Download credentials JSON and place in `./credentials/`
   - Create a Google Spreadsheet and share it with the service account email

5. **Build the project:**
```bash
npm run build
```

## 🚀 Usage

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

The API will be available at `http://localhost:3000`

## 📚 API Documentation

### Health Check
```
GET /health
```

### Get All Agents Data
```
GET /api/agents/all
```

### Agent-Specific Endpoints

#### Agent 1: Lead Generation
```
GET  /api/agents/agent1/data
GET  /api/agents/agent1/statistics
POST /api/agents/agent1/leads
POST /api/agents/agent1/generate
```

#### Agent 2: Lead Qualification
```
GET  /api/agents/agent2/data
GET  /api/agents/agent2/statistics
POST /api/agents/agent2/qualify
```

#### Agent 3: Competitor Analysis
```
GET  /api/agents/agent3/data
GET  /api/agents/agent3/statistics
POST /api/agents/agent3/competitors
POST /api/agents/agent3/analyze/:id
```

#### Agent 4: Market Research
```
GET  /api/agents/agent4/data
GET  /api/agents/agent4/statistics
POST /api/agents/agent4/segments
POST /api/agents/agent4/research
```

#### Agent 5: Content Strategy
```
GET  /api/agents/agent5/data
GET  /api/agents/agent5/statistics
POST /api/agents/agent5/content
```

#### Agent 6: SEO Optimization
```
GET  /api/agents/agent6/data
GET  /api/agents/agent6/statistics
POST /api/agents/agent6/keywords
```

#### Agent 7: Social Media
```
GET  /api/agents/agent7/data
GET  /api/agents/agent7/statistics
POST /api/agents/agent7/posts
```

#### Agent 8: Email Marketing
```
GET  /api/agents/agent8/data
GET  /api/agents/agent8/statistics
POST /api/agents/agent8/campaigns
```

#### Agent 9: Analytics
```
GET  /api/agents/agent9/data
GET  /api/agents/agent9/statistics
POST /api/agents/agent9/reports
```

#### Agent 10: Campaign Management
```
GET  /api/agents/agent10/data
GET  /api/agents/agent10/statistics
POST /api/agents/agent10/campaigns
```

#### Agent 11: Report Generation
```
GET  /api/agents/agent11/data
GET  /api/agents/agent11/statistics
POST /api/agents/agent11/reports
```

### Sync to Google Sheets
```
POST /api/agents/sync-sheets
```

## 📊 Google Sheets Integration

The system automatically syncs data to Google Sheets with the following worksheets:

1. Agent 1 - Leads
2. Agent 2 - Qualified Leads
3. Agent 3 - Competitors
4. Agent 4 - Market Segments
5. Agent 5 - Content
6. Agent 6 - SEO Keywords
7. Agent 7 - Social Posts
8. Agent 8 - Email Campaigns
9. Agent 9 - Analytics
10. Agent 10 - Campaigns
11. Agent 11 - Reports

## 🏗️ Project Structure

```
agent-pipeline/
├── src/
│   ├── api/
│   │   └── routes/
│   │       └── agents.routes.ts
│   ├── config/
│   │   └── index.ts
│   ├── middleware/
│   │   └── errorHandler.ts
│   ├── services/
│   │   ├── agents/
│   │   │   ├── agent1.service.ts
│   │   │   ├── agent2.service.ts
│   │   │   ├── agent3.service.ts
│   │   │   ├── agent4.service.ts
│   │   │   ├── agent5.service.ts
│   │   │   ├── agent6.service.ts
│   │   │   ├── agent7.service.ts
│   │   │   ├── agent8.service.ts
│   │   │   ├── agent9.service.ts
│   │   │   ├── agent10.service.ts
│   │   │   └── agent11.service.ts
│   │   └── googleSheets.service.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   └── logger.ts
│   └── index.ts
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

## 🧪 Testing

```bash
npm test
```

## 🔧 Development

### Build TypeScript
```bash
npm run build
```

### Watch Mode
```bash
npm run watch
```

### Linting
```bash
npm run lint
```

### Formatting
```bash
npm run format
```

## 📈 Example Usage

### Adding a Lead (Agent 1)
```bash
curl -X POST http://localhost:3000/api/agents/agent1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "source": {
      "name": "Website",
      "type": "website"
    }
  }'
```

### Qualifying a Lead (Agent 2)
```bash
curl -X POST http://localhost:3000/api/agents/agent2/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "lead": { ... },
    "criteria": {
      "budget": { "min": 10000, "max": 50000, "currency": "USD" },
      "authority": true,
      "need": true,
      "timeline": "immediate"
    }
  }'
```

### Syncing to Google Sheets
```bash
curl -X POST http://localhost:3000/api/agents/sync-sheets
```

## 🌟 Features in Detail

### Intelligent Lead Scoring
- Multi-factor scoring algorithm
- Source-based weighting
- Behavioral analysis
- Demographic matching

### Advanced Analytics
- Real-time metrics
- Custom KPI tracking
- Conversion funnel analysis
- Traffic source attribution

### Automated Reporting
- Scheduled report generation
- Multiple format support (PDF, Excel, CSV)
- Custom templates
- Email delivery

### Campaign Orchestration
- Multi-channel coordination
- Budget optimization
- Performance tracking
- ROI calculation

## 🔒 Security

- Helmet.js for security headers
- Rate limiting
- Input validation
- Error handling
- Secure credential management

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 3000 |
| NODE_ENV | Environment | development |
| GOOGLE_SHEETS_CREDENTIALS_PATH | Path to Google credentials | ./credentials/google-sheets-credentials.json |
| GOOGLE_SHEETS_SPREADSHEET_ID | Google Sheets ID | - |
| LOG_LEVEL | Logging level | info |
| API_RATE_LIMIT_WINDOW_MS | Rate limit window | 900000 |
| API_RATE_LIMIT_MAX_REQUESTS | Max requests per window | 100 |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review API examples

## 🗺️ Roadmap

- [ ] Real-time dashboard
- [ ] Webhook support
- [ ] Advanced AI/ML integration
- [ ] Multi-tenant support
- [ ] Mobile app
- [ ] Enhanced reporting templates
- [ ] Integration with CRM systems
- [ ] Advanced automation workflows

## ✨ Acknowledgments

Built with:
- Node.js & TypeScript
- Express.js
- Google Sheets API
- Winston Logger
- And many other great open-source libraries

---

**Made with ❤️ for marketing automation**
