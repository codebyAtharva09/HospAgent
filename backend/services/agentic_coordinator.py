"""
Agentic Coordination System
Manages autonomous collaboration between agents with event-driven triggers
"""
from typing import Dict, List, Any, Callable
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of events that trigger agent coordination"""
    SURGE_PREDICTED = "surge_predicted"
    HIGH_AQI_DETECTED = "high_aqi_detected"
    FESTIVAL_APPROACHING = "festival_approaching"
    EPIDEMIC_ALERT = "epidemic_alert"
    SUPPLY_LOW = "supply_low"
    STAFF_SHORTAGE = "staff_shortage"
    BED_CAPACITY_CRITICAL = "bed_capacity_critical"

class AgentEvent:
    """Event object passed between agents"""
    def __init__(self, event_type: EventType, data: Dict, priority: int = 5, source_agent: str = None):
        self.event_type = event_type
        self.data = data
        self.priority = priority  # 1-10, 10 being highest
        self.source_agent = source_agent
        self.timestamp = datetime.now()
        self.handled_by = []
    
    def to_dict(self):
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'priority': self.priority,
            'source_agent': self.source_agent,
            'timestamp': self.timestamp.isoformat(),
            'handled_by': self.handled_by
        }

class AgenticCoordinator:
    """
    Central coordinator for agent collaboration
    Implements event-driven architecture with shared knowledge base
    """
    
    def __init__(self):
        self.agents = {}
        self.event_handlers = {}
        self.shared_knowledge = {}
        self.event_history = []
        self.coordination_rules = self._initialize_rules()
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """Register an agent with the coordinator"""
        self.agents[agent_name] = agent_instance
        logger.info(f"Agent '{agent_name}' registered with coordinator")
    
    def subscribe_to_event(self, event_type: EventType, handler: Callable, agent_name: str):
        """Subscribe an agent to specific event types"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append({
            'handler': handler,
            'agent_name': agent_name
        })
        logger.info(f"Agent '{agent_name}' subscribed to {event_type.value}")
    
    def publish_event(self, event: AgentEvent):
        """
        Publish an event to all subscribed agents
        Implements priority-based execution
        """
        logger.info(f"Event published: {event.event_type.value} (priority: {event.priority})")
        
        # Store in history
        self.event_history.append(event)
        
        # Get handlers for this event type
        handlers = self.event_handlers.get(event.event_type, [])
        
        # Sort by priority (if defined in coordination rules)
        handlers = sorted(handlers, key=lambda h: self._get_handler_priority(h, event), reverse=True)
        
        # Execute handlers
        responses = []
        for handler_info in handlers:
            try:
                response = handler_info['handler'](event)
                event.handled_by.append(handler_info['agent_name'])
                responses.append({
                    'agent': handler_info['agent_name'],
                    'response': response
                })
            except Exception as e:
                logger.error(f"Error in handler {handler_info['agent_name']}: {e}")
        
        # Apply coordination rules
        coordinated_response = self._apply_coordination_rules(event, responses)
        
        return coordinated_response
    
    def update_shared_knowledge(self, key: str, value: Any, source_agent: str):
        """Update shared knowledge base"""
        self.shared_knowledge[key] = {
            'value': value,
            'updated_by': source_agent,
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"Shared knowledge updated: {key} by {source_agent}")
    
    def get_shared_knowledge(self, key: str) -> Any:
        """Retrieve from shared knowledge base"""
        return self.shared_knowledge.get(key, {}).get('value')
    
    def _initialize_rules(self) -> Dict:
        """
        Initialize coordination rules
        Defines how agents should collaborate on specific scenarios
        """
        return {
            'surge_response': {
                'triggers': [EventType.SURGE_PREDICTED, EventType.FESTIVAL_APPROACHING],
                'agent_sequence': ['PredictiveAgent', 'PlanningAgent', 'AdvisoryAgent'],
                'parallel_execution': False
            },
            'pollution_response': {
                'triggers': [EventType.HIGH_AQI_DETECTED],
                'agent_sequence': ['DataAgent', 'AdvisoryAgent', 'PlanningAgent'],
                'parallel_execution': True
            },
            'supply_crisis': {
                'triggers': [EventType.SUPPLY_LOW],
                'agent_sequence': ['PlanningAgent', 'AdvisoryAgent'],
                'parallel_execution': False
            },
            'epidemic_response': {
                'triggers': [EventType.EPIDEMIC_ALERT],
                'agent_sequence': ['DataAgent', 'PredictiveAgent', 'PlanningAgent', 'AdvisoryAgent'],
                'parallel_execution': False
            }
        }
    
    def _get_handler_priority(self, handler_info: Dict, event: AgentEvent) -> int:
        """Determine handler priority based on coordination rules"""
        # Check if there's a defined sequence for this event type
        for rule_name, rule in self.coordination_rules.items():
            if event.event_type in rule['triggers']:
                agent_sequence = rule['agent_sequence']
                agent_name = handler_info['agent_name']
                if agent_name in agent_sequence:
                    # Higher priority for agents earlier in sequence
                    return len(agent_sequence) - agent_sequence.index(agent_name)
        
        return 5  # Default priority
    
    def _apply_coordination_rules(self, event: AgentEvent, responses: List[Dict]) -> Dict:
        """
        Apply coordination rules to agent responses
        Resolves conflicts and generates unified action plan
        """
        # Find applicable rule
        applicable_rule = None
        for rule_name, rule in self.coordination_rules.items():
            if event.event_type in rule['triggers']:
                applicable_rule = rule
                break
        
        if not applicable_rule:
            return {'responses': responses, 'coordinated_action': None}
        
        # Merge responses based on rule
        coordinated_action = {
            'event_type': event.event_type.value,
            'timestamp': datetime.now().isoformat(),
            'participating_agents': [r['agent'] for r in responses],
            'actions': []
        }
        
        # Collect all recommended actions
        for response in responses:
            if response['response'] and 'actions' in response['response']:
                coordinated_action['actions'].extend(response['response']['actions'])
        
        # Prioritize and deduplicate actions
        coordinated_action['actions'] = self._prioritize_actions(coordinated_action['actions'])
        
        return coordinated_action
    
    def _prioritize_actions(self, actions: List[Dict]) -> List[Dict]:
        """Prioritize and deduplicate actions"""
        # Remove duplicates
        seen = set()
        unique_actions = []
        for action in actions:
            action_key = f"{action.get('type')}_{action.get('target')}"
            if action_key not in seen:
                seen.add(action_key)
                unique_actions.append(action)
        
        # Sort by priority
        return sorted(unique_actions, key=lambda a: a.get('priority', 5), reverse=True)
    
    def get_coordination_status(self) -> Dict:
        """Get current coordination status and metrics"""
        return {
            'registered_agents': list(self.agents.keys()),
            'active_subscriptions': {
                event_type.value: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
            'recent_events': [e.to_dict() for e in self.event_history[-10:]],
            'shared_knowledge_keys': list(self.shared_knowledge.keys()),
            'coordination_rules': list(self.coordination_rules.keys())
        }

# Singleton instance
coordinator = AgenticCoordinator()
