"""
Verification Script
Checks project setup and runs a quick test
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    min_version = (3, 7)
    if version >= min_version:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} is too old (need 3.7+)")
        return False


def check_files_exist():
    """Check if all required files exist"""
    print("\nChecking project files...")
    required_files = [
        'main.py',
        'resume_parser.py',
        'resume_scorer.py',
        'requirements.txt',
        'README.md',
        'data/job_description.txt',
        'data/resumes'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                resume_count = len(list(path.glob('*.txt')))
                print(f"✓ {file_path}/ ({resume_count} resumes)")
            else:
                size = path.stat().st_size
                print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"✗ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def check_module_imports():
    """Check if core modules can be imported"""
    print("\nChecking module imports...")
    
    try:
        import resume_parser
        print("✓ resume_parser.py can be imported")
    except Exception as e:
        print(f"✗ resume_parser.py import error: {e}")
        return False
    
    try:
        import resume_scorer
        print("✓ resume_scorer.py can be imported")
    except Exception as e:
        print(f"✗ resume_scorer.py import error: {e}")
        return False
    
    return True


def check_dependencies():
    """Check optional dependencies"""
    print("\nChecking optional dependencies...")
    
    optional_deps = [
        ('PyPDF2', 'PDF resume support'),
        ('docx', 'DOCX resume support'),
        ('openai', 'OpenAI API support')
    ]
    
    for module_name, feature in optional_deps:
        try:
            __import__(module_name)
            print(f"✓ {module_name} installed ({feature})")
        except ImportError:
            print(f"⚠ {module_name} not installed (optional - for {feature})")


def test_resume_parsing():
    """Test resume parsing"""
    print("\nTesting resume parsing...")
    
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        
        # Test with sample resume
        sample_resume = Path('data/resumes/resume_01_john_anderson.txt')
        if not sample_resume.exists():
            print("⚠ Sample resume not found, skipping parsing test")
            return True
        
        resume_data = parser.parse_resume(str(sample_resume))
        
        if resume_data and 'name' in resume_data and 'skills' in resume_data:
            print(f"✓ Successfully parsed sample resume")
            print(f"  - Name: {resume_data['name']}")
            print(f"  - Skills found: {len(resume_data['skills'])}")
            return True
        else:
            print("✗ Resume parsing returned incomplete data")
            return False
    except Exception as e:
        print(f"✗ Resume parsing error: {e}")
        return False


def test_scoring():
    """Test scoring logic"""
    print("\nTesting scoring logic...")
    
    try:
        from resume_scorer import ResumeScorer
        scorer = ResumeScorer()
        
        # Create minimal test data
        job_desc = "Python JavaScript React AWS Docker Kubernetes PostgreSQL"
        resume = {
            'name': 'Test Candidate',
            'skills': ['Python', 'React', 'AWS'],
            'experience': 'Software engineer',
            'education': 'Computer Science',
            'raw_text': 'Python React AWS Docker'
        }
        
        score, reasoning = scorer.score_resume(job_desc, resume)
        
        if 0 <= score <= 100:
            print(f"✓ Scoring works correctly")
            print(f"  - Test score: {score:.2f}/100")
            return True
        else:
            print(f"✗ Invalid score: {score}")
            return False
    except Exception as e:
        print(f"✗ Scoring error: {e}")
        return False


def test_output_creation():
    """Test output directory creation"""
    print("\nTesting output directory creation...")
    
    try:
        from pathlib import Path
        test_output = Path('test_output_dir')
        
        if test_output.exists():
            import shutil
            shutil.rmtree(test_output)
        
        test_output.mkdir(parents=True, exist_ok=True)
        
        if test_output.exists() and test_output.is_dir():
            print(f"✓ Output directory created successfully")
            import shutil
            shutil.rmtree(test_output)
            return True
        else:
            print("✗ Failed to create output directory")
            return False
    except Exception as e:
        print(f"✗ Output directory error: {e}")
        return False


def main():
    """Run all verification checks"""
    print("="*60)
    print("Resume Screening Agent - Setup Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Project Files", check_files_exist()),
        ("Module Imports", check_module_imports()),
        ("Resume Parsing", test_resume_parsing()),
        ("Scoring Logic", test_scoring()),
        ("Output Creation", test_output_creation()),
    ]
    
    # Check optional dependencies
    check_dependencies()
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ Setup verification successful!")
        print("\nYou can now run:")
        print("  python main.py --jd data/job_description.txt --resumes data/resumes --output outputs")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
