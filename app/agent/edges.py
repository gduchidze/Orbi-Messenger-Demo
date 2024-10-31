import logging
from typing import Literal

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from pydantic import BaseModel, Field

from app.agent.interface import AgentState
from app.config import settings


class GradeDocumentsNode:

    async def __call__(self, state: AgentState, config) -> Literal["generate", "rewrite", END]:
        """
            Determines whether the retrieved documents are relevant to the question.

            Args:
                state (messages): The current state

            Returns:
                str: A decision for whether the documents are relevant or not
        """

        messages = state.messages
        last_message = messages[-1]

        if last_message.name == 'send_contract_sample':
            return END

        logging.info("---CHECK RELEVANCE---")

        # Data model
        class Grade(BaseModel):
            """Binary score for relevance check."""

            binary_score: str = Field(description="Relevance score 'yes' or 'no'")

        # LLM
        model = ChatOpenAI(temperature=0,
                           api_key=settings.openai_api_key,
                           model='gpt-4o-mini')

        # LLM with tool and validation
        llm_with_tool = model.with_structured_output(Grade)

        # Prompt
        prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
                              Here is the retrieved document: \n\n {context} \n\n
                              Here is the user question: {question} \n
                              If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
                              Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
            input_variables=["context", "question"],
        )

        # Chain
        chain = prompt | llm_with_tool

        question = messages[0].content
        docs = last_message.content

        scored_result = await chain.ainvoke({"question": question, "context": docs})

        score = scored_result.binary_score

        if score == "yes":
            logging.info("---DECISION: DOCS RELEVANT---")
            return "generate"

        else:
            logging.info("---DECISION: DOCS NOT RELEVANT---")
            logging.info(score)
            return "rewrite"
