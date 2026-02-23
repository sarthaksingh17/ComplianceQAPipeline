import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

#schema for compliance result

class ComplianceIssue(TypedDict):
    category : str
    description: str
    severity: str 
    timestamp: Optional[str]
    
#gloabal graph state

class VideoAuditState(TypedDict):
    '''
    Docstring for VideoAuditState
    '''
    # Input
    video_url: str
    video_id: str

    # Ingestion
    local_file_path: Optional[str]
    video_metadata: Optional[Dict[str, Any]]
    transcript: Optional[str]
    ocr_text: Optional[str]
    
    #analysis
    compliance_issues: Annotated[List[ComplianceIssue], operator.add]
    
    #final status
    final_status: str  # pass | fail
    final_report : str
    
    
    