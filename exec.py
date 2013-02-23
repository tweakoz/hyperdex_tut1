#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal, weakref
import time, datetime
import hyperclient

#########################################

class child_process:
  def __init__(self,cmdlin,working_dir):
    args = shlex.split(cmdlin)
    self.cwd = working_dir
    self.pobj = subprocess.Popen(args,cwd=working_dir)
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

class tmp_dir:
  def __init__(self):
    now_object = datetime.datetime.now();
    todays_date_string = "%02d%02d%04d" % (now_object.month,now_object.day,now_object.year)
    current_time_string = "%02d%02d%02d" % (now_object.hour,now_object.minute,now_object.second)
    self.dtstring = "run_%s_%s" % (todays_date_string,current_time_string)

#########################################

class hyp_cfg:
  def __init__(self,tdir):
    self.tmp_dir = tdir
    self.coordhost = "127.0.0.1"
    self.coordport = 1982
    call("mkdir %s"%self.tmp_dir.dtstring, "./")
    coord_str = "hyperdex coordinator -f -l %s -p %d"%(self.coordhost,self.coordport)
    self.coordinator = child_process(coord_str,self.tmp_dir.dtstring)
  def __del__(self):
    self.coordinator.kill()

#########################################

class hyp_daemon:
  def __init__(self,hcfg,daenum):
    self.hcfg = weakref.ref(hcfg)
    self.tmp_dir = "%s_daem%d"%(self.hcfg.tmp_dir.dtstring,daenum)
    chost = self.hcfg.coordhost
    cport = self.hcfg.coordport
    self.dae_str = "hyperdex daemon -f --listen=%s --listen-port=2012 --coordinator=%s --coordinator-port=%d --data=./"%(chost,chost,cport)
    self.dae = child_process(self.dae_str,self.tmp_dir)
  def __del__(self):
    self.dae.kill()

#########################################

def call(cmd,wdir):
 a = child_process(cmd,wdir)
 a.join()

#########################################
call("killall -9 -r hyperdex", "./")
call("killall -9 -r replicant", "./")
call("rm -rf ./run_*", "./")
#########################################
#hyperdex server startup
localhost = "127.0.0.1"
coordport = 1982
#########################################

tmp_dir_base = tmp_dir()
coordinator = hyp_cfg(tmp_dir_base)
time.sleep(1)
daemons = list()
for i in range(0,4):
  time.sleep(2)
  d = hyp_daemon(coordinator,i)
  daemons.append(d)
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
