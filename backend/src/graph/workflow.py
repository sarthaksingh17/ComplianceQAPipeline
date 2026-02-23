"""
This module defines the DAG (Directed Acyclic Graph)
that orchestrates the video compliance audit process.

START -> index_video_node -> audit_content_node -> END
"""

from langgraph.graph import StateGraph, END

from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)

def create_graph():
    '''
    construct and complis the langraph
    and retrns 
    complied graph - runnable graph object for execution
    '''
    
    #ini graph with state schema
    workflow=StateGraph(VideoAuditState)
    
    # Add nodes
    workflow.add_node("index_video", index_video_node)
    workflow.add_node("audit_content", audit_content_node)
    
    # Define execution flow
    workflow.set_entry_point("index_video")

    workflow.add_edge("index_video", "audit_content")
    workflow.add_edge("audit_content", END)

    # Compile graph
    app = workflow.compile()
    return app

#expose this app
app = create_graph()
