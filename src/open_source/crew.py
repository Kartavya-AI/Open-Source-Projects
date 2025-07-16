import os
import yaml
import json
import requests
import time
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# --- Tool Definition using CrewAI's @tool decorator ---
@tool("Github Search")
def github_search_tool(query: str) -> str:
    """
    Searches Github for open-source projects based on a query.
    This tool uses the Serper API to perform a Google search focused on github.com.
    
    Args:
        query (str): The search query for GitHub projects
        
    Returns:
        str: Formatted search results
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable not set."

    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": f"site:github.com {query}", "num": 10})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        results = response.json()
        
        if 'organic' in results:
            # Formatting the results into a readable string for the agent
            formatted_results = []
            for item in results['organic']:
                formatted_results.append(
                    f"Title: {item.get('title', 'N/A')}\n"
                    f"Link: {item.get('link', '#')}\n"
                    f"Snippet: {item.get('snippet', 'No snippet available.')}\n"
                    "---"
                )
            return "\n".join(formatted_results) if formatted_results else "No relevant GitHub projects found."
        return "No organic results found."
    except requests.exceptions.RequestException as e:
        return f"Error making request to Serper API: {e}"
    except json.JSONDecodeError:
        return "Error: Failed to decode JSON response from Serper API."


class OpenSourceCrew:
    def __init__(self, business_requirement, gemini_api_key=None):
        self.business_requirement = business_requirement
        self.gemini_api_key = gemini_api_key
        self._setup_environment()
        self._load_configs()

    def _setup_environment(self):
        """Set up the Gemini API key in environment variables."""
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key
            # Also set it as GEMINI_API_KEY for compatibility
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        elif not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
            raise ValueError("Gemini API key is required. Please provide it either through the UI or environment variables.")

    def _load_configs(self):
        """Loads agent and task configurations from YAML files."""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        agents_config_path = os.path.join(dir_path, 'config/agents.yaml')
        tasks_config_path = os.path.join(dir_path, 'config/tasks.yaml')

        with open(agents_config_path, 'r') as f:
            self.agents_config = yaml.safe_load(f)
        
        with open(tasks_config_path, 'r') as f:
            self.tasks_config = yaml.safe_load(f)

    def _create_llm(self):
        """Create and configure the LLM instance."""
        try:
            # Try using LiteLLM with proper provider format
            from litellm import completion
            
            # Create a wrapper function that uses LiteLLM
            def llm_wrapper(prompt, **kwargs):
                response = completion(
                    model="gemini/gemini-pro",
                    messages=[{"role": "user", "content": prompt}],
                    api_key=self.gemini_api_key or os.getenv("GOOGLE_API_KEY"),
                    temperature=0.7,
                    max_tokens=4000
                )
                return response.choices[0].message.content
            
            return llm_wrapper
            
        except ImportError:
            # Fallback to direct Google API
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.7,
                    google_api_key=self.gemini_api_key or os.getenv("GOOGLE_API_KEY")
                )
            except ImportError:
                raise ImportError("Please install either 'litellm' or 'langchain-google-genai' package")

    def run(self):
        """Sets up and runs the crew with retry logic."""
        agents_cfg = self.agents_config
        tasks_cfg = self.tasks_config

        # Create LLM instance
        llm = self._create_llm()

        # Define Agents - let CrewAI handle the LLM configuration
        requirement_analyst = Agent(
            role=agents_cfg['requirement_analyst']['role'],
            goal=agents_cfg['requirement_analyst']['goal'],
            backstory=agents_cfg['requirement_analyst']['backstory'],
            verbose=True
        )
        
        open_source_researcher = Agent(
            role=agents_cfg['open_source_researcher']['role'],
            goal=agents_cfg['open_source_researcher']['goal'],
            backstory=agents_cfg['open_source_researcher']['backstory'],
            tools=[github_search_tool],
            verbose=True
        )
        # Define Tasks
        analyze_task = Task(
            description=tasks_cfg['analyze_requirements']['description'].format(business_requirement=self.business_requirement),
            expected_output=tasks_cfg['analyze_requirements']['expected_output'],
            agent=requirement_analyst
        )

        research_task = Task(
            description=tasks_cfg['research_projects']['description'],
            expected_output=tasks_cfg['research_projects']['expected_output'],
            agent=open_source_researcher,
            context=[analyze_task]
        )

        # Create and run the crew with retry logic
        crew = Crew(
            agents=[requirement_analyst, open_source_researcher],
            tasks=[analyze_task, research_task],
            process=Process.sequential,
            verbose=True
        )

        # Retry logic for handling model overload
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}")
                result = crew.kickoff()
                return result
            except Exception as e:
                error_msg = str(e)
                if ("overloaded" in error_msg.lower() or 
                    "unavailable" in error_msg.lower() or 
                    "503" in error_msg or
                    "rate limit" in error_msg.lower() or
                    "quota" in error_msg.lower()):
                    if attempt < max_retries - 1:
                        print(f"Model overloaded or rate limited. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print("Max retries reached. Model still overloaded or rate limited.")
                        raise ValueError(f"Service temporarily unavailable. Please try again later. Error: {error_msg}")
                elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise ValueError(f"Invalid API key or authentication error. Please check your Gemini API key. Error: {error_msg}")
                else:
                    # For other errors, don't retry
                    raise e