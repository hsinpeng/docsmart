import io, asyncio
from converter import (url2markdown_crawl4ai, url2markdown_docling)

test_url_list = []
test_url_list.append("https://www.hamimall.com.tw/product.php?id=522727&utm_source=hamipoint&utm_medium=productlist_rec&utm_campaign=pointpoint&utm_content=522727")
test_url_list.append("https://online.senao.com.tw/mart/1348423")
test_url_list.append("https://www.cht.com.tw/home/consumer")
test_url_list.append("https://www.momoshop.com.tw/main/Main.jsp")


async def main():
    run_option = 1
    test_url_index = 0
    try:
        match run_option:
            case 0:
                target_url = test_url_list[test_url_index]
                result = await url2markdown_crawl4ai(target_url, mode_type="filter")
                if result.code == 200:
                    print(result.content)
                else:
                    print(result.message)

            case 1:
                target_url = test_url_list[test_url_index]
                result = await url2markdown_docling(target_url, output_file="./outputs/pdf/url2markdown_docling.md")
                if result.code == 200:
                    print(result.content)
                else:
                    print(result.message)

            case 2:
                target_url = test_url_list[test_url_index]
                result = await url2markdown_docling(target_url, output_file="./outputs/image/url2markdown_docling.md",
                                                    intermediate_type="image")
                if result.code == 200:
                    print(result.content)
                else:
                    print(result.message)

            case _:
                print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)

    except Exception as e:
        print(f"Unknown Error: {e}") 

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


if __name__ == "__main__":
    asyncio.run(main())