import json
import subprocess
import shutil
from pathlib import Path

GITHUB_BASE_PATH = "/"
ROOT_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = ROOT_DIR / "frontend"
OUTPUT_DIR = ROOT_DIR / "legal/licenses"
NOTICES_FILE = ROOT_DIR / "THIRD-PARTY-NOTICES.md"

def setup_directories():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_python_licenses():
    cmd = ["pip-licenses", "--from=mixed", "--format=json", "--with-license-file"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else []

def get_frontend_licenses():
    cmd = f"cd {FRONTEND_DIR} && npx license-checker-rseidelsohn --json"
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode != 0:
        print(f"Error running license-checker: {result.stderr}")
        return {}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        start_index = result.stdout.find('{')
        if start_index != -1:
            return json.loads(result.stdout[start_index:])
        return {}

def process_package(name, version, license_type, source_path, section_name):
    safe_name = name.replace("/", "-").replace("@", "")
    dest_filename = f"{section_name.lower()}-{safe_name}-{version}-LICENSE.txt"
    dest_path = OUTPUT_DIR / dest_filename
    
    name_link = name
    if source_path and Path(source_path).exists():
        try:
            shutil.copy2(source_path, dest_path)
            relative_url = f"legal/licenses/{dest_filename}"
            full_url = f"{GITHUB_BASE_PATH}{relative_url}"
            name_link = f"[{name}]({full_url})"
        except Exception as e:
            print(f"Error copying {name}: {e}")
            
    return f"| {name_link} | {version} | {license_type} |"

def main():
    setup_directories()
    markdown_content = ["# Third-Party Notices", ""]

    markdown_content.extend(["## Scraper", "", "| Name | Version | License |", "| :--- | :------ | :------ |"])
    python_pkgs = get_python_licenses()
    for pkg in python_pkgs:
        row = process_package(
            pkg.get("Name"), 
            pkg.get("Version"), 
            pkg.get("License"), 
            pkg.get("LicenseFile"), 
            "scraper"
        )
        markdown_content.append(row)

    markdown_content.extend(["", "## Frontend", "", "| Name | Version | License |", "| :--- | :------ | :------ |"])
    frontend_pkgs = get_frontend_licenses()
    
    for pkg_name_version, data in frontend_pkgs.items():
        split_idx = pkg_name_version.rfind("@")
        name = pkg_name_version[:split_idx]
        version = pkg_name_version[split_idx+1:]
        license_type = data.get("licenses", "Unknown")
        
        if name == "price-comparator":
            continue

        rel_path = data.get("licenseFile")
        abs_source_path = FRONTEND_DIR / rel_path if rel_path else None
        
        row = process_package(name, version, license_type, abs_source_path, "frontend")
        markdown_content.append(row)

    NOTICES_FILE.write_text("\n".join(markdown_content), encoding="utf-8")

if __name__ == "__main__":
    main()