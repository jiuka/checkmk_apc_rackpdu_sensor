#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_apc_netbotz50_sensor - Checkmk extension for APC netbotz50 Sensors
#
# Copyright (C) 2024  Marius Rieder <marius.rieder@durchmesser.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# .1.3.6.1.4.1.52674.500.4.1.2.1.1.1234567 RELATIVE_HUMIDITY_ALINK_VIRTUAL_pod-XX_sensor-XX_XXXXXXXXXXXX_X-th --> NetBotz50-MIB::humiSensorId.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.2.1234567 32 --> NetBotz50-MIB::humiSensorValue.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.3.1234567 0 --> NetBotz50-MIB::humiSensorErrorStatus.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.4.1234567 Rack Oben --> NetBotz50-MIB::humiSensorLabel.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.5.1234567 ALINK_VIRTUAL_pod-XX_XXXXXXXXXXXX_X-th --> NetBotz50-MIB::humiSensorEncId.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.6.1234567 UNIVERSAL 1 --> NetBotz50-MIB::humiSensorPortId.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.7.1234567 32.0 --> NetBotz50-MIB::humiSensorValueStr.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.8.1234567 32 --> NetBotz50-MIB::humiSensorValueInt.1234567
# .1.3.6.1.4.1.52674.500.4.1.2.1.9.1234567 1234567 --> NetBotz50-MIB::humiSensorIndex.1234567

from cmk.agent_based.v2 import (
    CheckPlugin,
    exists,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
)
from cmk.plugins.lib.humidity import check_humidity

APC_NETBOTZ50_SENSOR_LEVEL_STATES = {
    0: (State.OK, 'Sensor State: Normal'),
    1: (State.OK, 'Sensor State: Info'),
    2: (State.WARN, 'Sensor State: Warning'),
    3: (State.CRIT, 'Sensor State: Error'),
    4: (State.CRIT, 'Sensor State: Critical'),
    5: (State.CRIT, 'Sensor State: Failure'),
}


def parse_apc_netbotz50_sensor_humidity(string_table):
    return {
        label: [int(value), int(status)]
        for label, value, status in string_table
    }


snmp_section_apc_netbotz50_sensor_humidity = SimpleSNMPSection(
    name='apc_netbotz50_sensor_humidity',
    detect=exists('.1.3.6.1.4.1.52674.500.4.1.2.*'),
    parse_function=parse_apc_netbotz50_sensor_humidity,
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.52674.500.4.1.2.1',
        oids=[
            '4',   # NetBotz50-MIB::humiSensorLabel
            '8',   # NetBotz50-MIB::humiSensorValueInt
            '3',   # NetBotz50-MIB::humiSensorErrorStatus
        ]
    ),
)


def discovery_apc_netbotz50_sensor_humidity(section):
    for sensor in section.keys():
        yield Service(item=sensor)


def check_apc_netbotz50_sensor_humidity(item, params, section):
    if item not in section:
        return

    humidity, dev_status = section[item]

    if dev_status in APC_NETBOTZ50_SENSOR_LEVEL_STATES:
        yield Result(
            state=APC_NETBOTZ50_SENSOR_LEVEL_STATES[dev_status][0],
            notice=APC_NETBOTZ50_SENSOR_LEVEL_STATES[dev_status][1]
        )

    yield from check_humidity(
        humidity=humidity,
        params=params,
    )


check_plugin_apc_netbotz50_sensor_humidity = CheckPlugin(
    name='apc_netbotz50_sensor_humidity',
    service_name='%s Humidity',
    discovery_function=discovery_apc_netbotz50_sensor_humidity,
    check_function=check_apc_netbotz50_sensor_humidity,
    check_default_parameters={},
    check_ruleset_name='humidity',
)
