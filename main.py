import argparse
import sys
import os
from campus_taskflow.adk.core import State
from campus_taskflow.agents.orchestrator import OrchestratorAgent

def main():
    parser = argparse.ArgumentParser(description="Campus TaskFlow Agent CLI")
    parser.add_argument("--pdf", help="Path to the PDF file to process", required=False)
    parser.add_argument("--ui", action="store_true", help="Launch the Streamlit UI")
    args = parser.parse_args()

    if args.ui:
        print("Launching Streamlit UI...")
        os.system("streamlit run campus_taskflow/ui/app.py")
        return

    if args.pdf:
        if not os.path.exists(args.pdf):
            print(f"Error: File {args.pdf} not found.")
            return

        print(f"Processing {args.pdf}...")
        orchestrator = OrchestratorAgent()
        state = State()
        
        try:
            orchestrator.run(state, args.pdf)
            print("\nPipeline completed successfully.")
            
            # Print summary
            summary = state.get("summary", {}).get("summary", "No summary")
            print(f"\nSummary:\n{summary}")
            
            # Print schedule
            print("\nSchedule:")
            for item in state.get("schedule", []):
                print(f"- {item['date']}: {item['task']}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
