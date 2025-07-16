# 🌌 AI Open Source Researcher

A sophisticated multi-agent AI system that helps you discover the perfect open-source projects for your needs. Using CrewAI's agent orchestration framework, this application deploys specialized AI agents to analyze your requirements, research GitHub repositories, and provide curated recommendations.

## ✨ Features

- **Multi-Agent Architecture**: Three specialized AI agents working in harmony
- **Intelligent Analysis**: Converts business requirements into technical specifications
- **GitHub Integration**: Searches and analyzes thousands of open-source projects
- **Smart Evaluation**: Provides detailed project assessments and recommendations
- **Modern UI**: Beautiful, responsive Streamlit interface with dark theme
- **Retry Logic**: Robust error handling with exponential backoff

## 🤖 Agent Roles

### 1. Requirement Analyst
- **Role**: Analyzes user requirements and extracts key technical specifications
- **Goal**: Translate business needs into searchable technical criteria
- **Output**: Structured summary of project requirements and evaluation criteria

### 2. Open Source Researcher
- **Role**: Searches GitHub for relevant open-source projects
- **Goal**: Find projects matching the analyzed requirements
- **Tools**: GitHub Search (via Serper API)
- **Output**: List of 10 potential projects with detailed information

### 3. Evaluator Agent
- **Role**: Evaluates and ranks the discovered projects
- **Goal**: Provide detailed analysis and final recommendations
- **Output**: Comprehensive evaluation report with pros/cons and recommendations

## 🚀 Installation

### Prerequisites

- Python 3.8+
- API Keys:
  - Serper API Key (for GitHub search)
  - Gmeini API Key (for CrewAI agents)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kartavya-AI/Open-Source-Projects.git
   cd Open-Source-Projects
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements.txt

```txt
streamlit>=1.28.0
crewai>=0.1.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0
langchain>=0.1.0
```

## 🔧 Configuration

### Agent Configuration (`src/open_source/config/agents.yaml`)

The agents are configured with specific roles, goals, and backstories. You can modify these configurations to adjust agent behavior:

```yaml
requirement_analyst:
  role: "Requirement Analyst"
  goal: "Analyze user-provided business requirements..."
  backstory: "An expert in software development..."
  allow_delegation: false
```

### Task Configuration (`src/open_source/config/tasks.yaml`)

Tasks define what each agent should accomplish:

```yaml
analyze_requirements:
  description: "Analyze the user's business requirement..."
  expected_output: "A structured summary..."
```

## 🎯 Usage

### Web Interface

1. **Launch the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the interface**
   - Open your browser to `http://localhost:8501`
   - Enter your project requirements in the text area
   - Click "🚀 Launch Agents" to start the research

### Command Line Interface

```bash
python src/open_source/main.py
```

### Example Requirements

```text
I need a self-hostable, lightweight CRM system with a modern UI, 
a good API for integrations, and built with Python/Django.
```

```text
Looking for a React-based dashboard library with TypeScript support, 
charting capabilities, and MIT license for a commercial project.
```

## 🏗️ Architecture

```
├── app.py                          # Streamlit web interface
├── src/
│   └── open_source/
│       ├── __init__.py
│       ├── main.py                 # CLI interface
│       ├── crew.py                 # Core CrewAI logic
│       ├── config/
│       │   ├── agents.yaml         # Agent configurations
│       │   └── tasks.yaml          # Task definitions
│       └── tools/
│           ├── __init__.py
│           └── custom_tool.py      # GitHub search tool
└── .env                            # Environment variables
```

## 🛠️ Technical Details

### Multi-Agent Workflow

1. **Analysis Phase**: Requirement Analyst processes user input
2. **Research Phase**: Open Source Researcher searches GitHub
3. **Evaluation Phase**: Evaluator Agent ranks and recommends projects

### Search Strategy

- Uses Serper API for Google-powered GitHub search
- Targets `site:github.com` for focused results
- Retrieves project metadata, activity, and licensing information
- Handles rate limiting and API errors gracefully

### Error Handling

- **Retry Logic**: Exponential backoff for API overload scenarios
- **Graceful Degradation**: Informative error messages for users
- **Validation**: Input validation and sanitization

## 🔍 API Integration

### Serper API
- **Purpose**: GitHub project search
- **Endpoint**: `https://google.serper.dev/search`
- **Rate Limits**: Configurable retry logic
- **Response Format**: JSON with organic search results

### CrewAI Integration
- **Framework**: Multi-agent orchestration
- **Process**: Sequential task execution
- **Tools**: Custom GitHub search tool
- **LLM**: Gemini 2.0 Flash models

## 📊 Output Format

The system provides structured recommendations including:

- **Project Summary**: Name, description, and purpose
- **Technical Details**: Languages, frameworks, dependencies
- **Community Metrics**: Stars, forks, contributors, activity
- **Licensing**: License type and commercial viability
- **Assessment**: Pros, cons, and fit analysis
- **Recommendation**: Ranked suggestions with justification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent framework
- **Streamlit**: Web interface framework
- **Serper API**: Search functionality
- **Google Gemini**: Language model capabilities

## 📞 Support

For issues and questions:
- Open an issue in the repository
- Check the troubleshooting section
- Review agent configurations
