#!/usr/bin/env python3
"""Check that the Ren'Py Vita port catalogue and its handbook stay aligned."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
README=(ROOT/"README.md").read_text(encoding="utf-8")
STATUS=(ROOT/"wiki-source/Port-Status.md").read_text(encoding="utf-8")
ISSUE=(ROOT/".github/ISSUE_TEMPLATE/ren-py-game.md").read_text(encoding="utf-8")
REQUIRED_PORTS={
 "Don-t-OpenYourVita",
 "Sakura-Succubus-Vita",
 "Sakura-Succubus-2-Vita",
 "Sakura-Succubus-3-Vita",
 "Sakura-Succubus-4-Vita",
 "Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita",
 "HIKE-BACK-Vita",
}
def main()->int:
 errors=[]
 links=re.findall(r"https://github\.com/SilverCrow2323/([A-Za-z0-9._-]+)",README)
 duplicates=sorted({name for name in links if links.count(name)>1})
 if duplicates: errors.append("Duplicate project links: "+", ".join(duplicates))
 missing=sorted(REQUIRED_PORTS-set(links))
 if missing: errors.append("Missing linked port repositories: "+", ".join(missing))
 for heading in ("PORT IN PROGRESS","FUTURE TESTS / SUGGESTIONS","FAILED PORTS"):
  if heading not in README: errors.append(f"README is missing catalogue section: {heading}")
 for phrase in ("In testing","Future tests and suggestions","Failed basic conversions"):
  if phrase not in STATUS: errors.append(f"Port-Status handbook is missing category: {phrase}")
 for field in ("GAME INFO","Game name","Link 1","SCREENSHOTS"):
  if field not in ISSUE: errors.append(f"Game suggestion issue template is missing: {field}")
 if errors:
  print("\n".join("ERROR: "+e for e in errors)); return 1
 print(f"Port catalogue OK: {len(REQUIRED_PORTS)} first-party port repositories linked; status handbook and suggestion template present.")
 return 0
if __name__=="__main__": raise SystemExit(main())
