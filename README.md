# CV Creator - AI-Powered Resume & Cover Letter Generator

Generate customized resumes and cover letters tailored to specific job applications, with optional AI optimization.

## Features

- **Plain Text Input**: Simply copy/paste job descriptions and company information - no need for structured JSON
- **AI-Powered Parsing** (optional): Automatically extracts key information from plain text job postings
- **AI Resume Generation** (optional): Complete resume rewrite with bullet points tailored to job requirements, company needs, and business impact
- **AI Cover Letter Generation** (optional): Professional, authentic cover letters that avoid clichés and emphasize impact
- **Professional Templates**: Clean, modern PDF templates optimized for ATS systems
- **Application Tracking**: Organizes generated documents by company and date
- **Works Without AI**: Generate resumes without OpenAI API key (using base data without optimization)

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

**Note for macOS users:** WeasyPrint requires some system dependencies:
```bash
brew install python3 cairo pango gdk-pixbuf libffi
```

2. **Set up AI API (Optional)**:
To enable AI-powered optimization and parsing, create a `.env` file in the project root:

**For OpenAI:**
```env
OPENAI_API_KEY=sk-your-api-key-here
```

**For Custom AI providers:**
```env
OPENAI_API_URL=[URL]/chat/completions
OPENAI_API_KEY=your-api-token-here
OPENAI_MODEL=[GPT-5-Mini]
```

**For other providers** (Grok, OpenRouter, Together AI, Ollama, etc.):
See [`.env.example`](.env.example) for more examples.

**Without AI**: The tool will still work, but will use your base data as-is without customization.

3. **Configure Your Base Data**:
Edit `inputs/base_data.json` with your personal information, experience, education, and skills.

## Usage

### Quick Start with Merged Format (Recommended)

The easiest way is to use a single JSON file with both company and job information:

1. **Create a job file** (`inputs/job.json`):
```json
{
    "company": {
        "name": "Tech Innovations Inc.",
        "about": "Company description...",
        "industry": "Enterprise SaaS",
        "values": ["Innovation", "Transparency"]
    },
    "job": {
        "title": "Senior Go Developer",
        "description": "Job description...",
        "responsibilities": [...],
        "requirements": [...]
    }
}
```

2. **Run the generator**:
```bash
# Without AI optimization (default, no API key needed)
python main.py -j inputs/job.json

# With AI optimization (requires OPENAI_API_KEY in .env)
python main.py -j inputs/job.json --use-ai
```

### Using Separate Files (Legacy Mode)

You can still use separate files for backwards compatibility:

```bash
# Without AI optimization
python main.py -j job.txt -c company.txt

# With AI optimization
python main.py -j job.txt -c company.txt --use-ai
```

**Without AI** (default), the tool will:
- Use basic text parsing for plain text files (or require JSON input)
- Use your base data as-is without optimization
- Still generate professional PDF documents

**With AI enabled** (`--use-ai` flag), the tool will:
**With AI enabled** (`--use-ai` flag), the tool will:
- Parse the job description to extract requirements, skills, and responsibilities
- Parse company information to understand their culture and values
- **Generate a complete AI-optimized resume** with:
  - Rewritten bullet points tailored to the job description
  - Reordered experience bullets by relevance to the target role
  - Emphasis on outcomes, ownership, scale, and reliability
  - Strong action verbs and impact-driven statements
  - ATS-friendly keywords naturally integrated
- **Generate an authentic, human-sounding cover letter** that:
  - Starts with a strong hook highlighting impact
  - Connects your experience to the company's mission
  - Avoids generic phrases and corporate jargon
  - Emphasizes measurable outcomes and engineering ownership
- Save everything in a timestamped folder under `applications/`

**Important:** The AI only uses information from your `base_data.json` - it never invents experience, skills, or achievements.

### Command Line Options

```bash
python main.py -j <job_file> [-c <company_file>] [-b <base_data_file>] [--use-ai]

Options:
  -j, --job       Path to job file (JSON with 'company' and 'job' sections, or plain text)
  -c, --company   Path to separate company info file (optional, for backwards compatibility)
  -b, --base      Path to your base data JSON (default: inputs/base_data.json)
  --use-ai        Enable AI optimization (requires OPENAI_API_KEY in .env)
```

**Note:** The `--base` parameter now defaults to `inputs/base_data.json`, so you don't need to specify it every time.

## How It Works

1. **Input Processing**: Accepts plain text or JSON files for job and company information
2. **AI Parsing** (if enabled): Uses AI to extract structured data from unstructured text
3. **AI Resume Generation** (if enabled): 
   - Analyzes your `base_data.json` in the context of the job description and company
   - Rewrites ALL experience bullet points to:
     - Align with job requirements and company technical needs
     - Emphasize business impact relevant to the role
     - Start with strong action verbs (designed, built, scaled, optimized)
     - Highlight outcomes, ownership, scale, and reliability
   - Reorders bullet points by relevance (most relevant first)
   - Optimizes professional summary to match the role
   - Maintains 100% accuracy - never invents skills or experience
4. **AI Cover Letter Generation** (if enabled):
   - Creates a confident, senior-level cover letter
   - Focuses on concrete achievements and engineering ownership
   - Avoids clichés like "I am excited to apply" or "passionate about technology"
   - Connects your experience to company mission and specific role
5. **Document Generation**: Creates professional PDF documents using customized templates
6. **Archive Management**: Saves all versions and source data for future reference

## Output Structure

After running, you'll get a folder like:
```
applications/
  Company_Name_20260202_220153/
    ├── resume.pdf
    ├── cover_letter.pdf
    ├── customized_data.json
    ├── base_data_snapshot.json
    ├── parsed_job_description.json
    └── parsed_company_info.json
```

## Tips for Best Results

### Resume Generation
1. **Complete Base Data**: Fill out `inputs/base_data.json` thoroughly with your real experience, including:
   - Specific metrics and achievements (e.g., "improved performance by 30%", "handled 100,000+ users")
   - Technical tools and technologies you've used
   - Team sizes you've led or mentored
   - Scale of systems you've built (users, requests, uptime, etc.)
2. **Detailed Job Input**: More context in job/company files = better customization
3. **AI Strategy**: The AI follows a senior-level resume strategy:
   - Uses strong action verbs: designed, built, scaled, optimized, owned, led
   - Avoids weak phrases: "worked on", "responsible for", "helped with"
   - Emphasizes impact, scale, and reliability
   - Keeps it human-readable, not corporate boilerplate
   - Naturally integrates ATS keywords from the job description

### Cover Letter Generation
1. **Company Research**: Include company mission, values, and recent achievements in company info
2. **Authentic Voice**: AI generates confident, senior-level prose without clichés
3. **Impact Focus**: Emphasizes measurable outcomes and engineering ownership

### General Tips
1. **Review Before Sending**: Always review generated documents before submitting
2. **Update Base Data**: Keep your base data current as you gain new skills/experience
3. **Version Control**: All generated documents are saved with timestamps for comparison

## Requirements

- Python 3.8+
- OpenAI API key (optional, for AI optimization)
- Dependencies: jinja2, weasyprint, openai, python-dotenv

## License

MIT License
