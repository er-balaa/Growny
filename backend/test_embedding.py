import google.generativeai as genai

# Configure Gemini
genai.configure(api_key='AIzaSyCA3IYmYDOcoNsGNiDcLeg0EzH4UDjX55s')

def get_vector(text: str):
    """
    Generates 768-dim vector using Gemini embedding
    Called: Once per task creation, once per search
    Cost: Very low (embedding model is cheap)
    """
    try:
        print(f"Generating embedding for: {text}")
        res = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        print(f"Embedding generated successfully, length: {len(res['embedding'])}")
        return res['embedding']
    except Exception as e:
        print(f"Vector Error: {e}")
        return None

if __name__ == "__main__":
    test_text = "Remember to purchase milk."
    result = get_vector(test_text)
    print(f"Success: {result is not None}")
    if result:
        print(f"First 5 values: {result[:5]}")
