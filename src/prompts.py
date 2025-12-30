from langchain_core.prompts import PromptTemplate

CODE_EXPERT_PROMPT = PromptTemplate(
    input_variables=["code", "context", "feedback"],
    template="""You are a Senior Python Engineer (Code Expert).
Your task is to analyze the following Python code and its context to understand its behavior, parameters, return values, and potential exceptions.

Context (related symbols):
{context}

Previous Feedback (if any):
{feedback}

Code to Analyze:
```python
{code}
```

Provide a detailed technical analysis including:
1. Summary of functionality.
2. Parameters (name, type, description).
3. Return value (type, description).
4. Exceptions raised.
5. Usage examples.

CRITICAL INSTRUCTIONS:
1. Be purely factual and structural.
2. DO NOT output internal monologue or "thinking".
3. Output ONLY the analysis.
/no_think
"""
)

DOCS_EXPERT_PROMPT = PromptTemplate(
    input_variables=["analysis"],
    template="""You are a Technical Writer.
Your task is to format the provided technical analysis into high-quality Markdown API documentation.

Technical Analysis:
{analysis}

Generate the Markdown documentation following this structure:
### `SymbolName`

**Summary**
...

**Parameters**
- `name` (type): description

**Returns**
- (type): description

**Raises**
- `Exception`: description

**Examples**
```python
...
```

**See also**
...

CRITICAL INSTRUCTIONS:
1. Output ONLY the Markdown content.
2. DO NOT output any "thinking" process, reasoning, or internal monologue.
3. DO NOT output any conversational text like "Here is the documentation".
4. DO NOT wrap the output in markdown code blocks (e.g. ```markdown ... ```). Just output the raw markdown.
/no_think
"""
)

DOCS_REVIEW_PROMPT = PromptTemplate(
    input_variables=["code", "current_docs", "usage_context"],
    template="""You are a Lead Software Architect (Documentation Reviewer).
Your task is to review the generated documentation for a specific code symbol and ensure it is complete, accurate, and safe.

Code:
```python
{code}
```

Generated Documentation:
{current_docs}

Usage Context (where this symbol is used in the codebase):
{usage_context}

Instructions:
1. Think step-by-step.
2. Check for missing parameters, return type mismatches, or missing exceptions.
3. **Verify side-effects**: Check if changes in this symbol might break the usages listed in 'Usage Context'.
4. If the documentation is accurate and complete, approve it.
5. If there are issues, promote specific feedback for the Code Expert to fix them.

Output must be a JSON object with the following structure:
{{
    "status": "APPROVED" or "REVISION_NEEDED",
    "reasoning": "Your step-by-step reasoning process...",
    "feedback": "Specific instructions for the Code Expert if revision is needed. Empty if APPROVED."
}}
"""
)
