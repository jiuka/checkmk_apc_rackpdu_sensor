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

# .1.3.6.1.4.1.318.1.1.26.10.2.1.1.3.1 SensorName --> PowerNet-MIB::rPDU2SensorTempHumidityConfigName.1
# .1.3.6.1.4.1.318.1.1.26.10.2.1.1.13.1 15 --> PowerNet-MIB::rPDU2SensorTempHumidityConfigHumidityLowThresh.1
# .1.3.6.1.4.1.318.1.1.26.10.2.1.1.14.1 10 --> PowerNet-MIB::rPDU2SensorTempHumidityConfigHumidityMinThresh.1
# .1.3.6.1.4.1.318.1.1.26.10.2.2.1.3.1 SensorName --> PowerNet-MIB::rPDU2SensorTempHumidityStatusName.1
# .1.3.6.1.4.1.318.1.1.26.10.2.2.1.10.1 10 --> PowerNet-MIB::rPDU2SensorTempHumidityStatusRelativeHumidity.1
# .1.3.6.1.4.1.318.1.1.26.10.2.2.1.11.1 2 --> PowerNet-MIB::rPDU2SensorTempHumidityStatusHumidityStatus.1

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

apc_netbotz50_SENSOR_LEVEL_STATES = {
    0: (State.OK, 'Sensor State: Normal'),
    1: (State.OK, 'Sensor State: Info'),
    2: (State.WARN, 'Sensor State: Warning'),
    3: (State.CRIT, 'Sensor State: Error'),
    4: (State.CRIT, 'Sensor State: Critical'),
    5: (State.CRIT, 'Sensor State: Failure'),
}


def parse_apc_netbotz50_sensor_humidity(string_table):
    return {
        label: [int(value) / 10, int(status)]
        for value, status, label in string_table
    }


snmp_section_apc_netbotz50_sensor_humidity = SimpleSNMPSection(
    name='apc_netbotz50_sensor_humidity',
    detect=exists('.1.3.6.1.4.1.52674.500.4.1.2.*'),
    parse_function=parse_apc_netbotz50_sensor_humidity,
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.52674.500.4.1.2.1',
        oids=[
            '2',   # NetBotz50-MIB::humiSensorValue
            '3',   # NetBotz50-MIB::humiSensorErrorStatus
            '4',   # NetBotz50-MIB::humiSensorLabel
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

    if dev_status in apc_netbotz50_SENSOR_LEVEL_STATES:
        yield Result(
            state=apc_netbotz50_SENSOR_LEVEL_STATES[dev_status][0],
            notice=apc_netbotz50_SENSOR_LEVEL_STATES[dev_status][1]
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
