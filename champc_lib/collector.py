import os
import json
from datetime import date
import traceback
import re
import champc_lib.utils as utils

class InvalidJSONException(Exception):
  #print("Raised when collector.py parses a file with unexpected JSON formatting.")
  pass

def get_stat_value(json_o, key_list):

  if not key_list:
    return json_o
  key = key_list[0]
  
  if isinstance(json_o, dict):
    if key in json_o:
      return get_stat_value(json_o[key], key_list[1:])
  elif isinstance(json_o, list):
    if key >= len(json_o):
      print(f"Invalid index into JSON list. {key}")
      return None
    return get_stat_value(json_o[key], key_list[1:])

  print("No value found for {key_list}.")
  return None

def parse_stats_list(stats_fn):
  stats_paths = []

  with open(stats_fn) as sl:
    for line in sl:
      l = line.strip().split(",")
      sanitized_l = []
      if line.strip() == "":
        continue
      for ent in l:
        if utils.check_str_int(ent):
          sanitized_l.append(int(ent))
        elif utils.check_str_float(ent):
          sanitized_l.append(int(ent))
        else:
          sanitized_l.append(ent.strip())

      if sanitized_l != []:
        stats_paths.append(sanitized_l)
      #print(stats_paths)
  return stats_paths

def print_level(level, level_str):
  symb = ""
  top_bot_buf = 40
  per_level_buf = 2

  if level == 1:
    print(f"{symb * top_bot_buf}")
  print(f"{symb * (level * per_level_buf)} {level_str}")
  if level == 1:
    print(f"{symb * top_bot_buf}")


def parse_json(data, level):

  if isinstance(data, dict):
    for a in data.keys():
      print_level(level + 1, f"Level {level + 1} : {a}")
      parse_json(data[a], level + 1)

  elif isinstance(data, list):
    for a in [entry for entry in data if not isinstance(entry, (int, float))]: #data:
      print_level(level + 1, f"Level {level + 1} : List len {len(a)} : {a}")
      parse_json(a, level + 1)

  elif isinstance(data, str) and data != "":
    print_level(level + 1, f"Level {level+1} Type : {data}")
 
  return

def print_stats(env_con):

  stat_dir = env_con.fields["results_collect_path"]
  print("Only printing stats found in JSON for the first file in the directory:")
  print(stat_dir + sorted(os.listdir(stat_dir))[0])
  
  for fil in sorted(os.listdir(stat_dir)): 
    split_name = fil.split(".")
    wl_name = split_name[0]
   
    #look for "bin:" to find the binary name 
    start = fil.find("bin:") + len("bin:")
    if start == -1:
      print("\nFile: {fil} does not contain \"bin:\". Skipping file.")
      continue

    try:
      f = open(stat_dir + fil, "r")
    except IOError:
      print("Collect Error: Could not open file -- " + stat_dir+fil)
      exit()
  
    #find the start of the JSON file text in a champsim output 
    start_index = 0 
    for line in f:
      if line.strip().startswith("["):
        break
      start_index += len(line)
    f.seek(start_index)

    text = f.read()
    try:
  
      data = json.loads(text)
      try: 
        if len(data) > 1: 
          raise InvalidJSONException
      except InvalidJSONException:
          print("\nAssumes JSON output starts with a [ ] encompassing the json\
            object and the 0th index is the start. LEN {}\nUpdate the collection file here:")
          print(traceback.format_exc())
          exit()

      pattern = r"cpu(\d+)_"

      print("|==================================================|")
      print("|>>>      Looking into JSON_OBJ[0][\"roi\"]      <<<<|")
      print("|==================================================|")
      parse_json(data[0]["roi"], 0)
  
      #print("{}".format(data[0]["roi"]["cpu0_L1I"]))
      #for a in data:
      #  if isinstance(a, dict):
      #    print(list(a.keys()))

      exit()
    except json.JSONDecodeError:
      print("File does not contain JSON formatted text.")

    f.close()
  print("Completed JSON print out...Exiting...")
  exit() 

def get_stats(env_con):

  stat_dir = env_con.fields["results_collect_path"]

  stats_list = parse_stats_list(env_con.fields["stats_list"]) 

  if len(stats_list) == 0:
    print("stats_list is empty. Run auto-champ with the following flags \"-c -p\" to see the JSON fields and their ordering.")
    print("Stats file must list the JSON hierarchy ordering, with commas between hierarchy levels.")
    exit()

  #stats dictionary for { BINARY : [Workload Stats] }
  bin_stats = {}

  count = 0
  num_files = len(os.listdir(stat_dir)) 
  
  #for each file in the directory...
  for fil in sorted(os.listdir(stat_dir)): 

    count += 1
    print("\r%.2f percent of files loaded" % (100 * float(count)/float(num_files)), end="")

    split_name = fil.split(".")
    wl_name = split_name[0]
   
    #look for "bin:" to find the binary name 
    start = fil.find("bin:") + len("bin:")
    if start == -1:
      print("\nFile: {} does not contain \"bin:\". Skipping file.".format(fil))
      continue

    end = fil.find(".", start)
    if end == -1:
      binary = fil[start:]
    else:
      binary = fil[start:end]

    try:
      f = open(stat_dir + fil, "r")
    except IOError:
      print("\nCollect Error: Could not open file -- " + stat_dir+fil)
      exit()
  
    #find the start of the JSON file text in a champsim output 
    start_index = 0 
    for line in f:
      if line.strip().startswith("["):
        break
      start_index += len(line)
    f.seek(start_index)

    text = f.read()
    try:
  
      data = json.loads(text)
      try: 
        if len(data) > 1: 
          raise InvalidJSONException
      except InvalidJSONException:
          print("\nAssumes JSON output starts with a [ ] encompassing the json\
            object and the 0th index is the start. LEN {}\nUpdate the collection file here:")
          print(traceback.format_exc())
          exit()

      if binary not in bin_stats.keys():
        bin_stats[binary] = {}

      bin_stats[binary][count] = {}
      bin_stats[binary][count]["traces"] = []

      for tn in data[0]['traces']:
        bin_stats[binary][count]["traces"].append(os.path.basename(str(tn)))
        print("\nLoading {}".format(os.path.basename(str(tn))))

      for stat_set in stats_list:
        stat_name = ""
        for temp in stat_set:
          if isinstance(temp, int) or isinstance(temp, float):
            continue
          stat_name += str(temp)
        t = [0] + ["roi"] + stat_set
        val = get_stat_value(data, t)
        bin_stats[binary][count][stat_name] = val

    except json.JSONDecodeError:
      print("\nFile does not contain JSON formatted text and will not be included: {}".format(fil))
      utils.check_continue(env_con.fields["yall"])
      continue

    f.close()
  print("")
  return bin_stats 

def collect_and_write(env_con):
  workload_keys = []

  if env_con.fields["print_stats"]:
    print_stats(env_con)

  bin_stats = get_stats(env_con) 

  if "baseline" in env_con.fields.keys():
    baseline = env_con.fields["baseline"]
  else:
    baseline = ""

  if baseline != "" and baseline not in bin_stats.keys():
    print("Stats Collection Error: Baseline [%s] not present in results directory" % (baseline))
    exit()

  #creates a csv file based on the date
  #and the number of same-dated files
  csv_name = str(date.today()) + ".csv"
  tag = 0
  while os.path.exists(csv_name):
    tag += 1
    csv_name = str(date.today()) + "_" + str(tag) + ".csv"
  csv_file = open(csv_name, "w")

  first = True
  
  for binary in bin_stats.keys():
    if binary == baseline:
      continue

    if first:
      first = False
      csv_file.write("Binary,")
      for a in bin_stats[binary][list(bin_stats[binary].keys())[0]]:
        csv_file.write("{}, ".format(a))
      csv_file.write("\n")

    #write header first
    for a in bin_stats[binary].keys():
      csv_file.write("{}, ".format(binary))
      for stat in bin_stats[binary][a].keys():
        if isinstance(bin_stats[binary][a][stat], list):
          out_str = "".join(bin_stats[binary][a][stat])
        else: out_str = bin_stats[binary][a][stat]
        csv_file.write("{}, ".format(out_str))
      csv_file.write("\n")
  #write the baseline first for reference
  #if baseline != "":
  #  for wl in workload_keys:
  #    if wl in bin_stats[baseline].ipc.keys():
  #      
  print("Writing results to " + csv_name)

