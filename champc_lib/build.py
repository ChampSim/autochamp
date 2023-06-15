import os
import sys
import json
import importlib
import tempfile
import itertools
import champc_lib.utils as utils

def parse_json(fname):
    with open(fname, "r") as rfp:
        parsed = json.load(rfp)
        if isinstance(parsed, list):
            return parsed
        return [parsed]

def parse_targets_file(build_list, config_path):
    with open(build_list) as build_file:
      for line in utils.filter_comments_and_blanks(build_file):
          target = os.path.join(config_path, line.strip())
          if os.path.exists(target):
              print("Found configuration", target)
              yield target
          else:
              print("Configuration", target, "not found ")
              exit()


def build_champsim(env_con):
    #spec = importlib.util.spec_from_file_location('.config', os.path.join(env_con.fields['champsim_root'], 'config'))
    #champsim_config = importlib.util.module_from_spec(spec)
    #spec.loader.exec_module(champsim_config)

    sys.path.append(env_con.fields['champsim_root'])
    import config.filewrite
    import config.parse

    build_list = env_con.fields["build_list"]
    if build_list == "all":
        targets = itertools.chain(*((os.path.join(base,f) for f in files) for base,_,files in os.walk(env_con.fields['configs_path'])))
        targets = filter(lambda t: os.path.splitext(t)[1] == '.json', targets)
    else:
        targets = parse_targets_file(build_list, env_con.fields['configs_path'])

    parsed_jsons = itertools.chain(*(parse_json(f) for f in targets))
    with tempfile.TemporaryDirectory() as objdir_name:
        with config.filewrite.FileWriter(env_con.fields['binaries_path'], objdir_name) as wr:
            for c in parsed_jsons:
                wr.write_files(config.parse.parse_config(c))

        os.system("make -C "+env_con.fields['champsim_root'])
