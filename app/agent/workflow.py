from typing import Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from app.agent.edges import GradeDocumentsNode
from app.agent.interface import AgentState
from app.agent.nodes import OrbiAgentNode, RewriteNode, GenerateNode
from app.agent.tools import tools


class AgentWorkflow:

    def compile(self, checkpointer: None | Literal[False] | BaseCheckpointSaver = None) -> CompiledStateGraph:
        #
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", OrbiAgentNode())

        workflow.add_node("tools", ToolNode(tools))
        workflow.add_node("rewrite", RewriteNode())
        workflow.add_node("generate", GenerateNode())

        workflow.add_edge(START, "agent")

        # Decide whether to retrieve
        workflow.add_conditional_edges(
            "agent",
            # Assess agent decision
            tools_condition,
            {
                # Translate the condition outputs to nodes in our graph
                "tools": "tools",
                END: END,
            },
        )

        # Edges taken after the `action` node is called.
        workflow.add_conditional_edges(
            "tools",
            # Assess agent decision
            GradeDocumentsNode(),
            {
                "rewrite": "rewrite_check",
                "generate": "generate",
                "__end__": END
            }
        )

        def rewrite_check(state: AgentState) -> AgentState:
            if state.rewrite_attempts < 2:
                state.rewrite_attempts = state.rewrite_attempts + 1
                return state
            else:
                return state

        workflow.add_node("rewrite_check", rewrite_check)
        workflow.add_conditional_edges(
            "rewrite_check",
            lambda x: "rewrite" if x.rewrite_attempts < 1 else "generate",
            {
                "rewrite": "rewrite",
                "generate": "generate",
            },
        )

        workflow.add_edge("generate", END)
        workflow.add_edge("rewrite", "agent")

        return workflow.compile(checkpointer=checkpointer)
