from pathlib import Path
from typing import Any, Dict

import yaml
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class LLMManager:
    def __init__(self):
        self.config = self._load_config()
        self._llm_cache = {}
        self._embedding_model = None

    def _load_config(self) -> Dict[str, Any]:
        config_path = Path("config/llm_config.yaml")
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def get_llm(self, task_type: str) -> ChatOpenAI:
        """Get the most appropriate LLM for a given task type"""
        for model_name, model_config in self.config["models"].items():
            if task_type in model_config.get("use_for", []):
                if model_name not in self._llm_cache:
                    self._llm_cache[model_name] = ChatOpenAI(
                        model=model_config["name"],
                        temperature=model_config.get("temperature", 0),
                        max_tokens=model_config.get("max_tokens"),
                    )
                return self._llm_cache[model_name]
        raise ValueError(f"No suitable model found for task type: {task_type}")

    def get_embedding_model(self) -> OpenAIEmbeddings:
        """Get the embedding model"""
        if not self._embedding_model:
            self._embedding_model = OpenAIEmbeddings()
        return self._embedding_model
