# 🌌 AI Open Source Researcher

A sophisticated multi-agent AI system that helps you discover the perfect open-source projects for your needs. Using CrewAI's agent orchestration framework, this application deploys specialized AI agents to analyze your requirements, research GitHub repositories, and provide curated recommendations.

## ✨ Features

- **Multi-Agent Architecture**: Three specialized AI agents working in harmony
- **Intelligent Analysis**: Converts business requirements into technical specifications
- **GitHub Integration**: Searches and analyzes thousands of open-source projects
- **Smart Evaluation**: Provides detailed project assessments and recommendations
- **Modern UI**: Beautiful, responsive Streamlit interface with dark theme
- **Retry Logic**: Robust error handling with exponential backoff
- **Containerized Deployment**: Docker support for easy deployment
- **Cloud Ready**: GCP Cloud Run deployment configuration

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

## 🚀 Installation & Deployment

### Prerequisites

- Python 3.11+
- Docker (for containerization)
- Google Cloud SDK (for GCP deployment)
- API Keys:
  - Serper API Key (for GitHub search)
  - Google Gemini API Key (for CrewAI agents)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kartavya-AI/Open-Source-Projects.git
   cd Open-Source-Projects
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SERPER_API_KEY=your_serper_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### 🐳 Docker Deployment

#### Local Docker Build and Run

1. **Build the Docker image**
   ```bash
   docker build -t ai-open-source-researcher .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 \
     -e SERPER_API_KEY=your_serper_api_key \
     -e GOOGLE_API_KEY=your_gemini_api_key \
     -e GEMINI_API_KEY=your_gemini_api_key \
     ai-open-source-researcher
   ```

3. **Access the application**
   - Open your browser to `http://localhost:8080`

#### Docker Configuration Details

The application uses a multi-stage Docker build with the following specifications:

- **Base Image**: `python:3.11-slim-bullseye`
- **Working Directory**: `/app`
- **Exposed Port**: `8080`
- **Web Server**: Gunicorn with Uvicorn workers
- **Configuration**: 1 worker, 2 threads per worker for optimal performance

### ☁️ Google Cloud Platform Deployment

#### Prerequisites for GCP Deployment

1. **Install Google Cloud SDK**
   ```bash
   # For macOS
   brew install google-cloud-sdk
   
   # For Ubuntu/Debian
   sudo apt-get install google-cloud-sdk
   
   # For Windows - download from https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Google Cloud**
   ```bash
   gcloud auth login
   ```

3. **List and select your project**
   ```bash
   gcloud projects list
   gcloud config set project YOUR_PROJECT_ID
   ```

#### Step-by-Step GCP Deployment

1. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Create Artifact Registry Repository**
   ```bash
   # Set variables
   export REPO_NAME="ai-researcher-repo"
   export REGION="us-central1"
   export PROJECT_ID=$(gcloud config get-value project)
   
   # Create repository
   gcloud artifacts repositories create $REPO_NAME \
       --repository-format=docker \
       --location=$REGION \
       --description="AI Open Source Researcher Docker Repository"
   ```

3. **Build and Push Docker Image**
   ```bash
   # Set image tag
   export IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/ai-researcher:latest"
   
   # Build and push using Cloud Build
   gcloud builds submit --tag $IMAGE_TAG
   ```

4. **Deploy to Cloud Run**
   ```bash
   export SERVICE_NAME="ai-open-source-researcher"
   
   gcloud run deploy $SERVICE_NAME \
       --image=$IMAGE_TAG \
       --platform=managed \
       --region=$REGION \
       --allow-unauthenticated \
       --port=8080 \
       --memory=2Gi \
       --cpu=1 \
       --set-env-vars="SERPER_API_KEY=your_serper_api_key,GOOGLE_API_KEY=your_gemini_api_key,GEMINI_API_KEY=your_gemini_api_key"
   ```

#### Alternative: Using Cloud Run with Secrets

For better security, store API keys in Google Secret Manager:

1. **Create secrets**
   ```bash
   echo -n "your_serper_api_key" | gcloud secrets create serper-api-key --data-file=-
   echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key --data-file=-
   ```

2. **Deploy with secrets**
   ```bash
   gcloud run deploy $SERVICE_NAME \
       --image=$IMAGE_TAG \
       --platform=managed \
       --region=$REGION \
       --allow-unauthenticated \
       --port=8080 \
       --memory=2Gi \
       --cpu=1 \
       --set-secrets="SERPER_API_KEY=serper-api-key:latest,GOOGLE_API_KEY=gemini-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest"
   ```

#### PowerShell Commands for Windows

If you're using PowerShell on Windows, use these commands:

```powershell
# Set variables
$REPO_NAME = "ai-researcher-repo"
$REGION = "us-central1"
$PROJECT_ID = $(gcloud config get-value project)
$IMAGE_TAG = "$($REGION)-docker.pkg.dev/$($PROJECT_ID)/$($REPO_NAME)/ai-researcher:latest"
$SERVICE_NAME = "ai-open-source-researcher"

# Create repository
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="AI Open Source Researcher Docker Repository"

# Build and push
gcloud builds submit --tag $IMAGE_TAG

# Deploy
gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_TAG `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --memory=2Gi `
    --cpu=1 `
    --set-env-vars="SERPER_API_KEY=your_serper_api_key,GOOGLE_API_KEY=your_gemini_api_key,GEMINI_API_KEY=your_gemini_api_key"
```

### 🔧 Configuration Files

#### Dockerfile
```dockerfile
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-w", "1", "--threads", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "api:app"]
```

#### .dockerignore
```
# Git
.git
.gitignore

# Virtual environment
.venv
venv/
env/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Report files
*.md
```

### 📋 Requirements

#### requirements.txt
```txt
crewai
crewai[tools]
langchain-community
fastapi
uvicorn
python-dotenv
gunicorn
```

#### pyproject.toml
```toml
[project]
name = "open_source"
version = "0.1.0"
description = "open_source using crewAI"
requires-python = ">=3.10,<3.14"
dependencies = [
    "crewai[tools]>=0.134.0,<1.0.0",
    "pysqlite3-binary == 0.5.4",
    "streamlit>=1.28.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "pyyaml>=6.0.1",
    "langchain>=0.1.0",
    "langchain-google-genai>=1.0.0",
    "google-generativeai>=0.3.0",
    "litellm>=1.0.0",
    "tenacity>=8.0.0"
]
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

### Web Interface (Streamlit)

1. **Launch the application locally**
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

### API Interface (FastAPI)

The application also supports FastAPI for programmatic access:

```bash
# Start the API server
uvicorn api:app --host 0.0.0.0 --port 8080

# Or using the Docker container
docker run -p 8080:8080 ai-open-source-researcher
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
├── api.py                          # FastAPI interface
├── Dockerfile                      # Docker configuration
├── requirements.txt                # Python dependencies
├── .dockerignore                   # Docker ignore file
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
├── knowledge/
│   └── user_preference.txt         # User preferences
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

### Deployment Considerations

- **Resource Requirements**: 2GB memory, 1 CPU recommended for production
- **Scaling**: Cloud Run automatically scales based on traffic
- **Cost Optimization**: Pay-per-use pricing model with Cloud Run
- **Security**: API keys stored in Google Secret Manager

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
- **LLM**: Gemini models via LiteLLM

### Google Gemini API
- **Model**: `gemini-1.5-pro-latest`
- **Provider**: Google AI
- **Integration**: Via LiteLLM for standardized interface
- **Configuration**: Temperature set to 0.1 for consistent responses

## 📊 Output Format

The system provides structured recommendations including:

- **Project Summary**: Name, description, and purpose
- **Technical Details**: Languages, frameworks, dependencies
- **Community Metrics**: Stars, forks, contributors, activity
- **Licensing**: License type and commercial viability
- **Assessment**: Pros, cons, and fit analysis
- **Recommendation**: Ranked suggestions with justification

## 🚀 Production Deployment Tips

### Performance Optimization
- Use Cloud Run with minimum instances for consistent response times
- Enable Cloud CDN for static assets if serving web content
- Monitor resource usage and adjust CPU/memory allocation

### Security Best Practices
- Store sensitive API keys in Google Secret Manager
- Use IAM roles with least privilege principle
- Enable audit logging for Cloud Run services
- Implement proper CORS policies if needed

### Monitoring and Logging
- Enable Cloud Run logging and monitoring
- Set up alerting for error rates and response times
- Use Cloud Trace for request tracing

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
- **Google Cloud Platform**: Cloud infrastructure

## 📞 Support

For issues and questions:
- Open an issue in the repository
- Check the troubleshooting section
- Review agent configurations
- Consult GCP documentation for deployment issues

## 🔍 Troubleshooting

### Common Issues

**Docker Build Fails**
- Ensure all dependencies are in requirements.txt
- Check that the Dockerfile syntax is correct
- Verify Python version compatibility

**GCP Deployment Issues**
- Verify API keys are correctly set as environment variables
- Check that all required APIs are enabled
- Ensure proper IAM permissions for Cloud Build and Cloud Run

**API Rate Limits**
- Monitor Serper API usage
- Implement proper retry logic
- Consider upgrading API plans if needed

**Memory Issues**
- Increase Cloud Run memory allocation
- Optimize agent configurations
- Monitor resource usage patterns
