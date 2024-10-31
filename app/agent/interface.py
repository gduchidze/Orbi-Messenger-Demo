from typing import Annotated, Sequence, List, Optional, Dict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[List[BaseMessage], add_messages]
    rewrite_attempts: int = 0
    quick_replies: Optional[List[Dict]] = Field(default=None)

def quick_buttons(buttons: List[str]) -> List[Dict]:
    r_buttons = []
    for b in buttons:
        r_buttons.append({
            "content_type": "text",
            "title": f"\n{b}\n",
            "payload": f"SELECTED_{b[:10].upper()}",
        })
    return r_buttons