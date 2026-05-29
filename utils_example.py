import os, time
from utils import (extract_urls, extract_image_urls, determine_type, generate_title, generate_image_description)

markdown_file = "./outputs/crawl4ai_output_fit.md" # "./outputs/crawl4ai_output_fit.md" "./outputs/crawl4ai_output_raw.md" "./outputs/docling_output.md"

def main():
    run_option = 0
    try:
        if os.path.exists(markdown_file):
            print(f"Hello. This is utility test. The run_option is {run_option}.")
        else:
            print(f"Error: File {markdown_file} does not exist.")
            return

        match run_option:
            case 0:
                print("----- Utility Test: extract_urls and extract_image_urls -----")
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                url_list = extract_urls(markdown_content, rm_redundancy=False)
                if url_list is not None:
                    print(f"----- URLs ({len(url_list)}) with Redundancy -----")
                    for url in url_list:
                        print(url)
                else:
                    print("Error: extract_urls_from_file() Fail!") 
                url_list = extract_image_urls(markdown_content, rm_redundancy=True)
                if url_list is not None:
                    print(f"----- Image URLs ({len(url_list)}) without Redundancy -----")
                    for url in url_list:
                        print(url)

            case 1:
                print("----- Utility Test: determine_type and generate_title -----")
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                start_time = time.time()
                page_type = determine_type(markdown_content)
                end_time = time.time() - start_time
                print(f"determine_type() in {end_time:.2f} seconds.")  
                print(f"Web Type: {page_type}")
                print(f"-----------------------------------------")
                start_time = time.time()
                page_title = generate_title(markdown_content)
                end_time = time.time() - start_time
                print(f"generate_title() in {end_time:.2f} seconds.") 
                print(f"Web Title: {page_title}")
                print(f"-----------------------------------------")
            
            case 2:
                print("----- Utility Test: generate_image_description -----")
                with open(markdown_file, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                img_url_list = extract_image_urls(markdown_content, rm_redundancy=True)
                for url in img_url_list:
                    print(url)
                print(f"--- Image description of {img_url_list[0]} ---")
                start_time = time.time()
                image_description = generate_image_description(img_url_list[0])
                end_time = time.time() - start_time
                print(image_description)
                print(f"-----------------------------------------")
                print(f"generate_image_description() in {end_time:.2f} seconds.") 
                print(f"-----------------------------------------")

            case _:
                print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)
        
    except Exception as e:
        print(f"Unknown Error: {e}") 

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


if __name__ == "__main__":
    main()
