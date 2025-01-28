import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from docling.document_converter import DocumentConverter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field


class CourseContent(BaseModel):
    title: str = Field(description="Course title/name")
    credits: Optional[float] = Field(description="Number of credit points/ECTS")
    content: List[str] = Field(
        description="Main topics and content covered in the course"
    )
    hours_per_week: Optional[float] = Field(
        description="Contact hours per week (if specified)"
    )


def convert_pdf_documents(input_path: str, output_dir: str = "./output") -> bool:
    converter = DocumentConverter()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    def convert_single_pdf(pdf_path: str) -> bool:
        try:
            result = converter.convert(pdf_path)
            base_name = Path(pdf_path).stem
            md_path = Path(output_dir) / f"{base_name}.md"
            if md_path.exists():
                print(f"{md_path} already exists. Skipping conversion.")
                return True
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result.document.export_to_markdown())
            json_path = Path(output_dir) / f"{base_name}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result.document.export_to_dict(), f, indent=2)
            print(f"Successfully converted {pdf_path} to {md_path}")
            return True
        except Exception as e:
            print(f"Error converting {pdf_path}: {str(e)}")
            return False

    input_path = Path(input_path)
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return convert_single_pdf(str(input_path))
    elif input_path.is_dir():
        results = [
            convert_single_pdf(str(pdf_file)) for pdf_file in input_path.glob("*.pdf")
        ]
        return any(results)
    return False


class DocumentProcessor:
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_document(self, file_path: str) -> List[Document]:
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()

    def split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        return splitter.split_documents(documents)

    def process(self, file_path: str) -> List[Document]:
        documents = self.load_document(file_path)
        return self.split_documents(documents)


class CourseExtractor:
    def __init__(self, llm):
        self.llm = llm
        self.chain = self._create_extraction_chain()

    def _create_extraction_prompt(self):
        return """
        You are a specialized academic module content extractor. Your task is to analyze course documentation and extract structured information about each module while maintaining academic precision and terminology.

        A module is a self-contained unit of study with these essential components:
        - Unique module title and code
        - Defined credit points/ECTS value
        - Teaching components (lectures, exercises, etc.)
        - Learning objectives
        - Module contents
        - Assessment methods
        - Time commitment details
        - Prerequisites (if any)
        - Teaching language

        Format the output as a structured JSON object with the following fields:
            {{
                "title": "string",
                "credits": number or null,
                "hours_per_week": number or null,
                "content": ["string"]
            }}

        ## Extraction Guidelines
        1. Only extract explicitly stated information
        2. Preserve exact terminology and numbering
        3. Keep technical terms in original language
        4. Use null for missing information
        5. Extract complete lists of topics/objectives
        6. Include all examination modalities
        7. Maintain hierarchical structure of content

        ## Information to Ignore
        - General program descriptions
        - Administrative details


        Human: {text}

        Assistant: Based on the provided text, here is the extracted course information:
        """

    def _create_extraction_chain(self):
        prompt = ChatPromptTemplate.from_template(self._create_extraction_prompt())
        return prompt | self.llm.with_structured_output(CourseContent)

    def extract(self, text: str) -> Optional[CourseContent]:
        try:
            return self.chain.invoke({"text": text})
        except Exception as e:
            print(f"Extraction error: {e}")
            return None


class JsonHandler:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._initialize_file()

    def _initialize_file(self):
        if not self.file_path.exists():
            self._save_data({"courses": []})

    def _load_data(self) -> Dict[str, Any]:
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save_data(self, data: Dict[str, Any]):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_course(self, course_info: Dict[str, Any]):
        data = self._load_data()
        data["courses"].append(course_info)
        self._save_data(data)


class Config(BaseModel):
    input_file: str
    output_file: str
    chunk_size: int = 5000
    chunk_overlap: int = 500
    model_name: str = "gpt-4o-mini"
    temperature: float = 0


def main():
    config = Config(
        input_file=r"D:\GenAI\git\AdmitAssist\data\example_1\example_1_course_catalogue_LMU_BSc_Informatics.pdf",
        output_file="courses.json",
    )

    output_dir = Path(config.input_file).parent / "output"
    md_file = output_dir / f"{Path(config.input_file).stem}.md"

    if not md_file.exists():
        convert_pdf_documents(config.input_file, str(output_dir))

    doc_processor = DocumentProcessor(
        chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
    )

    json_handler = JsonHandler(config.output_file)

    llm = ChatOpenAI(model_name=config.model_name, temperature=config.temperature)
    extractor = CourseExtractor(llm)

    documents = doc_processor.process(str(md_file))
    print(len(documents))
    for id, doc in enumerate(documents):
        if id > 1:
            break

        try:
            course_info = extractor.extract(doc.page_content)

            if course_info:
                json_handler.add_course(course_info.model_dump())
        except Exception as e:
            print(f"Error processing chunk: {e}")


if __name__ == "__main__":
    main()
