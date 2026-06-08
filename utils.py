import os, io, re, requests, base64, random, string
from PIL import Image
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

ollama_server = "http://localhost:11434"
ollama_model = "granite4.1:8b" # "qwen3.5:9b" "granite4.1:8b"
ollama_embed = "qwen3-embedding:latest" # "qwen3-embedding:latest" "nomic-embed-text-v2-moe:latest"
supported_image_formats = ('.jpg', '.jpeg', '.png')


def check_image_validity(image_uri:str, mode:str="databytes") -> bool:
    """
    Verify the given uri is a valid image format or not.
    mode: 'extension' or 'databytes'
    """
    try:
        check_string = None
        if mode == "extension":
            check_string = image_uri
        elif mode == "databytes":
            if os.path.isfile(image_uri):
                with open(image_uri, "rb") as f: # 'wb' opens the file in binary mode to write image data
                    data_bytes = f.read()
            else:
                response = requests.get(image_uri)
                if response.status_code == 200: # Check if the download was successful
                    data_bytes = response.content
                else:
                    print(f"Error: Cannot retrieve {image_uri}, code={response.status_code}!")
            check_string = "." + get_content_imagetype(data_bytes)
        else:
            print("Something wrong!")
            return False

        if check_string.lower().endswith(supported_image_formats):
            return True
        else:
            return False
    except Exception:
        return False


def get_content_imagetype(image_bytes: bytes) -> str:
    """
    Identify the image format of given data bytes
    """
    try:
        image_stream = io.BytesIO(image_bytes)
        with Image.open(image_stream) as img:
            return img.format # img.format：'JPEG', 'PNG', 'GIF', 'WEBP'
    except Exception:
        return "UNKNOWN"


def convert_image2pdf(image_path:str, pdf_path:str) -> bool:
    """
    Convert the image file to PDF.
    """
    try:
        if (check_image_validity(image_path)) and (pdf_path.lower().endswith(".pdf")):
            image = Image.open(image_path) # Open the image file
            image_rgb = image.convert("RGB") # Convert to RGB (required for JPG to PDF conversion)
            image_rgb.save(pdf_path, "PDF") # Save as PDF
            return True
        else:
            return False
    except Exception as e:
        print(f"{e}")
        return False


def gen_random_string(length:int=10, is_punctuation:bool=False) -> str:
    """
    Generate a random string of a specific length.
    """
    if is_punctuation:
        characters = string.ascii_letters + string.digits + string.punctuation
    else: 
        characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def encode_image_file(image_path:str):
    """
    Convert the content of the input file into base64 encoded data.
    """
    try:
        with open(image_path, "rb") as image_file:
            data_bytes = image_file.read()
        if get_content_imagetype(data_bytes) == "UNKNOWN":
            return None
        else:
            return base64.b64encode(data_bytes).decode("utf-8")
    except Exception:
        return None


def encode_image_url(image_url:str):
    """
    Convert the content of the URL into base64 encoded data.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            if get_content_imagetype(response.content) == "UNKNOWN":
                return None
            else:
                return base64.b64encode(response.content).decode("utf-8")
        else:
            return None
    except Exception:
        return None

    
def extract_urls_from_file(file_path:str, img_only:bool=False, rm_redundancy:bool=True):
    """
    Retrieve all hyperlinks in the file and output them as a list.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if img_only:
            return extract_image_urls(content, rm_redundancy=rm_redundancy)
        else:
            return extract_urls(content, rm_redundancy=rm_redundancy)
    except Exception:
        return None


def extract_urls(markdown_text:str, rm_redundancy:bool=True):
    """
    Retrieve all hyperlinks in the text and output them as a list.
    """
    try:
        pattern = r'!\[.*?\]\((.*?)\)'
        if rm_redundancy:
            original_list = re.findall(pattern, markdown_text)
            urls = list(dict.fromkeys(original_list))
        else:
            urls = re.findall(pattern, markdown_text)
        return urls
    except Exception:
        return None


def extract_image_urls(markdown_text:str, rm_redundancy:bool=True):
    """
    Retrieve all hyperlinks of images in the text and output them as a list.
    """
    try:
        url_list = extract_urls(markdown_text, rm_redundancy=rm_redundancy)
        image_url_list = [url for url in url_list if check_image_validity(url)]
        return image_url_list
    except Exception:
        return None


def add_markdown_link_comment(markdown_text:str, target_url:str, comment_text:str):
    """
    Finds a specific hyperlink in Markdown and inserts a comment right after it.
    """
    try:
        # Regex pattern matches [text](target_url)
        pattern = rf"(\[.*?\]\({re.escape(target_url)}\))" # re.escape handles special characters in the URL string
        comment_extension = f"<!-- {comment_text} -->" # Format the comment as an invisible HTML comment
        updated_text = re.sub(pattern, rf"\1{comment_extension}", markdown_text) # Replace the link with the link + the comment
        return updated_text
    except Exception:
        return None


def replace_comment_inside_brackets(markdown_text:str, target_url:str, new_comment:str):
    """
    Finds a Markdown link by its URL and inserts or replaces 
    an HTML comment inside its display text brackets [ ].
    """
    try:
        # Pattern looks for: [any text optionally containing an old comment](target_url)
        # Group 1 captures the core visible text before any existing comment
        pattern = rf"\[([^<]*?)(?:<!--.*?-->)?\]\({re.escape(target_url)}\)"
        replacement = rf"[\1 <!-- {new_comment} -->]({target_url})" # Structure the new replacement text
        return re.sub(pattern, replacement, markdown_text) # Perform the substitution
    except Exception:
        return None


def get_ollama_model(is_embed:bool=False):
    """
    Setup an Ollama model.
    """
    try:
        if is_embed:
            return OllamaEmbeddings(model=ollama_embed)
        else:
            return ChatOllama(model=ollama_model)
    except Exception:
        return None
    

def determine_type(markdown_text:str):
    """
    determine content type (product, activity, or other) based on text content.
    """
    try:
        model = get_ollama_model()
        messages = [SystemMessage(content="""You are a helpful and concise assistant. Please extract the main subject of the given content. There are three subject only: product, activity, or other.
                                            'product' indicates that the content is describing the only one and specific product.
                                            'activity' indicates that the content is describing the only one and specific activity or event.
                                            'other' means the content does not belong to any of the above categories.
                                                Note: Just answer 'product', 'activity', or 'other' only. No more words.""")]
        messages.append(HumanMessage(content=markdown_text)) # Add user message to history
        type_response = model.invoke(messages) # For streaming, you can use llm.stream(messages) 
        return type_response.content
    except Exception:
        return None


def generate_title(markdown_text:str):
    """
    Generate appropriate titles based on text content.
    """
    try:
        model = get_ollama_model()
        messages = [SystemMessage(content="""You are a helpful and concise assistant. Please extract the main title of the product or activity of the given content.
                                Note: Answer me in Traditional Chinese. Just give me the title only, no more explanation.""")]
        messages.append(HumanMessage(content=markdown_text)) # Add user message to history
        response = model.invoke(messages) # For streaming, you can use llm.stream(messages) 
        return response.content
    except Exception:
        return None


def verify_image_by_title(image_url:str, title:str):
    """
    Identify whether the content of an image matches a given title.
    """
    try:
        if not check_image_validity(image_url, mode="extension"):
            print(f"Error: {image_url} is not an image!")
            return None

        model = get_ollama_model()
        messages = [SystemMessage(content="You are a helpful and concise assistant. Please confirm that the image content has anything to do with the description in the title. Just answer 'YES' or 'NO' only, don't reply other message.")]
        image_data = encode_image_url(image_url)
        if image_data == None:
            return None
        else:
            messages.append(HumanMessage(
                content=[
                    {"type": "text", "text": f"The title: '{title}'"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ]
            ))
            response = model.invoke(messages)
            if response.content.upper().startswith(('YES')):
                return True
            else:
                return False
    except Exception:
        return None


def generate_image_description(image_url:str):
    """
    Identify the content of an image and generate text describing that content.
    """
    try:
        if not check_image_validity(image_url, mode="extension"):
            print(f"Error: {image_url} is not an image!")
            return None

        model = get_ollama_model()
        messages = [SystemMessage(content="You are a helpful and concise assistant. Please answer in Traditional Chinese.")]
        image_data = encode_image_url(image_url)
        if image_data == None:
            return None
        else:
            messages.append(HumanMessage(
                content=[
                    {"type": "text", "text": "Please identify the content of this image and list the verbatim text. No explanation of the image is required."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ]
            ))
            response = model.invoke(messages)
            return response.content
    except Exception:
        return None