---
title: "Streamsets - Java Heap Space Configuration and Monitoring"
description: "Steps to increase Java Heap Memory for Streamsets via Cloudera Manager, clean up redundant configs, restart services, and verify memory settings using process inspection tools (ps, jmap, jconsole)."
tags:
  - streamsets
  - java heap
  - memory configuration
  - cloudera manager
  - jmap
  - jconsole
  - troubleshooting
  - performance tuning
  - gc logs
  - bigstreamer
  - heap dump
  - xmx
  - xms
---
# Streamsets - Java Heap Space
Streamsets Java Heap Memory was increased due to [this](https://metis.ghi.com/obss/oss/sysadmin-group/support/-/issues/102#ndef_95081) issue.
This guide documents the resolution of a Java Heap Space issue on the Streamsets Data Collector. It includes steps to increase heap size using Cloudera Manager, remove deprecated safety valve overrides, verify JVM options with `ps`, and inspect memory usage via `jmap` and `jconsole`. Applicable for performance tuning and troubleshooting OOM errors on Streamsets pipelines.
## Actions Taken
This procedure outlines how to address Streamsets memory issues by increasing the Java heap size and verifying runtime memory settings.
1. Configure Java Options from CLoudera Manager
   ```bash
   cluster -> Streamsets -> Configuration -> Java options: `-Xmx32768m -Xms32768m -server -XX:-OmitStackTraceInFastThrow`
   ```
2. Remove old configuration
   ```bash
   cluster-> Streamsets -> Configuration -> Data Collector Advanced Configuration Snippet (Safety Valve) for sdc-env.sh
   ```
   ```bash
   #Remove the following line, if exists
   export SDC_JAVA_OPTS="-Xmx16384m -Xms16384m -server -XX:-OmitStackTraceInFastThrow ${SDC_JAVA_OPTS}"
   ```
3. Restart Streamsets
   ```bash
   cluster -> Streamsets -> Restart
   ```
4. Check Streamsets Process Options
   ```bash
   [root@un2 ~]# ps -ef | grep -i streamsets | grep -i xmx

   sdc      24898 24873 45 12:45 ?        00:40:11 /usr/java/default/bin/java -classpath /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libexec/bootstrap-libs/main/streamsets-datacollector-bootstrap-3.21.0.jar:/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/root-lib/* -Djava.security.manager -Djava.security.policy=file:///var/run/cloudera-scm-agent/process/147717-streamsets-DATACOLLECTOR/sdc-security.policy -Xmx1024m -Xms1024m -server -XX:-OmitStackTraceInFastThrow -Xmx32768m -Xms32768m -server -XX:-OmitStackTraceInFastThrow -Dsdc.dist.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0 -Dsdc.resources.dir=/var/lib/sdc/resources -Dsdc.hostname=un2.bigdata.abc.gr -Dsdc.conf.dir=/var/run/cloudera-scm-agent/process/147717-streamsets-DATACOLLECTOR -Dsdc.data.dir=/shared/sdc/data -Dsdc.log.dir=/shared/sdc/log/ -javaagent:/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libexec/bootstrap-libs/main/streamsets-datacollector-bootstrap-3.21.0.jar -Dsdc.libraries.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/streamsets-libs -Dsdc.librariesExtras.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/streamsets-libs-extras -Dsdc.rootLib.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/root-lib -Dsdc.bootstrapLib.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libexec/bootstrap-libs -Dsdc.apiLib.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/api-lib -Dsdc.asterClientLib.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/aster-client-lib -Dsdc.containerLib.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/container-lib -Dsdc.libsCommon.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libs-common-lib -Dsdc.userLibs.dir=/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/user-libs -XX:+UseConcMarkSweepGC -XX:+UseParNewGC -Djdk.nio.maxCachedBufferSize=262144 -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/shared/sdc/log//gc.log -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/shared/sdc/log//sdc_heapdump_1675334705.hprof -XX:ErrorFile=/shared/sdc/log//hs_err_1675334705.log com.streamsets.pipeline.BootstrapMain -mainClass com.streamsets.datacollector.main.DataCollectorMain -apiClasspath /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/api-lib/*.jar -containerClasspath /var/run/cloudera-scm-agent/process/147717-streamsets-DATACOLLECTOR:/opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/container-lib/*.jar -streamsetsLibrariesDir /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/streamsets-libs -userLibrariesDir /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/user-libs -configDir /var/run/cloudera-scm-agent/process/147717-streamsets-DATACOLLECTOR -libsCommonLibDir /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/libs-common-lib -streamsetsLibrariesExtraDir /opt/cloudera/parcels/STREAMSETS_DATACOLLECTOR-3.21.0/streamsets-libs-extras
   ```
   > Tip: When defining Java configuration options, avoid defining duplicate options. If you do define duplicates, the last option passed to the JVM usually takes precedence.
5. Check Max Java Heap Space for Streamsets via jconsole or jmap
### jconsole
   > Needs additional Java Options: -Dcom.sun.management.jmxremdef -Dcom.sun.management.jmxremdef.port=3333 -Dcom.sun.management.jmxremdef.local.only=false -Dcom.sun.management.jmxremdef.authenticate=false -Dcom.sun.management.jmxremdef.ssl=false"
   ```bash
   [root@un2 ~]# /usr/java/latest/bin/jconsole
   ```
   Select `com.streamsets.pipeline.BootstrapMain`,  `Connect` and check the metrics.
### jmap
   ```bash
   jmap -heap <pid>
   #output example
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
Reference: https://docs.streamsets.com/platform-datacollector/latest/datacollector/UserGuide/Configuration/DCEnvironmentConfig.html