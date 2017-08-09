#!/usr/bin/env python3
'''
Created on Aug 9, 2017

@author: arnon
'''

import os

def realname(path, root=None):
    ''' joins root with path, if root is provided.
        Then check is it is a symlink.  If it is, return 
        a string representing the link.  Otherwise, return 
        basename or path.
    '''
    if root is not None:
        path=os.path.join(root, path)
    result=os.path.basename(path)
    if os.path.islink(path):
        realpath=os.readlink(path)
        result= '%s -> %s' % (os.path.basename(path), realpath)
    return result

def ptree(startpath, depth=-1): 
    ''' prints directory tree in 'tree' structure.
    
    Args:
        startpath: root path to start
        depth: depth of tree to print; default: -1 which signals not limit
    '''
    prefix=0
    if startpath != '/':
        if startpath.endswith('/'): startpath=startpath[:-1]
        prefix=len(startpath)  
    for root, dirs, files in os.walk(startpath):
        level = root[prefix:].count(os.sep)
        if depth >-1 and level > depth: continue
        indent=subindent =''
        if level > 0:
            indent = '|   ' * (level-1) + '|-- '
        subindent = '|   ' * (level) + '|-- '
        print('{}{}/'.format(indent, realname(root)))
        # print dir only if symbolic link; otherwise, will be printed as root
        for d in dirs:
            if os.path.islink(os.path.join(root, d)):
                print('{}{}'.format(subindent, realname(d, root=root)))
        for f in files:
            print('{}{}'.format(subindent, realname(f, root=root)))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""prints directory tree""")
    parser.add_argument('--level', '-l', type=int, dest='depth', help='depth of tree to print')
    parser.add_argument('startpath', type=str, help='path to stating directory')
    args = parser.parse_args()
    argsd=vars(args)
    ptree(**argsd)
