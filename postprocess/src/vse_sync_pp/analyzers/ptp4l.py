### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyze ptp4l log messages"""
from .analyzer import TimeErrorAnalyzerBase
from .analyzer import TimeDeviationAnalyzerBase
from .analyzer import MaxTimeIntervalErrorAnalyzerBase


class TimeErrorAnalyzer(TimeErrorAnalyzerBase):
    """Analyze time error for ptp4l boundary clock"""
    id_ = 'ptp4l/time-error'
    parser = id_
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class TimeDeviationAnalyzer(TimeDeviationAnalyzerBase):
    """Analyze time deviation for ptp4l boundary clock"""
    id_ = 'ptp4l/time-deviation'
    parser = 'ptp4l/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class MaxTimeIntervalErrorAnalyzer(MaxTimeIntervalErrorAnalyzerBase):
    """Analyze max time interval error for ptp4l boundary clock"""
    id_ = 'ptp4l/mtie'
    parser = 'ptp4l/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class PortStateAnalyzer:
    """Analyze ptp4l port state transitions"""
    id_ = 'ptp4l/port-state'
    parser = id_

    def test(self, data):
        """Analyze port state transition data for boundary clock behavior"""
        if not data:
            return False, "No port state data available"
        
        # Check for proper BC state transitions
        expected_slave_transitions = ['INITIALIZING', 'LISTENING', 'UNCALIBRATED', 'SLAVE']
        expected_master_transitions = ['INITIALIZING', 'LISTENING', 'MASTER']
        
        slave_ports = []
        master_ports = []
        
        for entry in data:
            port = entry.port
            to_state = entry.to_state
            
            if to_state == 'SLAVE':
                slave_ports.append(port)
            elif to_state == 'MASTER':
                master_ports.append(port)
        
        has_slave = len(slave_ports) > 0
        has_master = len(master_ports) > 0
        
        if has_slave and has_master:
            return True, f"Boundary Clock operating correctly: Slave ports {slave_ports}, Master ports {master_ports}"
        elif has_slave and not has_master:
            return True, f"Operating as Ordinary Clock (slave): ports {slave_ports}"
        elif has_master and not has_slave:
            return True, f"Operating as Ordinary Clock (master): ports {master_ports}"
        else:
            return False, "No ports reached operational state (SLAVE or MASTER)" 