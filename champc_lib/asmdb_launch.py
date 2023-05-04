import sys
import os
from datetime import date
import time 
import subprocess
import champc_lib.launch as launcher

sw_keys = ["multighb", "asmdb", "anchor", "comparer", "mpki_measurements", "ispy"]

def check_load(env_con):
  username = env_con.fields["username"]
  job_limit = int(env_con.fields["job_limit"])
  procs_running = int(subprocess.check_output("squeue -u " + username + " | wc -l",\
    stderr = subprocess.STDOUT, shell = True)) - 1
  print(time.strftime("%H:%M:%S", time.localtime()) + ": Jobs running " + str(procs_running) + " Limit " + str(job_limit))
  if procs_running < job_limit:
    return False
  else:
    time.sleep(30)
    return True

class asmdb_params:
  def __init__(self):
    self.asmdb_traces = {}

def asmdb_check(env_con):
    if self.fields["asmdb_path"] == "":
      print("Launch Error: AsmDB traces path not defined")
      exit()

    if self.fields["asmdb_MT"] == "":
      print("Launch Warning: Launching AsmDB with every MT possible")
      decision = "" 
      while decision != "y" and decision != "n":
        decision = input("Continue? [y/n] ").lower()
      if decision == "n":
        print("Canceling launch...")
        exit()
    if self.fields["asmdb_FT"] == "":
      print("Launch Warning: Launching AsmDB with every FT possible")
      decision = "" 
      while decision != "y" and decision != "n":
        decision = input("Continue? [y/n] ").lower()
      if decision == "n":
        print("Canceling launch...")
        exit()

    if self.fields["asmdb_window"] == "":
      print("Launch Warning: Launching AsmDB with every window possible")
      decision = "" 
      while decision != "y" and decision != "n":
        decision = input("Continue? [y/n] ").lower()
      if decision == "n":
        print("Canceling launch...")
        exit()

    if not os.path.isdir(self.fields["asmdb_path"]):
      print("Launch Error: Path to AsmDB traces does not exist.")
      exit()

def load_params(env_con, asmdb_para):

  #asmdb traces to launch of the form:
  # {Workload : [List of matching AsmDB traces]}
  num_asmdb = 0
  
  #Go through the AsmDB trace directory
  for asm_name in os.listdir(env_con.fields["asmdb_path"]):
    if asm_name[-6:] != ".trace":
      continue

    #Split the trace names so it includes the first field
    #so its a direct comparison between workload/asmdb_trace names
    name = asm_name.split(".")
    comp_name_l = name[0].split("_")
    comp_name = ""

    for a in comp_name_l:
      comp_name += a

    workload_name = name[0]
    comp_workload_name_l = workload_name.split("_")
    comp_workload_name = ""

    for a in comp_workload_name_l:
      comp_workload_name += a

    #print("name: " + str(name) + " comp_name: " + str(comp_name))
    #print("WL name: " + workload_name + " CWL name: " + str(comp_workload_name))

    FT_match = True
    MT_match = True
    window_match = True

    fo = ""
    mt = ""

    for a in name:
      params = a.split("_")
      
      for p in params:
        if "Fo" not in p and "MT" not in p and "W" not in p:
          continue

        if "Fo" in p:
          fo = p[2:4]
          if env_con.fields["asmdb_FT"] == "":
            continue
        elif "MT" in p:
          mt = p[2:]
        elif "W" in p:
          wind = p[1:]

        if env_con.fields["asmdb_window"] != "" and "W" in p and "Work" not in p:
          #print("Window? " + p[1:])
          if p[1:] != env_con.fields["asmdb_window"]:
            window_match = False
            #print("Does not match!")
          continue

        #check for matching fanout threshold, if defined
        elif env_con.fields["asmdb_FT"] != "" and "Fo" in p:
          if p[2:4] != env_con.fields["asmdb_FT"]:
            FT_match = False 
          continue

        elif env_con.fields["asmdb_MT"] != "" and "MT" in p:
          #print("MT match? " + str(p[2:]))
          if p[2:] != env_con.fields["asmdb_MT"]:
            #print("MT Does not match")
            MT_match = False
        else:
          continue

        #print("checking if " + str(asm_name) + " matches")
        if FT_match and MT_match and window_match:
          print("Matches: " + str(asm_name))
          if workload_name not in asmdb_para.asmdb_traces.keys():
            asmdb_para.asmdb_traces[workload_name] = []
          asmdb_para.asmdb_traces[workload_name].append((asm_name, fo, mt))
          num_asmdb += 1
          break

    #print("Number of matching AsmDB traces: %s" % str(num_asmdb))
def launch(env_con):
  asmdb_check(env_con)
  a_param = asmdb_params()
  load_params(env_con, a_param) 
  
  asmdb_based = 0

  print("Binaries launching: ")
  for a in binaries:
    print(a, end=" ")
    if "asmdb" in a.lower() or "anchor" in a.lower() or "comparer" in a.lower() or "mpki_measurements" in a.lower() or "ispy" in a.lower() or "multighb" in a.lower():
      asmdb_based += 1
  print()
  print("asmdb based " + str(asmdb_based))
  print("Launching workloads: ")
  count = 0
  for a in workloads:
    count += 1
    print(a, end="\t")
    if count == 4:
      count = 0
      print()
  print()

  print("Launching " + str(((len(binaries) - asmdb_based) * len(workloads)) + (num_asmdb * asmdb_based)) + " continue? [Y/N]") 

  asmdb_path = env_con.fields["asmdb_path"]
  
  if env_con.fields["output_path"] == "":
    results_path = create_results_directory(env_con)
    env_con.fields["output_path"] = results_path
  else:
    results_path = env_con.fields["output_path"]

  warmup = env_con.fields["warmup"]
  sim_inst = env_con.fields["sim_inst"]

  results_str = "" 
  launch_str = "{}{} -warmup_instructions {} -simulation_instructions {} -cfg_trace {} -traces {}\n" 
  trace_str = "" 
  output_name = "" 
 
  num_launch = 0
  for a in binaries:
    print("LAUNCHING ---------------------------- " + a)
    if (a.lower() not in sw_keys):
      continue
    for b in workloads:
      raw_name = b.split(".")[0]#.split("_")
      #print("Skipping " + str(raw_name))
      #if len(raw_name) == 4:
      #  raw_name = raw_name[0] + "_" + raw_name[1] + "_" + raw_name[2]
      #elif "crypto" not in raw_name[1]:
      #  raw_name = raw_name[0] + "_" + raw_name[1][0:3] + "_" + raw_name[1][3:]
      #elif "crypto" in raw_name[1]:
      #  raw_name = raw_name[0] + "_" + raw_name[1][0:6] + "_" + raw_name[1][6:]

      if raw_name not in a_param.asmdb_traces.keys():
        continue
      for c in a_param.asmdb_traces[raw_name]:
        output_name = b + "_" + a
        results_str = results_path + b + "_" + a + "_" + c[1] + "_" + c[2] 
        launch_str =  binaries_path + a + " -warmup_instructions 00000000 -simulation_instructions 100000000 -cfg_trace " + asmdb_path + c[0] + " -traces " + workload_dir + b + "\n"
        launcher.sbatch_launch(env_con, launch_str, results_str, output_name)
        sanity += 1
    env_con.add_ignore_bin(a) 
  print("AsmDB and Anchor Jobs Launched: " + str(sanity))
  print("Result output directory: " + results_path)
  launcher.terra_launch(env_con)

