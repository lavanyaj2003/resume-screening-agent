"""
Resume Screening Agent - Main CLI
Ranks resumes against a job description and outputs results
"""
import argparse
import json
import csv
import sys
from pathlib import Path
import os

from resume_parser import ResumeParser
from resume_scorer import ResumeScorer


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Candidate Fit Analyzer - Rank applicants against a role description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --jd data/job_description.txt --resumes data/resumes --output outputs
  python main.py --jd job.txt --resumes ./resumes --output ./results --use-openai
        """
    )
    
    parser.add_argument(
        '--jd',
        required=True,
        type=str,
        help='Path to job description file'
    )
    
    parser.add_argument(
        '--resumes',
        required=True,
        type=str,
        help='Path to folder containing resume files'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        type=str,
        help='Output directory for results (CSV and JSON)'
    )
    
    parser.add_argument(
        '--use-openai',
        action='store_true',
        help='Use OpenAI API for enhanced scoring (requires OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output'
    )
    
    return parser.parse_args()


def load_job_description(jd_path):
    """Load and read job description file"""
    try:
        with open(jd_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Job description file not found: {jd_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading job description: {e}")
        sys.exit(1)


def load_resumes(resumes_dir):
    """Load and parse all resume files from a directory"""
    resumes_path = Path(resumes_dir)
    
    if not resumes_path.exists():
        print(f"Error: Resumes directory not found: {resumes_dir}")
        sys.exit(1)
    
    parser = ResumeParser()
    resumes = []
    
    # Find all supported resume files
    supported_extensions = parser.supported_formats
    resume_files = []
    
    for ext in supported_extensions:
        resume_files.extend(resumes_path.glob(f'*{ext}'))
    
    if not resume_files:
        print(f"Error: No resume files found in {resumes_dir}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        sys.exit(1)
    
    print(f"Found {len(resume_files)} resume(s) to process")
    
    for resume_file in sorted(resume_files):
        try:
            resume_data = parser.parse_resume(str(resume_file))
            resumes.append(resume_data)
            print(f"  ✓ Parsed: {resume_file.name}")
        except Exception as e:
            print(f"  ✗ Error parsing {resume_file.name}: {e}")
    
    if not resumes:
        print("Error: No resumes were successfully parsed")
        sys.exit(1)
    
    return resumes


def create_output_directory(output_dir):
    """Create output directory if it doesn't exist"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def save_csv_results(ranked_resumes, output_path):
    """Save results to CSV file"""
    csv_file = output_path / 'ranked_candidates.csv'
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['rank', 'name', 'score', 'match_strength', 'skills', 'education', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for rank, resume in enumerate(ranked_resumes, 1):
            writer.writerow({
                'rank': rank,
                'name': resume['name'],
                'score': f"{resume['score']:.2f}",
                'match_strength': resume.get('fit_level', 'Moderate'),
                'skills': ', '.join(resume['skills'][:5]),
                'education': resume['education'][:100],
                'reasoning': resume['reasoning'].split('\n')[0]  # First line only
            })
    
    return csv_file


def save_json_results(ranked_resumes, output_path):
    """Save results to JSON file"""
    json_file = output_path / 'ranked_candidates.json'
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json_data = {
            'total_candidates': len(ranked_resumes),
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'candidates': [
                {
                    'rank': rank,
                    'name': resume['name'],
                    'score': round(resume['score'], 2),
                    'confidence': resume.get('confidence', round(resume['score'], 2)),
                    'fit_level': resume.get('fit_level', 'Moderate'),
                    'skills': resume['skills'],
                    'education': resume['education'][:200],
                    'experience': resume['experience'][:200],
                    'reasoning': resume['reasoning']
                }
                for rank, resume in enumerate(ranked_resumes, 1)
            ]
        }
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return json_file


def print_results(ranked_resumes):
    """Print ranking results to console"""
    print("\n" + "="*80)
    print("RESUME RANKING RESULTS")
    print("="*80)
    
    for rank, resume in enumerate(ranked_resumes, 1):
        print(f"\n{'#'*80}")
        print(f"Rank: {rank}")
        print(f"Name: {resume['name']}")
        print(f"Score: {resume['score']:.2f}/100")
        print(f"Skills: {', '.join(resume['skills'][:10])}")
        if len(resume['skills']) > 10:
            print(f"        +{len(resume['skills'])-10} more")
        print(f"\nReasoning:")
        print(resume['reasoning'])
    
    print("\n" + "="*80)
    print(f"Total candidates ranked: {len(ranked_resumes)}")
    print("="*80 + "\n")


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Validate OpenAI usage
    if args.use_openai and not os.getenv('OPENAI_API_KEY'):
        print("Warning: --use-openai flag used but OPENAI_API_KEY not set")
        print("Will use local scoring method instead\n")
    
    # Load job description
    print("Loading job description...")
    job_description = load_job_description(args.jd)
    print(f"✓ Job description loaded ({len(job_description)} characters)\n")
    
    # Load resumes
    print("Loading and parsing resumes...")
    resumes = load_resumes(args.resumes)
    print(f"✓ Successfully parsed {len(resumes)} resume(s)\n")
    
    # Score resumes
    print("Scoring resumes against job description...")
    scorer = ResumeScorer(use_openai=args.use_openai)
    ranked_resumes = scorer.rank_resumes(job_description, resumes)
    print("✓ Scoring complete\n")
    
    # Create output directory
    print("Creating output directory...")
    output_path = create_output_directory(args.output)
    print(f"✓ Output directory: {output_path}\n")
    
    # Save results
    print("Saving results...")
    csv_file = save_csv_results(ranked_resumes, output_path)
    print(f"✓ CSV results saved: {csv_file}")
    
    json_file = save_json_results(ranked_resumes, output_path)
    print(f"✓ JSON results saved: {json_file}\n")
    
    # Print to console
    print_results(ranked_resumes)
    
    print("✓ Candidate fit analysis complete!")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
