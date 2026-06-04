import os, sys, json
from PIL import Image
from base64 import b64decode
from pydantic import BaseModel, Field
from typing import Annotated, NamedTuple
from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, AdaptiveConfig, 
                      AdaptiveCrawler, LLMConfig, LLMExtractionStrategy)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableStructureOptions,
    AcceleratorOptions
)
from utils import (gen_random_string, check_image, convert_image2pdf)

mode_type_list = ["basic", "filter", "docling"]
intermediate_type_list = ["pdf", "image"]

# Check operating system (OS)
if sys.platform.startswith('win'):
    print("Operating System: Windows")
    is_macOS = False
elif sys.platform.startswith('darwin'):
    print("Operating System: macOS")
    is_macOS = True
elif sys.platform.startswith('linux'):
    print("Operating System: Linux")
    is_macOS = False

class Result(NamedTuple):
    code: int
    content: str
    message: str


async def url2markdown(url:str, mode_type:str='basic', threshold:float=0.3, 
                       threshold_type:str="fixed", intermediate_type:str="pdf") -> Result:
    try:
        match mode_type:
            case "basic":
                return url2markdown_basic_mode(url=url)
            
            case "filter":
                return url2markdown_filter_mode(url=url, threshold=threshold, threshold_type=threshold_type)

            case "docling":
                return url2markdown_docling_mode(url=url, intermediate_type=intermediate_type)

            case _:
                return Result(400, None, f"Wrong mode_type:{mode_type}.")

    except Exception as e:
        #print(f"Unknown Error: {e}")
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


async def url2markdown_basic_mode(url:str) -> Result:
    try:
        #  BrowserConfig: Controls browser behavior (headless or full UI, user agent, JavaScript toggles, etc.)
        browser_conf = BrowserConfig(headless=True)  # or False to see the browser
        # CrawlerRunConfig: Controls how each crawl runs (caching, extraction, timeouts, hooking, etc.)
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS
        )
        # Create an instance of AsyncWebCrawler
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_conf
            )
            if result.success:
                return Result(200, result.markdown, f"Conversion done.")
            else:
                return Result(400, None, result.error_message)
    
    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


async def url2markdown_filter_mode(url:str, threshold:float=0.3, threshold_type:str="fixed") -> Result:
    try:
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=threshold, threshold_type=threshold_type)
        )
        run_conf = CrawlerRunConfig(
            cache_mode = CacheMode.BYPASS,
            markdown_generator = md_generator
        )
        # Create an instance of AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            # Run the crawler on a URL
            result = await crawler.arun(
                url=url,
                config=run_conf,
            )

            if result.success:
                return Result(200, result.fit_markdown, f"Conversion done.")
            else:
                return Result(400, None, result.error_message)
    
    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


async def url2markdown_docling_mode(url:str, intermediate_type:str="pdf") -> Result:
    temporary_pdf = f"./outputs/{gen_random_string(length=15)}.pdf"
    try:
        # Image conversion for PdfPipeline
        if check_image(url):
            if convert_image2pdf(url, temporary_pdf):
                pass
            else:
                print(f"Error: Connot convert {input_doc_path} to PDF.")
                return
            
        conv_res = pdf2markdown_docling(temporary_pdf)

        if result.success:
            return Result(200, result.fit_markdown, f"Conversion done.")
        else:
            return Result(400, None, result.error_message)
    
    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        if os.path.exists(temporary_pdf) and os.path.isfile(temporary_pdf):
            os.remove(temporary_pdf)


def pdf2markdown_docling(pdf_path:str, is_ocr:bool=True, image_mode:str="referenced"):
    try:
        if pdf_path.lower().endswith(".pdf") and os.path.isfile(pdf_path):
            print("----- Docling DocumentConverter with PdfPipeline + EasyOcr + TableStructure -----")
        else:
            print(f"Error: File {pdf_path} is not valid.")
            return
        
        if is_macOS:
            # Docling Parse Pipeline with EasyOCR (CPU only)
            accelerator_options = AcceleratorOptions(device="cpu")
            pipeline_options = PdfPipelineOptions(accelerator_options=accelerator_options)
        else:
            pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)
        pipeline_options.images_scale = 2.0  # The rendered image resolution (scale = 1 ~ 72 DPI)
        pipeline_options.generate_page_images = True # The `generate_*` toggles decide which elements are enriched with images.
        pipeline_options.generate_table_images = True
        pipeline_options.generate_picture_images = True
        if is_ocr:
            pipeline_options.do_ocr = True # Enable OCR
            pipeline_options.ocr_options = EasyOcrOptions() # Use EasyOCR
            pipeline_options.ocr_options.lang = ["en", "ch_tra"]
            pipeline_options.ocr_options.force_full_page_ocr = True

        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        conv_res = doc_converter.convert(pdf_path)

        if result.success:
            return Result(200, result.fit_markdown, f"Conversion done.")
        else:
            return Result(400, None, result.error_message)


    except Exception as e:
        #print(f"Unknown Error: {e}") 
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass
