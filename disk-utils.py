#!/usr/bin/python

'''
__author__ = 'liboo'
mail: striveliboo@163.com
'''

import os
import sys
import commands


ONE_SECTOR_BYTES = 512
PART_TYPE_GPT = 0
PART_TYPE_DOS = 1
PART_TYPE_UNKOWN = 2
INPUT_ERROR = 3
ERROR_MSG='error'
SUCCESS_MSG='success'

def list_all_disk():
    status, output = commands.getstatusoutput('fdisk -l 2>/dev/null | grep -o "Disk /dev/.d[a-z]"')
    allDisk = map(lambda x: x.strip('Disk').strip(), output.split('\n'))
    return allDisk

def get_part_type(disk_path):
    if not disk_path in list_all_disk():
        return INPUT_ERROR
    
    with open(disk_path, 'rb') as fp:
        hex_list = ["{:02x}".format(ord(c)) for c in fp.read(ONE_SECTOR_BYTES)]
    
    if hex_list[511] != 'aa' and hex_list[510] != '55':
        return PART_TYPE_UNKOWN
        
    if hex_list[450] == 'ee': 
        return PART_TYPE_GPT
    else:
        return PART_TYPE_DOS

def get_empty_disk():
    allEmptyDisk = []
    disk_path_list = list_all_disk()
    for disk_path in disk_path_list:
        res = get_part_type(disk_path)
        if res == 2:
            allEmptyDisk.append(disk_path)
    return allEmptyDisk

def get_disk_uuid(disk_path):
    status, output = commands.getstatusoutput('blkid ' + disk_path + ' |awk \'{print $2}\'')
    disk_uuid = output.replace('"','')
    return disk_uuid

def auto_mount_disk(disk_path,mount_path,disk_type):
    disk_uuid = get_disk_uuid(disk_path)
    os.system('sed -i \'/\''+disk_uuid+'\'/d\' /etc/fstab')
    os.system('echo ' + disk_uuid + ' ' + mount_path + ' ' + disk_type + ' defaults 0 0 >> /etc/fstab')
    os.system('mount -a')
    return SUCCESS_MSG
        
def useage():
    print('')
    print('Useage:')
    print(' infodisk options [disk]')
    print(' infodisk -m disk point type')
    print('Options')
    print(' -l    List all disks')
    print(' -e    List all empty disks')
    print(' -t    Get disk partition type') 
    print(' -u    Get the first partition UUID') 
    print(' -m    Set the first partition to mount automatically')
    print('')


def main():
    if (len(sys.argv)) == 2:
        if sys.argv[1] == '-l':
            for disk1 in list_all_disk():
                print(disk1)
        elif sys.argv[1] == '-e':
            for disk2 in get_empty_disk():
                print(disk2)
        else:
            useage()
    elif (len(sys.argv)) == 3:
        if sys.argv[1] == '-t':
            res = {0:'gpt',1:'mbr',2:'unkown',3:ERROR_MSG}
            print(res[get_part_type(sys.argv[2])])
        elif sys.argv[1] == '-u':
            print(get_disk_uuid(sys.argv[2]))
        else:
            useage()
    elif (len(sys.argv)) == 5:
        if sys.argv[1] == '-m':
            print(auto_mount_disk(sys.argv[2],sys.argv[3],sys.argv[4]))
        else:
            useage()   
    else:
        useage()

if __name__ == '__main__':
    main()
