import json
from intent_to_code.support.capability_resolver import CapabilityResolver

def test_trait_intelligence():
    print("Testing Trait Intelligence Layer (Stage 2.5)...")
    resolver = CapabilityResolver(capabilities_dir="capabilities")

    # Scenario 1: Analytics Goal -> Should prefer ClickHouse (high throughput)
    print("\nScenario 1: Analytics platform")
    graph_analytics = resolver.resolve(["analytics_engine"], goal="Large scale analytics platform")
    nodes_analytics = set(graph_analytics.nodes.keys())
    print(f"Nodes selected: {nodes_analytics}")
    
    if "clickhouse_db" in nodes_analytics:
        print("SUCCESS: Selected ClickHouse for analytics goal.")
    else:
        print("FAILURE: Did not select ClickHouse for analytics.")

    # Scenario 2: Finance Goal -> Should prefer Postgres (strong consistency)
    print("\nScenario 2: Financial system")
    graph_finance = resolver.resolve(["analytics_engine"], goal="Financial transaction auditing system")
    nodes_finance = set(graph_finance.nodes.keys())
    print(f"Nodes selected: {nodes_finance}")
    
    if "postgres_db" in nodes_finance:
        print("SUCCESS: Selected Postgres for financial goal.")
    else:
        print("FAILURE: Did not select Postgres for finance.")

if __name__ == "__main__":
    test_trait_intelligence()
