import sys
import re
import os

def writeToFile(file, data):
    file.seek(0, os.SEEK_END)
    file.write(data)

def createPatch(lumps, lumpData, filename):
    sizes = []
    for lump in lumps:
        sizes.append(int.from_bytes(lump[4:8], "little"))
    offsets = [12]
    dictOffset = 12
    for size in sizes:
        offsets.append(offsets[-1]+size)
        dictOffset += size
    file = open("{}-hard.wad".format(filename), "wb")
    writeToFile(file, b'PWAD')
    writeToFile(file, len(lumps).to_bytes(4, "little"))
    writeToFile(file, dictOffset.to_bytes(4, "little"))
    for lump in lumpData:
        writeToFile(file, lump)
    for i in range(0, len(lumps)):
        writeToFile(file, offsets[i].to_bytes(4, "little"))
        writeToFile(file, sizes[i].to_bytes(4, "little"))
        writeToFile(file, lumps[i][-8:])

if __name__ == "__main__":
    
    file = open(sys.argv[1], "rb")
    filename = os.path.splitext(os.path.basename(file.name))[0]
    wadType = file.read(4)
    if wadType != b'PWAD':
        print("User error: selected file is not a PWAD")
        input("Press any key to exit")
        quit()
    
    numLumps = int.from_bytes(file.read(4), "little")
    dictOffset = int.from_bytes(file.read(4), "little")
    lumps = []
    file.seek(dictOffset)
    for i in range(0, numLumps):
        lump = file.read(16)
        lumpName = lump[-8:].decode("ascii")
        if re.search("(E[1-9]M[1-9])|(MAP[0-9][0-9])|THINGS|LINEDEFS|SIDEDEFS|VERTEXES|SEGS|SSECTORS|NODES|SECTORS|REJECT|BLOCKMAP", lumpName) != None:
            lumps.append(lump)
    
    lumpData = []    
    for lump in lumps:
        file.seek(int.from_bytes(lump[:4], "little"))
        data = file.read(int.from_bytes(lump[4:8], "little"))
        if lump[-8:].decode("ascii") == "THINGS":
            byteArr = list(data)
            for i in range(8, len(byteArr), 10):
                byteArr[i] &= 0xef
            data = (bytes(byteArr))
        lumpData.append(data)
    
    file.close()
    
    createPatch(lumps, lumpData, filename)