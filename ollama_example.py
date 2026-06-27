import json 
from datetime import datetime
from ollama import Client
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel, Field
from ddgs import DDGS

ollama_server = "http://localhost:11434"
ollama_model = "qwen3.5:9b" # "lfm2.5:8b" "granite4.1:8b"
ollama_embed = "qwen3-embedding:8b" # "nomic-embed-text-v2-moe:latest"


# Extracct the AI message to text(string)
def extract_text(message) -> str:
    content = message.content
    # Case 1: Content is already a standard string
    if isinstance(content, str):
        return content
    # Case 2: Content is a list of blocks (e.g., text, reasoning, image)
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)  
    return ""

# Example A: Simple tool (automatically generates schema from docstring and type hints)
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers.
    Use this tool when you need to perform multiplication (e.g., 3 multiplied by 12).
    """
    return a * b

# Example B: Complex tool (using Pydantic to explicitly define more detailed input structures)
class CalculatorInput(BaseModel):
    first_number: float = Field(description="The first number (dividend)")
    second_number: float = Field(description="The second number (the divisor, which cannot be zero)")

@tool("division-tool", args_schema=CalculatorInput)
def divide(first_number: float, second_number: float) -> float:
    """Perform a division operation on two numbers."""
    if second_number == 0:
        raise ValueError("The divisor cannot be zero.")
    return first_number / second_number

# Example C: Get current datetime
@tool
def get_current_datetime() -> str:
    """Returns the current date and time. Use this when the user requests the current time or date."""
    return datetime.now().isoformat()

# Example D: Searching online for information
@tool
def quick_web_search(query:str, max_results:int=3) -> str:
    """Searching online for information. 
    This tool must be used if LLM need to obtain unknown knowledge or real-time information.
    Returns:
        str: A string in JSON format.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results)) # Retrieve the search results (in list format).
        json_string = json.dumps(results, ensure_ascii=False, indent=4) # Convert results to JSON string
        return json_string


def main():
    run_option = 2
    print("Hello from ollama-test!")
    try:
        match run_option:
            case 0:
                client = Client(host=ollama_server) # Initialize the client with the remote server's IP
                is_loop:bool = True # Loop chat (True) or single test (False)
                if is_loop:
                    print(f"--------- Ollama Client Chat (Model:{ollama_model}) Loop (Type 'exit' to quit) ----------")
                    while True:
                        user_input = input("You: ")
                        if user_input.lower() in ["exit", "quit", "bye"]:
                            print("Goodbye!")
                            break
                        else:
                            response = client.chat(model=ollama_model, messages=[
                            {
                                'role': 'user',
                                'content': user_input,
                            },
                            ])
                            print(response['message']['content'])
                else:
                    print(f"--------- Ollama Client Chat (Model:{ollama_model}) Single Test ----------")
                    response = client.chat(model=ollama_model, messages=[
                    {
                        'role': 'user',
                        'content': 'Who are you? Please answer me in Taiwanese.',
                    },
                    ])
                    print(response['message']['content'])
            
            case 1:
                client = Client(host=ollama_server) # Initialize the client with the remote server's IP
                print(f"--------- Ollama Client Embedding (Model:{ollama_embed}) Single Test ----------")
                response = client.embed(
                    model=ollama_embed,
                    input="Ollama makes local AI accessible to everyone."
                )

                # Access the generated embedding vector
                embedding = response['embeddings'][0]

                print(f"Model: {response['model']}")
                print(f"Embedding Vector (first 5 values): {embedding[:5]}")
                print(f"Vector Dimension: {len(embedding)}")

            case 2:
                print(f"--------- LangChain Embedding (Model:{ollama_embed}) Text Comparison ----------")
                embeddings = OllamaEmbeddings(model=ollama_embed)

                main_text = "I enjoy taking walks in the park"
                compare_texts = [
                    "J'aime me promener dans le parc",
                    "Saya senang berjalan-jalan di taman",
                    "It feels great to take a walk in the park", 
                    "It's very hot today",
                    "I want to eat beef noodles"
                ]

                main_vector = embeddings.embed_query(main_text) # embed_query
                compare_vectors = embeddings.embed_documents(compare_texts) # embed_documents

                # Comparision
                print(f"-------- Query text: {main_text} --------")
                similarities = cosine_similarity([main_vector], compare_vectors)
                for text, score in zip(compare_texts, similarities[0]):
                    print(f"Similarity: {score:.4f} | Text: {text}")

            case 3:
                llm = ChatOllama(model=ollama_model) # Initialize the local model
                messages = [SystemMessage(content="You are a helpful and concise assistant.")]
                print(f"--------- LangChain Chat (Model:{ollama_model}) Chatbot (Type 'exit' to quit) ----------")
                while True:
                    user_input = input("You: ")
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        print("Goodbye!")
                        break
                    messages.append(HumanMessage(content=user_input)) # Add user message to history
                    response = llm.invoke(messages) # For streaming, you can use llm.stream(messages) 
                    print(f"AI: {response.content}")
                    messages.append(response) # Add AI response to history to maintain context
            
            case 4:
                llm = ChatOllama(model=ollama_model) # Initialize the local model
                tool_list = [get_current_datetime, quick_web_search] #, multiply, divide]
                checkpointer = InMemorySaver()
                config = {"configurable": {"thread_id": "session_123"}} # Use thread_id to identify the current session.

                agent = create_agent(
                    model=llm,
                    tools=tool_list,
                    system_prompt="You are a helpful assistant.",
                    checkpointer=checkpointer,
                )

                print(f"--------- LangChain Agent (Model:{ollama_model}) Chatbot (Type 'exit' to quit) ----------")
                while True:
                    user_input = input("You: ")
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        print("Goodbye!")
                        break
                    resp = agent.invoke(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config
                    )
                    final_reply = extract_text(resp["messages"][-1])
                    print(f"AI Agent: {final_reply}")
            
            case _:
                print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)
        
    except Exception as e:
        print(f"Unknown Error: {e}")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass

if __name__ == "__main__":
    main()