import os, time, requests
from utils import (extract_urls, extract_image_urls, determine_type, generate_title, generate_image_description,
                   convert_image2pdf, get_content_imagetype, check_image_validity)

def main():
    run_option = 5
    try:
        print(f"Hello. This is utility test. The run_option is {run_option}.")
        match run_option:
            case 0:
                markdown_file = "./outputs/url2markdown_crawl4ai.md"
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
                markdown_file = "./outputs/url2markdown_crawl4ai.md"
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
                markdown_file = "./outputs/crawl4ai_output_fit.md" # "./outputs/crawl4ai_output_fit.md" "./outputs/crawl4ai_output_raw.md" "./outputs/docling_output.md"
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

            case 3:
                input_doc_path = "./inputs/crawl4ai_output.png"
                output_doc_path = "./outputs/crawl4ai_output_png.pdf"
                print("----- Utility Test: generate_image_description -----")
                if convert_image2pdf(input_doc_path, output_doc_path):
                    print(f"File {input_doc_path} has been converted to {output_doc_path}.")
                else:
                    print(f"Error: Connot convert {input_doc_path} to PDF.")
            
            case 4:
                data_bytes = None
                #target_uri = "./inputs/crawl4ai_output.png" #"./inputs/Fan01.pdf"
                target_uri = "https://pdinfo.senao.com.tw/octopus/contents/a3704041768446f8bb8dd3cfa0f688bc.jpg"
                if os.path.isfile(target_uri):
                    # 'wb' opens the file in binary mode to write image data
                    with open(target_uri, "rb") as f:
                        data_bytes = f.read()
                else:
                    response = requests.get(target_uri)
                    # Check if the download was successful
                    if response.status_code == 200:
                        data_bytes = response.content
                    else:
                        print(f"Error: Cannot retrieve {target_uri}, code={response.status_code}!")
                image_type = get_content_imagetype(data_bytes)
                print(f"Image type: {image_type}")
            
            case 5:
                target_uri = "./inputs/Fan01.jpg" # "./inputs/crawl4ai_output.png" #"./inputs/Fan01.pdf"
                #target_uri = "https://supabase.com/" # "https://pdinfo.senao.com.tw/octopus/contents/a3704041768446f8bb8dd3cfa0f688bc.jpg"
                result = check_image_validity(target_uri) #, mode="extension")
                print(f"Result: {result}")
            
            case _:
                print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)
        
    except Exception as e:
        print(f"Unknown Error: {e}") 

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


if __name__ == "__main__":
    main()
