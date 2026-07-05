import asyncio
import os
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
import cognee
from cognee.infrastructure.databases.graph import get_graph_engine

async def main():
    print("Step 1: Check the Raw Metrics")
    graph_engine = await get_graph_engine()
    metrics = await graph_engine.get_graph_metrics()
    print("Graph Metrics:", metrics)
    print("--------------------------------------------------")
    
    print("Step 2: Generate the Visual HTML Map")
    dest_path = os.path.join(os.getcwd(), "graph.html")
    await cognee.visualize_graph(dest_path)
    print(f"Graph successfully exported to {dest_path}")
    print("--------------------------------------------------")
    
    print("Step 3: Run an 'Insights' Search")
    results = await cognee.search(
        query_type=cognee.SearchType.INSIGHTS,
        query_text="What happened to the server?"
    )
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
