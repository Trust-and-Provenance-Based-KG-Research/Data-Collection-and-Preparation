# Data-Collection-and-Preparation






## Prerequisites Setup 

### Requirements

- GraphDB


### Install GraphDB dependencies 


Java 11+ (JDK or JRE) if you’re running the standalone server. (Not required when using Docker.)
Default Workbench URL: http://localhost:7200/

### Option A — Standalone Server (Linux/macOS/Windows)

- Download & unpack the GraphDB distribution (graphdb-<version>.zip), then open the unpacked folder.
- Start the server from the distribution’s bin/ directory:

```
# macOS/Linux
./bin/graphdb

# Windows (PowerShell)
.\bin\graphdb.bat
```
When it starts, open http://localhost:7200/
 to access the Workbench

(FYI) Default data locations
If you don’t set graphdb.home, defaults are:

- Standalone: the distribution directory you unzipped.

- Other installs: macOS ~/Library/Application Support/GraphDB, Windows \Users\<username>\AppData\Roaming\GraphDB, Linux/Unix ~/.graphdb. 
graphdb.ontotext.com

Stop the server
- Press Ctrl+C in the terminal, or send kill <pid> (avoid -9 to allow a clean shutdown).


### Option B — Docker (fastest to get started)

```
# Create local folders for data and imports
mkdir -p ./graphdb-data ./graphdb-import

# Run GraphDB (exposes http://localhost:7200)
docker run --name graphdb \
  -p 7200:7200 \
  -v "$PWD/graphdb-data:/opt/graphdb/home" \
  -v "$PWD/graphdb-import:/root/graphdb-import" \
  ontotext/graphdb:10.7.0
```

- The container stores data at /opt/graphdb/home; the default Workbench import dir is $HOME/graphdb-import (mapped above to /root/graphdb-import). 
GitHub

- You can pass properties via env var or CLI:
```
docker run -p 7200:7200 \
  -e GDB_JAVA_OPTS="-Dgraphdb.workbench.importDirectory=/var/graphdb/import" \
  ontotext/graphdb:10.7.0
```

Stop & remove when done:
```
docker stop graphdb && docker rm graphdb
```

