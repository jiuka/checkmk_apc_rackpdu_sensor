#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_apc_rackpdu - Checkmk extension for Dell Rack PDUs
#
# Copyright (C) 2021  Marius Rieder <marius.rieder@scs.ch>
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

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import apc_rackpdu_sensor_temp


def get_value_store():
    return {}


@pytest.mark.parametrize('string_table, result', [
    (
        [[], []], {}
    ),
    (
        [[['SensorName', '60', '59']], [['SensorName', '244', '4']]],
        {'SensorName': [24.4, 4, 60, 59]}
    ),
])
def test_parse_apc_rackpdu_sensor_temp(string_table, result):
    assert apc_rackpdu_sensor_temp.parse_apc_rackpdu_sensor_temp(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (
        {'SensorName': [24.4, 1, 60, 59]},
        []
    ),
    (
        {'SensorName': [24.4, 4, 60, 59]},
        [Service(item='SensorName')]
    ),
])
def test_discovery_apc_rackpdu_sensor_temp(section, result):
    assert list(apc_rackpdu_sensor_temp.discovery_apc_rackpdu_sensor_temp(section)) == result


@pytest.mark.parametrize('item, params, section, result', [
    ('', {}, {}, []),
    (
        'foo', {},
        {'SensorName': [24.4, 4, 60, 59]},
        []
    ),
    (
        'SensorName', {},
        {'SensorName': [24.4, 4, 60, 59]},
        [
            Metric('temp', 24.4, levels=(60.0, 59.0)),
            Result(state=State.OK, summary='Temperature: 24.4°C'),
            Result(state=State.OK, notice='State on device: SensorName'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (used device levels)'),
        ]
    ),
    (
        'SensorName', {},
        {'SensorName': [24.4, 4, 60, 59]},
        [
            Metric('temp', 24.4, levels=(60.0, 59.0)),
            Result(state=State.OK, summary='Temperature: 24.4°C'),
            Result(state=State.OK, notice='State on device: SensorName'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (used device levels)'),
        ]
    ),
])
def test_check_apc_rackpdu_sensor_temp(monkeypatch, item, params, section, result):
    monkeypatch.setattr(apc_rackpdu_sensor_temp, 'get_value_store', get_value_store)
    assert list(apc_rackpdu_sensor_temp.check_apc_rackpdu_sensor_temp(item, params, section)) == result


@pytest.mark.parametrize('params, result', [
    (
        {'levels': (24, 26)},
        Result(state=State.OK, summary='Temperature: 22.4°C'),
    ),
    (
        {'levels': (18, 26)},
        Result(state=State.WARN, summary='Temperature: 22.4°C (warn/crit at 18°C/26°C)'),
    ),
    (
        {'levels': (18, 20)},
        Result(state=State.CRIT, summary='Temperature: 22.4°C (warn/crit at 18°C/20°C)'),
    ),
    (
        {'levels_lower': (20, 18)},
        Result(state=State.OK, summary='Temperature: 22.4°C'),
    ),
    (
        {'levels_lower': (26, 18)},
        Result(state=State.WARN, summary='Temperature: 22.4°C (warn/crit below 26°C/18°C)'),
    ),
    (
        {'levels_lower': (26, 24)},
        Result(state=State.CRIT, summary='Temperature: 22.4°C (warn/crit below 26°C/24°C)'),
    ),
    (
        {'output_unit': 'c'},
        Result(state=State.OK, summary='Temperature: 22.4°C'),
    ),
    (
        {'output_unit': 'f'},
        Result(state=State.OK, summary='Temperature: 72.3°F'),
    ),
    (
        {'output_unit': 'k'},
        Result(state=State.OK, summary='Temperature: 295.5K'),
    ),
])
def test_check_apc_rackpdu_sensor_temp_w_param(monkeypatch, params, result):
    monkeypatch.setattr(apc_rackpdu_sensor_temp, 'get_value_store', get_value_store)
    assert result in list(apc_rackpdu_sensor_temp.check_apc_rackpdu_sensor_temp('SensorName', params, {'SensorName': [22.4, 4, 60, 59]},))
