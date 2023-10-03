# AutoChamp
AutoChamp is meant as a tool to assist ChampSim users with building, launching, and collecting statistics from simulations.
To enable different features (launching, building, etc.) the fields in the configuration file must be filled out. Once set up, the environment allows for multiple configurations to be built and launched at a time, organizing the simulations' outputs into seperate directories to allow AutoChamp to collect from multiple simulation result files at once. 

AutoChamp is intended to provide very basic functionality and infrastructure for new users to expand as necessary.

DISCLAIMER: This infrastructure is currently untested for the wide range of environments ChampSim might be used in. Please post any issues you encounter and submit pull requests as needed. 

## Setting up and Running AutoChamp

### Setup
Note: This is a draft and quick introduction to using AutoChamp in its current state.
	1) Download ChampSim
	2) Change to the ChampSim directory
	3) Download autochamp into the champsim directory
	4) Open autochamp/autochamp-config.cfg and set champsim_root to the champsim directory.
	5) Fill out the fields in autochamp-config.cfg
 
Options:

	-h, --help : Show this help message and exit
	-f CONFIG, --config CONFIG : Configuration file needed to load in auto-champ's configurations.
	-b, --build : Build the files in the configurations path and defined in build_list in control.cfg.
	-l, --launch : Launch binarys in file defined in binary_list with workloads in workload_list defined in the control file
	-c, --collect : Collect command reads JSON file embedded in the results output file. NOTE: Currently only supports single trace outputs and it scrapes from the "sim" section of ChampSim's output
	-p, --print_stats : Prints the stats available for the collect command/field.
  -y, --yall : Says yes to all prompts.

### Building ChampSim

Building with AutoChamp requires the following fields in the configration file be populated:

  build_list - path to a text file containing a configuration file name per line.
	configs_path - path to the directory containing the configuration files
 
From the champsim directory run:

	 python3 autochamp/auto-champ.py -f autochamp/autochamp-config.cfg -b
  
### Launching ChampSim

Fill out the parameters for running multiple simulations

  HPRC - determines if the jobs will launch using slurm
  Enable_json_output - passes json output flag to champsim. Note: This must be on in order to use the collect (-c) flag
	Warmup and sim_inst - describes the number of instructions used for warm up and simulation
	Binaries path - the location of the binaries you want to launch
	Results path - where the results will be written
	Workload path - location of the traces listed in workload_list
	Binary list - path to file that lists which binaries to launch
	Launch template - used to create job files for use with slurm
 
From the champsim directory run:

  python3 autochamp/auto-champ.py -f autochamp/autochamp-config.cfg -l

### Collecting Statistics

ChampSim outputs the results of the simulations to the <code>output_path</code> based on the date the result was generated (note launching simulations overnight generates a folder for the new date) and seperates the simulations into folders based on the number of launches previously done in that day. i.e. Launching 6 different sets of simulations on 1/1/2023 will place the results in 2023-01-01/1/ through /6/.

Fill out the parameters for collecting stats:
	
	results_collect_path - where the results you want to scrape are
	stats_list - this file decribes which stats to collect

The <code>stats_list</code> is filled out based on the JSON structure outputted by ChampSim with the <code>enable_json_output</code> flag. To make it easier to fill out, running AutoChamp with the <code>-c -p<\code> flags with a valid <code>results_collect_path<\code> displays the levels in the JSON output. Examples are included in <code>to_collect.txt</code>
	
 
