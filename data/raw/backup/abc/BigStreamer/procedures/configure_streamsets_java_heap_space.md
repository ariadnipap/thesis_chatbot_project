# Streamsets - Java Heap Space

## Description
Streamsets Java Heap Memory was increased due to [this](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/issues/102#ndef_95081) issue.

## Prerequisites
- Access to Cloudera Manager for configuration changes.
- SSH access to the system where Streamsets is running.
- Knowledge of Java configuration settings.

## Procedure Steps

### 1. Configure Java Options from Cloudera Manager
- Update Java options:
  ```bash
  cluster -> Streamsets -> Configuration -> Java options: `-Xmx32768m -Xms32768m -server -XX:-OmitStackTraceInFastThrow`
  ```

### 2. Remove Old Configuration
- Navigate to:
  ```bash
  cluster-> Streamsets -> Configuration -> Data Collector Advanced Configuration Snippet (Safety Valve) for sdc-env.sh
  ```
- Remove the following line if it exists:
  ```bash
  export SDC_JAVA_OPTS="-Xmx16384m -Xms16384m -server -XX:-OmitStackTraceInFastThrow ${SDC_JAVA_OPTS}"
  ```

### 3. Restart Streamsets
- Restart the Streamsets service:
  ```bash
  cluster -> Streamsets -> Restart
  ```

### 4. Check Streamsets Process Options
- Verify that the process is running with the correct Java options:
  ```bash
  [root@un2 ~]# ps -ef | grep -i streamsets | grep -i xmx
  ```
- Example output:
  ```
  sdc      24898 24873 45 12:45 ?        00:40:11 /usr/java/default/bin/java -classpath /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libexec/bootstrap-libs/main/streamsets-datacollector-bootstrap-3.21.0.jar:/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/root-lib/* -Djava.security.manager -Djava.security.policy=file:///var/run/cloudera-scm-agent/process/147717-streamsets-DATACOLLECTOR/sdc-security.policy -Xmx1024m -Xms1024m -server -XX:-OmitStackTraceInFastThrow -Xmx32768m -Xms32768m -server -XX:-OmitStackTraceInFastThrow ...
  ```

### 5. Check Max Java Heap Space for Streamsets
#### **Using jconsole**
- Needs additional Java options:
  ```
  -Dcom.sun.management.jmxremdef -Dcom.sun.management.jmxremdef.port=3333 -Dcom.sun.management.jmxremdef.local.only=false -Dcom.sun.management.jmxremdef.authenticate=false -Dcom.sun.management.jmxremdef.ssl=false
  ```
- Run:
  ```bash
  [root@un2 ~]# /usr/java/latest/bin/jconsole
  ```
- Select `com.streamsets.pipeline.BootstrapMain`, click `Connect`, and check the metrics.

#### **Using jmap**
- Run:
  ```bash
  jmap -heap <pid>
  ```
- Example output:
  ```bash
  [root@un2 ~]# jmap -heap 24898
  Attaching to process ID 24898, please wait...
  Debugger attached successfully.
  Server compiler detected.
  JVM version is 25.181-b13

  using parallel threads in the new generation.
  using thread-local object allocation.
  Concurrent Mark-Sweep GC

  Heap Configuration:
     MinHeapFreeRatio         = 40
     MaxHeapFreeRatio         = 70
     MaxHeapSize              = 34359738368 (32768.0MB)
     NewSize                  = 2442723328 (2329.5625MB)
     MaxNewSize               = 2442723328 (2329.5625MB)
     OldSize                  = 31917015040 (30438.4375MB)
     NewRatio                 = 2
     SurvivorRatio            = 8
     MetaspaceSize            = 21807104 (20.796875MB)
     CompressedClassSpaceSize = 1073741824 (1024.0MB)
     MaxMetaspaceSize         = 17592186044415 MB
     G1HeapRegionSize         = 0 (0.0MB)

  Heap Usage:
  New Generation (Eden + 1 Survivor Space):
     capacity = 2198470656 (2096.625MB)
     used     = 1493838840 (1424.6357345581055MB)
     free     = 704631816 (671.9892654418945MB)
     67.94900063473942% used
  Eden Space:
     capacity = 1954217984 (1863.6875MB)
     used     = 1433160568 (1366.768424987793MB)
     free     = 521057416 (496.91907501220703MB)
     73.33678124620104% used
  From Space:
     capacity = 244252672 (232.9375MB)
     used     = 60678272 (57.8673095703125MB)
     free     = 183574400 (175.0701904296875MB)
     24.84241891937215% used
  To Space:
     capacity = 244252672 (232.9375MB)
     used     = 0 (0.0MB)
     free     = 244252672 (232.9375MB)
     0.0% used
  concurrent mark-sweep generation:
     capacity = 31917015040 (30438.4375MB)
     used     = 12194092928 (11629.193237304688MB)
     free     = 19722922112 (18809.244262695312MB)
     38.20561826573617% used

  57229 interned Strings occupying 8110512 bytes.
  ```

## Actions Taken / Expected Output
- Java heap memory was increased successfully.
- Streamsets should now run with updated memory configurations.
- Running `ps -ef | grep -i streamsets | grep -i xmx` should confirm the new Java options.
- The memory allocation can be validated via `jconsole` or `jmap`.

## Notes and Warnings
> When defining Java configuration options, avoid defining duplicate options.  
> If duplicate options are set, the last option passed to the JVM usually takes precedence.

## Affected Systems / Scope
- Streamsets Data Collector
- Cloudera Manager Configuration

## Troubleshooting / Error Handling
- If Streamsets fails to start, check the logs for error messages:
  ```bash
  tail -f /var/log/streamsets/streamsets.log
  ```
- If memory settings do not apply correctly, recheck the configuration in Cloudera Manager.
- Restart the Streamsets service manually:
  ```bash
  systemctl restart streamsets
  ```

## References
- [Streamsets Documentation on Configuration](https://docs.streamsets.com/platform-datacollector/latest/datacollector/UserGuide/Configuration/DCEnvironmentConfig.html)

