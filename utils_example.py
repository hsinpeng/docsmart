from utils import (extract_urls, extract_image_urls, determine_type, generate_title, generate_image_description)

run_option = 1
markdown_file = "./outputs/docling_output.md"

def main():
    try:
        match run_option:
            case 0:
                print("----- Utility Test -----")

            case 1:
                print("----- Utility Test: determine_type and generate_title -----")
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                page_type = determine_type(markdown_content)
                print(f"----- Web Type: {page_type} -----")
                page_title = generate_title(markdown_content)
                print(f"----- Web Title: {page_title} -----")
            
            case 2:
                print("----- Utility Test: generate_image_description -----")
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                img_url_list = extract_image_urls(markdown_content, rm_redundancy=True)
                for url in img_url_list:
                    print(url)
                print(f"--- Image description of {img_url_list[0]} ---")
                image_description = generate_image_description(img_url_list[0])
                print(image_description)

            case _:
                print(f"Error: Unknown run_option ({run_option})!") # Wildcard (default case)
        
    except Exception as e:
        print(f"Unknown Error: {e}") 


if __name__ == "__main__":
    main()
