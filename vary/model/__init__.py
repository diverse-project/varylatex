from pathlib import Path
# Create the required folders if they do not exist
Path("vary/build").mkdir(parents=True, exist_ok=True)
Path("vary/source").mkdir(parents=True, exist_ok=True)
Path("vary/results").mkdir(parents=True, exist_ok=True)