import os
def build_champsim(env_con):
  
  build_list = env_con.fields["build_list"]

  if build_list == "all":
    for js in os.listdir(env_con.fields["configs_path"]):
      if js[-4:] == "json":
        os.system("./config.sh " + env_con.fields["configs_path"] + js)
        os.system("make")

  else:

    build_file = open(build_list)
   
    with open(build_list) as build_file:
      for line in filter(lambda l: not l.startswith('#'),  build_file):
        target = line.strip()
        if target not in os.listdir(env_con.fields["configs_path"]):
          print("Build file: " + target + " not found ")
          exit()
        else:
          print("Building: " + env_con.fields["configs_path"] + target)
          os.system("./config.sh " + env_con.fields["configs_path"] + target)
        os.system("make")
