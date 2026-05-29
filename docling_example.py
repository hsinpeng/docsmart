import os, sys, asyncio, time
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from docling.document_converter import DocumentConverter, PdfFormatOption, HTMLFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PaginatedPipelineOptions,
    EasyOcrOptions,
    TableStructureOptions,
    AcceleratorOptions
)
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from utils import check_image, gen_random_string, convert_image2pdf

run_option = 2
test_url_index = 0
test_url_list = []
test_url_list.append("https://www.hamimall.com.tw/product.php?id=522727&utm_source=hamipoint&utm_medium=productlist_rec&utm_campaign=pointpoint&utm_content=522727")
test_url_list.append("https://online.senao.com.tw/mart/1348423")
test_url_list.append("https://www.cht.com.tw/home/consumer")
test_url_list.append("https://www.momoshop.com.tw/main/Main.jsp")

output_mdfile_docling = "./outputs/docling_output.md"
temporary_pdf = f"./outputs/{gen_random_string(length=15)}.pdf"


def save_page_images(conv_result:ConversionResult, filepath_prefix:str):
    # Save page images
    for page_no, page in conv_result.document.pages.items():
        print(f"Get page image:{page_no}")
        page_no = page.page_no
        page_image_filename = Path(f"{filepath_prefix}-page-{page_no}.png")
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")


def save_table_figure_images(conv_result:ConversionResult, filepath_prefix:str):
    # Save images of figures and tables
    table_counter = 0
    figure_counter = 0
    for element, _level in conv_result.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            print(f"Get table:{table_counter}")
            element_image_filename = (
                Path(f"{filepath_prefix}-table-{table_counter}.png")
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_result.document).save(fp, "PNG")

        if isinstance(element, PictureItem):
            figure_counter += 1
            print(f"Get figure:{figure_counter}")
            element_image_filename = (
                Path(f"{filepath_prefix}-figure-{figure_counter}.png")
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_result.document).save(fp, "PNG")


def save_conversion_result(conv_result:ConversionResult, filepath_prefix:str, 
                           file_type:str="all", image_mode:str="referenced"):
    if (file_type == "all") or (file_type == "markdown"):
        if (file_type == "all") or (image_mode == "placeholder"):
            # Save markdown without pictures
            md_filename = Path(f"{filepath_prefix}-out-without-images.md")
            conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.PLACEHOLDER)

        if (file_type == "all") or (image_mode == "embedded"):
            # Save markdown with embedded pictures
            md_filename = Path(f"{filepath_prefix}-out-with-images.md")
            conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

        if (file_type == "all") or (image_mode == "referenced"):
            # Save markdown with externally referenced pictures
            md_filename = Path(f"{filepath_prefix}-out-with-images-refs.md")
            conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    if (file_type == "all") or (file_type == "html"):
        # Save HTML with externally referenced pictures
        html_filename = Path(f"{filepath_prefix}-out-with-images-refs.html")
        conv_result.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)


async def main():
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
    
    try:
        match run_option:
            case 0:
                target_url = test_url_list[test_url_index]
                output_prefix = "./outputs/url"
                print("----- Basic Docling DocumentConverter -----")
                converter = DocumentConverter()
                start_time = time.time()
                conv_res = converter.convert(
                    source=target_url,
                    max_num_pages=20,
                    max_file_size=52428800,
                    raises_on_error=True
                ) 
                end_time = time.time() - start_time
                print(f"Document converted in {end_time:.2f} seconds.")      

                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"Document converted and files exported in {end_time:.2f} seconds.")

            case 1: ## PdfPipeline (No OCR)
                input_doc_path = "./inputs/Fan01.jpg"
                # input_doc_path = "./inputs/38xx_ct.pdf"
                output_prefix = "./outputs/no-ocr"
                if os.path.exists(input_doc_path):
                    print("----- Docling DocumentConverter with PdfPipeline (No OCR) -----")
                else:
                    print(f"Error: File {input_doc_path} does not exist.")
                    return
                
                # Image processing for PdfPipeline
                if check_image(input_doc_path):
                    if convert_image2pdf(input_doc_path, temporary_pdf):
                        input_doc_path = temporary_pdf
                    else:
                        print(f"Error: Connot convert {input_doc_path} to PDF.")
                        return
                if not (input_doc_path.lower().endswith(".pdf")):
                    print(f"Error: Connot find {input_doc_path}.")
                    return

                # Docling Parse Pipeline without EasyOCR
                if is_macOS:
                    # Docling Parse Pipeline with EasyOCR (CPU only)
                    accelerator_options = AcceleratorOptions(device="cpu")
                    pipeline_options = PdfPipelineOptions(accelerator_options=accelerator_options)
                else:
                    pipeline_options = PdfPipelineOptions()
                pipeline_options.images_scale = 2.0  # The rendered image resolution (scale = 1 ~ 72 DPI)
                pipeline_options.generate_page_images = True # The `generate_*` toggles decide which elements are enriched with images.
                pipeline_options.generate_table_images = True
                pipeline_options.generate_picture_images = True

                converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                    }
                )
                start_time = time.time()
                conv_res = converter.convert(input_doc_path)
                end_time = time.time() - start_time
                print(f"Document converted in {end_time:.2f} seconds.")

                save_page_images(conv_res, output_prefix) # Save page images
                save_table_figure_images(conv_res, output_prefix) # Save images of figures and tables
                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"Document converted and images/files exported in {end_time:.2f} seconds.")
            
            case 2: ## PdfPipeline (with OCR)
                input_doc_path = "./inputs/Fan01.jpg"
                # input_doc_path = "./inputs/38xx_ct.pdf"
                output_prefix = "./outputs/ocr"
                if os.path.exists(input_doc_path):
                    print("----- Docling DocumentConverter with PdfPipeline + EasyOcr + TableStructure -----")
                else:
                    print(f"Error: File {input_doc_path} does not exist.")
                    return
                
                # Image processing for PdfPipeline
                if check_image(input_doc_path):
                    if convert_image2pdf(input_doc_path, temporary_pdf):
                        input_doc_path = temporary_pdf
                    else:
                        print(f"Error: Connot convert {input_doc_path} to PDF.")
                        return
                if not (input_doc_path.lower().endswith(".pdf")):
                    print(f"Error: Connot find {input_doc_path}.")
                    return
                
                if is_macOS:
                    # Docling Parse Pipeline with EasyOCR (CPU only)
                    accelerator_options = AcceleratorOptions(device="cpu")
                    pipeline_options = PdfPipelineOptions(accelerator_options=accelerator_options)
                else:
                    pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True # Enable OCR
                pipeline_options.ocr_options = EasyOcrOptions() # Use EasyOCR
                pipeline_options.ocr_options.lang = ["en", "ch_tra"]
                pipeline_options.ocr_options.force_full_page_ocr = True
                pipeline_options.do_table_structure = True
                pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)
                pipeline_options.images_scale = 2.0  # The rendered image resolution (scale = 1 ~ 72 DPI)
                pipeline_options.generate_page_images = True # The `generate_*` toggles decide which elements are enriched with images.
                pipeline_options.generate_table_images = True
                pipeline_options.generate_picture_images = True

                doc_converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                    }
                )
                start_time = time.time()
                conv_res = doc_converter.convert(input_doc_path)
                end_time = time.time() - start_time
                print(f"Document converted in {end_time:.2f} seconds.")
                
                save_page_images(conv_res, output_prefix) # Save page images
                save_table_figure_images(conv_res, output_prefix) # Save images of figures and tables
                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"Document converted and images/files exported in {end_time:.2f} seconds.")

            case 3:
                target_url = test_url_list[test_url_index]
                output_prefix = "./outputs/crawl4ai-ocr"
                pdf_temp = f"{output_prefix}-temp.pdf"
                print("----- Docling DocumentConverter + Crawl4AI AsyncWebCrawler -----")
                ##### Crawl4AI #####
                browser_conf = BrowserConfig(headless=True)  # or False to see the browser
                # The customized output depends on whether you specify a markdown generator or content filter.
                md_generator = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.3, threshold_type="fixed")
                )
                run_conf = CrawlerRunConfig(
                    wait_for_images=True, # Force the crawler to wait until images are fully loaded
                    cache_mode=CacheMode.BYPASS,
                    markdown_generator=md_generator,
                    pdf=True  # Instructs Playwright to capture the full page as a PDF
                )

                # Run the asynchronous web crawler
                start_time = time.time()
                async with AsyncWebCrawler(config=browser_conf) as crawler:
                    result = await crawler.arun(url=target_url, config=run_conf)
                    # Check for success and save the binary data
                    if result.success and result.pdf:
                        with open(pdf_temp, "wb") as f:
                            f.write(result.pdf)
                        print(f"Successfully converted and saved: {pdf_temp}")
                    else:
                        print(f"Failed to generate PDF. Error: {result.error_message}")
                end_time = time.time() - start_time
                print(f"Web crawlered and PDF converted in {end_time:.2f} seconds.")
                
                ##### Docling #####
                if is_macOS:
                    # Docling Parse Pipeline with EasyOCR (CPU only)
                    accelerator_options = AcceleratorOptions(device="cpu")
                    pipeline_options = PdfPipelineOptions(accelerator_options=accelerator_options)
                else:
                    pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True # Enable OCR
                pipeline_options.ocr_options = EasyOcrOptions() # Use EasyOCR
                pipeline_options.ocr_options.lang = ["en", "ch_tra"]
                pipeline_options.ocr_options.force_full_page_ocr = True
                pipeline_options.do_table_structure = True
                pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)
                pipeline_options.images_scale = 2.0  # The rendered image resolution (scale = 1 ~ 72 DPI)
                pipeline_options.generate_page_images = True # The `generate_*` toggles decide which elements are enriched with images.
                pipeline_options.generate_table_images = True
                pipeline_options.generate_picture_images = True

                doc_converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                    }
                )
                start_time = time.time()
                conv_res = doc_converter.convert(pdf_temp)
                end_time = time.time() - start_time
                print(f"Document converted in {end_time:.2f} seconds.")
                
                save_page_images(conv_res, output_prefix) # Save page images
                save_table_figure_images(conv_res, output_prefix) # Save images of figures and tables
                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"Document converted and images/files exported in {end_time:.2f} seconds.")

            case 101: # No good. OCR and images extraction are not working to HTML or docx.
                target_url = test_url_list[test_url_index]
                output_prefix = "./outputs/url-no-ocr"
                print("----- DocumentConverter with HTMLFormatOption -----")
                if is_macOS:
                    # Docling Parse Pipeline with EasyOCR (CPU only)
                    accelerator_options = AcceleratorOptions(device="cpu")
                    pipeline_options = PdfPipelineOptions(accelerator_options=accelerator_options)
                else:
                    pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True # Enable OCR
                pipeline_options.ocr_options = EasyOcrOptions() # Use EasyOCR
                pipeline_options.ocr_options.lang = ["en", "ch_tra"]
                pipeline_options.ocr_options.force_full_page_ocr = True
                pipeline_options.do_table_structure = True
                pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)
                pipeline_options.images_scale = 2.0
                pipeline_options.generate_page_images = True
                pipeline_options.generate_picture_images = True

                converter = DocumentConverter(
                    format_options={
                        InputFormat.HTML: HTMLFormatOption(pipeline_options=pipeline_options)
                    }
                )
                start_time = time.time()
                conv_res = converter.convert(target_url)       
                end_time = time.time() - start_time
                print(f"URL converted in {end_time:.2f} seconds.")
                
                # save_page_images(conv_res, output_prefix) # Save page images
                # save_table_figure_images(conv_res, output_prefix) # Save images of figures and tables
                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"URL converted and images/files exported in {end_time:.2f} seconds.")

            case 102: # No good. OCR and images extraction are not working to HTML or docx.
                target_url = test_url_list[test_url_index]
                output_prefix = "./outputs/url-no-ocr"
                print("----- DocumentConverter with HTMLFormatOption -----")
                if is_macOS:
                    # Docling Parse Pipeline with EasyOCR (CPU only)
                    accelerator_options = AcceleratorOptions(device="cpu")
                    pipeline_options = PaginatedPipelineOptions(accelerator_options=accelerator_options)
                else:
                    pipeline_options = PaginatedPipelineOptions()
                pipeline_options.images_scale = 2.0
                pipeline_options.generate_page_images = True
                pipeline_options.generate_picture_images = True

                converter = DocumentConverter(
                    format_options={
                        InputFormat.HTML: HTMLFormatOption(pipeline_options=pipeline_options)
                    }
                )
                start_time = time.time()
                conv_res = converter.convert(target_url)       
                end_time = time.time() - start_time
                print(f"URL converted in {end_time:.2f} seconds.")
                
                # save_page_images(conv_res, output_prefix) # Save page images
                # save_table_figure_images(conv_res, output_prefix) # Save images of figures and tables
                save_conversion_result(conv_res, output_prefix) # Save result to markdown or html
                end_time = time.time() - start_time
                print(f"URL converted and images/files exported in {end_time:.2f} seconds.")
            
            case _:
                print(f"Error: Invalid run_option ({run_option})!") # Wildcard (default case)

    except Exception as e:
        print(f"Unknown Error:{e}")

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        if os.path.exists(temporary_pdf) and os.path.isfile(temporary_pdf):
            os.remove(temporary_pdf)
                
if __name__ == "__main__":
    asyncio.run(main())