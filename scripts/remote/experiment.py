#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'run.py a experiment.py  with parameter'

import re
import csv
import const
import os
import time
from collections import OrderedDict
class parser(object):
    #kw need experimentID testOption
    def __init__(self,benchmark,string,**kw):
        self.string=string.split('\n')
        self.benchmark=benchmark
        self.kw=kw
        ec2metadata=os.popen('ec2metadata').read()
        self.kw['instanceType']=re.search(r'instance-type: (\w*\.\w*)',ec2metadata).group(1)
        self.kw['instanceID']=re.search(r'instance-id: (.*)\n',ec2metadata).group(1)


    def y_cruncher(self):
        needHeader=False
        if not os.path.isfile(const.datadir+'y_cruncher.csv'):
            needHeader=True
        os.system("mkdir "+const.datadir)
        with open(const.datadir+'y_cruncher.csv', 'a') as fout:
            row=OrderedDict([('instanceID',None),('experimentID',None),('instanceType',None),\
                            ('memoryInfo',None),('processorInfo',None),('sysTopology',None),\
                             ('osVersion',None),('testStartTime',None),('availableMemory',None),\
                            ('isMultiThread',None),('cpuUtilization',None),('multiCoreEfficiency',None),\
                            ('computationTime',None),('benchmarkTime',None),('benchmarkTime',None)\
                            ])
            #benchmarkTime = computationTime + I/O operation overhead
            writer = csv.DictWriter(fout,fieldnames=row)
            if needHeader:
                writer.writeheader()
            row['instanceType']=self.kw['instanceType']
            row['instanceID']=self.kw['instanceID']
            row['experimentID']=self.kw['experimentID']
            row['benchmarkTime']=self.kw['duration']
            #row['testOption']=self.kw['testOption']

                
            for line in self.string:

                if line.find('Multi-core Efficiency')!=-1:
                    obj = re.search(r'(\d*\.\d* %)',line)
                    row['multiCoreEfficiency']=obj.group(1)
                if line.find('CPU Utilization')!=-1:
                    obj = re.search(r'(\d*\.\d* %)',line)
                    row['cpuUtilization']=obj.group(1)
                if line.find('Multi-Threading')!=-1:
                    obj = re.search(r'\[01;36m(\w*)',line)
                    row['isMultiThread']=obj.group(1)
                if line.find('Available Memory')!=-1:
                    obj = re.search(r'\[01;33m(*.*? \w*?B)',line)
                    row['availableMemory']=obj.group(1)
                if line.find('Version')!=-1:
                    obj = re.search(r'(\s+)(.*)',line)
                    row['osVersion']=obj.group(2)
                if line.find('Topology')!=-1:
                    obj = re.search(r'(\s+)(.*)',line)
                    row['sysTopology']=obj.group(2)
                if line.find('Processor(s):')!=-1:
                    obj = re.search(r'(\s+)(.*)',line)
                    row['processorInfo']=obj.group(2)
                if line.find('Usable Memory')!=-1:
                    obj = re.search(r'\((*.*? \w*?B)',line)
                    row['memoryInfo']=obj.group(1)
                if line.find('Start Time')!=-1:
                    obj = re.search( r'Start Time: .*?(01;33m)(.*)(\[01;37m)', line)
                    row['testStartTime']=obj.group(2)
                if line.find('Wall Time')!=-1:
                    obj = re.search( r'(\d*\.\d*).*seconds', line)
                    row['benchmarkTime']=obj.group(1)
                if line.find('Total Computation')!=-1:
                    obj = re.search( r'(\d*\.\d*).*seconds', line)
                    row['computationTime']=obj.group(1)
                #TODO more attributes 
        
            writer.writerow(row)
            
    def sysbench(self):
        pass
    def stress_ng(self):
        pass
    def bonnie(self):
        pass
    def iperf3(self):
        pass
    def bandwidth(self):
        pass
    def mbw(self):
        pass

    def getfunc(self):
        return getattr(self,self.benchmark)


class Experiment(object):
	def __init__(self, benchmark,cycle,parameter,experimentID):
		self.benchmark = benchmark
		self.cycle=int(cycle)
		self.parameter=parameter
		self.experimentID=experimentID
	def run(self):
		for i in range(self.cycle):
            time1=time.time()
            result=os.popen(const.command[self.benchmark]+self.parameter[self.benchmark]).read()
            time2=time.time()
            duration=time2-time1 # unit in seconds
			myParser=parser(self.benchmark,result,testOption=self.parameter[self.benchmark],\
                duration=duration,experimentID=self.experimentID)
			func=myParser.getfunc()
			func()
		
