import json
import argparse
import logging
from pathlib import Path

def setup_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def analyze_github_issues(filepath, min_comments=0, copy=False):
    try:
        logging.info(f"Reading file: {filepath}")
        with open(filepath, 'r') as file:
            data = json.load(file)
        
        logging.info(f"Found {len(data)} issues in the file")
        
        def has_bug_label(labels):
            for label in labels:
                if isinstance(label, str):
                    if "bug" in label.lower():
                        return True
                elif isinstance(label, dict):
                    if "bug" in label.get('name', '').lower():
                        return True
            return False
        
        bug_issues = [issue for issue in data 
                      if has_bug_label(issue.get('labels', []))
                      and issue.get('num_comments', 0) >= min_comments]
        
        bug_issue_count = len(bug_issues)
        
        logging.info(f"Counted {bug_issue_count} issues with 'bug' label and at least {min_comments} comment(s)")
        
        if copy:
            output_filepath = filepath.with_name(filepath.stem + '_filtered.json')
            with open(output_filepath, 'w') as outfile:
                json.dump(bug_issues, outfile, indent=2)
            logging.info(f"Filtered issues saved to {output_filepath}")
        
        return {
            'total_issues': len(data),
            'bug_issue_count': bug_issue_count,
            'percentage': round((bug_issue_count / len(data)) * 100, 2) if data else 0
        }
    except FileNotFoundError:
        logging.error(f"The file {filepath} was not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"The file {filepath} is not a valid JSON file.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Filter GitHub issues from a JSON file.")
    parser.add_argument("file_path", type=str, help="Path to the JSON file")
    parser.add_argument("-c", "--min_comments", type=int, default=0, help="Minimum number of comments for GitHub issues (default: 1)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--copy", action="store_true", help="Copy filtered results to a new JSON file")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    file_path = Path(args.file_path)
    if not file_path.is_file():
        logging.error(f"The specified file does not exist: {file_path}")
        return
    
    result = analyze_github_issues(file_path, args.min_comments, args.copy)
    if result:
        print("\nGitHub issues analysis:")
        print(f"Total issues: {result['total_issues']}")
        print(f"Bug issues with at least {args.min_comments} comment(s): {result['bug_issue_count']}")
        print(f"Percentage: {result['percentage']}%")
        if args.copy:
            print(f"Filtered issues saved to {file_path.stem}_filtered.json")
    else:
        print("Failed to process GitHub issues. Check the logs for more information.")

if __name__ == "__main__":
    main()