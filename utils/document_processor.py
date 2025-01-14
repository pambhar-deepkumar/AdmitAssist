from types import Any, Dict

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from llm_manager import LLMManager


class DocumentProcessor:
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.embedding_model = llm_manager.get_embedding_model()

    def process_documents(self, documents: Dict[str, Any]):
        processed_docs = {}

        for doc_type, document in documents.items():
            # Use cheaper model for initial processing
            llm = self.llm_manager.get_llm("data_extraction")

            processed_docs[doc_type] = self._process_single_document(
                document, doc_type, llm
            )

        return processed_docs

    def _process_single_document(self, document, doc_type, llm):
        prompt = PromptTemplate(
            template="""
            Extract key information from this {doc_type}.
            Focus on relevant facts, figures, and important statements.

            Document content: {content}
            """,
            input_variables=["doc_type", "content"],
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run(doc_type=doc_type, content=self._extract_content(document))

    def _extract_content(self, document):
        # Implementation of content extraction based on document type
        pass
