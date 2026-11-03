from app.services.rag_service import search_knowledge_base


def policy_agent(state):
    query = state["query"]

    # Retrieve the 3 most relevant policy sections
    policy_matches = search_knowledge_base(query, top_k=3)

    return {"policy_matches": policy_matches}