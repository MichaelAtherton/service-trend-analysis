# Sample Academic Papers for MVP Testing

This directory contains 10 curated academic papers used for validating the AI Technique Extraction Service MVP.

## Required Papers

Each paper should be:
- Published 2023-2025 from arXiv
- 3-5 pages of text (or relevant sections extracted)
- English language only
- Contains clear AI technique mentions (not oblique references)
- Includes LaTeX formatting for preprocessing validation

### Paper List (Tasks T008-T017)

1. **paper_001_rag.txt** - Retrieval-Augmented Generation
   - Topic: RAG systems for knowledge-intensive NLP
   - Expected techniques: RAG, retrieval, transformer
   - Example: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
   - arXiv: https://arxiv.org/abs/2005.11401

2. **paper_002_rlhf.txt** - Reinforcement Learning from Human Feedback
   - Topic: RLHF for LLM alignment
   - Expected techniques: RLHF, reinforcement learning, reward modeling
   - Example: Papers on InstructGPT or similar RLHF approaches

3. **paper_003_finetuning.txt** - Fine-tuning / LoRA
   - Topic: Parameter-efficient fine-tuning methods
   - Expected techniques: LoRA, fine-tuning, adapter layers
   - Example: "LoRA: Low-Rank Adaptation of Large Language Models"

4. **paper_004_transformers.txt** - Transformer Architecture
   - Topic: Transformer models and attention mechanisms
   - Expected techniques: transformer, attention, self-attention
   - Example: "Attention Is All You Need" or derivative work

5. **paper_005_diffusion.txt** - Diffusion Models
   - Topic: Diffusion models for image generation
   - Expected techniques: diffusion models, denoising, latent diffusion
   - Example: "Denoising Diffusion Probabilistic Models" or Stable Diffusion papers

6. **paper_006_multimodal.txt** - Multi-modal AI
   - Topic: Multi-modal learning (vision + language)
   - Expected techniques: multi-modal, CLIP, vision-language
   - Example: CLIP, Flamingo, or similar multi-modal models

7. **paper_007_quantization.txt** - Model Compression / Quantization
   - Topic: Model compression and quantization techniques
   - Expected techniques: quantization, pruning, knowledge distillation
   - Example: Papers on 8-bit or 4-bit quantization methods

8. **paper_008_prompting.txt** - Prompt Engineering
   - Topic: Prompting strategies and in-context learning
   - Expected techniques: prompt engineering, few-shot learning, chain-of-thought
   - Example: Papers on CoT, few-shot prompting, or prompt design

9. **paper_009_evaluation.txt** - Evaluation Metrics
   - Topic: Evaluation methods for LLMs
   - Expected techniques: evaluation metrics, benchmarking, BLEU/ROUGE
   - Example: Papers on LLM evaluation frameworks or benchmark suites

10. **paper_010_agents.txt** - AI Agents / Tool Use
    - Topic: LLM agents with tool use
    - Expected techniques: AI agents, tool use, ReAct
    - Example: Papers on ReAct, Toolformer, or autonomous agents

## Curation Process (Task T018)

After collecting papers:
1. Extract relevant sections (abstract, introduction, methods, results)
2. Remove references section (test preprocessing)
3. Manually identify all AI techniques mentioned
4. Label context types for each mention (production/research/tutorial/criticism/general)
5. Estimate confidence ranges based on mention frequency and clarity
6. Document character count and LaTeX presence

## Metadata Schema

See `../contracts/sample-paper-schema.json` for the required metadata structure that will be created in `metadata.json` (Task T019).

## Status

- [ ] Paper 001 - RAG (T008)
- [ ] Paper 002 - RLHF (T009)
- [ ] Paper 003 - Fine-tuning (T010)
- [ ] Paper 004 - Transformers (T011)
- [ ] Paper 005 - Diffusion (T012)
- [ ] Paper 006 - Multi-modal (T013)
- [ ] Paper 007 - Quantization (T014)
- [ ] Paper 008 - Prompt Engineering (T015)
- [ ] Paper 009 - Evaluation (T016)
- [ ] Paper 010 - AI Agents (T017)

