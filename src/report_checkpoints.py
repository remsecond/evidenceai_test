import argparse
from pathlib import Path
from utils.checkpoint_reporter import CheckpointReporter

def main():
    parser = argparse.ArgumentParser(description='Generate checkpoint reports')
    parser.add_argument('--full', action='store_true', help='Generate full report')
    parser.add_argument('--stage', help='Report on specific stage')
    parser.add_argument('--verify', action='store_true', help='Run verification only')
    parser.add_argument('--recommendations', action='store_true', help='Show recommendations only')
    
    args = parser.parse_args()
    reporter = CheckpointReporter()
    
    if args.full or not any([args.stage, args.verify, args.recommendations]):
        print("\nGenerating full checkpoint report...")
        report_file = reporter.generate_full_report()
        print(f"Report saved to: {report_file}")
        
    if args.stage:
        # Read the stage section from the report
        with open(report_file) as f:
            content = f.read()
            start = content.find(f"### {args.stage.upper()}")
            if start == -1:
                print(f"Stage {args.stage} not found in report")
            else:
                end = content.find("###", start + 1)
                if end == -1:
                    end = len(content)
                print(content[start:end])
                
    if args.verify:
        valid_files, invalid_files = reporter._checkpoint_manager.verify_all_checkpoints()
        print("\nCheckpoint Verification Results:")
        print(f"Valid Checkpoints: {len(valid_files)}")
        print(f"Invalid Checkpoints: {len(invalid_files)}")
        if invalid_files:
            print("\nInvalid checkpoints:")
            for f in invalid_files:
                print(f"- {f.name}")
                
    if args.recommendations:
        print("\nRecommendations:")
        print(reporter._generate_recommendations())

if __name__ == "__main__":
    main()