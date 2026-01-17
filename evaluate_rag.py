import time
from typing import Any, Dict, List

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI

from src import config, rag_pipeline_w_git_diff, agentic_rag_pipeline, llm_pipeline


class MetricsCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.reset()

    def reset(self):
        self.llm_calls = 0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        self.llm_calls += 1

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.total_tokens += usage.get("total_tokens", 0)
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)
        else:
            print("Something went wrong when computing the token usage. Please try again.")


class APILLM_WithCallbacks(ChatOpenAI):
    def __init__(self, callback_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = [callback_handler]


def eval_llm_new(target_dir, llm, metrics):
    # --- LLM Pipeline (AST) ---
    print("\n[Evaluating] LLM Pipeline (AST)...")
    metrics.reset()
    start_time = time.time()
    try:
        llm_pipeline.evaluate_ast(target_dir, llm)
    except Exception as e:
        print(f"Error in LLM Pipeline (AST): {e}")
    end_time = time.time()

    with open("eval_llm_new.txt", "w", encoding="utf-8") as f:
        f.write(f"LLM Pipeline (AST)\n")
        f.write(f"Calls: {metrics.llm_calls}\n")
        f.write(f"Tokens: {metrics.total_tokens}\n")
        f.write(f"Time: {end_time - start_time:.2f} seconds\n")


def eval_rag_new(llm, metrics):
    # --- RAG Pipeline ---
    print("\n[Evaluating] RAG Pipeline (Git Diff)...")
    metrics.reset()
    start_time = time.time()
    try:
        rag_pipeline_w_git_diff.process_pipeline(llm, test_run=True)
    except Exception as e:
        print(f"Error in RAG Pipeline: {e}")
    end_time = time.time()

    with open("eval_rag_new.txt", "w", encoding="utf-8") as f:
        f.write(f"RAG Pipeline (Git Diff) New\n")
        f.write(f"Calls: {metrics.llm_calls}\n")
        f.write(f"Tokens: {metrics.total_tokens}\n")
        f.write(f"Time: {end_time - start_time:.2f} seconds\n")


def eval_rag_update(llm, metrics):
    # --- RAG Pipeline ---
    print("\n[Evaluating] RAG Pipeline (Git Diff)...")
    metrics.reset()
    start_time = time.time()
    try:
        rag_pipeline_w_git_diff.process_pipeline(llm, test_run=True)
    except Exception as e:
        print(f"Error in RAG Pipeline: {e}")
    end_time = time.time()

    with open("eval_rag_update.txt", "w", encoding="utf-8") as f:
        f.write(f"RAG Pipeline (Git Diff) Update\n")
        f.write(f"Calls: {metrics.llm_calls}\n")
        f.write(f"Tokens: {metrics.total_tokens}\n")
        f.write(f"Time: {end_time - start_time:.2f} seconds\n")


def eval_agentic_rag_new(llm, metrics):
    # --- Agentic RAG Pipeline ---
    print("\n[Evaluating] Agentic RAG Pipeline...")
    metrics.reset()
    start_time = time.time()
    try:
        agentic_rag_pipeline.process_pipeline(llm, test_run=True)
    except Exception as e:
        print(f"Error in Agentic RAG Pipeline: {e}")
    end_time = time.time()

    with open("eval_agentic_rag_new.txt", "w", encoding="utf-8") as f:
        f.write(f"Agentic RAG Pipeline New\n")
        f.write(f"Calls: {metrics.llm_calls}\n")
        f.write(f"Tokens: {metrics.total_tokens}\n")
        f.write(f"Time: {end_time - start_time:.2f} seconds\n")


def eval_agentic_rag_update(llm, metrics):
    # --- Agentic RAG Pipeline ---
    print("\n[Evaluating] Agentic RAG Pipeline...")
    metrics.reset()
    start_time = time.time()
    try:
        agentic_rag_pipeline.process_pipeline(llm, test_run=True)
    except Exception as e:
        print(f"Error in Agentic RAG Pipeline: {e}")
    end_time = time.time()

    with open("eval_agentic_rag_update.txt", "w", encoding="utf-8") as f:
        f.write(f"Agentic RAG Pipeline Update\n")
        f.write(f"Calls: {metrics.llm_calls}\n")
        f.write(f"Tokens: {metrics.total_tokens}\n")
        f.write(f"Time: {end_time - start_time:.2f} seconds\n")


if __name__ == "__main__":
    # 1. Setup LLM and Callback override
    metrics = MetricsCallbackHandler()

    # Re-create LLM with our callback
    # We use the config from src/config.py
    llm = APILLM_WithCallbacks(
        callback_handler=metrics,
        base_url=config.LLM_API_BASE,
        api_key=config.LLM_API_KEY,
        model_name=config.LLM_MODEL_NAME,
        temperature=0
    )

    target_dir = "./sample_project"

    # eval_llm_new(target_dir, llm, metrics)
    # eval_rag_new(llm, metrics)
    # eval_rag_update(llm, metrics)
    # eval_agentic_rag_new(llm, metrics)
    eval_agentic_rag_update(llm, metrics)
