
# PYTHON start-up file. Define PYTHONSTARTUP to point to this file

print("Running Python-IDL bridge startup...")
import os
cur_dir=os.getcwd()

try:
   ssw=os.environ.get('SSW')
   if ssw is None:
      print("$SSW is not defined.")
   
   bridge_dir=os.path.join(ssw,'gen','python','bridge')
   bexists=os.path.exists(bridge_dir)
   if bexists == False:
      print("SSW Python-IDL bridge setup directory not found.")
   
   os.chdir(bridge_dir)
   import bridge
   
   pp=os.environ.get('PYTHONPATH')
   if pp is None:
      path=bridge_dir
   else:
      ll=(pp,bridge_dir)
      path=';'.join(ll)
	  
   os.environ['PYTHONPATH']=path
   
   IDL=bridge.startup()
   print("Loaded SSWIDL...")
   
except:
   print("Loading vanilla IDL...")
   from idlpy import * 
	
os.chdir(cur_dir)
