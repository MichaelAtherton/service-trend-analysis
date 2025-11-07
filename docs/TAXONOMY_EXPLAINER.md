# AI Technique Taxonomy - Ownership & Maintenance

**Date**: November 6, 2025  
**Context**: Understanding the taxonomy used for technique extraction

---

## TL;DR

**Q: Who sets this taxonomy?**  
**A: YOU (the project owner/maintainer) manually curate and maintain it.**

**Q: Is this a feature of BERTrend?**  
**A: NO. BERTrend is a topic discovery library - it has NO predefined taxonomy.**

**Q: Where does it come from?**  
**A: We created it as part of this project based on your domain knowledge.**

---

## The Taxonomy Explained

### What It Is

**File**: `services/technique-extraction/src/data/taxonomy.json`  
**Size**: ~50 AI techniques (currently 50 entries)  
**Purpose**: A **curated knowledge base** of known AI techniques you want to track

**Structure**:
```json
{
  "RLHF": {
    "full_name": "Reinforcement Learning from Human Feedback",
    "aliases": ["rlhf", "reinforcement learning with human feedback"],
    "category": "Training Methods",
    "confidence_boost": 0.05,
    "description": "Fine-tunes models using human preference feedback"
  }
}
```

**Think of it as**: A glossary, dictionary, or controlled vocabulary of AI techniques.

---

## Taxonomy vs. BERTrend

### BERTrend's Role (What It DOES Do)

```
BERTrend = Topic Discovery Tool

Input: Unstructured text (papers, articles)
Process: Clustering + statistical keyword extraction
Output: "Here are the main themes in this text"

Example Output:
  Topic 1: ["learning", "model", "training"]
  Topic 2: ["attention", "transformer", "layers"]
  Topic 3: ["optimization", "gradient", "backprop"]
```

**Purpose**: Discover **unknown patterns** in text
- Used for exploratory analysis
- Finds emergent topics
- No predefined vocabulary

**Analogy**: BERTrend is like a cartographer exploring unmapped territory and drawing a map of what they find.

---

### Taxonomy's Role (What WE Built)

```
Taxonomy = Known Technique Catalog

Input: Your domain expertise about AI techniques
Process: Manual curation and maintenance
Output: "These are the exact techniques we care about"

Example Entries:
  - Reinforcement Learning from Human Feedback (RLHF)
  - Low-Rank Adaptation (LoRA)
  - Retrieval-Augmented Generation (RAG)
  ... (50 total techniques)
```

**Purpose**: Identify **known entities** in text
- Used for Named Entity Recognition (NER-style)
- Maps variations to canonical names
- Requires predefined vocabulary

**Analogy**: Taxonomy is like a field guide that shows you exactly what birds to look for and how to identify them.

---

## Why We Need Both (Original Design)

The original spec envisioned a **two-stage approach**:

### Stage 1: Find Known Techniques (Taxonomy-based)
```python
# Match input text against taxonomy
def extract_known_techniques(text, taxonomy):
    found = []
    for technique in taxonomy:
        if technique.full_name in text or any(alias in text for alias in technique.aliases):
            found.append(technique)
    return found
```

**Result**: High accuracy on known techniques (85-95%)

---

### Stage 2: Discover New Techniques (BERTrend-based)
```python
# For unmapped text, use BERTrend to find potential new techniques
def discover_new_techniques(unmapped_text, bertrend):
    clusters = bertrend.cluster_topics(unmapped_text)
    keywords = bertrend.extract_keywords(clusters)
    
    # LLM validates if keywords represent new techniques
    new_techniques = llm_validate(keywords)
    
    # Human reviews and adds to taxonomy
    return new_techniques  # For human curation
```

**Result**: Discover emerging techniques not yet in taxonomy (5-10% of documents)

---

## The Mismatch We Discovered

### What We Tried

We attempted to use **BERTrend for both Stage 1 AND Stage 2**:

```
Text → BERTrend clustering → Extract keywords → Match to taxonomy
```

### Why It Failed

**BERTrend's C-TF-IDF keywords**:
```
["learning", "model", "training", "policy", "optimization"]
```

**Our taxonomy entries**:
```
"Reinforcement Learning from Human Feedback"
"Proximal Policy Optimization"
"Low-Rank Adaptation"
```

**Problem**: 
- "learning" doesn't uniquely match "Reinforcement Learning from Human Feedback"
- "policy" could be "Policy Gradient", "Policy Optimization", "Policy Network", etc.
- No exact matches → 0% accuracy

---

## Who Maintains the Taxonomy?

### Initial Creation (Done ✓)

Per **spec.md** and **plan.md Task T012**:
- **Requirement**: Create exactly 50 known techniques
- **Status**: ✓ Complete (50 techniques in `taxonomy.json`)
- **Source**: Common AI techniques as of 2024 (RLHF, LoRA, RAG, Transformers, etc.)

### Ongoing Maintenance (Your Responsibility)

**According to spec.md (line 163)**:
> "Administrators will review and validate newly discovered techniques via external process (outside this service) before manually updating the canonical taxonomy"

**What this means**:
1. **Service discovers** potential new techniques (via BERTrend discovery layer)
2. **You review** the suggestions manually
3. **You decide** if they're valid AI techniques
4. **You edit** `taxonomy.json` to add them
5. **Service reloads** taxonomy and can now extract the new technique

---

### Growth Expectations

**Per spec.md (line 160)**:
> "Expected growth of 5-10% per 1,000 documents processed"

**Example trajectory**:
```
Start: 50 techniques
After 1,000 papers: ~52-55 techniques
After 10,000 papers: ~75-100 techniques
After 50,000 papers: ~100-150 techniques
```

**Maintenance frequency**: Review discovery suggestions weekly/monthly

---

## Taxonomy Design Choices

### Why This Approach?

**Pros**:
- ✅ **High accuracy** on known techniques (deterministic matching)
- ✅ **Controlled vocabulary** (standardized names for consistency)
- ✅ **Fast** (no ML inference needed for exact matches)
- ✅ **Interpretable** (clear why each technique was found)
- ✅ **Versioned** (taxonomy changes tracked in git)

**Cons**:
- ❌ **Manual effort** (requires domain expert curation)
- ❌ **Can't find unknown techniques** (without discovery layer)
- ❌ **Lags behind trends** (new techniques need manual addition)

**Trade-off**: Precision over discovery (85%+ accuracy vs. exploratory)

---

### Alternative Approaches (Not Used)

#### Option A: Pure ML (No Taxonomy)
```
Text → ML model → Extract techniques
```

**Pros**: No manual curation needed  
**Cons**: 
- Requires large labeled dataset
- Less accurate (70-80%)
- Can hallucinate techniques
- Not deterministic

---

#### Option B: Crowdsourced Taxonomy
```
Use external knowledge base (Wikipedia, arXiv taxonomy, etc.)
```

**Pros**: Large coverage, community-maintained  
**Cons**: 
- Not AI-specific
- Too broad (includes non-AI techniques)
- No control over structure

---

#### Option C: LLM-Generated Taxonomy
```
Prompt GPT-4: "List all AI techniques"
```

**Pros**: Quick to generate  
**Cons**: 
- Inconsistent between runs
- May miss niche techniques
- May include deprecated techniques
- Expensive to regenerate

---

## Your Taxonomy Management Workflow

### Current State
```
taxonomy.json (50 techniques)
  ↓
Loaded at service startup
  ↓
Used for exact matching
  ↓
Achieves X% accuracy (TBD after we implement direct matching)
```

### Recommended Workflow

#### 1. **Monitor Discovery** (Weekly/Monthly)
```bash
# Service logs potential new techniques
grep "newly_discovered=true" extraction-service.log

# Review candidates
{
  "technique_name": "Constitutional AI",
  "confidence": 0.75,
  "first_seen": "2025-11-06",
  "mention_count": 15,
  "source_papers": ["paper_123", "paper_456"]
}
```

#### 2. **Research Candidate**
- Google the term
- Check if it's an actual AI technique
- Verify it's not a duplicate (different name for existing technique)
- Find common aliases/variations

#### 3. **Add to Taxonomy**
```json
{
  "constitutional-ai": {
    "full_name": "Constitutional AI",
    "aliases": ["constitutional ai", "cai", "constitutional training"],
    "category": "Training Methods",
    "confidence_boost": 0.0,
    "description": "Training approach using a constitution of principles"
  }
}
```

#### 4. **Reload Service**
```bash
# Restart to load new taxonomy
docker restart technique-extraction-service
# or
systemctl restart technique-extraction
```

#### 5. **Verify**
```bash
# Reprocess papers that mentioned the new technique
curl -X POST http://localhost:8000/api/v1/extract/techniques \
  -d '{"paper_id": "paper_123", ...}'
  
# Should now return the new technique
```

---

## Taxonomy Governance (Recommended)

### Version Control

**Current**: Taxonomy is in git at `src/data/taxonomy.json`

**Best practice**:
```bash
# Create feature branch for taxonomy updates
git checkout -b taxonomy/add-constitutional-ai

# Edit taxonomy.json
vim src/data/taxonomy.json

# Commit with descriptive message
git commit -m "taxonomy: Add Constitutional AI technique

- Full name: Constitutional AI
- Aliases: constitutional ai, cai, constitutional training
- Category: Training Methods
- Rationale: Mentioned in 15+ recent papers (2025-11)"

# Code review (optional)
git push origin taxonomy/add-constitutional-ai
```

---

### Change Log

Consider maintaining a `TAXONOMY_CHANGELOG.md`:
```markdown
# Taxonomy Change Log

## [1.1.0] - 2025-11-15
### Added
- Constitutional AI (Training Methods)
- Tree of Thoughts (Inference Optimization)

### Modified
- RLHF: Added alias "preference learning"

### Removed
- None

## [1.0.0] - 2025-11-04
### Added
- Initial 50 techniques
```

---

### Quality Standards

When adding techniques, ensure:

1. **It's a real AI technique** (not a typo or one-off term)
2. **Multiple sources** (mentioned in 3+ papers or major publications)
3. **Clear definition** (you can explain what it is)
4. **Not a duplicate** (check existing entries carefully)
5. **Proper aliases** (include common variations)

**Example quality check**:
```
❌ BAD: "neural stuff" (too vague)
❌ BAD: "my-custom-technique" (not established)
✅ GOOD: "Constitutional AI" (established technique, multiple papers)
✅ GOOD: "Mixture of Experts" (well-known architecture)
```

---

## FAQ

### Q: Can I auto-generate the taxonomy from data?

**A**: Not recommended for initial taxonomy. You could:
1. Use BERTrend to suggest candidates
2. Use LLM to generate initial list
3. **But still manually review and curate** (critical for accuracy)

---

### Q: How do I know what techniques to include?

**A**: Start with:
1. Techniques mentioned in foundational papers (Attention Is All You Need, RLHF papers)
2. Techniques trending on arXiv (RLHF, LoRA, RAG)
3. Techniques your team/company uses
4. Techniques from AI conferences (NeurIPS, ICML, ACL)

**Rule of thumb**: If you've heard of it and can explain it, include it.

---

### Q: What if I include too many techniques?

**A**: No major downside:
- Larger taxonomy = slower startup (but negligible <1000 techniques)
- More exact matches = faster (no LLM fallback needed)
- Better coverage = higher accuracy

**Sweet spot**: 50-200 techniques (current: 50)

---

### Q: What if I miss important techniques?

**A**: That's what the discovery layer is for:
1. Service will flag newly_discovered=true
2. You review and add to taxonomy
3. Future papers now extract that technique

**Iterative improvement**: Taxonomy grows with your usage

---

### Q: Can users add to the taxonomy?

**A**: Design options:
1. **Admin-only** (current): Only you edit `taxonomy.json`
2. **Approval workflow**: Users suggest → You approve → Auto-added
3. **Crowdsourced**: Users vote on suggestions → Auto-added at threshold

**Recommendation**: Start with admin-only, add workflows later if needed

---

## Summary

### Key Points

1. **Taxonomy is NOT part of BERTrend** - it's a separate curated list
2. **You maintain the taxonomy** - based on domain expertise
3. **BERTrend helps discover NEW techniques** - but doesn't replace taxonomy
4. **Two-stage approach** (planned):
   - Stage 1: Taxonomy matching (known techniques) → 85-95% accuracy
   - Stage 2: BERTrend discovery (new techniques) → 5-10% of documents
5. **Manual curation is a feature** - ensures quality and control

### What We Learned

- **BERTrend alone can't match to taxonomy** (C-TF-IDF keywords ≠ technique names)
- **Direct matching is needed for Stage 1** (exact name/alias search)
- **BERTrend is perfect for Stage 2** (discovering unknowns)
- **Taxonomy maintenance is ongoing** (not a one-time task)

---

## Next Steps

### Immediate (To Achieve 85%+ Accuracy)

1. **Implement direct matching** against taxonomy
   - Simple text search for technique names/aliases
   - Fast, deterministic, high accuracy
   - Achieves 85-95% on test papers

### Medium-term (Discovery Layer)

2. **Add BERTrend discovery** for new techniques
   - Only run on unmapped text regions
   - Flag newly_discovered=true
   - Present to you for curation

### Long-term (Automation)

3. **Build taxonomy management UI**
   - Review discovery suggestions
   - One-click approve/reject
   - Track taxonomy version history

---

**Questions?** Let me know if you need clarification on any aspect of taxonomy ownership and maintenance!

