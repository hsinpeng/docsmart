from ollama import Client
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.utils.math import cosine_similarity

run_option = 3

ollama_server = "http://localhost:11434"
ollama_model = "granite4.1:8b"
ollama_embed = "qwen3-embedding:latest" # "nomic-embed-text-v2-moe:latest"

def main():
    print("Hello from ollama-test!")
    match run_option:
        case 0:
            client = Client(host=ollama_server) # Initialize the client with the remote server's IP
            is_loop:bool = True # Loop chat (True) or single test (False)
            if is_loop:
                print(f"--------- Ollama LLM model({ollama_model}) chatbot (Type 'exit' to quit) ----------")
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
                print(f"--------- Ollama LLM model({ollama_model}) single test ----------")
                response = client.chat(model=ollama_model, messages=[
                {
                    'role': 'user',
                    'content': 'Who are you? Please answer me in Taiwanese.',
                },
                ])
                print(response['message']['content'])
        
        case 1:
            client = Client(host=ollama_server) # Initialize the client with the remote server's IP
            print(f"--------- Ollama embedding model({ollama_embed}) test ----------")
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
            print(f"--------- Ollama embedding model({ollama_embed}) text comparison ----------")
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
            print(f"--------- LangChain with Ollama({ollama_model}) chatbot (Type 'exit' to quit) ----------")
            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("Goodbye!")
                    break
                messages.append(HumanMessage(content=user_input)) # Add user message to history
                response = llm.invoke(messages) # For streaming, you can use llm.stream(messages) 
                print(f"AI: {response.content}")
                messages.append(response) # Add AI response to history to maintain context
        
        case _:
            print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)
    


if __name__ == "__main__":
    main()
