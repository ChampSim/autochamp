
import sys
import os
from datetime import date
import time 
import subprocess
import champc_lib.config_env as conf
import champc_lib.build as build
import champc_lib.launch as launcher
import champc_lib.collector as collect
import champc_lib.utils as utils
import argparse

parser = argparse.ArgumentParser(description='Example script with 3 options.')

parser.add_argument('-f', '--config', type=str, help='Control file needed to load in auto-champ\'s configurations.')
parser.add_argument('-b', '--build', help='Build the files in the configurations path and defined in build_list in control.cfg.',action='store_true')
parser.add_argument('-l', '--launch',  help='Launch binarys in file defined in binary_list with workloads in workload_list defined in control.cfg\
  \nNOTE: Currently does not support multicore launching.',action='store_true')
parser.add_argument('-c', '--collect', help='Collect command reads JSON file embedded in the results output file.\
\nNOTE: Currently only supports single trace outputs and it scrapes from the \"sim\" section of ChampSim\'s output',action='store_true')
parser.add_argument('-p', '--print_stats', help='Prints the stats available for the collect command/field.',action='store_true')
parser.add_argument('-y', '--yall', help='Says yes to all prompts.', action='store_true')

args = parser.parse_args()

env_con = conf.env_config()

env_con.fields["yall"] = args.yall

env_con.load_env_config(args.config)
env_con.config_check(args)

#for build, include the name of the json file
if args.build:
  
  build.build_champsim(env_con)
  
elif args.launch:

  if "launch_template" in env_con.fields.keys():
    if env_con.fields["HPRC"]:
      print("Launching HPRC Job.")
      utils.check_continue(env_con.fields["yall"])
      env_con.load_launch_template()
  launcher.launch_handler(env_con)

elif args.collect:

  if args.print_stats:
    env_con.fields["print_stats"] = True
    print("Only printing JSON tree not scraping stats...")
  else:
    env_con.fields["print_stats"] = False

  collect.collect_and_write(env_con)
  print("Complete")
