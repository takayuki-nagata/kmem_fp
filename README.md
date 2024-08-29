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

# Background

Free pointer obfuscation is introduced in [2482ddec670f](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2482ddec670fb83717d129012bc558777cb159f7) ("mm: add SLUB free list pointer obfuscation"), and free pointers cannot be read easily from free slub objects if `CONFIG_SLAB_FREELIST_HARDENED` is enabled. In addition, the free pointer is relocated to the middle of the object due to [3202fa62fb43](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3202fa62fb43087387c65bfa9c100feffac74aa6) ("slub: relocate freelist pointer to middle of object"). Its order is also randomised with enabling `CONFIG_SLAB_FREELIST_RANDOM` introduced in [210e7a43fa90](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=210e7a43fa905bccafa9bb5966fba1d71f33eb8b) ("mm: SLUB freelist randomization").

`kmem_fp.py` is created to aim at understanding of the free pointers with above commit/configurations.
