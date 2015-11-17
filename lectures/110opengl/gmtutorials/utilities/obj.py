
import os, sys, string
import numpy as N

def readOBJ(filename):
    pos = []
    norm = []
    uv = []
    verts = []
    with open(os.path.join("..","objs",filename)) as fp:
        for line in fp:
            splitline = string.split(line)
            if splitline[0] == "v":
                pos.append([float(x) for x in splitline[1:4]])
            elif splitline[0] == "vn":
                norm.append([float(x) for x in splitline[1:4]])
            elif splitline[0] == "vt":
                uv.append([float(x) for x in splitline[1:3]])
    with open(os.path.join("..","objs",filename)) as fp:
        for line in fp:
            splitline = string.split(line)
            if splitline[0] == "f":
                p1 = [int(x)-1 for x in string.split(splitline[1],"/")]
                p2 = [int(x)-1 for x in string.split(splitline[2],"/")]
                p3 = [int(x)-1 for x in string.split(splitline[3],"/")]
                for p in (p1,p2,p3):
                    verts.extend(pos[p[0]] + [1])
                    verts.extend(norm[p[2]] + [0])
                    verts.extend([1,0,0,0])
                    verts.extend([0,0,1,0])
                    verts.extend(uv[p[1]])
    return (N.array(verts, dtype=N.float32),
            N.array(range(0, len(verts)/18), dtype=N.uint16))
