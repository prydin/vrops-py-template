'''
Created on Dec 16, 2015

@author: Pontus Rydin

This software is freely available to anyone who likes to use it. You are permitted to include this in your own 
projects freely and without restriction. However, you use it at your own risk! I make no guarantee it will work
or that it will not harm the system it is running on. Here's some legalease stating the same thing:

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF 
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import nagini
import re
from sys import argv
import time
import subprocess
import shlex
import socket

adapterKind = None
adapterName = None

def parseConfig(filename):
    config = {}
    configFile = open(filename)
    content = configFile.readlines()
    for line in content:
        line = line.strip()
        if line[0] == '#':
            continue
        m = re.search('(.+)\s*\=\s*(.+)', line)
        config[m.group(1)] = m.group(2)
    configFile.close();
    return config;

def sendData(vrops, resourceKind, resourceName, stats, properties):
    global adapterKind
    global adapterName

    statList = [] if stats else None
    propList = [] if properties else None
    timestamp = long(time.time() * 1000)
    for key, value in stats.iteritems():
        statList.append( { "statKey" : key, "timestamps": [ timestamp ], "data": [ value ]})
    for key, value in properties.iteritems():
        propList.append( { "statKey" : key, "timestamps": [ timestamp ], "values": [ value ]})
    return vrops.find_create_resource_push_data(resourceName=resourceName, 
                                         adapterKindKey=adapterKind, 
                                         resourceKindKey=resourceKind,
                                         resourceIdentifiers={}, 
                                         pushAdapterKindKey=adapterName, 
                                         stats={ "stat-content": statList } if stats else None, 
                                         properties={ "prop-content": propList if properties else None })
    
def addChild(vrops, parentAdapterKindKey, parentAdapterKey, parentResourceKindKey, parentResourceName, child, create=False):
    if create:
        parent = vrops.find_create_resource_with_adapter_key(adapterKindKey=parentAdapterKindKey, pushAdapterKindKey=parentAdapterKey,
                                                             resourceKindKey=parentResourceKindKey, resourceName=parentResourceName,
                                                             resourceIdentifiers={})
    else:
        parent = vrops.get_resources_with_adapter_and_resource_kind(identifiers={}, name=parentResourceName, adapterKindKey=parentAdapterKindKey, 
                                                                    resourceKindKey=parentResourceKindKey) 
        if parent['pageInfo']['totalCount'] == 0:
            return
    vrops.add_relationship({ "uuids": [ child["identifier"] ] }, relationshipType="CHILD", resourceId=parent['resourceList'][0]['identifier'])
        
    
def run(configFile):
    global adapterKind 
    global adapterName 

    # Load configuration and sanity check
    #
    config = parseConfig(configFile)
    if  not config['vropshost']: 
        raise Exception("A value for vropshost must be specified")
    if  not config['vropsuser']: 
        raise Exception("A value for vropsuser must be specified")
    if  not config['vropspassword']: 
        raise Exception("A value for vropshost must be specified")
    
    # Create a connection to vR Ops
    #
    vrops = nagini.Nagini(host=config['vropshost'], user_pass=(config['vropsuser'], config['vropspassword']))
    
    
    ##########################################################################################################
    #
    # YOUR CODE GOES HERE!
    #
    ##########################################################################################################
    
    adapterKind = "SamplePythonAdapter"
    adapterName = "MySamplePythonAdapter"
    resource = sendData(vrops, "PythonThingy", "MyPythonThingy", { "metric1": 1, "metric2": 2}, {"prop1": "value1", "prop2": "value2"})
    addChild(vrops, adapterKind, adapterName, "ParentThingy", "MyParentThingy", resource);
    
    ##########################################################################################################
    #
    # YOUR CODE ENDS HERE!
    #
    ##########################################################################################################

if __name__ == '__main__':
    run(argv[1])
