# *****************************************************************************
#  Copyright (c) 2018 Fraunhofer IEM and others
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#
#  Contributors: Fraunhofer IEM
# *****************************************************************************

SUMMARY = "App IDS"
DESCRIPTION = "Implementation of the STIDE Intrusion Detection Approach with additional BoSC implementation"
HOMEPAGE = "https://github.com/siegeldaniel/mqtt-ids-influx"
LICENSE = "EPL-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=c7cc8aa73fb5717f8291fcec5ce9ed6c"

inherit systemd

#Add a release revision as soon as this is stable
SRCREV = "${AUTOREV}"

RDEPENDS_${PN} = "\
		  python3 \
		  python3-simplejson \
		  python3-paho-mqtt \
		  python3-psutil \
		  sqlite \
		  mosquitto \
		  strace \
      python3-influxdb 
      "

SRC_URI = "\
	   git://github.com/SiegelDaniel/MQTT-IDS-INFLUX.git;protocol=https \
	   file://syscall_tracer.service \
	   file://stide_syscall_formatter.service \
	   file://stide.service \
     file://bosc.service \
     file://influx_adapter.service"

 
SRC_URI[sha256sum] = "dd91a39785fba3129517c44522145afc00a89bce5e2e10f49893637a8e817a29"

#Forces an automatic update whenever the revision of the source code changes.
#Remove this for release builds.
PV = "0.1.0+git${SRCPV}"

S = "${WORKDIR}/git"

do_install () {
  install -d ${D}${bindir}/app-ids

  install -d ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/syscall_tracer.py ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/stide_syscall_formatter.py ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/stide.py ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/BoSC.py ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/influx_adapter.py ${D}${bindir}/app-ids/src
  install -m 0644 ${S}/src/create_LUT.py ${D}${bindir}/app-ids/src
  

  
  #install service files in order for the services to run
  install -d ${D}${systemd_system_unitdir}
  install -m 0644 ${WORKDIR}/syscall_tracer.service ${D}${systemd_system_unitdir}
  install -m 0644 ${WORKDIR}/stide_syscall_formatter.service ${D}${systemd_system_unitdir}
  install -m 0644 ${WORKDIR}/stide.service ${D}${systemd_system_unitdir}
  install -m 0644 ${WORKDIR}/bosc.service ${D}${systemd_system_unitdir}
  install -m 0644 ${WORKDIR}/influx_adapter.service ${D}${systemd_system_unitdir}
}

SYSTEMD_SERVICE_${PN} = "\
			syscall_tracer.service \
			stide_syscall_formatter.service \
			stide.service \
      bosc.service \
      influx_adapter.service"

SYSTEMD_AUTO_ENABLE_${PN} = "disable"
