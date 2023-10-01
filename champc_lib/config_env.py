import os
import re
import champc_lib.utils as utils
import sys

class env_config:
  
  def __init__(self):
    self.fields = {}
    self.ignore_bin = []
    self.output_path = ""

    self.required_build_fields = ["build_list", "configs_path"]
    self.required_launch_fields = ["workload_path", "workload_list", "binaries_path", "warmup", "sim_inst", "enable_json_output", "results_path"]
    self.required_collect_fields = ["stats_list", "enable_json_output", "results_collect_path"]
    self.required_hprc_fields = ["limit_hours", "ntasks", "account", "HPRC",]

    self.required_fields = ["champsim_root"] 
                    
    self.required_bool = ["HPRC", "enable_json_output"]
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
    
    lt = open(self.fields["launch_template"], "r")

    self.fields["launch_fields"] = [] 

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

    lt.close()

  def build_check(self):
    if self.fields["build_list"] == "":
      print("Build Error: No defined build list")
      exit()
    if self.fields["configs_path"] == "":
      print("Build Error: No defined build configurations path")
      exit() 

  def check_fields(self, fields_to_check, optional):
    failed_check = [] 
    for f in fields_to_check:
      if f not in self.fields.keys() or self.fields[f] == '':
        failed_check.append(f)
      if f in self.required_bool and f not in failed_check:
        if not isinstance(self.fields[f], bool):
          self.fields[f] = (self.fields[f] == '1' or self.fields[f] == 'True')
        if (self.fields[f] != '0' and self.fields[f] != '1') \
        and ((bool(self.fields[f]) != True) and (bool(self.fields[f]) != False)):
          print("ERROR: field {} must be set to 0 or 1, currently: {}".format(f,bool(self.fields[f])))
          exit()

    if len(failed_check) != 0 and not optional:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      exit()
    elif len(failed_check) != 0 and optional:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      utils.check_continue(self.fields["yall"]) 

  def config_check(self, command):
   
    #check required fields
    self.check_fields(self.required_fields, 0)
    #check optional fields
    self.check_fields(self.optional_fields, 1)
    #check build fields
    self.check_fields(self.required_build_fields, 0)
    #check launch fields
    self.check_fields(self.required_launch_fields, 0)
    #check collect fields
    self.check_fields(self.required_collect_fields, 0)
    #check hprc fields
    self.check_fields(self.required_hprc_fields, 0)

    #failed_check = [] 
    #for f in self.required_fields:
    #  if f not in self.fields.keys() or self.fields[f] == '':
    #    failed_check.append(f)
    #  if f in self.required_bool and f not in failed_check:
    #    if self.fields[f] != '0' and self.fields[f] != '1':
    #      print("ERROR: field {} must be set to 0 or 1, currently: {}".format(f, self.fields[f]))
    #      exit()
    #    self.fields[f] = (self.fields[f] == '1')
    #if len(failed_check) != 0:
    #  print("Fields were undefined or failed to load:")
    #  for fc in failed_check:
    #    print(fc)
    #  exit()

    #failed_check = []
    #check optional fields 
    #for f in self.optional_fields:
    #  if f not in self.fields.keys():
    #    failed_check.append(f)
    #if len(failed_check) != 0:
    #  print("Fields were undefined or failed to load:")
    #  for fc in failed_check:
    #    print(fc)
    #  utils.check_continue(self.fields["yall"]) 

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
    
  def username_check(self):
    import pwd
    try: pwd.getpwnam(self.fields["username"])
    except KeyError:
        print("Username {} does not exist".format(self.fields["username"]))
        exit()
    return
  
