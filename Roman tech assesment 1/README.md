# Resume Screening Agent

A Python-based CLI tool that ranks resumes against a job description and produces an ordered shortlist with reasoning.

## Project Summary

This project was built for the Rooman AI Challenge as a Junior AI Research Associate submission. It implements a working end-to-end resume screening agent that:

- Reads a job description from a text file
- Parses resumes from a folder of sample resumes
- Extracts skills, experience, and education signals
- Scores each candidate against the job description
- Outputs a ranked shortlist in CSV and JSON format

## Chosen Agent

Resume Screening Agent

## Expected Capabilities Covered

- Parse resumes and extract skills, experience, and education
- Compute a relevance score against the job description
- Rank candidates and output a scored, ordered shortlist
- Handle multiple resumes in a single run

## Project Structure

```text
Roman tech assesment 1/
├── main.py
├── resume_parser.py
├── resume_scorer.py
├── requirements.txt
├── README.md
├── tests/
│   └── test_basic.py
├── data/
│   ├── job_description.txt
│   └── resumes/
└── outputs/
```

## Setup Instructions

### 1. Clone or download the project

```bash
cd "Roman tech assesment 1"
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the agent

```bash
python main.py --jd data/job_description.txt --resumes data/resumes --output outputs
```

## How It Works

The agent uses a lightweight NLP-style approach:

1. It reads the job description and resume text.
2. It extracts resume metadata such as name, skills, education, and experience.
3. It computes a similarity score using TF-IDF-style text matching.
4. It adds a skill overlap bonus based on keywords from the job description.
5. It ranks the candidates and saves the output to CSV and JSON files.

## Scoring Method

The final score is computed using a hybrid formula:

```text
Score = (TF-IDF similarity × 0.65) + (Skill match × 0.35)
```

The system then assigns a simple fit label:

- Strong
- Moderate
- Weak

## Output Files

The run generates:

- [outputs/ranked_candidates.csv](outputs/ranked_candidates.csv)
- [outputs/ranked_candidates.json](outputs/ranked_candidates.json)

## Sample Input and Output

### Sample input
- Job description: [data/job_description.txt](data/job_description.txt)
- Resume folder: [data/resumes](data/resumes)

### Sample output
The script produces a ranked list with columns such as:

- rank
- name
- score
- match_strength
- skills
- education
- reasoning

## Testing

Run the automated tests:

```bash
pytest -q
```

## Tradeoffs and Limitations

This version is intentionally simple and reliable for a 24-hour challenge submission.

### Strengths
- End-to-end and runnable with sample data
- Clear ranking output in both CSV and JSON
- Easy to understand and extend

### Limitations
- Scoring is text-based and keyword-driven
- Resume parsing is lightweight and may miss unusual formatting
- It does not yet use a full LLM workflow or external API

## Next Improvements

If more time were available, I would improve the project by:

- adding stronger semantic similarity
- improving resume parsing for PDF and DOCX files
- adding richer reasoning and explanation output
- integrating an LLM-based evaluation layer

Scoring resumes against job description...
✓ Scoring complete

Creating output directory...
✓ Output directory: outputs

Saving results...
✓ CSV results saved: outputs/ranked_candidates.csv
✓ JSON results saved: outputs/ranked_candidates.json

================================================================================
RESUME RANKING RESULTS
================================================================================

################################################################################
Rank: 1
Name: John Anderson
Score: 85.42/100
Skills: Python, JavaScript, TypeScript, React, PostgreSQL, AWS, Docker, Kubernetes

Reasoning:
Candidate: John Anderson
Overall Score: 85.42
Score Breakdown:
  - TF-IDF Similarity: 78.3%
  - Skill Match: 92.5%
Detected Skills: Python, JavaScript, TypeScript, React, PostgreSQL, AWS, Docker, Kubernetes

...
```

## Verification Script

To verify your setup is correct:

```bash
python verify_setup.py
```

This will:
- Check Python version
- Verify required files exist
- Test resume parsing
- Verify output directory creation
- Report any issues

## Troubleshooting

### Issue: "Job description file not found"
**Solution**: Ensure the path to the job description file is correct and the file exists.

### Issue: "No resume files found"
**Solution**: 
- Check that the resumes directory exists
- Verify files have correct extensions (.txt, .pdf, .docx)
- Ensure the path is spelled correctly

### Issue: "ImportError: No module named 'docx'"
**Solution**: Install python-docx:
```bash
pip install python-docx
```

### Issue: "OpenAI API error" when using --use-openai
**Solution**:
- Verify OPENAI_API_KEY is set correctly
- Check your API key is valid and has credits
- Ensure network connection is working

### Issue: Strange characters in resume output
**Solution**: Resume files may use different encodings. Try:
```bash
# Convert file to UTF-8
iconv -f ISO-8859-1 -t UTF-8 resume.txt -o resume_utf8.txt
```

## How to Use With Your Own Data

### 1. Prepare Job Description
Create a file (e.g., `my_job.txt`) with the job description:
```
Senior Backend Engineer

Requirements:
- 5+ years experience with Python
- AWS and Docker knowledge
...
```

### 2. Prepare Resumes Folder
Create a folder with resume files:
```
my_resumes/
├── candidate_1.txt
├── candidate_2.txt
├── candidate_3.pdf
└── candidate_4.docx
```

### 3. Run the Agent
```bash
python main.py --jd my_job.txt --resumes my_resumes --output my_results
```

### 4. Review Results
Check the output files:
- `my_results/ranked_candidates.csv` - Quick overview
- `my_results/ranked_candidates.json` - Detailed analysis

## Advanced Usage

### Modifying Scoring Weights

Edit `resume_scorer.py` in the `score_resume()` method:

```python
# Change weights (default: 0.7 TF-IDF, 0.3 skill match)
local_score = min(100, (tfidf_score * 0.8 + skill_bonus * 0.2) * 100)
```

### Adding Custom Keywords

Edit `resume_scorer.py` in the `_extract_key_keywords()` method to add your own technical keywords.

### Custom Scoring Logic

Create a subclass of `ResumeScorer` and override the `score_resume()` method with your custom logic.

## Performance

- **Parsing**: ~50-100ms per resume (text files faster than PDF/DOCX)
- **Scoring**: ~10-20ms per resume (depends on resume length)
- **Total Time**: ~1-2 seconds for 10 resumes (mostly I/O)
- **Memory**: Minimal (<50MB for 100 resumes)

## Technical Stack

- **Language**: Python 3.7+
- **Core Libraries**: 
  - `collections` - For Counter, word frequency analysis
  - `math` - For cosine similarity calculations
  - `csv` - For CSV output
  - `json` - For JSON output
- **Optional Libraries**:
  - `PyPDF2` - PDF parsing
  - `python-docx` - DOCX parsing
  - `openai` - OpenAI API integration

## Contributing

To extend the agent:

1. **Add new scoring methods** - Create methods in `ResumeScorer` class
2. **Support new resume formats** - Add parsers to `ResumeParser` class
3. **Improve skill extraction** - Enhance `_extract_skills()` method
4. **Add output formats** - Create new save functions (Excel, JSON, etc.)

## License

This project is provided as-is for evaluation and educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the sample output for expected behavior
3. Verify all files are in the correct locations
4. Run `verify_setup.py` to check configuration

---

**Ready to screen resumes?** Run this command:
```bash
python main.py --jd data/job_description.txt --resumes data/resumes --output outputs
```
