import subprocess
import sys
import os

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"Starting {script_name}...")
    print(f"{'='*50}\n")
    
    try:
        # Run the script using the same Python executable currently running
        subprocess.run([sys.executable, script_name], check=True)
        print(f"\n[SUCCESS] {script_name} completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {script_name} failed with exit code {e.returncode}.")
        print("Stopping the pipeline to prevent cascading errors.")
        sys.exit(1) # Stop the runner if a script fails

if __name__ == "__main__":
    # List of scripts to run in order
    scripts_to_run = [
        "download.py",
        "parsing.py",
        "csv_maker.py",
        "analysis.py"
    ]
    
    print("Starting the WB Election 2026 Automation Pipeline")
    
    for script in scripts_to_run:
        if not os.path.exists(script):
            print(f"[ERROR] {script} not found in the current directory.")
            sys.exit(1)
            
        run_script(script)
        
    print("\nPipeline finished completely! All scripts executed successfully.")
