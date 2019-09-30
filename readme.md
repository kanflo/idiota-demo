## Idiota, a silly way to deploy firmware upgrades

Hi! If you are looking for an industrial grade firmware update solution, look elsewhere. I wrote one some time ago but it's locked in a git at a Fortune 500 company.

This is the insecure lite version given the time I had to implement an upgrade solution for the nodes in my home. All firmware images will live on a central upgrade server and nodes will from time to time query the server for the latest and greatest firmware.

A firmware is identified by the sha256 of the binary and a node will know its running sha256. On calling the server, the nodes will provide their node IDs, node type (opendps, esp32cam, ...) and hardware revision and from this the server responds with the latest sha256. This allows for tieing a debug firmware to a special node while the rest of the eg. esp32cams run another firmware.

See ```ota_demo.c``` for an example. Build an flash an ESP8266:

```
make IDIOTA_SERVER="172.16.3.113" NODE_ID=42
make flash
```

Note that as the sha256 currently is not embedded in the firmware, the node will not know the sha256 when flashed via the uart.

Now start the server:

```
./otaserv.py firmwares.db
```

Upload a firmware to the server:

```
./otatool.py -t esp32cam localhost ../firmware/idiota-test.bin
```

The node will download and flash the latest firmware. In this case it happens to be the same firmware it is currently running. Make a change to a print, build and upload again.
