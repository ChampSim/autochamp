import sys
import os
from datetime import date
import time 
import subprocess
import re
import champc_lib.utils as utils
import champc_lib.config_env as ce 

def check_load(env_con):
  username = env_con.fields["username"]
  job_limit = int(env_con.fields["job_limit"])
  curr_bin = env_con.fields["current_binary"]

  if env_con.fields["HPRC"]:
    procs_running = int(subprocess.check_output(f"squeue -u {username} | wc -l", stderr = subprocess.STDOUT, shell = True)) - 1

    print(time.strftime("%H:%M:%S", time.localtime()) + f" - Jobs running {str(procs_running)} Limit {str(job_limit)}")
    
    if procs_running < job_limit:
      return False
    else:
      time.sleep(30)
      return True
  else:
    procs_running = int(subprocess.check_output(f"ps -u {username} | grep \"{curr_bin}\" | wc -l", stderr = subprocess.STDOUT, shell = True))

    print(f"Procs running: {procs_running} Bin {curr_bin}")

    print(time.strftime("%H:%M:%S", time.localtime()) + f" - Jobs running {str(procs_running)} Limit {str(job_limit)}")
    #print(time.strftime("%H:%M:%S", f"{time.localtime()} - Jobs running {str(procs_running)} Limit {str(job_limit)}"))

    if procs_running < job_limit:
      return False
    else:
      time.sleep(30)
      return True

def create_results_directory(env_con):

  results_path = env_con.fields["results_path"]
  num_cores = str(env_con.fields["num_cores"])
  td = str(date.today())

  path_parts = [td+"/", num_cores + "_cores/"]
  count = 1

  count_str = f"{str(count)}/"
  if not os.path.isdir(os.path.join(results_path, *path_parts)):
    path_parts.append(count_str)
    os.makedirs(os.path.join(results_path, *path_parts))
  else:
    while os.path.isdir(os.path.join(results_path, *path_parts, count_str)):
        count += 1
        count_str = f"{str(count)}/"
    path_parts.append(count_str)
    os.makedirs(os.path.join(results_path, *path_parts))
  results_path += "".join(path_parts)
  print(f"Created directory {results_path}")
  return results_path

def launch_simulations(env_con, launch_str, result_str, output_name):
  launch_str = f"{launch_str.strip()} > {result_str} &"
  print(f"Final CMD: {launch_str}")
  while check_load(env_con):
    continue

  os.system(launch_str)

def sbatch_launch(env_con, launch_str, result_str, output_name): 

  while check_load(env_con):
    continue

  launchf = env_con.fields["launch_file"]
  temp_launch = open(launchf, "w")

  #open the template file
  tmpl = open(env_con.fields["launch_template"], "r")

  for line in tmpl:
    matches = re.findall(r"{([^{}]*)}", line)
    out_line = line
    for match in matches:
      if match not in env_con.fields.keys() and match not in env_con.ignore_fields:
        print(f"{match}: Not defined and required for launching\n")
        exit()
      if match in env_con.ignore_fields:
        if match == "result_str":
          out_line = out_line.replace("{" + match + "}", result_str)
        elif match == "output_name":
          print(output_name)
          out_line = out_line.replace("{" + match + "}", output_name)
      else:
        out_line = out_line.replace("{" + match + "}", env_con.fields[match])

    temp_launch.write(out_line.strip() + "\n") 

  temp_launch.write(launch_str)
  temp_launch.close()

  print(f"Running command: sbatch {launchf}")
  os.system(f"sbatch launch_f")
  os.system(f"rm {launch_f}")

def launch_handler(env_con):

  #init the structs holding the list of launching items
  binaries = []
  workloads = []

  with open(env_con.fields["binary_list"], "r") as binary_list_file:
    #gather each binary 
    binaries = list(utils.filter_comments_and_blanks(binary_list_file))

  with open(env_con.fields["workload_list"], "r") as workloads_list_file:
    workloads = list(utils.filter_comments_and_blanks(workloads_list_file))

 
  #workload director
  workload_dir = env_con.fields["workload_path"]

  env_con.username_check()

  print("Binaries launching: ")
  print("Launching workloads: ")
  count = 0

  #This prints the workloads in 4 columns
  for a in workloads:
    count += 1
    print(a, end="\t")
    if count == 4:
      count = 0
      print()
  print()

  ################################################################
# Leaving this in beyond --yall to prevent accidently
# launching too many jobs
  ################################
  print(f"Launching {len(binaries) * len(workloads)} continue? [Y/N]") 
  cont = input().lower()
  if cont != "y":
    print("Exiting job launch...")
    exit()
  print("Launching jobs...")
##################################
################################################################

  binaries_path = env_con.fields["binaries_path"]
  results_path = ""

  if env_con.output_path == "":
    results_path = create_results_directory(env_con)
  else:
    results_path = env_con.output_path

  warmup = env_con.fields["warmup"]
  sim_inst = env_con.fields["sim_inst"]

  results_str = "" 
  launch_str = "{}{} --warmup_instructions {} --simulation_instructions {} {}\n" 
  results_output_s = ""
  trace_str = "" 
  output_name = "" 
  num_launch = 0
 
  print(f"Job binaries: {binaries}")

  for a in binaries:
    for b in workloads:
      splitload = b.split(" ")

      env_con.fields["current_binary"] = a

      #supporting multicore by iterating through the workload list
      if(len(splitload) > 1):
        for subwl in splitload:
          #create results file name
          results_output_s += subwl.strip() + "_"
          #trace str needs to include wl directory since it references each trace's location
          trace_str += workload_dir.strip() + subwl.strip() + " "
        results_output_s += "multi"
      else:
        results_output_s = b
        trace_str = workload_dir + b

      json_flag = ''
      if env_con.fields["enable_json_output"]:
        json_flag = " --json"

      output_name = f"{results_output_s}_{a}_"
      results_str = f"{results_path}{results_output_s}_bin:{a}"
      f_launch_str = launch_str.format(binaries_path, a, str(env_con.fields["warmup"]), str(env_con.fields["sim_inst"]) + json_flag, trace_str)
      print(f"Launching command: {f_launch_str}")
      print(f"Writing results to: {results_str}")

      if env_con.fields["HPRC"]:
        sbatch_launch(env_con, f_launch_str, results_str, output_name)
      else:
        launch_simulations(env_con, f_launch_str, results_str, output_name)
      num_launch += 1
      print(f"Launching Job {num_launch}")
