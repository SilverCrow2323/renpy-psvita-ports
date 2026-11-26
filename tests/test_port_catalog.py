import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from validate_port_catalog import load, validate, ROOT

class PortCatalogueTests(unittest.TestCase):
 def setUp(self):
  self.catalogue=load(ROOT/"catalog"/"ports.json")
  self.cat_schema=load(ROOT/"schemas"/"port-catalogue.schema.json")
  self.manifest_schema=load(ROOT/"schemas"/"port-manifest.schema.json")
 def test_repository_catalogue_is_valid(self):
  self.assertEqual(validate(self.catalogue,self.cat_schema,self.manifest_schema),[])
 def test_duplicate_title_id_is_rejected(self):
  value=copy.deepcopy(self.catalogue)
  value["ports"][1]["title_id"]=value["ports"][0]["title_id"]
  self.assertTrue(validate(value,self.cat_schema,self.manifest_schema))
 def test_invalid_game_data_path_is_rejected(self):
  value=copy.deepcopy(self.catalogue)
  value["ports"][0]["game_data_path"]="ux0:/app/../escape/"
  self.assertTrue(validate(value,self.cat_schema,self.manifest_schema))
 def test_unknown_title_id_is_not_required(self):
  value=copy.deepcopy(self.catalogue)
  value["ports"][-1].pop("title_id",None)
  self.assertEqual(validate(value,self.cat_schema,self.manifest_schema),[])

if __name__=="__main__": unittest.main()
