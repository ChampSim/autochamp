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
    
    for line in build_file:
      if line[0] != "#":
        target = line.strip()
      else:
        continue
      if target not in os.listdir(env_con.fields["configs_path"]):
        print("Build file: " + target + " not found ")
        exit()
      else:
          print("Building: " + env_con.fields["configs_path"] + target)
          os.system("./config.sh " + env_con.fields["configs_path"] + target)
          os.system("make")
