"""Agent 注册与管理"""

from kk.agents.buildin.chatbot.graph import ChatbotAgent
class AgentManager:
    """Agent 实例管理（模块级单例）"""

    def __init__(self):
        self._classes = {}
        self._instances = {}

    def register_agent(self, agent_class) -> None:
        """注册 Agent 类，agent_id 用类名"""
        self._classes[agent_class.__name__] = agent_class

    def get_agent(self, agent_id: str):
        """获取 Agent 实例，不存在则创建并缓存"""
        if agent_id not in self._instances:
            agent_class = self._classes[agent_id]
            self._instances[agent_id] = agent_class()
        return self._instances[agent_id]

    def get_agents(self):
        return list(self._instances.values())


agent_manager = AgentManager()
agent_manager.register_agent(ChatbotAgent)

__all__ = ["agent_manager"]
