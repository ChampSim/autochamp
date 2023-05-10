import sys
import os
from datetime import date
import time 
import subprocess
import re
import champc_lib.utils as utils

def check_load(env_con):
  username = env_con.fields["username"]
  job_limit = int(env_con.fields["job_limit"])
  current_binary = env_con.fields["current_binary"]

  hms_t = time.strftime("%H:%M:%S", time.localtime())

  #if on the TAMU HPRC machines, use squeue to see how many jobs are currently
  #running based on the username given in the control file
  if env_con.fields["HPRC"]:
    procs_running = int(subprocess.check_output("squeue -u " + username + " | wc -l",\
      stderr = subprocess.STDOUT, shell = True)) - 1

    print(f"{hms_t}: Jobs running: {procs_running} Job Limit {job_limit}")

  else:
    procs_running = int(subprocess.check_output("ps -u {} | grep \"{}\" | wc -l".format(username, str(current_binary)),\
      stderr = subprocess.STDOUT, shell = True))

    print(f"{hms_t}: Jobs running: {procs_running} Job Limit {job_limit}")
    
  if procs_running < job_limit:
    return False
  else:
    time.sleep(30)
    return True

def create_results_directory(env_con):

  results_path = env_con.fields["results_path"]
  num_cores = env_con.fields["num_cores"]
  today = str(date.today())

  core_path = [results_path, today, f"/{num_cores}_cores/"]
  core_path_str = "".join(core_path)
  print("".join(core_path))
  path = ""
  if not os.path.isdir("".join(core_path)):
    core_path.append("1/")
    for s in core_path:
      path += s
      if not os.path.isdir(path):
        print(f"Creating new directory: {path}")
        os.makedirs(path)
  else:
    num_dirs = len([f for f in os.listdir(core_path_str) if os.path.isdir(os.path.join(core_path_str, f)) and f.isdigit()])
    core_path_str = f"{core_path_str}{num_dirs + 1}/"
    print(f"Creating new results directory: {core_path_str}")
    os.makedirs(core_path_str)
    results_path += core_path_str 

  return core_path_str

def launch_simulations(env_con, launch_str, result_str, output_name):
  launch_str = launch_str.strip() + f" &> {result_str}"
  print(f"Final CMD: {launch_str}")
  while check_load(env_con):
    continue

  os.system(launch_str)

def sbatch_launch(env_con, launch_str, result_str, output_name): 

  while check_load(env_con):
    continue

  with open(env_con.fields["launch_template"], "r") as templ, open(env_con.fields["launch_file"], "w") as temp_launch:

    #check for missing fields
    ignore_fields = set(env_con.ignore_fields)
    required_fields = set(field.strip("{}") for field in re.findall(r"{[^{}]*}", templ.read()))
    missing_fields = required_fields - set(env_con.fields.keys()) - ignore_fields
    if missing_fields:
      print("Following fields are not defined and required for launching:\n", "\n".join([str(entry) for entry in missing_fields]))
    
    templ.seek(0)

    for line in templ:

      matches = re.findall(r"{([^{}]*)}", line)
      out_line = line

      for match in matches:
        if match in ignore_fields:
          if match == "result_str":
            out_line = out_line.replace("{" + match + "}", result_str)
          elif match == "output_name":
            print(output_name)
            out_line = out_line.replace("{" + match + "}", output_name)
        else:
          out_line = out_line.replace("{" + match + "}", env_con.fields[match])

      temp_launch.write(out_line.strip() + "\n") 

    temp_launch.write(launch_str)

  print("Running command: sbatch ", env_con.fields["launch_file"])
  os.system("sbatch " + env_con.fields["launch_file"])
  os.system("rm " + env_con.fields["launch_file"])

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

  #######################################################################
  #Keeping this in to prevent users from using yall to accidently launch#
  #a large number of jobs                                               #
  #TODO: Find safer/better way of doing this                            #
  #######################################################################
  print("Launching {len(binaries) * len(workloads)} continue? [y/n]")
  cont = input().lower()
  if cont != "y":
    print("Exiting job launch...")
    exit()
  print("Launching jobs...")
  #######################################################################

  binaries_path = env_con.fields["binaries_path"]
  results_path = ""

  if env_con.output_path == "":
    results_path = create_results_directory(env_con)
  else:
    results_path = env_con.output_path

  warmup = env_con.fields["warmup"]
  sim_inst = env_con.fields["sim_inst"]

  results_str = "" 
  launch_str = "{}{} -warmup_instructions {} -simulation_instructions {} -traces {}\n" 
  results_output_s = ""
  trace_str = "" 
  output_name = "" 
  num_launch = 0
 
  print("Job binaries: {}".format(binaries))

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
        json_flag = " -j"

      output_name = results_output_s + "_" + a + "_"
      results_str = results_path + results_output_s + "_bin:" + a 
      f_launch_str = launch_str.format(binaries_path, a, str(env_con.fields["warmup"]), str(env_con.fields["sim_inst"]) + json_flag, trace_str)
      print("Launching command: {}".format(f_launch_str))
      print("Writing results to: {}".format(results_str))
      if env_con.fields["HPRC"]:
        sbatch_launch(env_con, f_launch_str, results_str, output_name)
      else:
        launch_simulations(env_con, f_launch_str, results_str, output_name)
      num_launch += 1
      print("Launching Job " + str(num_launch))
