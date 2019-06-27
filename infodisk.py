#!/usr/bin/env python

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

def get_all_disk():
    status, output = commands.getstatusoutput('fdisk -l 2>/dev/null | grep -o "Disk /dev/.d[a-z]"')
    allDisk = map(lambda x: x.strip('Disk').strip(), output.split('\n'))
    return allDisk

def get_part_type(disk_path):
    if not disk_path in get_all_disk():
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
    disk_path_list = get_all_disk()
    for disk_path in disk_path_list:
        res = get_part_type(disk_path)
        if res == 2:
            allEmptyDisk.append(disk_path)
    return allEmptyDisk

def format_disk(disk_path, disk_type):
    if not disk_path in get_empty_disk():
        return INPUT_ERROR
    if not disk_type in ('ext4', 'xfs'):
        return INPUT_ERROR
    s1, output1 = commands.getstatusoutput('echo -e "n\np\n\n\n\nw\n"|fdisk ' + disk_path + ' 1>/dev/null 2>&1')
    if s1 == 256:
        return ERROR_MSG
    s2, output2 = commands.getstatusoutput('mkfs.' + disk_type + ' ' + disk_path + '1 1>/dev/null 2>&1')
    if s2 == 256:
        return ERROR_MSG
    return SUCCESS_MSG
    
def get_disk_uuid(disk_path):
    status, output = commands.getstatusoutput('blkid ' + disk_path + ' |awk \'{print $2}\'')
    disk_uuid = output.replace('"','')
    return disk_uuid

def auto_mount_disk(disk_path, mount_path, disk_type):
    disk_uuid = get_disk_uuid(disk_path)
    os.system('sed -i \'/\''+disk_uuid+'\'/d\' /etc/fstab')
    os.system('echo ' + disk_uuid + ' ' + mount_path + ' ' + disk_type + ' defaults 0 0 1>/dev/null 2>&1 >> /etc/fstab')
    os.system('mount -a')
    return SUCCESS_MSG

def byte_to_str(size):
    size = float(size) * 512
    k = 1024
    m = k * k
    g = m * k
    t = g * k
    if size >= t:
        size_str = str('%.2f' % (size / t )) + 'TB'
    elif size >= g:
        size_str = str('%.2f' % (size / g )) + 'GB'
    elif size >= m:
        size_str = str('%.2f' % (size / m )) + 'MB'
    elif size >= k:
        size_str = str('%.2f' % (size / k )) + 'KB'
    else:
        size_str = str('%.2f' % size) + 'Byte'
    return size_str

SCSI_DEV = '/sys/class/scsi_device/'
LIST_HCTL = 'H:C:T:L'
LIST_PATH = 'DevicePath'
LIST_SIZE = 'Size'
LIST_VENDOR = 'Vendor'
LIST_MODEL = 'Model'
LIST_REVISION = 'Rev'
LIST_DMNAME = 'BlockName'

def get_all_disk_detail_comm(hctl, dmname):
    path = '/dev/' + dmname
    s1, size = commands.getstatusoutput('cat /sys/block/' + dmname + '/size')
    s2, vendor = commands.getstatusoutput('cat /sys/block/' + dmname + '/device/vendor')
    if s2 == 256:
        vendor = '-'
    s3, model = commands.getstatusoutput('cat /sys/block/' + dmname + '/device/model')
    if s3 == 256:
        model = '-'
    s4, rev = commands.getstatusoutput('cat /sys/block/' + dmname + '/device/rev')
    if s4 == 256:
        rev = '-'
    return (hctl, path, byte_to_str(size), vendor, model, rev, dmname)

def get_all_disk_detail():
    allDiskDetailList = []
    s1, htclListStr = commands.getstatusoutput('ls ' + SCSI_DEV + '|awk \'{print $1}\'')
    if len(htclListStr) != 0:
        hctlList = htclListStr.split('\n')
        for hctl in hctlList:
            hctlDir = hctl.replace(':', '\:')
            s2, dmname2 = commands.getstatusoutput('ls ' + SCSI_DEV + hctlDir + '/device/block')
            allDiskDetailList.append(get_all_disk_detail_comm(hctl, dmname2))
    else:
        s2, dmnameListStr = commands.getstatusoutput('ls /sys/block/|grep -o ".d[a-z]"')
        dmnameList = dmnameListStr.split('\n')
        for dmname in dmnameList:
            hctl = '-'
            allDiskDetailList.append(get_all_disk_detail_comm(hctl, dmname))
    return allDiskDetailList

def list_all_disk_detail():
    allDiskDetailList = get_all_disk_detail()
    print('%-10s%-12s%-11s%-10s%-18s%-6s%-10s' % (LIST_HCTL, LIST_PATH, LIST_SIZE, LIST_VENDOR, LIST_MODEL, LIST_REVISION, LIST_DMNAME))
    for diskDetail in allDiskDetailList:
        print('%-10s%-12s%-11s%-10s%-18s%-6s%-10s' % diskDetail)

def list_all_empty_disk_detail():
    allEmptyDisk = get_empty_disk()
    if len(allEmptyDisk) == 0:
        return
    print('%-10s%-12s%-11s%-10s%-18s%-6s%-10s' % (LIST_HCTL, LIST_PATH, LIST_SIZE, LIST_VENDOR, LIST_MODEL, LIST_REVISION, LIST_DMNAME))
    allDiskDetailList = get_all_disk_detail()
    for emptyDisk in allEmptyDisk:
        for diskDetail in allDiskDetailList:
            if emptyDisk in diskDetail:
                print('%-10s%-12s%-11s%-10s%-18s%-6s%-10s' % diskDetail)
    
def useage():
    print(' -l|--list      List all disks')
    print(' -e|--empty     List all empty disks')
    print(' -t|--type      Get disk partition type')
    print(' -u|--uuid      Get the disk partition UUID')
    print(' -f|--format    Format the empty disk as ext4 or xfs')
    print(' -m|--mount     Set the disk partition to mount automatically')

def main():
    if (len(sys.argv)) == 2:
        if (sys.argv[1] == '-l') or (sys.argv[1] == '--list'):
            list_all_disk_detail()
        elif(sys.argv[1] == '-e') or (sys.argv[1] == '--empty'):
            list_all_empty_disk_detail()
        else:
            useage()
    elif(len(sys.argv)) == 3:
        if (sys.argv[1] == '-t') or (sys.argv[1] == '--type'):
            res = {
                0: 'gpt',
                1: 'mbr',
                2: 'unkown',
                3: ERROR_MSG
            }
            print(res[get_part_type(sys.argv[2])])
        elif(sys.argv[1] == '-u') or (sys.argv[1] == '--uuid'):
            print(get_disk_uuid(sys.argv[2]))
        else:
            useage()
    elif(len(sys.argv)) == 4:
        if (sys.argv[1] == '-f') or (sys.argv[1] == '--format'):
            print(format_disk(sys.argv[2], sys.argv[3]))
        else:
            useage()
    elif(len(sys.argv)) == 5:
        if (sys.argv[1] == '-m') or (sys.argv[1] == '--mount'):
            print(auto_mount_disk(sys.argv[2], sys.argv[3], sys.argv[4]))
        else:
            useage()
    else:
        useage()

if __name__ == '__main__':
    main()
