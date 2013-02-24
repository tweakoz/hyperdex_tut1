#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal, weakref
import time, datetime
import hyperclient
import exec_common as ec

#########################################

tmp_dir_base = ec.tmp_dir()
cfg = ec.hyp_cfg(tmp_dir_base)

#########################################

client = hyperclient.Client(cfg.coordhost, cfg.coordport)
print dir(client)
print client

#res = client.put('phonebook', 'jsmith1', {'first': 'John', 'last': 'Smith', 'phone': 6075551024})

#print res

res = client.get('phonebook', 'jsmith1')
print res

#client.rm_space('phonebook')

#########################################
