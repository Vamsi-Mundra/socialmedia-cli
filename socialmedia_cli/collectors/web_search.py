"""Web search collector for gathering topic information."""
from typing import List

from ..llm.base import BaseLLM
from ..core.errors import CollectorError

def collect(topic: str, hours: int, llm: BaseLLM) -> List[str]:
    """Collect recent information about a topic."""
    prompt = f"""Give me 5 bullet points about the most significant developments in {topic} 
    over the last {hours} hours. Focus on concrete facts and avoid speculation.
    Format each point as a single line starting with a bullet point."""
    
    try:
        response = llm.generate(prompt)
        # Split response into bullet points and clean up
        bullets = [
            line.strip()[2:].strip()  # Remove bullet point and extra whitespace
            for line in response.split('\n')
            if line.strip().startswith('•') or line.strip().startswith('-')
        ]
        return bullets
    except Exception as e:
        raise CollectorError(f"Failed to collect information: {str(e)}") 