import os
import yaml
import json
import requests
import time
from typing import Optional, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_community.chat_models import ChatLiteLLM

from dotenv import load_dotenv
load_dotenv()

@tool("Github Search")
def github_search_tool(query: str) -> str:
    """
    Searches Github for open-source projects based on a query.
    This tool uses the Serper API to perform a Google search focused on github.com.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable not set."

    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": f"site:github.com {query} stars:>100",  # Added stars filter for better results
        "num": 8,  # Reduced from 10 for faster response
        "gl": "us",
        "hl": "en"
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)  # Reduced timeout
        response.raise_for_status()
        results = response.json()
        
        if 'organic' in results and results['organic']:
            formatted_results = []
            for idx, item in enumerate(results['organic'][:6], 1):  # Limit to top 6 results
                title = item.get('title', 'N/A')
                link = item.get('link', '#')
                snippet = item.get('snippet', 'No description available.')
                
                formatted_results.append(
                    f"{idx}. **{title}**\n   URL: {link}\n   Description: {snippet}\n"
                )
            
            return "\n".join(formatted_results) if formatted_results else "No relevant GitHub projects found."
        else:
            return f"No GitHub projects found for query: {query}."
            
    except Exception as e:
        return f"Search error: {str(e)[:100]}..."


class OpenSourceCrew:
    def __init__(self, business_requirement: str, gemini_api_key: Optional[str] = None):
        self.business_requirement = business_requirement
        self.gemini_api_key = gemini_api_key
        self.llm = self._create_llm()
        self._setup_environment()
        self._load_configs()

    def _setup_environment(self):
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        elif not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
            raise ValueError("Gemini API key is required.")

    def _load_configs(self):
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            agents_config_path = os.path.join(dir_path, 'config/agents.yaml')
            tasks_config_path = os.path.join(dir_path, 'config/tasks.yaml')
            with open(agents_config_path, 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f)
            with open(tasks_config_path, 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f)
                
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def _create_llm(self):
        try:
            return ChatLiteLLM(
                model="gemini/gemini-2.5-flash",  # Changed to Flash for speed
                temperature=0.1,  # Fixed typo
                max_tokens=1000  # Limit token usage for faster responses
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini AI: {str(e)}")

    def _execute_crew(self, crew: Crew) -> str:
        """Execute the crew with timeout protection."""
        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['overloaded', 'unavailable', '503', 'rate limit', 'quota', 'resource_exhausted']):
                raise e
            elif any(keyword in error_msg for keyword in ['api key', 'authentication', 'permission', 'forbidden']):
                raise ValueError(f"Authentication error: Please check your Gemini API key.")
            else:
                raise e

    def run(self) -> str:
        """Sets up and runs the crew with optimized configuration."""
        try:
            agents_cfg = self.agents_config
            tasks_cfg = self.tasks_config
            llm = self._create_llm()

            # Create streamlined agents
            requirement_analyst = Agent(
                role=agents_cfg['requirement_analyst']['role'],
                goal=agents_cfg['requirement_analyst']['goal'],
                backstory=agents_cfg['requirement_analyst']['backstory'],
                llm=llm,
                verbose=False,  # Reduced verbosity for speed
                max_execution_time=30  # 30 second timeout
            )
            
            open_source_researcher = Agent(
                role=agents_cfg['open_source_researcher']['role'],
                goal=agents_cfg['open_source_researcher']['goal'],
                backstory=agents_cfg['open_source_researcher']['backstory'],
                tools=[github_search_tool],
                llm=llm,
                verbose=False,
                max_execution_time=45  # 45 second timeout
            )
            
            project_evaluator = Agent(
                role=agents_cfg['project_evaluator']['role'],
                goal=agents_cfg['project_evaluator']['goal'],
                backstory=agents_cfg['project_evaluator']['backstory'],
                llm=llm,
                verbose=False,
                max_execution_time=30  # 30 second timeout
            )
            
            # Create optimized tasks
            analyze_task = Task(
                description=tasks_cfg['analyze_requirements']['description'].format(
                    business_requirement=self.business_requirement
                ),
                expected_output=tasks_cfg['analyze_requirements']['expected_output'],
                agent=requirement_analyst
            )

            research_task = Task(
                description=tasks_cfg['research_projects']['description'],
                expected_output=tasks_cfg['research_projects']['expected_output'],
                agent=open_source_researcher,
                context=[analyze_task]
            )
            
            evaluate_task = Task(
                description=tasks_cfg['evaluate_projects']['description'],
                expected_output=tasks_cfg['evaluate_projects']['expected_output'],
                agent=project_evaluator,
                context=[analyze_task, research_task]
            )

            # Optimized crew configuration
            crew = Crew(
                agents=[requirement_analyst, open_source_researcher, project_evaluator],
                tasks=[analyze_task, research_task, evaluate_task],
                process=Process.sequential,
                verbose=False,  # Reduced verbosity
                memory=False,
                max_rpm=30,  # Increased from 5 to 30
                max_execution_time=120  # 2 minute total timeout
            )

            result = self._execute_crew(crew)
            return result

        except ValueError as e:
            raise e
        except Exception as e:
            error_msg = str(e)
            if any(keyword in error_msg.lower() for keyword in ['overloaded', 'unavailable', '503', 'rate limit', 'quota']):
                return f"⚠️ Service temporarily unavailable. Please try again shortly.\n\nDetails: {error_msg}"
            else:
                return f"❌ Execution error: {error_msg}"
