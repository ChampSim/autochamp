
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
