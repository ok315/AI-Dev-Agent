from src.agents.codebase_agent import ask_codebase

results = ask_codebase("how does this codebase search the web?", repo="Multi-Tool-Agent")

for r in results:
    print(f"{r['name']} ({r['type']}) — {r['file_path']}:{r['start_line']}-{r['end_line']}")
    print(f"  Distance: {r['distance']:.4f}")
    print()