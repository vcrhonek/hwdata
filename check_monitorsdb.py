#!/usr/bin/python

f = open("MonitorsDB", "r")
out = open("MonitorsDBOut", "w")

monIds = dict()

for line in f.readlines():
    if len(line.strip()) and not line.strip().startswith('#'):
        values = map(lambda x: x.strip(), line.split(';'))
        if len(values) < 5:
            print "This line contains two few values\n%s" % line
        manufacturer = values[0]
        model = values[1]
        monId = values[2]
        vGh = values[3]
        hGh = values[4]
        if len(manufacturer) == 0:
            print "This line doesn't contain Manufacturer\t%s" % line
            continue
        if len(model) == 0:
            print "This line contains empty model\t%s" % line
            continue
        if len(monId) == 0 or monId == "0":
            print "This line contains empty monitor Id\n%s" % line
            continue
        if len(vGh) == 0 or len(hGh) == 0:
            print "This line contains wrong Gh\t%s" % line
            continue
        if monIds.has_key(monId):
            print "Two line have the same monitor Ids\n%s%s" % (monIds[monId], line)
            continue
        else:
            monIds[monId] = line
    out.write(line)
f.close()
out.close()

