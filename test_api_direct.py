import sys
sys.path.append('.')

# Test the API components directly
from query.phase_9_refusal.refusal_handler import is_advisory, get_refusal_response
from query.phase_9_refusal.citation_formatter import format_response
from query.phase_7_retriever.retriever import retrieve
from query.phase_8_llm.llm_handler import generate_response

print("Testing API components...")

# Test 1: Refusal handler
query = "What is SBI Large Cap Fund?"
print(f"Query: {query}")
print(f"Is advisory: {is_advisory(query)}")

# Test 2: Retrieval
print("\nTesting retrieval...")
chunks = retrieve(query)
print(f"Retrieved {len(chunks)} chunks")

# Test 3: LLM response (if chunks available)
if chunks:
    print("\nTesting LLM response...")
    try:
        response = generate_response(query, chunks)
        print(f"LLM Response: {response['answer'][:200]}...")
        print(f"Source URL: {response['source_url']}")
        print(f"Scraped Date: {response['scraped_date']}")
        
        # Test 4: Citation formatting
        print("\nTesting citation formatting...")
        formatted = format_response(response['answer'], response['source_url'], response['scraped_date'])
        print(f"Formatted Response: {formatted[:300]}...")
        
    except Exception as e:
        print(f"LLM Error: {e}")
        print("This might be due to missing GROQ_API_KEY in .env")
        
print("\nAPI component test completed!")
