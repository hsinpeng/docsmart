import os, io, sys
from PIL import Image
from pathlib import Path
from base64 import b64decode
from pydantic import Field
from typing import NamedTuple
from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import ImageRefMode
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableStructureOptions,
    AcceleratorOptions
)
from utils import (gen_random_string, check_image, convert_image2pdf)

# Check operating system (OS)
if sys.platform.startswith('win'):
    #print("Operating System: Windows")
    is_macOS = False
elif sys.platform.startswith('darwin'):
    #print("Operating System: macOS")
    is_macOS = True
elif sys.platform.startswith('linux'):
    #print("Operating System: Linux")
    is_macOS = False

class Result(NamedTuple):
    code: int
    content: str
    message: str


async def url2markdown_crawl4ai(url:str, mode_type:str='basic', 
                                threshold:float=0.3, threshold_type:str="fixed") -> Result:
    try:
        match mode_type:
            case "basic":
                return await url2markdown_crawl4ai_basic_mode(url=url)
            
            case "filter":
                return await url2markdown_crawl4ai_filter_mode(url=url, threshold=threshold, threshold_type=threshold_type)

            case _:
                return Result(400, None, f"Wrong mode_type:{mode_type}.")

    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


async def url2markdown_crawl4ai_basic_mode(url:str) -> Result:
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


async def url2markdown_crawl4ai_filter_mode(url:str, threshold:float=0.3, threshold_type:str="fixed") -> Result:
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
                return Result(200, result.markdown.fit_markdown, f"Conversion done.")
            else:
                return Result(400, None, result.error_message)
    
    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass


async def url2markdown_docling(url:str, output_file:str, intermediate_type:str="pdf") -> Result:
    temporary_pdf = f"./outputs/{gen_random_string(length=15)}.pdf"
    temporary_jpg = f"./outputs/{gen_random_string(length=15)}.jpg"
    try:
        # Convert URL to Image and PDF and Image
        run_conf = CrawlerRunConfig(
            cache_mode = CacheMode.BYPASS,
            wait_for_images=True,
            scan_full_page=True,
            screenshot=True,
            pdf=True
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=run_conf
            ) 
        if result.success and result.screenshot:
            if intermediate_type == "pdf":
                # Save screenshot to PDF file (Good enough for docling)
                with open(temporary_pdf, "wb") as f:
                    f.write(result.pdf)
            elif intermediate_type == "image":
                # Save screenshot to image file (Poor quality for docling)
                image_data = b64decode(result.screenshot) # The screenshot of Crawl4AI is a Base64 string, which needs to be decoded first.
                image = Image.open(io.BytesIO(image_data)) # Open image bytes by Pillow (PIL)
                image.save(temporary_jpg)
                if os.path.exists(temporary_jpg) and os.path.isfile(temporary_jpg):
                    if convert_image2pdf(temporary_jpg, temporary_pdf):
                        if os.path.isfile(temporary_pdf):
                            pass
                        else:
                            return Result(400, None, f"Error: Temporary PDF {temporary_pdf} cannot be created.")
                    else:
                        return Result(400, None, f"Error: Connot convert temporary image {temporary_jpg} to PDF.")
                else:
                    return Result(400, None, f"Error: Temporary image {temporary_jpg} does not exist.")
            else:
                return Result(400, None, f"Error: intermediate_type({temporary_pdf}) is invalid.")
        else:
            return Result(400, None, f"Unable to crawl webpage({url}). Error message: {result.error_message}")

        return pdf2markdown_docling(temporary_pdf, output_file=output_file)

    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        if os.path.exists(temporary_pdf) and os.path.isfile(temporary_pdf):
            os.remove(temporary_pdf)
        if os.path.exists(temporary_jpg) and os.path.isfile(temporary_jpg):
            os.remove(temporary_jpg)


def pdf2markdown_docling(pdf_path:str, output_file:str, is_ocr:bool=True, image_mode:str="referenced"):
    try:
        if (pdf_path.lower().endswith(".pdf")) and (os.path.isfile(pdf_path)):
            pass
        else:
            print(os.path.isfile(pdf_path))
            return Result(400, None, f"Error: File {pdf_path} is not valid.")
        
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

        md_filename = Path(output_file)
        if image_mode == "placeholder":
            # Save markdown without pictures
            image_mode=ImageRefMode.PLACEHOLDER
        elif image_mode == "embedded":
            # Save markdown with embedded pictures
            image_mode=ImageRefMode.EMBEDDED
        elif image_mode == "referenced":
            # Save markdown with externally referenced pictures
            image_mode=ImageRefMode.REFERENCED
        else:
            return Result(400, None, f"Error: Unsupported image_mode({image_mode}).")

        conv_res.document.save_as_markdown(md_filename, image_mode=image_mode)
        return Result(200, str(md_filename), f"Conversion done.")

    except Exception as e:
        return Result(500, None, f"Unknown Error: {e}.")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass
