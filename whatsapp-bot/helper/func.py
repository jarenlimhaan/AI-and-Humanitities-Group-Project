import time

def get_vertex_response_with_retry(vertex_ai, user_msg: str, max_retries: int = 3) -> list:
    """Get response from Vertex AI with retry logic"""
    for attempt in range(max_retries):
        try:
            response = vertex_ai.get_vertex_response(user_msg)
            if response:
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second between retries
            else:
                raise
    raise Exception("Failed to get response after all retries")

