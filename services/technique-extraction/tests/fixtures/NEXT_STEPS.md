# Next Steps: Complete Manual Labeling (T018)

## ✅ What's Done

- ✅ 10 papers curated (T008-T017)
- ✅ Test infrastructure complete (conftest.py, utilities, assertions)
- ✅ All 51 test functions implemented
- ✅ metadata.json initialized with your actual filenames
- ✅ Labeling guide created (LABELING_GUIDE.md)

## 🎯 What You Need to Do (T018)

Complete the manual labeling by updating `metadata.json` for each paper.

### Quick Process (Per Paper)

1. **Extract title** - Find the paper title and update `"title"` field
2. **Get character count** - Run: `wc -c "papers/FILENAME.txt"`
3. **Check for LaTeX** - Search for `\begin`, `\cite`, `\ref` and set `contains_latex`
4. **Identify techniques** - Read the paper and list all AI techniques mentioned
5. **Estimate confidence** - Based on frequency and clarity (see LABELING_GUIDE.md)
6. **Classify context** - research/production/tutorial/criticism/general
7. **Count mentions** - Rough count or search

### Example Template

```json
{
  "paper_id": "paper_001",
  "file_path": "papers/rlhf.txt",
  "title": "Reinforcement Learning from Human Feedback",
  "source_type": "academic",
  "character_count": 287934,
  "contains_latex": true,
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
    }
  ],
  "notes": "Primary RLHF paper with comprehensive coverage"
}
```

## 🚨 Priority Issues

### Papers 9 & 10 Need Verification

Your papers `2016 IJRM Hanssens Fang Zhang.txt` and `2017 AMA HWZ.txt` may not be AI-related:
- IJRM = International Journal of Research in Marketing
- AMA = American Marketing Association

**Action**: Check if these papers contain AI techniques. If not, replace them with:
- AI Agents paper (ReAct, Toolformer, or similar)
- RAG paper (Retrieval-Augmented Generation)

## ⚡ Quick Commands

### Get character counts for all papers:
```bash
cd tests/fixtures/papers
for file in *.txt; do
  if [ "$file" != "README.md" ]; then
    echo "$file: $(wc -c < "$file") characters"
  fi
done
```

### Check for LaTeX in a paper:
```bash
grep -q '\\begin\|\\cite\|\\ref' "papers/rlhf.txt" && echo "Has LaTeX" || echo "No LaTeX"
```

### Extract paper title (first non-empty line):
```bash
head -20 "papers/rlhf.txt" | grep -v '^$' | head -1
```

## 📋 Completion Checklist

Once you've labeled all papers, verify:

- [ ] All 10 papers have actual titles (no `[TODO: ...]`)
- [ ] All `character_count` fields are filled with actual counts
- [ ] All `contains_latex` fields are set correctly
- [ ] All papers have at least 1 expected technique
- [ ] All technique names match entries in `src/data/taxonomy.json`
- [ ] All confidence ranges are between 0.0 and 1.0
- [ ] All context types are valid (research/production/tutorial/criticism/general)
- [ ] Papers 009 and 010 are AI-related (or replaced)

## ✅ Validate metadata.json (T020)

After completing labeling:

```bash
# Install jsonschema if not already installed
pip install jsonschema

# Validate metadata
cd services/technique-extraction/tests/fixtures
jsonschema -i metadata.json ../../specs/002-mvp-testing/contracts/sample-paper-schema.json

# If validation passes, you'll see no output
# If validation fails, fix the errors and rerun
```

## 🧪 Test Your Work (T038)

After validation passes:

1. **Start the extraction service**:
   ```bash
   cd services/technique-extraction
   uvicorn src.main:app --reload
   ```

2. **Run health check test**:
   ```bash
   pytest tests/test_pipeline.py::test_health_check -v
   ```

3. **Run full pipeline tests**:
   ```bash
   pytest tests/test_pipeline.py -v
   ```

4. **Generate HTML report**:
   ```bash
   pytest tests/ --html=test-reports/report.html --self-contained-html
   open test-reports/report.html
   ```

## 📊 Expected Timeline

- **Labeling**: 2-3 hours (all 10 papers)
- **Character counts**: 5 minutes
- **LaTeX checking**: 5 minutes
- **Validation**: 1 minute
- **First test run**: 5-10 minutes

Total: **~3-4 hours** to complete T018 and run first tests

## 💡 Tips

1. **Start with easy papers**: Do RLHF and Diffusion Models first (obvious techniques)
2. **Use paper abstracts**: Often lists all key techniques mentioned
3. **Search for technique names**: Use Ctrl+F to count mentions
4. **Be consistent**: Use exact names from taxonomy.json
5. **Take breaks**: Labeling requires concentration

## 🆘 If You Get Stuck

**Schema validation errors**:
- Check that all required fields are present
- Verify confidence values are 0.0-1.0
- Ensure JSON syntax is valid (commas, brackets)

**Can't find technique name**:
- Check `services/technique-extraction/src/data/taxonomy.json`
- Use the full_name, not aliases
- If technique not in taxonomy, use generic name

**Unsure about confidence**:
- Use wider ranges when uncertain (e.g., 0.70-0.95)
- Tests allow ±0.05 tolerance for BERTrend variation

## 📁 Files to Edit

- **Primary**: `tests/fixtures/metadata.json` (update all 10 papers)
- **Optional**: Add notes to paper entries for context

## 🎉 Success Criteria

When done, you should have:
- ✅ Complete metadata.json with all 10 papers labeled
- ✅ Schema validation passes
- ✅ All tests can load fixtures without errors
- ✅ Ready to run full MVP test suite

---

**Current Status**: 📍 **YOU ARE HERE** → Complete T018 manual labeling

**Next Milestone**: First successful test run (T038)

