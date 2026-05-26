import os, asyncio, time
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from docling.document_converter import DocumentConverter, PdfFormatOption, HTMLFormatOption
from docling.datamodel.base_models import InputFormat, FigureElement
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableStructureOptions,
    AcceleratorOptions
)
from docling.datamodel.backend_options import HTMLBackendOptions
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

BASE_DIR = Path(__file__).parent
is_MacOS:bool = True

run_option = 3
test_url_index = 0
test_url_list = []
test_url_list.append("https://www.hamimall.com.tw/product.php?id=522727&utm_source=hamipoint&utm_medium=productlist_rec&utm_campaign=pointpoint&utm_content=522727")
test_url_list.append("https://online.senao.com.tw/mart/1348423")
test_url_list.append("https://www.cht.com.tw/home/consumer")
test_url_list.append("https://www.momoshop.com.tw/main/Main.jsp")

output_mdfile_docling = "./outputs/docling_output.md"

async def main():
    # 強制 PyTorch 忽略 MPS 裝置
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["PYTORCH_IGNORE_MPS"] = "1"
    match run_option:
        case 0:
            target_url = test_url_list[test_url_index]
            print("----- Basic DocumentConverter -----")
            converter = DocumentConverter()
            start_time = time.time()
            conv_res = converter.convert(
                source=target_url,
                max_num_pages=20,           # 限制只處理前 20 頁（防止大檔案卡死）
                max_file_size=52428800,     # 限制檔案大小（單位：Bytes，此處為 50MB）
                raises_on_error=True        # 發生錯誤時立即拋出例外
            ) 
            end_time = time.time() - start_time
            print(f"Document converted in {end_time:.2f} seconds.")      

            # print("Docling Technical Report:", len(conv_res.document.export_to_markdown()))
            # with open(output_mdfile_docling, "w", encoding="utf-8") as f:
            #     f.write(conv_res.document.export_to_markdown()) # Access the generated markdown
            # Save markdown without pictures
            md_filename = Path(f"./outputs/url-out-without-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.PLACEHOLDER)

            # Save markdown with embedded pictures
            #md_filename = output_dir / f"{doc_filename}-with-images.md"
            md_filename = Path(f"./outputs/url-out-with-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

            # Save markdown with externally referenced pictures
            md_filename = Path(f"./outputs/url-out-with-images-refs.md")
            #md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

            # Save HTML with externally referenced pictures
            #html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
            html_filename = Path(f"./outputs/url-out-with-images-refs.html")
            conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

            end_time = time.time() - start_time
            print(f"Document converted and figures exported in {end_time:.2f} seconds.")

        case 1:
            input_doc_path = "./inputs/Fan01.pdf"
            print("----- DocumentConverter with PdfPipelineOptions (No OCR settins) -----")
            # Docling Parse Pipeline without EasyOCR
            if is_MacOS:
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

            # Save page images
            for page_no, page in conv_res.document.pages.items():
                print(f"Get image:{page_no}")
                page_no = page.page_no
                page_image_filename = Path(f"./outputs/no-ocr-{page_no}.png")
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")
            
            # Save images of figures and tables
            table_counter = 0
            picture_counter = 0
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    table_counter += 1
                    print(f"Get table:{table_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-table-{table_counter}.png"
                        Path(f"./outputs/no-ocr-table-{table_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

                if isinstance(element, PictureItem):
                    picture_counter += 1
                    print(f"Get picture:{picture_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-picture-{picture_counter}.png"
                        Path(f"./outputs/no-ocr-picture-{picture_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")
            
            # Save markdown without pictures
            md_filename = Path(f"./outputs/no-ocr-out-without-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.PLACEHOLDER)

            # Save markdown with embedded pictures
            #md_filename = output_dir / f"{doc_filename}-with-images.md"
            md_filename = Path(f"./outputs/no-ocr-out-with-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

            # Save markdown with externally referenced pictures
            md_filename = Path(f"./outputs/no-ocr-out-with-images-refs.md")
            #md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

            # Save HTML with externally referenced pictures
            #html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
            html_filename = Path(f"./outputs/no-ocr-out-with-images-refs.html")
            conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

            end_time = time.time() - start_time
            print(f"Document converted and figures exported in {end_time:.2f} seconds.")
        
        case 2:
            input_doc_path = "./inputs/Fan01.pdf"
            print("----- DocumentConverter with PdfPipelineOptions + EasyOcrOptions + TableStructureOptions -----")
            if is_MacOS:
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

            # Export Markdown format:
            with open("./outputs/ocr_out.md", "w", encoding="utf-8") as fp:
                fp.write(conv_res.document.export_to_markdown())
            
            # Save page images
            for page_no, page in conv_res.document.pages.items():
                print(f"Get image:{page_no}")
                page_no = page.page_no
                page_image_filename = Path(f"./outputs/ocr-{page_no}.png")
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")

            # Save images of figures and tables
            table_counter = 0
            picture_counter = 0
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    table_counter += 1
                    print(f"Get table:{table_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-table-{table_counter}.png"
                        Path(f"./outputs/ocr-table-{table_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

                if isinstance(element, PictureItem):
                    picture_counter += 1
                    print(f"Get picture:{picture_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-picture-{picture_counter}.png"
                        Path(f"./outputs/ocr-picture-{picture_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

            # Save markdown without pictures
            md_filename = Path(f"./outputs/ocr-out-without-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.PLACEHOLDER)

            # Save markdown with embedded pictures
            #md_filename = output_dir / f"{doc_filename}-with-images.md"
            md_filename = Path(f"./outputs/ocr-out-with-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

            # Save markdown with externally referenced pictures
            md_filename = Path(f"./outputs/ocr-out-with-images-refs.md")
            #md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

            # Save HTML with externally referenced pictures
            #html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
            html_filename = Path(f"./outputs/ocr-out-with-images-refs.html")
            conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

            end_time = time.time() - start_time
            print(f"Document converted and figures exported in {end_time:.2f} seconds.")

        case 3:
            target_url = test_url_list[test_url_index]
            pdf_temp = "./outputs/crawl4ai_temp.pdf"
            print("----- DocumentConverter + Crawl4AI -----")
            
            ##### Crawl4AI #####
            browser_conf = BrowserConfig(headless=True)  # or False to see the browser
            # The customized output depends on whether you specify a markdown generator or content filter.
            md_generator = DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.3, threshold_type="fixed")
            )
            run_conf = CrawlerRunConfig(
                cache_mode = CacheMode.BYPASS,
                markdown_generator = md_generator,
                pdf = True  # Instructs Playwright to capture the full page as a PDF
            )

            # Run the asynchronous web crawler
            start_time = time.time()
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                result = await crawler.arun(url=target_url, config=run_conf)
                
                # 3. Check for success and save the binary data
                if result.success and result.pdf:
                    with open(pdf_temp, "wb") as f:
                        f.write(result.pdf)
                    print(f"Successfully converted and saved: {pdf_temp}")
                else:
                    print(f"Failed to generate PDF. Error: {result.error_message}")
            end_time = time.time() - start_time
            print(f"Web crawlered and PDF converted in {end_time:.2f} seconds.")
            
            ##### Docling #####
            # Docling Parse Pipeline with EasyOCR (CPU only)
            if is_MacOS:
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

            # Export Markdown format:
            with open("./outputs/url_ocr_out.md", "w", encoding="utf-8") as fp:
                fp.write(conv_res.document.export_to_markdown())
            
            # Save page images
            for page_no, page in conv_res.document.pages.items():
                print(f"Get image:{page_no}")
                page_no = page.page_no
                page_image_filename = Path(f"./outputs/url_ocr-{page_no}.png")
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")

            # Save images of figures and tables
            table_counter = 0
            picture_counter = 0
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    table_counter += 1
                    print(f"Get table:{table_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-table-{table_counter}.png"
                        Path(f"./outputs/url_ocr-table-{table_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

                if isinstance(element, PictureItem):
                    picture_counter += 1
                    print(f"Get picture:{picture_counter}")
                    element_image_filename = (
                        #output_dir / f"{doc_filename}-picture-{picture_counter}.png"
                        Path(f"./outputs/url_ocr-picture-{picture_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

            # Save markdown without pictures
            md_filename = Path(f"./outputs/url_ocr-out-without-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.PLACEHOLDER)

            # Save markdown with embedded pictures
            #md_filename = output_dir / f"{doc_filename}-with-images.md"
            md_filename = Path(f"./outputs/url_ocr-out-with-images.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

            # Save markdown with externally referenced pictures
            md_filename = Path(f"./outputs/url_ocr-out-with-images-refs.md")
            #md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

            # Save HTML with externally referenced pictures
            #html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
            html_filename = Path(f"./outputs/url_ocr-out-with-images-refs.html")
            conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

            end_time = time.time() - start_time
            print(f"Document converted and figures exported in {end_time:.2f} seconds.")

            ##### Clean up #####
            if os.path.exists(pdf_temp):
                os.remove(pdf_temp)
                print(f"File {pdf_temp} deleted successfully.")
            else:
                print(f"Error: File {pdf_temp} does not exist.")

        case 100:
            print("----- AI converter with Gemini -----")

        case 101: # No Good
            target_url = test_url_list[test_url_index]
            print("----- Basic DocumentConverter with HTMLFormatOption -----")
            if is_MacOS:
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
            conv_res = converter.convert(target_url)       
            print("Docling Technical Report:", len(conv_res.document.export_to_markdown()))
            with open(output_mdfile_docling, "w", encoding="utf-8") as f:
                f.write(conv_res.document.export_to_markdown()) # Access the generated markdown
            
            # Save page images
            for page_no, page in conv_res.document.pages.items():
                print(f"Get image:{page_no}")
                page_no = page.page_no
                page_image_filename = Path(f"./outputs/url-{page_no}.png")
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")

            # Save images of figures and tables
            table_counter = 0
            picture_counter = 0
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    table_counter += 1
                    print(f"Get table:{table_counter}")
                    element_image_filename = (
                        Path(f"./outputs/url-table-{table_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")

                if isinstance(element, PictureItem):
                    picture_counter += 1
                    print(f"Get picture:{picture_counter}")
                    element_image_filename = (
                        Path(f"./outputs/url-picture-{picture_counter}.png")
                    )
                    with element_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")
        
        case _:
            print(f"Error: Unknown run_option ({run_option})!") # Wildcard (default case)
    
                
if __name__ == "__main__":
    asyncio.run(main())