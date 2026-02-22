"""Extract productNumber from inline script"""
import requests
import re

url = "https://www.selfio.de/produkte/ideal-standard-brausethermostat-ap-cerat-ausld-80mm-chrom"
r = requests.get(url)
html = r.text

# Find all inline scripts
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

print(f"Found {len(scripts)} scripts\n")

# Check script 5 (the large one)
if len(scripts) > 5:
    script = scripts[5]
    print(f"Script 5 length: {len(script)} chars")
    
    if 'productNumber' in script:
        print("✓ Contains 'productNumber'\n")
        
        # Try different patterns
        patterns = [
            r'"productNumber"\s*:\s*"([^"]+)"',
            r'productNumber:\s*"([^"]+)"',
            r'productNumber\s*:\s*\'([^\']+)\'',
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, script)
            if matches:
                print(f"Pattern '{pattern}' found {len(matches)} matches:")
                all_matches.extend(matches)
                for m in list(set(matches))[:5]:
                    print(f"  - {m}")
                print()
        
        # Get unique values
        unique = list(set(all_matches))
        print(f"\nTotal unique productNumbers found: {len(unique)}")
        print(f"Sample values: {unique[:10]}")
        
        # Check if our expected value is there
        if 'A4632AA' in unique:
            print("\n✓✓ Found expected article number: A4632AA")
        else:
            print(f"\n⚠ Expected 'A4632AA' not found")
            print(f"All values: {unique}")
    else:
        print("'productNumber' not found in script 5")
else:
    print("Script 5 not found")
