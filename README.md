# kmem_fp
A script using drgn (https://github.com/osandov/drgn) to interpret freeponter of a slab cache. The output is similar to kmem -S of the crash utility.

# Usage

~~~
kmem_fp.py [VMCORE [VMLINX]] SLAB
~~~

# Example

~~~
$ sudo ./kmem_fp.py kmalloc-64 | head -n 15
CACHE             OBJSIZE  OFFSET  NAME
ff49263c41034500       64      32  kmalloc-64
CPU 0 KMEM_CACHE_CPU:
  ff49263cbfa380a0
CPU 0 SLAB:
  SLAB              MEMORY            TOTAL  ALLOCATED  FREE
  ffc1658a4028dec0  ff49263c4a37b000     64         45    19
  FREE / [ALLOCATED] FP (HARDENED)     FP
  [ff49263c4a37b000]
  [ff49263c4a37b040]
  [ff49263c4a37b080]
  [ff49263c4a37b0c0]
  [ff49263c4a37b100]
   ff49263c4a37b140  846020c9d6c1d911  ff49263c4a37b900
  [ff49263c4a37b180]
~~~
