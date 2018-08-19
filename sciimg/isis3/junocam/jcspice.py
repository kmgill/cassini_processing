import spiceypy as spice
import sys
import os

def load_kernels(kernelbase):
    kernels = [
        "juno/kernels/pck/pck00010.tpc",
        "juno/kernels/fk/juno_v12.tf",
        "juno/kernels/ik/juno_junocam_v02.ti",
        "juno/kernels/lsk/naif0012.tls",
        "juno/kernels/sclk/JNO_SCLKSCET.00074.tsc",
        "juno/kernels/spk/spk_ref_180429_210731_180509.bsp",
        "juno/kernels/spk/spk_ref_160226_180221_160226.bsp",
        "juno/kernels/spk/spk_ref_160829_190912_161027.bsp",
        "juno/kernels/spk/spk_ref_161212_210731_170320.bsp",
        "juno/kernels/tspk/de436s.bsp",
        "juno/kernels/tspk/jup310.bsp",
        "juno/kernels/spk/juno_struct_v04.bsp",
        "juno/kernels/ck/juno_sc_rec_180715_180716_v01.bc",
        "juno/kernels/ck/juno_sc_rec_180701_180707_v01.bc",
        "juno/kernels/ck/juno_sc_rec_180624_180630_v01.bc",
        "juno/kernels/ck/juno_sc_rec_180617_180623_v01.bc",
        "juno/kernels/ck/juno_sc_rec_180610_180616_v01.bc",
        "juno/kernels/ck/juno_sc_rec_180603_180609_v01.bc"
    ]

    for file in os.listdir("%s/juno/kernels/spk"%kernelbase):
        if file[-4:] == ".bsp":
            kernels.append("juno/kernels/spk/%s" % (file))

    for file in os.listdir("%s/juno/kernels/ck"%kernelbase):
        if file[-3:] == ".bc":
            kernels.append("juno/kernels/ck/%s" % (file))

    for kernel in kernels:
        spice.furnsh("%s/%s" % (kernelbase, kernel))

