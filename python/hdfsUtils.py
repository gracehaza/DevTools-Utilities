import os
import sys
import logging
import argparse

from DevTools.Utilities.utilities import which, runCommand

HAS_HDFS = which('hdfs')

def strip_hdfs(directory):
    return '/'.join([x for x in directory.split('/') if x not in ['hdfs']])

def hdfs_ls_directory(storeDir):
    '''Utility for ls'ing /hdfs at UW'''
    if not HAS_HDFS: return []
    storeDir = strip_hdfs(storeDir)
    command = 'gfal-ls gsiftp://cms-lvs-gridftp.hep.wisc.edu/{0}'.format(storeDir)
    command = 'ls /hdfs/{}'.format(storeDir)
    out = runCommand(command)
    if 'gfal-ls' in out:
        logging.error(command)
        logging.error(out)
        return []
    return out.split()

def get_hdfs_root_files(topDir,lastDir='',extension='root'):
    '''Utility for getting all root files in a directory (and subdirectories)'''
    if not HAS_HDFS: return []
    lsDir = strip_hdfs('{0}/{1}'.format(topDir,lastDir)) if lastDir else strip_hdfs(topDir)
    nextLevel = hdfs_ls_directory(lsDir)
    if 'ls:' in nextLevel:
        logging.error('Problem with directory')
        logging.error(topDir)
        logging.error(lastDir)
        return []
    out = []
    for nl in nextLevel:
        if nl in ['failed','log']: # dont include
            continue
        elif nl[-1*len(extension):]==extension: # its a root file
            out += ['{0}/{1}'.format(lsDir,nl)]
        else: # keep going down
            out += get_hdfs_root_files(lsDir,nl,extension)
    return out

def get_hdfs_directory_size(directory):
    '''Get the size of a hdfs directory (in bytes).'''
    if HAS_HDFS:
        directory = strip_hdfs(directory)
        command = 'hdfs dfs -du -s {0}'.format(directory)
        out = runCommand(command)
        try:
            return float(out.split()[0])
        except:
            print command
            print out
            raise
    else:
        totalSize = 0.
        return totalSize # sorry, don't do it this way, too slow
        for fname in get_hdfs_root_files(directory):
            command = 'gfal-ls -l gsiftp://cms-lvs-gridftp.hep.wisc.edu//hdfs{0} | awk \'{{print $5;}}\''.format(strip_hdfs(directory))
            out = runCommand(command)
            try:
                totalSize += float(out.split()[0])
            except:
                print command
                print out
                raise
        return totalSize
