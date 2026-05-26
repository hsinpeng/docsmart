import asyncio
from pathlib import Path
from docling.document_converter import DocumentConverter

BASE_DIR = Path(__file__).parent

run_option = 0

test_url_index = 0
test_url_list = []
test_url_list.append("https://www.hamimall.com.tw/product.php?id=522727&utm_source=hamipoint&utm_medium=productlist_rec&utm_campaign=pointpoint&utm_content=522727")
test_url_list.append("https://online.senao.com.tw/mart/1348423")

output_mdfile_docling = "./outputs/docling_output.md"


async def main():
    match run_option:
        case 0:
            target_url = test_url_list[test_url_index]
            print("----- Basic (Raw) converter -----")
            converter = DocumentConverter()
            result = converter.convert(target_url)
            print("Docling Technical Report:", len(result.document.export_to_markdown()))
            with open(output_mdfile_docling, "w", encoding="utf-8") as f:
                f.write(result.document.export_to_markdown()) # Access the generated markdown

        case 1:
            print("----- Default Filter converter -----")
            print("Sorry. Under Construction...")

        case 2:
            print("----- Customized Filter converter -----")
            print("Sorry. Under Construction...")

        case _:
            print(f"Error: Unknown run_option ({run_option})!") # Wildcard (default case)
    
                
if __name__ == "__main__":
    asyncio.run(main())