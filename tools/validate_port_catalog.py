#!/usr/bin/env python3
"""Validate the central Ren'Py PSVita port catalogue and its local documentation."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def validate(catalogue,catalogue_schema,manifest_schema):
 checker=FormatChecker()
 errors=list(Draft202012Validator(catalogue_schema,format_checker=checker).iter_errors(catalogue))
 if errors: return errors
 manifest_validator=Draft202012Validator(manifest_schema,format_checker=checker)
 ids=set(); repositories=set(); title_ids=set()
 for index,port in enumerate(catalogue["ports"]):
  errors.extend(manifest_validator.iter_errors(port))
  port_id=port.get("port_id")
  if port_id in ids: errors.append(ValueError(f"duplicate port_id at ports[{index}]: {port_id}"))
  ids.add(port_id)
  repository=port.get("repository")
  if repository in repositories: errors.append(ValueError(f"duplicate repository at ports[{index}]: {repository}"))
  repositories.add(repository)
  title_id=port.get("title_id")
  if title_id and title_id in title_ids: errors.append(ValueError(f"duplicate Vita title ID at ports[{index}]: {title_id}"))
  if title_id: title_ids.add(title_id)
  docs=port.get("docs_path","")
  if docs:
   candidate=(ROOT/docs).resolve()
   if not candidate.is_relative_to(ROOT.resolve()) or not candidate.is_file():
    errors.append(ValueError(f"missing or unsafe docs_path at ports[{index}]: {docs}"))
 return errors
def main():
 catalogue=load(ROOT/"catalog"/"ports.json")
 catalogue_schema=load(ROOT/"schemas"/"port-catalogue.schema.json")
 manifest_schema=load(ROOT/"schemas"/"port-manifest.schema.json")
 Draft202012Validator.check_schema(catalogue_schema)
 Draft202012Validator.check_schema(manifest_schema)
 errors=validate(catalogue,catalogue_schema,manifest_schema)
 if errors:
  for error in errors: print(f"INVALID: {getattr(error,'json_path','<catalogue>')} {error}",file=sys.stderr)
  return 1
 print(f"Ren'Py PSVita catalogue valid: {len(catalogue['ports'])} ports, unique IDs/title IDs and existing documentation.")
 return 0
if __name__=="__main__": raise SystemExit(main())
