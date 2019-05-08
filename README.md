### 介绍

Linux下磁盘分区检测工具，根据第一扇区中的特殊值来判断磁盘分区。

### 使用

```shell
[root@localhost ~]# python disk-utils.py

Useage:
 python disk-utils.py /dev/sda

Show all disk:
/dev/sda
/dev/sdb
/dev/sdc
```

### 示例

```shell
[root@localhost ~]#  python disk-utils.py /dev/sda
/dev/sda : mbr

[root@localhost ~]#  python disk-utils.py /dev/sdb
/dev/sdb : gpt

[root@localhost ~]#  python disk-utils.py /dev/sdc
/dev/sdc : unkown

[root@localhost ~]#  python disk-utils.py /dev/sde
/dev/sde : error
```

