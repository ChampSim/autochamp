import sys
import os
import re
import champc_lib.utils as utils

class env_config:
  
  def __init__(self):
    self.fields = {}
    self.ignore_bin = []
    self.output_path = ""

    self.required_fields = ["champsim_root", "build_list", "configs_path", "results_path", "workload_path", "binaries_path", 
                    "limit_hours", "ntasks", "account", "workload_list", "warmup", "sim_inst",
                    "results_collect_path", "runner_format","enable_json_output", "stats_list"]
    self.required_bool = ["enable_json_output"]
    self.optional_fields = ["launch_file", "baseline", "launch_template","yall"]
    self.ignore_fields = ["output_name", "result_str"]

  def add_ignore_bin(self, bin_str):
    self.ignore_bin.append(bin_str)
 
  def load_env_config(self, config_name):
    if not os.path.exists(config_name):
      sys.exit("ERROR: CONTROL CONFIG FILE DOES NOT EXIST\nFile: " + config_name)

    with open(config_name, "r") as config_file:
        for line in utils.filter_comments_and_blanks(config_file):
            key, delim, value = line.partition('=')
            if delim != '=':
                sys.exit('Error parsing line: '+line)

            key = key.strip()
            value = value.strip()

            if key in self.fields.keys():
                sys.exit("ERROR: REPEATING CONFIGURATION FIELD: "+ key)

            self.fields[key] = value

  def load_launch_template(self):

    if not os.path.exists(self.fields["launch_template"]):
      print("ERROR: LAUNCH TEMPLATE DEFINED BUT DOES NOT EXIST: " + self.fields["launch_template"] + "\n")
      exit()

    self.fields["launch_fields"] = [] 

    with open(self.fields["launch_template"], "r") as lt:
        for line in lt:
          line = line.strip()
          if "=" not in line:
            continue
          matches = re.findall(r"{([^{}]*)}", line)
          for match in matches:
            if match not in self.fields.keys() and match not in self.ignore_fields:
              print("{} defined in template file but not in control.cfg\n".format(match))
              utils.check_continue(self.fields["yall"]) 
            self.fields["launch_fields"].append(match) 

  def build_check(self):
    if self.fields["build_list"] == "":
      print("Build Error: No defined build list")
      exit()
    if self.fields["configs_path"] == "":
      print("Build Error: No defined build configurations path")
      exit() 

  def config_check(self, command):
   
    #check required fields 
    failed_check = [] 
    for f in self.required_fields:
      if f not in self.fields.keys():
        failed_check.append(f)
      if f in self.required_bool and f not in failed_check:
        if self.fields[f] != '0' and self.fields[f] != '1':
          print("ERROR: field {} must be set to 0 or 1, currently: {}".format(f, self.fields[f]))
          exit()
        self.fields[f] = (self.fields[f] == '1')
    if len(failed_check) != 0:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      exit()

    failed_check = []
    #check optional fields 
    for f in self.optional_fields:
      if f not in self.fields.keys():
        failed_check.append(f)
    if len(failed_check) != 0:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      utils.check_continue(self.fields["yall"]) 

    if command.collect:
      if not os.path.isdir(self.fields["results_collect_path"]):
        print("Stats Collection Error: Results collect path does not exist\nInput: %s" % (self.fields["results_collect_path"])) 
        exit()
      
  def stats_check(self):
    if self.fields["results_collect_path"] == "":
      print("Stats Collection Error: Results collect path not specified")
      exit()
    if "baseline" not in self.fields.keys() or self.fields["baseline"] == "":
      print("Stats Collection Warning: Baseline not specified. Will not generate IPC improvement.")
    
    
  
