
def list_col_print(in_list):
    from math import isqrt as isqrt
    from math import ceil as ceil
    num = len(in_list)
    num_col = isqrt(num)
    ele_per_col = ceil(num / num_col)

    max_len = max(len(str(item)) for item in in_list)
    
    for i in range(0, num, ele_per_col):
        col = in_list[i:i + ele_per_col]
        for item in col:
            print(str(item).ljust(max_len), end=' ')
        print()

def check_continue(yall):
  decision = ""
  if yall:
    print("Continue? [y/n] y")
    return
 
  while decision != "y" and decision != "n":
    decision = input("Continue? [y/n] ").lower()
    if decision == "n":
      print("Canceling launch...")
      exit()
  return

def check_str_int(ent):
  try:
    int(ent)
    return True
  except ValueError:
    return False

def check_str_float(ent):
  try:
    float(ent)
    return True
  except ValueError:
    return False

def filter_comments_and_blanks(file_iter):
    trimmed_lines = (l.partition('#')[0].strip() for l in file_iter)
    yield from (l for l in trimmed_lines if len(l) > 0)
