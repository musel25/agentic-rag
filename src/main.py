# main.py
import os
from dotenv import load_dotenv
from graph import build_graph

# Load environment variables (API keys, etc.)
load_dotenv()

def main():
    # 1. Initialize the graph
    intent_graph = build_graph()
    
    # 2. Define the query
    query = """
    I need to monitor the management interface statistics on my Nokia SR Linux router.
    The router is at clab-quickstart-lab-r1:57400.
    Send the data via dial-out gRPC to my collector at 10.0.0.5 port 50000.
    Use a sample interval of 2000ms.
    """

    # 3. Execute
    print("Extracting intent...\n")
    result = intent_graph.invoke({
        "query": query,
        "skeleton": None
    })

    # 4. Output the result
    if result.get("skeleton"):
        print(result["skeleton"].model_dump_json(indent=2))
    else:
        print("Failed to extract intent.")

if __name__ == "__main__":
    main()