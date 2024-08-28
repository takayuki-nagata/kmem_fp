#!/usr/bin/env python3

#   kmem_fp.py: a python script to intepret freeponter of a slab cache.
#   Copyright (C) 2024 Takayuki Nagata <tnagata@redhat.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import drgn
from drgn.helpers.linux.slab import find_slab_cache
from drgn.helpers.linux.cpumask import for_each_possible_cpu
from drgn.helpers.linux.percpu import per_cpu_ptr
from drgn.helpers.linux.mm import phys_to_virt, page_to_phys


def swab(data64):
    data64_bytes = int(data64).to_bytes(8, byteorder='big')
    return int.from_bytes(data64_bytes, byteorder='little')


def freelist_ptr(s, ptr, ptr_addr):
    if hasattr(s, "random"):
        return ptr ^ s.random ^ swab(ptr_addr)
    else:
        return ptr


def getfp(prog, s, obj_addr):
    ptr_addr = obj_addr + s.offset
    ptr = prog.read_u64(ptr_addr)
    fp = freelist_ptr(s, ptr, ptr_addr)
    return fp, ptr


def main(argv):
    if len(argv) == 2:
        prog = drgn.program_from_kernel()
        name = argv[1]
    elif len(argv) == 3:
        prog = drgn.program_from_core_dump(argv[1])
        name = argv[2]
    elif len(argv) == 4:
        prog = drgn.program_from_core_dump(argv[1])
        prog.load_debug_info([argv[2]])
        name = argv[3]
    else:
        print(f"usage: {argv[0]} [VMCORE] [VMLINX] SLAB")
        return
    kmem_cache = find_slab_cache(prog, name)
    if kmem_cache is None:
        print(f"No slab:{name} is found")
        return
    size = kmem_cache.size
    offset = kmem_cache.offset
    print("CACHE             OBJSIZE  OFFSET  NAME")
    print(f"{int(kmem_cache):016x}  "
          f"{int(kmem_cache.object_size):>7d}  "
          f"{int(offset):>6d}  "
          f"{name}")
    for cpu in for_each_possible_cpu(prog):
        kmem_cache_cpu = per_cpu_ptr(kmem_cache.cpu_slab, cpu)
        print(f"CPU {cpu} KMEM_CACHE_CPU:")
        print(f"  {int(kmem_cache_cpu):016x}")
        if hasattr(kmem_cache_cpu, "slab"):
            slab = kmem_cache_cpu.slab
        else:
            slab = kmem_cache_cpu.page
        memory = phys_to_virt(page_to_phys(slab))
        total = slab.objects
        freelist = kmem_cache_cpu.freelist
        freeobjs = []
        while freelist:
            freeobjs.append(int(freelist))
            freelist, ptr = getfp(prog, kmem_cache, int(freelist))
        free = len(freeobjs)
        allocated = total - free
        print(f"CPU {cpu} SLAB:")
        print("  SLAB              MEMORY            "
              "TOTAL  ALLOCATED  FREE")
        print(f"  {int(slab):016x}  "
              f"{int(memory):016x}  "
              f"{int(total):>5d}  "
              f"{int(allocated):>9d}  "
              f"{free:>4d}")
        print("  FREE / [ALLOCATED] FP (HARDENED)     FP")
        obj = memory
        for i in range(0, total):
            if int(obj) in freeobjs:
                fp, ptr = getfp(prog, kmem_cache, obj)
                if int(fp) == int(ptr):
                    print(f"   {int(obj):016x}  "
                          f"                  "
                          f"{int(fp):016x}")
                else:
                    print(f"   {int(obj):016x}  "
                          f"{int(ptr):016x}  "
                          f"{int(fp):016x}")
            else:
                print(f"  [{int(obj):016x}]")
            obj += size


if __name__ == "__main__":
    main(sys.argv)
