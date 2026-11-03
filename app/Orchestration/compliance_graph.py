
from langgraph.graph import StateGraph, START, END

from app.Orchestration.state import ComplianceState
from app.Agents.regulatory_agent import regulatory_agent
from app.Agents.policy_agent import policy_agent
from app.Agents.evidence_agent import evidence_agent
from app.Agents.reporting_agent import reporting_agent


workflow = StateGraph(ComplianceState)

workflow.add_node("regulatory_agent", regulatory_agent)
workflow.add_node("policy_agent", policy_agent)
workflow.add_node("evidence_agent", evidence_agent)
workflow.add_node("reporting_agent", reporting_agent)

workflow.add_edge(START, "regulatory_agent")
workflow.add_edge("regulatory_agent", "policy_agent")
workflow.add_edge("policy_agent", "evidence_agent")
workflow.add_edge("evidence_agent", "reporting_agent")
workflow.add_edge("reporting_agent", END)

compliance_graph = workflow.compile()
