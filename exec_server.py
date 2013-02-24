#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal, weakref
import time, datetime
import hyperclient
import exec_common as ec

cur_dir = os.getcwd()

#########################################

class hyp_coord:
  def __init__(self,cfg):
    self.cfg = cfg
    self.tmp_dir = cfg.tmp_dir
    self.coordhost = cfg.coordhost
    self.coordport = cfg.coordport
    ec.call("mkdir %s"%self.tmp_dir.dtstring, cur_dir )
    coord_str = "hyperdex coordinator -f -l %s -p %d"%(self.coordhost,self.coordport)
    self.coordinator = ec.child_process(coord_str,self.tmp_dir.dtstring)
  def kill(self):
    self.coordinator.kill()    
    ec.call("rm -rf %s"%self.tmp_dir.dtstring, cur_dir)
  def __del__(self):
    self.kill()

#########################################

class hyp_daemon:
  def __init__(self,hcfg,daenum):
    self.hcfg = weakref.ref(hcfg)
    self.tmp_dir = "%s_daem%d"%(self.hcfg().tmp_dir.dtstring,daenum)
    ec.call("mkdir %s"%self.tmp_dir, cur_dir)
    chost = self.hcfg().coordhost
    cport = self.hcfg().coordport
    self.dae_str = "hyperdex daemon -f --listen=%s --listen-port=2012 --coordinator=%s --coordinator-port=%d --data=./"%(chost,chost,cport)
    self.dae = ec.child_process(self.dae_str,self.tmp_dir)
  def kill(self):
    self.dae.kill()    
    ec.call("rm -rf %s"%self.tmp_dir, cur_dir)
  def __del__(self):
    self.kill()

#########################################
ec.call("killall -r hyperdex", cur_dir)
ec.call("killall -r replicant", cur_dir)
#########################################

tmp_dir_base = ec.tmp_dir()
cfg = ec.hyp_cfg(tmp_dir_base)
coordinator = hyp_coord(cfg)
time.sleep(1)
daemons = list()
for i in range(1):
  d = hyp_daemon(cfg,i)
  daemons.append(d)
time.sleep(1)

#########################################

client = hyperclient.Client(cfg.coordhost, cfg.coordport)
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

res = client.get('phonebook', 'jsmith1')
print res

#client.rm_space('phonebook')

time.sleep(1)

#########################################

def signal_handler(signal, frame):
  print "##################################################"
  print "CTRLC DETECTED, inititiating DEX shutdown"
  print "##################################################"

  for d in daemons:
    d.kill()

  coordinator.kill()
  
  sys.exit(0)

#########################################

signal.signal(signal.SIGINT, signal_handler)

while True:
  time.sleep(1.0)

#########################################
