#!/usr/bin/python
'''
__author__ = 'liboo'
mail: striveliboo@163.com
'''
import sys
import commands


ONE_SECTOR_BYTES = 512
PART_TYPE_GPT = 0
PART_TYPE_DOS = 1
PART_TYPE_UNKOWN = 2
INPUT_ERROR = 3

def list_all_disk():
    status, output = commands.getstatusoutput('fdisk -l 2>/dev/null | grep -o "Disk /dev/.d[a-z]"')
    allDisk = map(lambda x: x.strip('Disk').strip(), output.split('\n'))
    return allDisk

def get_part_type(disk_path):
    
    if not disk_path:
        return INPUT_ERROR
    
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

def main():
    if (len(sys.argv)) == 2:
        res = {0:'gpt',1:'mbr',2:'unkown',3:'error'}
        print(sys.argv[1] + ' : ' + res[get_part_type(sys.argv[1])])
    else:
        print('')
        print('Useage:')
        print(' python disk-utils.py /dev/sda')
        print('')
        print('Show all disk:')
        for i in list_all_disk():
            print(i)
        print('')


if __name__ == '__main__':
    main()

