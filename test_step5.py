import sys
sys.path.append('.')
from query.phase_7_retriever.retriever import retrieve

print('Testing retriever...')
results = retrieve("What is the expense ratio?")
print(f'Found {len(results)} results:')
for i, result in enumerate(results):
    print(f'Result {i+1}:')
    print(f'  Distance: {result["distance"]:.4f}')
    print(f'  Scheme Name: {result["metadata"]["scheme_name"]}')
    print(f'  First 100 chars: {result["text"][:100]}...')
    print()
