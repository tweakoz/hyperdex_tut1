#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal, weakref
import time, datetime
import hyperclient
import exec_common as ec

#########################################

tmp_dir_base = ec.tmp_dir()
cfg = ec.hyp_cfg(tmp_dir_base)

#########################################

print "DEX_HOST<%s>" % cfg.coordhost
print "DEX_PORT<%s>" % cfg.coordport
client = hyperclient.Client(cfg.coordhost, cfg.coordport)
print client
#res = client.put('phonebook', 'jsmith1', {'first': 'John', 'last': 'Smith', 'phone': 6075551024})

print client.get('phonebook', 'jsmith1')

atomic_prev_val0 = {"first":"John", "last":"Smith"}
atomic_next_val0 = {"first":"JJ"}
atomic_prev_val1 = {"first":"JJ", "last":"Smith"}
atomic_next_val1 = {"first":"John"}

changed = 0
iters = 0

for i in range(10000):
  res = client.cond_put("phonebook", "jsmith1", atomic_prev_val0, atomic_next_val0)
  changed += int(res)
  iters += 1
  # the change request will only succeed if the value on the data store was
  #equal to the data specified in the atomic_prev_val. This will be enforced 
  # atomically, even across an entire cluster of shards
  res = client.cond_put("phonebook", "jsmith1", atomic_prev_val1, atomic_next_val1)
  changed += int(res)
  iters += 1
  print "jsmith changed %d times out of %d" % (changed,iters)

#client.rm_space('phonebook')

#########################################
