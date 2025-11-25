import uuid
import PyPDF2
import asyncio
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup
from playwright import async_api
from jee_data_base.core.types import HtmlLike

class PdfEngine:
    def __init__(self,html):
        self.html = html
        self.parsed_html = BeautifulSoup(html,"html.parser")
        self.working_directory = tempfile.gettempdir()
        self.working_directory_path = Path(self.working_directory)

    def _get_individual_html(self,scoped_html_block)->HtmlLike:
        """
        Return a html block with styling and scoped_html_block as body
        :param:
        - style_theme : dark or white
        - scoped _html_block: selecte html block out of the whole original html
        scoping logic will be defined somewhere else
        """
        style = self.parsed_html.find("style")
        
        individual_html = rf"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>Questions</title>
    <script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
    {style}
    </head>

    <body>
    {scoped_html_block}
    </body>
    """
        return individual_html

    def _count_image(self,html_block)->int:
        html = BeautifulSoup(html_block,"html.parser")
        img_tags = html.find_all("img")
        return len(img_tags)

    def _get_summury_html(self)->HtmlLike:
        summury_html = self.parsed_html.find("div",class_="summary")
        return summury_html
    
    def _get_cluster_list(self)->list:
        cluster_list = self.parsed_html.find_all("section",class_="cluster")
        return [str(i) for i in cluster_list]
    
    def _get_question_block_list(self,html_block)->list:
        html = BeautifulSoup(html_block,"html.parser")
        question_block_list = html.find_all("div",class_="question-block")
        return [str(i) for i in question_block_list]
    
    def _get_chunk(self,lst:list,atmost_size:int)->list:
        """
        - Input: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
          Output: [[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15], [16,17]]
        """
        return [lst[i:i+atmost_size] for i in range(0, len(lst), atmost_size)]
    
    async def _process_clusters(self)->list:
        cluster_folder = self.working_directory_path/f"{uuid.uuid4()}"
        cluster_folder.mkdir()
        clusters = self._get_cluster_list()
        
        p =  await async_api.async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        
        pdf_list = []
        for cluster in clusters:
            questions = self._get_question_block_list(cluster)
            chunked_questions = self._get_chunk(questions,atmost_size=5)
            # print(len(chunked_questions))
        
            for chunk in chunked_questions:
        
                new_cluster_folder = cluster_folder/f"cluster-{clusters.index(cluster)}"
                new_cluster_folder.mkdir(exist_ok=True)
                html_block = ""
        
                for question in chunk:
                    html_block = f"{html_block}\n{question}"
                
                indivisual_html = self._get_individual_html(html_block)
                
                chunk_file_html = new_cluster_folder/f"chunk-{chunked_questions.index(chunk)}.html"
                file = open(chunk_file_html,"w",encoding="utf-8")
                file.write(indivisual_html)
                file.close()

                page = await browser.new_page()
                await page.goto(chunk_file_html.as_uri(),wait_until="networkidle")
                chunk_file_pdf = new_cluster_folder/f"chunk-{chunked_questions.index(chunk)}.pdf"
                await page.pdf(
                    format="A4",
                    path=str(chunk_file_pdf)
                )
                pdf_list.append(chunk_file_pdf)
                await page.close()
        await browser.close()

        return pdf_list
    
    async def render(self,output_path:str):
        pdf_list = await self._process_clusters()
        merger = PyPDF2.PdfMerger()
        for pdf in pdf_list:
            merger.append(pdf)
        merger.write(output_path)
        merger.close()