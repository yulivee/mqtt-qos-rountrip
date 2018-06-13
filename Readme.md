## Create File of fixed filesize
```
dd if=/dev/zero of=1Byte.txt bs=1B count=1
dd if=/dev/zero of=1Byte.txt bs=1 count=1
dd if=/dev/zero of=10Byte.txt bs=10 count=1
dd if=/dev/zero of=100Byte.txt bs=100 count=1
dd if=/dev/zero of=1KByte.txt bs=1K count=1
dd if=/dev/zero of=1500Byte.txt bs=1500 count=1
dd if=/dev/zero of=10KByte.txt bs=10K count=1
dd if=/dev/zero of=100KByte.txt bs=100K count=1
dd if=/dev/zero of=1MByte.txt bs=1M count=1
dd if=/dev/zero of=10MByte.txt bs=10M count=1
dd if=/dev/zero of=100MByte.txt bs=100M count=1
dd if=/dev/zero of=256MByte.txt bs=256M count=1
```

## Most efficient measuring
```
for qos in 0 1 2; do; for cycles in 10 100 1000; do echo "qos: $qos, cycles: $cycles"; python client1.py --file files/100Byte.txt --cycles $cycles --qos_level $qos ; sleep 3; killall python ; done ; done
```
