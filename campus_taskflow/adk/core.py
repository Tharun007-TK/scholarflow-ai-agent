import uuid
import logging
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

# --- State Management ---
@dataclass
class State:
    """Manages the session state and context for agents."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value

    def add_history(self, entry: Dict[str, Any]):
        entry['timestamp'] = datetime.now().isoformat()
        self.history.append(entry)

# --- Base Agent ---
class Agent(ABC):
    """Base class for all ADK agents."""
    def __init__(self, name: str, description: str, tools: List[Any] = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.logger = logging.getLogger(name)

    @abstractmethod
    def run(self, state: State, input_data: Any) -> Any:
        """Execute the agent's logic."""
        pass

    def log_execution(self, state: State, input_data: Any, output_data: Any):
        state.add_history({
            'agent': self.name,
            'input': str(input_data), # Simplify for log
            'output': str(output_data)
        })

# --- Sequential Agent ---
class SequentialAgent(Agent):
    """Executes a list of sub-agents in sequence."""
    def __init__(self, name: str, description: str, agents: List[Agent]):
        super().__init__(name, description)
        self.agents = agents

    def run(self, state: State, input_data: Any) -> Any:
        current_input = input_data
        self.logger.info(f"Starting SequentialAgent: {self.name}")
        
        for agent in self.agents:
            self.logger.info(f"Running sub-agent: {agent.name}")
            try:
                # Pass the output of the previous agent as input to the next
                # But also allow agents to access the shared State
                output = agent.run(state, current_input)
                agent.log_execution(state, current_input, output)
                current_input = output
            except Exception as e:
                self.logger.error(f"Error in agent {agent.name}: {e}")
                raise e
                
        return current_input
