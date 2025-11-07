# Manual Labeling Guide (T018)

## Overview

For each paper, you need to identify:
1. **Expected techniques** - AI techniques explicitly mentioned
2. **Context type** - How the technique is discussed
3. **Confidence ranges** - Based on frequency and clarity of mentions
4. **Mention count** - Approximate number of times mentioned

## Step-by-Step Process

### 1. Read Each Paper

Scan through the paper and note every AI technique mentioned. Look for:
- Technique names in titles, abstracts, sections
- Aliases (e.g., "RLHF" = "Reinforcement Learning from Human Feedback")
- Related techniques (e.g., paper about RLHF may also mention "reward modeling")

### 2. Classify Context Type

For each technique, determine the primary context:

- **`research`** - Academic research, experiments, novel methods
  - Keywords: "we propose", "experiment", "study", "investigate", "paper"
  
- **`production`** - Real-world deployment, systems in use
  - Keywords: "production", "deployed", "live", "released", "system"
  
- **`tutorial`** - Educational, how-to, examples
  - Keywords: "tutorial", "guide", "how-to", "example", "introduction"
  
- **`criticism`** - Problems, limitations, failures
  - Keywords: "failed", "problem", "issue", "limitation", "challenge"
  
- **`general`** - Neutral mention, background, or unclear
  - Fallback when other categories don't clearly apply

### 3. Estimate Confidence Ranges

Based on how clearly and frequently the technique is mentioned:

**High Confidence (0.90-1.00)**:
- Primary topic of the paper
- Mentioned 5+ times
- Clear, unambiguous mentions
- Example: "RLHF" in an RLHF paper

**Medium Confidence (0.75-0.89)**:
- Secondary topic or related technique
- Mentioned 2-4 times
- Relatively clear mentions
- Example: "reward modeling" in an RLHF paper

**Lower Confidence (0.60-0.74)**:
- Tangential mention
- Mentioned 1-2 times
- May be ambiguous
- Example: "fine-tuning" mentioned briefly in context

### 4. Count Mentions

Do a rough count (or search) for how many times each technique appears:
- 1 mention = frequency_boost 1.0
- 2-4 mentions = frequency_boost 1.1
- 5+ mentions = frequency_boost 1.2

## Example: rlhf.txt

From reading the first 50 lines, I can identify:

```json
{
  "expected_techniques": [
    {
      "full_name": "Reinforcement Learning from Human Feedback",
      "min_confidence": 0.95,
      "max_confidence": 1.00,
      "expected_context_type": "research",
      "mention_count": 50
    },
    {
      "full_name": "Reward Modeling",
      "min_confidence": 0.85,
      "max_confidence": 0.95,
      "expected_context_type": "research",
      "mention_count": 15
    },
    {
      "full_name": "Instruction Tuning",
      "min_confidence": 0.80,
      "max_confidence": 0.90,
      "expected_context_type": "research",
      "mention_count": 8
    },
    {
      "full_name": "Direct Alignment",
      "min_confidence": 0.75,
      "max_confidence": 0.85,
      "expected_context_type": "research",
      "mention_count": 5
    }
  ]
}
```

**Rationale**:
- RLHF is the main topic (title, abstract, throughout) → 0.95-1.00
- Reward modeling is a core component of RLHF → 0.85-0.95
- Instruction tuning mentioned as related technique → 0.80-0.90
- Direct alignment mentioned as alternative approach → 0.75-0.85

## Tips

1. **Be conservative**: It's better to set wider ranges (e.g., 0.75-0.95) initially
2. **Focus on clear mentions**: If unsure whether something is a technique, skip it
3. **Check aliases**: Make sure technique names match taxonomy.json
4. **Document reasoning**: Add notes in metadata for ambiguous cases
5. **Character count**: Use `wc -c filename.txt` to get character count
6. **LaTeX check**: Search for `\begin`, `\cite`, `\ref` to set `contains_latex: true`

## Validation Checklist

For each paper in metadata.json, verify:
- [ ] `paper_id` is unique (paper_001 through paper_010)
- [ ] `file_path` matches actual filename
- [ ] `title` extracted from paper
- [ ] `character_count` is accurate
- [ ] `contains_latex` is correct
- [ ] At least 1 expected technique listed
- [ ] All confidence ranges are 0.0-1.0
- [ ] Context types are valid (research/production/tutorial/criticism/general)
- [ ] Mention counts are reasonable estimates

## Next Steps

After labeling all papers:
1. Update `metadata.json` with your findings
2. Run schema validation: 
   ```bash
   pip install jsonschema
   cd services/technique-extraction/tests/fixtures
   jsonschema -i metadata.json ../../specs/002-mvp-testing/contracts/sample-paper-schema.json
   ```
3. Run initial tests to verify fixtures work:
   ```bash
   cd services/technique-extraction
   pytest tests/test_pipeline.py::test_health_check -v
   ```

