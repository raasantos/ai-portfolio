# Week 7 — AI Engineering: Chapter 6 (RAG)

**Date:** June 30, 2026
**Chapter covered:** Chapter 6 — RAG section
**Recall score:** 6/10 → gaps closed in session

---

## 8 observations I made (not a summary, what caught my attention)

1. RAG is for context improvement in AI applications, but the use is only justified when the context is dynamic, domain-specific, or too large to fit in every prompt. Stuffing everything into every prompt is expensive and degrades quality because of lost-in-the-middle. RAG solves both problems — it retrieves only what matters for that query.

2. As a PM, I shouldn't think about which retrieval algorithm to implement. I should understand what each does well enough to choose the right one for the problem. That's a product decision, not a technical one. Embedding vs. term-based is the first choice. Hybrid is the production answer when you need both.

3. Term-based retrieval is lexical — it matches exact words. It works better for codes, sequences, and exact identifiers like error codes or product names. Embedding-based is semantic — it retrieves by meaning, not exact match. It works better when the user's words don't match the document's words but the intent does. Neither is sufficient alone in production.

4. Reciprocal Rank Fusion (RRF) is the algorithm that combines rankings from multiple retrievers. Documents that rank well across both retrievers float to the top. It's how hybrid search works in practice: term-based handles the exact match problem, embedding handles the semantic problem, and RRF merges the two ranked lists into one.

5. When deciding whether to build a RAG system, the business question is: what's the cost of a bad output vs. the cost of building and maintaining the system? This also means thinking about cost of opportunity — automating a workflow doesn't just save time, it can change the speed at which a business corrects its route. Sometimes velocity is the real outcome.

6. RAG won't fix bad data. Garbage in, garbage out. The system is only as good as what's indexed.

7. The harder question before building is: how do you know the data is the problem? The fast diagnostic is to give the same data to a human analyst and see what they produce. If a human can't generate a good answer with that data, the system won't either. That's your data quality gate before writing a single line of RAG code.

8. I've used RAG in practice — I built a PM Brain with all my project information indexed, and the outcome was spending less time updating documents and searching across scattered documentation. The maintenance cost was low: less than one hour per week to keep it current. That's a real unit economics case for RAG. The cost of the system was lower than the cost of manual search.

---

## Questions I had and how I closed them

**How does reranking work mechanically? How do documents get scored in different positions?**

Every retriever produces a relevance score for each document — BM25 score for term-based, cosine similarity for embedding-based. Those scores produce a ranked list. Reranking takes that list and runs a second, more expensive scoring model over only the top candidates. The first retriever casts a wide net cheaply. The reranker re-scores and reorders the top results with more precision. Classic pattern: BM25 retrieves top 100, reranker picks the best 10 from those 100. You get precision without paying the cost of running the expensive model over the full corpus.

**How do you even diagnose whether the data is the problem vs. the retrieval system?**

Most teams assume retrieval quality is the bottleneck when outputs are poor. Sometimes it is. But often the real problem is the behavioral or domain data doesn't exist yet — and no retrieval architecture fixes that. The fast test: give the same data a human analyst and evaluate what they produce. If the human can't generate a good answer with that data, the system won't either. This is the data quality gate. Run it before building.

---

## How this changes how I think about product and building

**Before:** I thought of RAG as a context amplifier — a technical component that makes AI applications smarter by giving them more information.

**After:** RAG is a product decision, not a technical default. The questions are: is the context dynamic enough to justify it? What's the data freshness requirement and what does re-indexing cost at that frequency? What retrieval approach fits the query type — lexical, semantic, or hybrid? What's the cost of a wrong output vs. the cost of building and maintaining the system? I won't implement RAG again without going through those questions first.

**Before:** I thought chunking was just splitting text into smaller pieces.

**After:** Chunking strategy is a design choice with real trade-offs. Small chunks give diversity but can cut context mid-sentence. Large chunks preserve context but reduce diversity and increase cost. Contextual retrieval — the Anthropic technique of prepending an AI-generated 50–100 token summary to each chunk before indexing — fixes the problem of isolated chunks losing their relationship to the original document. I wish I'd known this when I built the PM Brain. It would have improved retrieval quality significantly.

**Open question carrying forward:** Agents — how does the chapter frame the line between a fixed prompt decomposition chain and an agent? When does adding dynamic routing actually justify the added complexity and cost?

---

## Key concepts for interview readiness

1. **RAG (Retrieval-Augmented Generation):** a pattern for context construction — for each query, retrieve only the relevant context and inject it into the prompt. More efficient and more accurate than stuffing everything into every prompt.

2. **Term-based retrieval (lexical):** matches exact words. Best for codes, identifiers, and exact-match queries. TF-IDF scores by term frequency weighted against how common the term is across documents. BM25 improves on TF-IDF by normalizing for document length.

3. **Embedding-based retrieval (semantic):** converts query and documents into vectors using the same embedding model, then measures cosine similarity. Smaller angle between vectors means higher relevance. Best when the user's words don't match the document's words but the intent does. Weakness: specific identifiers like error codes get dissolved in the embedding space.

4. **Hybrid search + RRF:** combines term-based and embedding-based retrieval. Reciprocal Rank Fusion merges the two ranked lists — documents that score well in both float to the top. This is the production standard because neither retriever alone handles all query types well.

5. **Contextual retrieval:** before indexing, send each chunk plus the full original document to an AI model and generate 50–100 tokens explaining what the chunk is about. Prepend that context to the chunk before indexing. Prevents isolated chunks from losing their relationship to the original document.

6. **Context precision vs. context recall:** precision is the ratio of retrieved chunks that are actually relevant. Recall is the share of all relevant chunks in the corpus that were retrieved. Precision is easy to compute — you only need the retrieved set. Recall requires knowing the full set of relevant documents, which usually needs human-labeled ground truth.

7. **Text-to-SQL (RAG with tabular data):** natural language query → model identifies relevant table schema → generates SQL → executes against database → generates answer in natural language. The model needs schema context injected before query generation. Key failure mode: syntactically valid SQL that runs but answers the wrong question because the schema description was imprecise.