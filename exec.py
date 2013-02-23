#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal
import time, datetime
import hyperclient

#########################################

class child_process:
  def __init__(self,cmdlin):
    args = shlex.split(cmdlin)
    self.pobj = subprocess.Popen(args)
 	#, shell=True, stderr=sys.stdout, stdout=sys.stdout
  def join(self):
    while self.is_running():
      time.sleep(.1)
  def is_running(self):
        return (self.pobj.poll()==None)
  def kill(self):
        if self.is_running():
          self.pobj.send_signal(signal.SIGKILL)
  def interrupt(self):
        if self.is_running():
          self.pobj.send_signal(signal.SIGINT)

#########################################
def call(cmd):
 a = child_process(cmd)
 a.join()
#########################################

now_object = datetime.datetime.now();
todays_date_string = "%02d%02d%04d" % (now_object.month,now_object.day,now_object.year)
current_time_string = "%02d%02d%02d" % (now_object.hour,now_object.minute,now_object.second)
dtstring = "run_%s_%s" % (todays_date_string,current_time_string)

#########################################
call("killall -9 -r hyperdex")
call("killall -9 -r replicant")
call("rm -rf ./run_*")
call("mkdir %s"%dtstring)
#########################################
#hyperdex server startup
localhost = "127.0.0.1"
coordport = 1982
#########################################
os.chdir(dtstring)
coordinator = child_process("hyperdex coordinator -f -l %s -p %d"%(localhost,coordport))
time.sleep(1)
daemon = child_process("hyperdex daemon -f --listen=%s --listen-port=2012 --coordinator=%s --coordinator-port=%d --data=./"%(localhost,localhost,coordport))
time.sleep(1)
#########################################
client = hyperclient.Client(localhost, coordport)
print client
spec = '''
... space phonebook 
... key username 
... attributes first, last, int phone
... subspace first, last, phone
... create 8 partitions
... tolerate 2 failures
... '''
space = client.add_space(spec)

time.sleep(1)

print space

res = client.put('phonebook', 'jsmith1', {'first': 'John', 'last': 'Smith', 'phone': 6075551024})

print res

time.sleep(1)

res = client.get('phonebook', 'jsmith1')
print res

client.rm_space('phonebook')

#########################################
#hyperdex server shutdown
##########################################
#daemon.kill()
#time.sleep(1)
#coordinator.kill()
#time.sleep(1)
os.chdir("..")
#########################################hyperdex daemon -f --listen=127.0.0.1 --listen-port=2012 --coordinator=127.0.0.1 --coordinator-port=1982 --data=./
