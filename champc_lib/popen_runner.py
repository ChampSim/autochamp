import subprocess
import time
import collections
import os
import sys
import itertools
from timeit import default_timer as timer
from datetime import timedelta

def begin(fname, *args):
    f = open(fname, 'wt')
    return f, subprocess.Popen(args, stdout=f, stderr=f)

def check_finish(f, p):
    retval = p.poll()
    if retval is not None:
        f.close()
    return retval

def run(runs, env_con):
  start = timer()
  processargs = collections.deque(runs)
  active_processes = []
  while processargs or active_processes:
      unfinished = [(check_finish(*p) is None) for p in active_processes]
      active_processes = list(itertools.compress(active_processes, unfinished))

      while processargs and len(active_processes) < int(env_con.fields['job_limit']):
          active_processes.append(begin(str(len(runs)-len(processargs)) + '.txt', *processargs[0]))
          processargs.popleft()
      time.sleep(1)

