# Part II Models and Inference Layer

This part no longer enforces a uniform three-layer chapter template. Instead, it follows the actual decision chain of the models and inference layer: first answering "Which model to choose," then "How to serve locally," followed by "How to optimize inference cost and latency," "How to enable system-consumable model outputs," and finally, "How to customize capabilities and integrate enterprise knowledge." Each chapter retains objectives, key topics, charts, interface contracts, engineering implementation, and launch checks, but the chapter structure is tailored to the content itself.

## Chapters in This Part

| Chapter | Questions Addressed | Key Figures/Charts |
|---|---|---|
| [Chapter 5 Model Selection for Large Models](ch05.md) | Which model to choose and how to make model selection measurable, routable, and reversible | Model matrix, Quality-Cost-Latency triangle |
| [Chapter 6 Local Inference Engine](ch06.md) | How to serve open-weight models locally and trade off throughput vs. latency | Boundaries of local inference service, Throughput vs. latency curves |
| [Chapter 7 Inference Optimization](ch07.md) | How to identify inference bottlenecks and choose KV Cache, Prefix Cache, speculative decoding, or quantization | Optimization effect locations, KV Cache VRAM growth |
| [Chapter 8 Structured Output and Prompt Engineering](ch08.md) | How to make model output a verifiable, auditable, and recoverable system contract | Four-layer contract, verification and recovery closed-loop |
| [Chapter 9 Model Capability Customization and Knowledge Augmentation](ch09.md) | When to use Prompting, RAG, fine-tuning, or alignment; how to govern version releases | Customization routes, training and release closed-loop |
