# Part IV Vectors, Retrieval, and Knowledge Engineering

## Goals of this part

Part IV explains how enterprise knowledge enters retrieval and reasoning systems. It starts with embedding models, then covers fine-tuning, reranking, vector databases, document parsing, RAG engineering, and knowledge engineering. The common thread is evidence: retrieved material must be permission-aware, citable, replayable, and governed through versions.

## Chapters in This Part

- [Chapter 16 Embedding Models](ch16.md) - BGE, E5, GTE, Conan, Qwen-Embedding, CLIP/SigLIP
- [Chapter 17 Embedding Fine-tuning and Re-ranking](ch17.md) - sentence-transformers, contrastive learning, hard negatives; bge-reranker, Cohere Rerank
- [Chapter 18 Vector Databases and Indexing Algorithms](ch18.md) - pgvector, Milvus, Qdrant, Weaviate, Chroma, Vespa; HNSW, IVF, PQ
- [Chapter 19 Document Parsing and Multimodal OCR](ch19-ocr.md) - unstructured, LlamaParse, PaddleOCR, Nougat, Marker, Donut, Qwen-VL
- [Chapter 20 RAG Engineering and Advanced Retrieval](ch20-rag.md) - chunking, hybrid retrieval, RRF, SPLADE, ColBERT, Parent-Child, Small-to-Big
- [Chapter 21 Knowledge Engineering: Ontologies, Extraction, and Knowledge Graphs](ch21.md) - NER/RE, LLM extraction, entity linking, OWL/RDF, Neo4j/NebulaGraph, GraphRAG

## Reading path

Read Chapters 16 to 18 before choosing embedding and vector infrastructure. Read Chapters 19 to 20 before building RAG on enterprise documents. Chapter 21 is most useful when questions depend on entities, relationships, impact chains, and cross-document synthesis.
