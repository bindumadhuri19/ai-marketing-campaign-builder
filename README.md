< HEAD
# AI Marketing Campaign Builder & QA System

A portfolio project demonstrating Marketing Operations expertise and AI integration for the **Sky Society Marketing Operations & AI Specialist** role.

## 🎯 Project Overview

This application combines AI-powered campaign content generation with automated quality assurance checks to streamline marketing campaign creation while ensuring compliance and quality standards.

### Key Features

- **Three-Stage AI Workflow**: Strategist → Content Creator → QA Reviewer
- **Multi-Channel Support**: Email and SMS campaigns
- **Automated QA Checks**: 6 deterministic Python validations
- **Human-in-Loop**: Review, edit, and approve campaigns before deployment
- **Persistence**: JSON-based campaign storage with status tracking
- **Export Options**: Download campaigns in JSON, text, and QA report formats
- **Demo Mode**: Works without API credentials using sample campaigns

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│          Campaign Input → Review → Approval             │
└────────────────┬────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┬──────────────┐
      │                     │              │
┌─────▼──────┐      ┌──────▼───────┐  ┌──▼─────────┐
│ AI Service │      │  QA Engine   │  │  Storage   │
│ (3 stages) │      │ (6 checks)   │  │   (JSON)   │
└────────────┘      └──────────────┘  └────────────┘
```

### Technology Stack

- **Python 3.9+** - Core language
- **Streamlit** - Web interface
- **Anthropic Claude API** - AI content generation (configurable model)
- **pytest** - Testing framework
- **JSON** - Campaign persistence

---

## 📁 Project Structure

```
campaign-builder/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
├── services/
│   ├── ai_service.py              # Three-stage AI workflow
│   ├── qa_engine.py               # Automated QA checks
│   └── storage.py                 # JSON persistence
│
├── utils/
│   ├── constants.py               # Channel configs, demo campaigns
│   ├── validators.py              # URL, UTM, placeholder validation
│   └── export.py                  # Export formatters
│
├── campaigns/                      # Saved campaigns (gitignored)
│
└── tests/                          # Test suite (69 tests)
    ├── test_ai_service.py
    ├── test_qa_engine.py
    ├── test_storage.py
    ├── test_validators.py
    └── test_export.py
```

---

## 🚀 Windows Setup Instructions

### Prerequisites

1. **Python 3.9 or higher**
   - Check version: `python --version`
   - Download from: https://www.python.org/downloads/

2. **Anthropic API Key** (optional for demo mode)
   - Sign up at: https://console.anthropic.com/
   - Navigate to API Keys section
   - Create a new key
   - **Note**: Requires credit card; check current pricing in the console

### Installation Steps

```cmd
REM 1. Navigate to project folder
cd C:\Users\bindu\OneDrive\Desktop\campaign-builder

REM 2. Create virtual environment
python -m venv venv

REM 3. Activate virtual environment
venv\Scripts\activate

REM 4. Install dependencies
pip install -r requirements.txt

REM 5. Configure environment variables
copy .env.example .env
notepad .env
```

### Environment Configuration

Edit `.env` file and configure:

```bash
# Required for AI generation (leave blank for demo mode)
ANTHROPIC_API_KEY=your_api_key_here

# Model configuration - check Anthropic docs for current models
# As of Oct 2024: claude-3-5-sonnet-20241022, claude-3-opus-20240229
# Visit https://docs.anthropic.com/en/docs/about-claude/models for latest
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Demo mode (uses sample campaigns without API calls)
DEMO_MODE=false
```

**Important**: 
- Billing and API pricing must be verified in the Anthropic Console
- Model names change over time - update `CLAUDE_MODEL` if you encounter deprecation errors
- Leave `ANTHROPIC_API_KEY` blank or set `DEMO_MODE=true` to use sample campaigns

---

## ▶️ Running the Application

```cmd
REM Make sure virtual environment is activated
venv\Scripts\activate

REM Start the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🧪 Running Tests

```cmd
REM Activate virtual environment
venv\Scripts\activate

REM Run all tests
pytest

REM Run with verbose output
pytest -v

REM Run specific test file
pytest tests/test_qa_engine.py

REM Run with coverage (requires pytest-cov)
pytest --cov=. --cov-report=html
```

**Test Coverage**: 69 tests covering:
- AI service (demo mode, API integration, error handling)
- QA engine (6 automated checks)
- Storage (CRUD operations, JSON persistence)
- Validators (URL, UTM, placeholders)
- Export formatters (JSON, text, QA reports)

---

## 📊 Using the Application

### 1. Create Campaign

1. Select channel (Email or SMS)
2. Fill in campaign details:
   - **Goal**: Campaign objective (e.g., "Drive demo signups")
   - **Audience**: Target audience description
   - **CTA**: Call-to-action text
   - **Destination URL**: Landing page with UTM parameters
   - **Additional Context**: Optional messaging requirements
3. Click "Generate Campaign"

### 2. Review AI Stages

The system runs three AI stages automatically:

1. **Strategist**: Analyzes requirements and creates campaign strategy
2. **Content Creator**: Generates campaign copy based on strategy
3. **QA Reviewer**: Reviews content and provides improvement suggestions

### 3. Automated QA Checks

Six deterministic Python checks run automatically:

- ✓ **CTA Presence**: Verifies CTA text appears in message
- ✓ **URL Format**: Validates destination URL structure
- ✓ **UTM Parameters**: Checks for utm_source, utm_medium, utm_campaign
- ✓ **Placeholder Detection**: Scans for unreplaced {{variables}}
- ✓ **Character Limits**: Email subject ≤78 chars, SMS ≤160 chars
- ✓ **Link in Body**: Ensures destination URL appears in message

### 4. Review & Approve

- Edit subject line and body if needed
- Review QA summary
- Choose action:
  - **Approve & Save**: Mark as approved
  - **Save as Draft**: Save for later revision
  - **Reject**: Archive as rejected

### 5. Export

Download campaign in multiple formats:
- **JSON**: Machine-readable data
- **Text**: Human-readable formatted campaign
- **QA Report**: Detailed check results

### 6. View Saved Campaigns

Use the sidebar to:
- Browse saved campaigns
- Filter by status (approved, draft, rejected)
- Load campaigns for review

---

## 🎤 Interview Demo Strategy

### 5-Minute Demo Script

**1. Introduction (30 seconds)**

> "I built an AI-powered Marketing Campaign Builder that addresses a key pain point in marketing ops: campaigns launching with broken links, missing UTM tracking, or placeholder text. This combines AI efficiency with operational rigor."

**2. Live Demo (3 minutes)**

*Create Email Campaign:*
- Fill form: "Product Launch Email" | "Tech-savvy marketers" | "Drive demo signups"
- CTA: "Book Demo"
- URL: `https://example.com/demo?utm_source=email&utm_medium=newsletter&utm_campaign=product_launch`
- Generate campaign

*Show Three AI Stages:*
- Point out Strategist analysis
- Show generated subject line and body
- Note AI Reviewer feedback

*Demonstrate QA Checks:*
- Show all checks passing with green [OK] indicators
- Edit URL to remove UTM parameters
- Regenerate → Show [ERROR] for missing tracking
- Fix URL → Regenerate → Show [OK] restored

*Complete Workflow:*
- Edit campaign copy slightly
- Click "Approve & Save"
- Show saved campaign in sidebar
- Download QA report

**3. Technical Highlights (1 minute)**

- **Three-stage AI architecture**: Strategist, Content Creator, QA Reviewer
- **6 deterministic QA checks**: Not just AI - Python validation for compliance
- **Configurable model**: CLAUDE_MODEL env var supports any Anthropic model
- **Demo mode**: Works without API credentials for easy testing
- **Tested**: 69 pytest tests with mocked API calls
- **Production-ready**: Error handling, env vars, no hardcoded secrets

**4. Value Proposition (30 seconds)**

- **Time Savings**: QA time from 15 minutes → 30 seconds
- **Error Prevention**: Catches broken links, missing tracking, placeholders before launch
- **Human Oversight**: AI-assisted but human-approved (not fully automated)
- **Extensibility**: Easy to add new channels, checks, or integrate with marketing platforms

### Key Talking Points

✅ **Demonstrates Marketing Ops Understanding**: Not just AI generation - shows awareness of campaign compliance requirements

✅ **Production Thinking**: Error handling, configurable models, demo mode, comprehensive testing

✅ **Practical Problem**: Based on real marketing QA pain points (broken links, UTM tracking)

✅ **Balance**: AI efficiency + human oversight + automated validation

### Backup Plan

If API fails during demo:
- Demo mode is always available (set `DEMO_MODE=true`)
- Pre-generated sample campaigns work without internet
- Can demonstrate QA checks, approval workflow, and exports using demo data

---

## 🔍 Automated QA Checks Explained

### 1. CTA Presence (Warning)
- **Check**: Verifies CTA text appears in message body
- **Why**: Ensures call-to-action is actually included in campaign
- **Example**: CTA "Book Demo" should appear in body text

### 2. URL Format (Error)
- **Check**: Validates destination URL structure
- **Why**: Prevents broken links from being sent
- **Example**: `https://example.com/page` is valid, `not-a-url` fails

### 3. UTM Parameters (Warning/Error)
- **Check**: Verifies presence of utm_source, utm_medium, utm_campaign
- **Why**: Essential for campaign tracking and attribution
- **Example**: `?utm_source=email&utm_medium=newsletter&utm_campaign=launch`

### 4. Placeholder Detection (Error)
- **Check**: Scans for unreplaced {{variables}}, [VARIABLES], {VARIABLES}
- **Why**: Prevents sending campaigns with merge tags still visible
- **Example**: "Hello {{FIRST_NAME}}" would trigger error

### 5. Character Limits (Warning/Error)
- **Email**: Subject line ≤78 characters (recommended for preview text)
- **SMS**: Body ≤160 characters (standard SMS limit)
- **Why**: Prevents content truncation or multi-part SMS charges

### 6. Link in Body (Warning)
- **Check**: Verifies destination URL or domain appears in message
- **Why**: Ensures users know where they're being directed
- **Example**: If destination is `example.com/demo`, "example.com" should appear in body

---

## 🚧 Known Limitations & Future Enhancements

### Current Scope

- ✅ Email and SMS channels only (no social media ads yet)
- ✅ Single user (no authentication)
- ✅ JSON file storage (no database)
- ✅ Simulation only (no actual sending)
- ✅ English language only

### Future Enhancements

- 📅 Campaign scheduling
- 🔗 Integration with marketing platforms (Mailchimp, HubSpot, Marketo)
- 📊 A/B testing support
- 👥 Multi-user authentication
- 🌐 Additional channels (LinkedIn, Facebook Ads, Google Ads)
- 📈 Analytics dashboard
- 🗄️ Database migration (PostgreSQL/MongoDB)
- 🌍 Multi-language support

---

## 🛠️ Troubleshooting

### Issue: "Anthropic API error"

**Solution**: 
1. Verify API key is correct in `.env`
2. Check https://docs.anthropic.com/en/docs/about-claude/models for current model names
3. Update `CLAUDE_MODEL` if model is deprecated
4. Enable demo mode: `DEMO_MODE=true`

### Issue: "Module not found"

**Solution**:
```cmd
REM Ensure virtual environment is activated
venv\Scripts\activate

REM Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Streamlit won't start

**Solution**:
```cmd
REM Check Python version (need 3.9+)
python --version

REM Try running with full path
venv\Scripts\streamlit run app.py
```

### Issue: Tests fail with import errors

**Solution**:
```cmd
REM Install in editable mode
pip install -e .

REM Or run from project root with PYTHONPATH
set PYTHONPATH=%cd%
pytest
```

---

## 📝 Development Notes

### Design Decisions

1. **Three-stage AI workflow**: Separates strategy, creation, and review for transparency
2. **Deterministic QA**: Python checks (not AI) ensure consistency
3. **Demo mode**: Enables testing without API costs or credentials
4. **ASCII indicators**: `[OK]`, `[WARN]`, `[ERROR]` instead of Unicode for Windows compatibility
5. **JSON storage**: Simple, version-controllable, no database setup required
6. **Configurable model**: Env var supports any Anthropic model for future-proofing

### Testing Strategy

- **Unit tests**: Individual functions (validators, QA checks, storage)
- **Integration tests**: End-to-end workflows with mocked APIs
- **Mocked AI calls**: Avoid API costs in tests
- **Unicode testing**: Verify international character support

---

## 📄 License

This is a portfolio project created for the Sky Society interview process.

---

## 👤 Author

**Bindu**

For: Sky Society - Marketing Operations & AI Specialist Role

Date: October 2024

---

## 🙏 Acknowledgments

- Anthropic Claude API for AI content generation
- Streamlit for rapid prototyping
- pytest for comprehensive testing framework

---

## 📞 Contact

For questions about this project or interview discussion, please contact via Sky Society interview coordinators.

# ai-marketing-campaign-builder
AI-powered marketing campaign generation and QA using Claude, Python, and Streamlit
 5b413ccebe0ac33e7058202baf7c82dd027c856e
