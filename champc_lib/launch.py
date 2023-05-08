import sys
import os
from datetime import date
import itertools

import champc_lib.popen_runner as popen_runner
import champc_lib.slurm_runner as slurm_runner
import champc_lib.utils as utils

def create_results_directory(env_con):
  results_path = os.path.join(env_con.fields["results_path"], str(date.today()), str(env_con.fields["num_cores"]) + "_cores")
  num_dirs = 1
  while os.path.isdir(os.path.join(results_path, str(num_dirs))):
      num_dirs += 1

  results_path = os.path.join(results_path, str(num_dirs))
  print("Creating new directory:", results_path)
  os.makedirs(results_path, exist_ok=True)
  return results_path

def get_command_tuple(binary, workload, env_con):
    launch_str = ("{binary}", "-warmup_instructions", "{warmup_instructions}", "-simulation_instructions", "{simulation_instructions}", "{json}", "--", "{traces}", "&>", "{output_name}")

    splitload = workload.split(" ")

    #trace str needs to include wl directory since it references each trace's location
    trace_str = ' '.join(os.path.join(env_con.fields['workload_path'], subwl) for subwl in splitload)

    # create results file name
    results_output_s = workload if len(splitload) == 1 else '_'.join((*splitload, "multi"))
    output_name = '_'.join((results_output_s, binary))

    json_flag = '-j' if env_con.fields["enable_json_output"] else ''

    return tuple(arg.format(
        binary=os.path.join(env_con.fields["binaries_path"], binary),
        warmup_instructions=env_con.fields["warmup"],
        simulation_instructions=env_con.fields["sim_inst"],
        json=json_flag,
        traces=trace_str,
        output_name=os.path.join(env_con.output_path, output_name)
    ) for arg in launch_str)

def launch(env_con):
    with open(env_con.fields['binary_list'], 'r') as binary_list_file:
        binaries = list(utils.filter_comments_and_blanks(binary_list_file)) #gather each binary

    print("Binaries launching: ")
    for a in binaries:
        print(a)
    print()

    with open(env_con.fields['workload_list'], 'r') as workloads_list_file:
        workloads = list(utils.filter_comments_and_blanks(workloads_list_file))

    #This prints the workloads in 4 columns
    print("Launching workloads: ")
    workload_print_groups = [iter(workloads)] * 4
    for a in itertools.zip_longest(*workload_print_groups, fillvalue=''):
        print('\t'.join(a))
    print()

    launch_cmds = [get_command_tuple(b,w,env_con) for b,w in itertools.product(binaries, workloads)]
    if input("Launching " + str(len(launch_cmds)) + " continue? [y/N] ").lower() != "y":
        sys.exit("Exiting job launch...")
    print("Launching jobs...")

    env_con.output_path = env_con.output_path or create_results_directory(env_con)
    if env_con.fields["runner_format"] == 'slurm':
      slurm_runner.run(launch_cmds, env_con)
    elif env_con.fields["runner_format"] == 'echo':
      for r in launch_cmds:
        print(*r)
    else:
      popen_runner.run(launch_cmds, env_con)
