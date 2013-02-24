#!/usr/bin/python

import subprocess, sys, os, string, shlex, signal, weakref
import time, datetime
import hyperclient

DEX_PORT = 6666
DEX_HOST = "127.0.0.1"

if "DEX_PORT" in os.environ:
  DEX_PORT = os.environ["DEX_PORT"]
if "DEX_HOST" in os.environ:
  DEX_HOST = os.environ["DEX_HOST"]

#########################################

class child_process:
  def __init__(self,cmdlin,working_dir):
    args = shlex.split(cmdlin)
    self.cwd = working_dir
    self.pobj = subprocess.Popen(args,cwd=working_dir)
    time.sleep(0.5)
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
    self.coordhost = DEX_HOST
    self.coordport = DEX_PORT

#########################################

def call(cmd,wdir):
 a = child_process(cmd,wdir)
 a.join()

#########################################
