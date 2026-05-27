import asyncio, json, time
from pydantic import BaseModel, Field
from typing import Annotated
from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, AdaptiveConfig, 
                      AdaptiveCrawler, LLMConfig, LLMExtractionStrategy)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from utils import (extract_urls, extract_image_urls, determine_type, generate_title, generate_image_description)

run_option = 2
test_url_index = 0
test_url_list = []
test_url_list.append("https://www.hamimall.com.tw/product.php?id=522727&utm_source=hamipoint&utm_medium=productlist_rec&utm_campaign=pointpoint&utm_content=522727")
test_url_list.append("https://online.senao.com.tw/mart/1348423")
test_url_list.append("https://www.cht.com.tw/home/consumer")
test_url_list.append("https://www.momoshop.com.tw/main/Main.jsp")

output_mdfile_raw = "./outputs/crawl4ai_output_raw.md"
output_mdfile_fit = "./outputs/crawl4ai_output_fit.md"

ollama_model = "ollama/granite4.1:8b" # "ollama/qwen3.5:9b" "ollama/granite4.1:8b"
ollama_embed = "ollama/qwen3-embedding:latest" # "ollama/qwen3-embedding:latest" "ollama/nomic-embed-text-v2-moe:latest"

async def main():
    try:
        match run_option:
            case 0:
                target_url = test_url_list[test_url_index]
                print("----- Basic (Raw) Crawling -----")
                # Create an instance of AsyncWebCrawler
                async with AsyncWebCrawler() as crawler:
                    # Run the crawler on a URL
                    start_time = time.time()
                    result = await crawler.arun(url=target_url)
                    end_time = time.time() - start_time
                    print(f"Crawler run in {end_time:.2f} seconds.")
                    # Print the extracted content
                    if result.success:
                        print("Markdown length:", len(result.markdown))
                        with open(output_mdfile_raw, "w", encoding="utf-8") as f:
                            f.write(result.markdown) 

            case 1:
                target_url = test_url_list[test_url_index]
                print("----- Basic Configuration (Light Introduction) -----")
                #  BrowserConfig: Controls browser behavior (headless or full UI, user agent, JavaScript toggles, etc.)
                browser_conf = BrowserConfig(headless=True)  # or False to see the browser
                # CrawlerRunConfig: Controls how each crawl runs (caching, extraction, timeouts, hooking, etc.)
                run_conf = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS
                )
                # Create an instance of AsyncWebCrawler
                async with AsyncWebCrawler(config=browser_conf) as crawler:
                    start_time = time.time()
                    result = await crawler.arun(
                        url=target_url,
                        config=run_conf
                    )
                    end_time = time.time() - start_time
                    print(f"Crawler run in {end_time:.2f} seconds.")
                    # Print the extracted content
                    if result.success:
                        print("Markdown length:", len(result.markdown))
                        with open(output_mdfile_raw, "w", encoding="utf-8") as f:
                            f.write(result.markdown) 

            case 2:
                target_url = test_url_list[test_url_index]
                print("----- Generating Markdown Output -----")
                browser_conf = BrowserConfig(headless=True)  # or False to see the browser
                # The customized output depends on whether you specify a markdown generator or content filter.
                md_generator = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.3, threshold_type="fixed")
                )
                run_conf = CrawlerRunConfig(
                    cache_mode = CacheMode.BYPASS,
                    markdown_generator = md_generator
                )
                # Create an instance of AsyncWebCrawler
                async with AsyncWebCrawler() as crawler:
                    # Run the crawler on a URL
                    start_time = time.time()
                    result = await crawler.arun(
                        url=target_url,
                        config=run_conf,
                    )
                    end_time = time.time() - start_time
                    print(f"Crawler run in {end_time:.2f} seconds.")
                    # Print the extracted content
                    if result.success:
                        markdown_content = result.markdown.fit_markdown # Access fit markdown (if filters were used)
                        print(f"----- Fit Markdown length: {len(markdown_content)} -----")
                        with open(output_mdfile_fit, "w", encoding="utf-8") as f:
                            f.write(markdown_content) 
                        
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
                        else:
                            print("Error: extract_urls_from_file() Fail!") 
                    else:
                        print("Error: crawler.arun() Fail!")

            case 3:
                # A three-layer scoring system that determines when you have "enough" information.
                # (1) Coverage: How well your collected pages cover the query terms
                # (2) Consistency: Whether the information is coherent across pages
                # (3) Saturation: Detecting when new pages aren't adding new information
                target_url = test_url_list[test_url_index]
                print("----- Adaptive Crawling (Statistical Strategy) -----")
                async with AsyncWebCrawler() as crawler:
                    #adaptive = AdaptiveCrawler(crawler)
                    config = AdaptiveConfig(
                        strategy="statistical",     # This is the default
                        confidence_threshold=0.8,   # Stop when 80% confident (default: 0.7)
                        max_pages=30,               # Maximum pages to crawl (default: 20)
                        top_k_links=5,              # Links to follow per page (default: 3)
                        min_gain_threshold=0.05     # Minimum expected gain to continue (default: 0.1)
                    )
                    adaptive = AdaptiveCrawler(crawler, config)

                    # Start adaptive crawling
                    start_time = time.time()
                    result = await adaptive.digest(
                        start_url=target_url,
                        query="shopping website"
                    )
                    end_time = time.time() - start_time

                    # View results
                    print("--- Statistics ---")
                    adaptive.print_stats()

                    print("--- Summary ---")
                    print(f"Crawled {len(result.crawled_urls)} pages")
                    print(f"Achieved {adaptive.confidence:.0%} confidence")
                    # Check if query was irrelevant
                    if result.metrics.get('is_irrelevant', False):
                        print("Query is unrelated to the content!")
                    else:
                        print("Query is related to the content!")

                    print("--- get_relevant_content(top_k=3) ---")
                    relevant_pages = adaptive.get_relevant_content(top_k=3)
                    for page in relevant_pages:
                        print(f"URL: {page['url']} | Relevant: {page['score']:.2%}")
                        print(f"Abstrat: {page['content'][:100]}...")
                    print(f"Adaptive-crawler(Statistical) run in {end_time:.2f} seconds.")
            
            case 4:
                target_url = test_url_list[test_url_index]
                print("----- Adaptive Crawling (Embedding Strategy) -----")
                async with AsyncWebCrawler() as crawler:
                    config = AdaptiveConfig(
                        strategy="embedding", # Embedding Strategy
                        embedding_llm_config=LLMConfig(
                            provider=ollama_embed,
                            api_token='your-api-key'
                        ), # Use for API-based embeddings (embedding model)
                        query_llm_config=LLMConfig(
                            provider=ollama_model,
                            api_token='your-api-key'
                        ), # Use for query expansion (chat completion model)
                        # Query expansion
                        n_query_variations=10,  # Number of query variations to generate
                        # Coverage parameters
                        embedding_coverage_radius=0.2,  # Distance threshold for coverage
                        embedding_k_exp=3.0,            # Exponential decay factor (higher = stricter)
                        # Stopping criteria
                        embedding_min_relative_improvement=0.1, # Min improvement to continue
                        embedding_validation_min_score=0.3,     # Min validation score
                        embedding_min_confidence_threshold=0.1, # Below this = irrelevant
                        # Link selection
                        embedding_overlap_threshold=0.85,  # Similarity for deduplication
                        # Display confidence mapping
                        embedding_quality_min_confidence=0.7,  # Min displayed confidence
                        embedding_quality_max_confidence=0.95  # Max displayed confidence
                    )
                    adaptive = AdaptiveCrawler(crawler, config)

                    # Start adaptive crawling
                    start_time = time.time()
                    result = await adaptive.digest(
                        # start_url="https://docs.python.org/3/",
                        # query="async context managers"
                        start_url=target_url,
                        query="shopping website"
                    )
                    end_time = time.time() - start_time

                    # View results
                    print("--- Statistics ---")
                    adaptive.print_stats()

                    print("--- Summary ---")
                    print(f"Crawled {len(result.crawled_urls)} pages")
                    print(f"Achieved {adaptive.confidence:.0%} confidence")
                    # Check if query was irrelevant
                    if result.metrics.get('is_irrelevant', False):
                        print("Query is unrelated to the content!")
                    else:
                        print("Query is related to the content!")

                    print("--- get_relevant_content(top_k=3) ---")
                    relevant_pages = adaptive.get_relevant_content(top_k=3)
                    for page in relevant_pages:
                        print(f"URL: {page['url']} | Relevant: {page['score']:.2%}")
                        print(f"Abstrat: {page['content'][:100]}...")
                    print(f"Adaptive-crawler(Embedding) run in {end_time:.2f} seconds.")

            case 5:
                print("----- Multi-URL Concurrency -----")
                run_conf = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    stream=True  # Enable streaming mode (Default: batch mode)
                )
                is_stream:bool = True
                async with AsyncWebCrawler() as crawler:
                    start_time = time.time()
                    if is_stream:
                        # Streaming mode: Stream results as they complete
                        async for result in await crawler.arun_many(test_url_list, config=run_conf):
                            if result.success:
                                print(f"[OK] {result.url}, length: {len(result.markdown.raw_markdown)}")
                            else:
                                print(f"[ERROR] {result.url} => {result.error_message}")
                    else:
                        # Batch mode : Get all results at once (default behavior)
                        run_conf = run_conf.clone(stream=False)
                        results = await crawler.arun_many(test_url_list, config=run_conf)
                        for res in results:
                            if res.success:
                                print(f"[OK] {res.url}, length: {len(res.markdown.raw_markdown)}")
                            else:
                                print(f"[ERROR] {res.url} => {res.error_message}")
                    end_time = time.time() - start_time
                    print(f"Multi-crawler run in {end_time:.2f} seconds.")

            case 6:
                print("----- Extract Subject(Type) and Title from URL -----")
                # Target URL
                target_url = test_url_list[test_url_index]
                
                # Instruction
                query_instruction = "You are a helpful and concise assistant. Please extract the subject and main title of the product or activity of the given content."
                            
                # Schema
                class WebPageProfile(BaseModel):
                    page_type: Annotated[str, Field(description="""The main subject of the given webpage. There are three subject only: product, activity, or other.
                                                    'product' indicates that the content is describing the only one and specific product.
                                                    'activity' indicates that the content is describing the only one and specific activity or event.
                                                    'other' means the webpage does not belong to any of the above categories.
                                                    Note: Just answer 'product', 'activity', or 'other' only. No more words.""")]
                    page_title: Annotated[str, Field(description="""You are a helpful and concise assistant. Please extract the main title of the product or activity of the given content.
                              Note: Answer me in Traditional Chinese. Just give me the title only, no more explanation.""")]
                    # page_type: str = Field(..., description="The main subject of the given webpage. There are three subject: product, activity, or other.")
                    # page_title: str = Field(..., description="The main title of the given webpage, if the subject is product or activity. Reply 'None' if the subject is other.")
                query_schema = WebPageProfile.model_json_schema()

                extra_args = {
                    "temperature": 0
                }

                crawler_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=1,
                    page_timeout=80000,
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config = LLMConfig(provider=ollama_model, api_token="your-api-key"),
                        schema=query_schema,
                        extraction_type="schema",
                        instruction=query_instruction,
                        extra_args=extra_args,
                    ),
                )

                browser_config = BrowserConfig(headless=True)
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    start_time = time.time()
                    result = await crawler.arun(
                        url=target_url, config=crawler_config
                    )
                    end_time = time.time() - start_time
                    json_result = json.loads(result.extracted_content)
                    print(f"Page Type: {json_result[0]['page_type']}")
                    print(f"Page Title: {json_result[0]['page_title']}")
                    print(f"Crawler(LLM Extraction) run in {end_time:.2f} seconds.") 

            case _:
                print(f"Error: Unknown run_option ({run_option})!") # Wildcard (default case)
        
    except Exception as e:
        print(f"Unknown Error: {e}") 


if __name__ == "__main__":
    asyncio.run(main())