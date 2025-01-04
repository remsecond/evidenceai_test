from pathlib import Path
from src.pipeline import PreprocessingPipeline

def main():
    # Set up paths
    base_dir = Path(__file__).parent
    input_file = base_dir / "input" / "OFW_Messages_Report_Dec.pdf"
    
    # Create pipeline
    pipeline = PreprocessingPipeline(base_dir)
    
    # Process files
    print(f"\nProcessing file: {input_file}")
    outputs, state = pipeline.process([input_file])
    
    if outputs:
        print("\nProcessing completed successfully!")
        
        print("\nGenerated Files:")
        for output_type, files in outputs.items():
            print(f"\n{output_type.upper()}:")
            if isinstance(files, dict):
                for name, path in files.items():
                    print(f"- {name}: {path}")
            else:
                print(f"- {files}")
        
        print("\nStatistics:")
        for stat, value in state.stats.items():
            print(f"- {stat}: {value}")
            
        print("\nProcessing Times:")
        for stage, times in state.processing_time.items():
            duration = times.get('duration', 0)
            print(f"- {stage}: {duration:.2f} seconds")
            
    else:
        print("\nProcessing failed!")
        print("\nErrors:")
        for error in state.errors:
            print(f"- {error}")
            
        print("\nWarnings:")
        for warning in state.warnings:
            print(f"- {warning}")

if __name__ == "__main__":
    main()