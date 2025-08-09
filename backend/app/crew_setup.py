import os
from typing import List, Dict, Any

from pydantic import BaseModel

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool, tool
import arxiv

from google import genai
import json
import re

# Configure Gemini direct client
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# Normalize model id if user set 'models/...' like in some docs
if GEMINI_MODEL.startswith("models/"):
    GEMINI_MODEL = GEMINI_MODEL.split("/", 1)[1]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Create a Gemini client (reads GEMINI_API_KEY from env)
try:
    GENAI_CLIENT = genai.Client()
except Exception:
    GENAI_CLIENT = None

# Create CrewAI LLM for Gemini
def get_gemini_llm():
    if GEMINI_API_KEY:
        return LLM(
            model=f"gemini/{GEMINI_MODEL}",
            api_key=GEMINI_API_KEY
        )
    return None


class PaperMeta(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    link: str
    published: str


# Arxiv search function (without decorator first)
def _arxiv_search_function(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search arXiv for the most relevant papers for the given query.
    Returns a list of dicts with title, authors, abstract, link, published.
    """
    try:
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        results: List[Dict[str, Any]] = []
        for r in search.results():
            authors = [a.name for a in r.authors]
            results.append({
                "title": r.title,
                "authors": authors,
                "abstract": r.summary,
                "link": r.entry_id,
                "published": r.published.strftime("%Y-%m-%d") if r.published else None,
            })
        return results
    except Exception as e:
        print(f"Error in arXiv search: {e}")
        # Return empty list if search fails
        return []

# Create the tool using the decorator (proper CrewAI way)
@tool
def arxiv_search_tool(query: str, max_results: int = 5) -> str:
    """Search arXiv for the most relevant papers for the given query and return as JSON string."""
    print(f"ArXiv tool called with query: {query}, max_results: {max_results}")
    import json
    results = _arxiv_search_function(query, max_results)
    print(f"ArXiv tool found {len(results)} papers")
    json_result = json.dumps(results)
    print(f"ArXiv tool returning JSON of length: {len(json_result)}")
    return json_result


def build_agents():
    print("Building CrewAI agents...")

    # Get Gemini LLM for agents
    gemini_llm = get_gemini_llm()
    print(f"Using LLM: {gemini_llm.model if gemini_llm else 'None'}")

    # SearchAgent - uses tool to search arXiv
    search_agent = Agent(
        role="Research Paper Finder",
        goal="Search arXiv for top N papers matching the topic using the arxiv search tool.",
        backstory="You are skilled at finding relevant academic papers using arXiv. Use the arxiv_search_tool to fetch paper metadata.",
        tools=[arxiv_search_tool],
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm,
    )
    print(f"Created search agent with {len(search_agent.tools)} tools")

    # SummaryAgent - simple agent for coordination
    summary_agent = Agent(
        role="Research Paper Summarizer",
        goal="Coordinate the summarization process.",
        backstory="You help coordinate the research paper summarization workflow.",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm,
    )
    print("Created summary agent")

    return search_agent, summary_agent


def build_tasks(topic: str, top_n: int, search_agent: Agent, summary_agent: Agent):
    print(f"Building CrewAI tasks for topic: {topic}, top_n: {top_n}")

    # Task 1: search using the tool
    search_task = Task(
        description=f"Use the arxiv_search_tool to search for {top_n} papers about '{topic}'. Return the JSON result from the tool.",
        agent=search_agent,
        expected_output="JSON string containing paper metadata from arXiv search.",
    )
    print("Created search task")

    # Task 2: format the results
    summary_task = Task(
        description="Take the JSON results from the search task and return them as-is for backend processing.",
        agent=summary_agent,
        expected_output="The same JSON string from the search task.",
        context=[search_task],
    )
    print("Created summary task")

    return search_task, summary_task


# --- Direct Gemini summarization helper ---
def _clean_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


def _summarize_with_gemini(paper: Dict[str, Any]) -> Dict[str, Any]:
    if GENAI_CLIENT is None:
        return {"problem": "", "methodology": "", "findings": "", "limitations": ""}
    prompt = (
        "Summarize the following paper metadata into strict JSON with keys: problem, methodology, findings, limitations.\n"
        "Respond with JSON only.\n\n"
        f"Title: {paper.get('title','')}\n"
        f"Authors: {', '.join(paper.get('authors', []))}\n"
        f"Abstract: {paper.get('abstract','')}\n"
    )
    resp = GENAI_CLIENT.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    text = getattr(resp, "text", None) or "{}"
    try:
        return json.loads(_clean_json_text(text))
    except Exception:
        return {"problem": "", "methodology": "", "findings": "", "limitations": ""}



def run_research_crew(topic: str, top_n: int = 5):
    print(f"Starting research crew for topic: {topic}")

    try:
        print("Initializing CrewAI agents and tasks...")
        search_agent, summary_agent = build_agents()
        search_task, summary_task = build_tasks(topic, top_n, search_agent, summary_agent)

        print("Creating CrewAI crew...")
        crew = Crew(
            agents=[search_agent, summary_agent],
            tasks=[search_task, summary_task],
            process=Process.sequential,
            verbose=True,
        )

        print("Executing CrewAI crew...")
        result = crew.kickoff()
        print(f"CrewAI result type: {type(result)}")
        print(f"CrewAI result: {result}")

    except Exception as e:
        print(f"CrewAI execution failed: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: direct arXiv search without crew
        print("Falling back to direct arXiv search...")
        papers = _arxiv_search_function(topic, max_results=top_n)
        result = papers

    # Process the result from CrewAI or fallback
    model = GEMINI_MODEL if GEMINI_API_KEY else "gemini-2.5-flash"

    # Handle different result types
    papers: List[Dict[str, Any]] = []

    if isinstance(result, str):
        # CrewAI returned JSON string from tool
        try:
            import json
            papers = json.loads(result)
            print("Successfully parsed JSON result from CrewAI")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON result from CrewAI: {e}")
            papers = []
    elif isinstance(result, list):
        # Direct search result or parsed list
        papers = result
        print("Using direct list result")
    elif hasattr(result, 'raw') and isinstance(result.raw, str):
        # CrewAI TaskOutput with raw string
        try:
            import json
            papers = json.loads(result.raw)
            print("Successfully parsed JSON from CrewAI TaskOutput.raw")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from CrewAI TaskOutput: {e}")
            papers = []
    elif hasattr(result, 'raw'):
        # CrewAI TaskOutput with non-string raw
        if isinstance(result.raw, list):
            papers = result.raw
            print("Using CrewAI TaskOutput.raw as list")
        else:
            print(f"Unexpected CrewAI TaskOutput.raw type: {type(result.raw)}")
            papers = []
    else:
        print(f"Unexpected result type: {type(result)}")
        papers = []

    print(f"Found {len(papers)} papers for topic: {topic}")

    # If no papers found, try direct search as final fallback
    if not papers:
        print("No papers found from CrewAI, trying direct arXiv search as final fallback...")
        papers = _arxiv_search_function(topic, max_results=top_n)
        print(f"Direct search found {len(papers)} papers")

    # Ensure each paper has required fields and generate summaries directly via Gemini
    normalized: List[Dict[str, Any]] = []
    for p in papers:
        if not isinstance(p, dict):
            continue
        base = {
            "title": p.get("title") or "",
            "authors": p.get("authors") or [],
            "abstract": p.get("abstract") or "",
            "link": p.get("link") or "",
            "published": p.get("published"),
        }
        summary = p.get("summary")
        if not summary or not isinstance(summary, dict):
            summary = _summarize_with_gemini(base)
        normalized.append({**base, "summary": {
            "problem": summary.get("problem", ""),
            "methodology": summary.get("methodology", ""),
            "findings": summary.get("findings", ""),
            "limitations": summary.get("limitations", ""),
        }})

    return {
        "topic": topic,
        "model": model,
        "papers": normalized,
    }

