'''
main execution entry point 
'''

import uuid
import json
import logging
from pprint import pprint

from dotenv import load_dotenv
load_dotenv()

from backend.src.graph.workflow import create_graph


# Logging Configuration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("llmops.compliance.cli")


def run_cli_simulation():
    """
    Runs the local video compliance audit pipeline.
    """

    
    # Generate Session ID
    
    session_id = str(uuid.uuid4())
    logger.info(f"Starting Audit Session: {session_id}")

    
    # Ask user for YouTube URL
    
    video_url = input("Enter YouTube Video URL: ").strip()

    if not video_url:
        print("Video URL is required.")
        return

    
    # Define Initial State
    
    initial_inputs = {
        "video_url": video_url,
        "video_id": f"vid_{session_id[:8]}",
        "transcript": "",
        "ocr_text": "",
        "video_metadata": {},
        "compliance_issues": [],
        "final_status": "",
        "final_report": "",
        "errors": []
    }

    print("\n----- Initializing Workflow -----")
    print("Input Payload:")
    print(json.dumps(initial_inputs, indent=2))

    try:
        
        # Creating Graph
        
        app = create_graph()

       
        # Execute Graph
        
        final_state = app.invoke(initial_inputs)

        print("\n===== Workflow Execution Complete =====")

        print("\n=== Compliance Audit Report ===")
        print(f"Video ID : {final_state.get('video_id')}")
        print(f"Status   : {final_state.get('final_status')}")

        print("\n[VIOLATIONS DETECTED]")
        results = final_state.get("compliance_issues", [])

        if results:
            for issue in results:
                print(
                    f"- [{issue.get('severity')}] "
                    f"[{issue.get('category')}] : "
                    f"{issue.get('description')}"
                )
        else:
            print("No violations detected.")

        print("\n[FINAL SUMMARY]")
        print(final_state.get("final_report"))

    except Exception as e:
        logger.error(f"Workflow Execution Failed: {str(e)}")


if __name__ == "__main__":
    run_cli_simulation()