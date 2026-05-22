# modules/attacks/evil_twin.py
import time
import logging
import threading

logger = logging.getLogger(__name__)

class EvilTwinAttack:
    """
    Evil Twin Attack Module
    Creates a fake Access Point to lure clients.
    """
    def __init__(self, interface, packet_engine):
        self.interface = interface
        self.packet_engine = packet_engine
        self.running = False
        self.fake_ap_process = None
        
    def start(self, ssid, channel=6):
        """
        Start the Evil Twin AP
        """
        self.running = True
        logger.info(f"[Attack] Starting Evil Twin '{ssid}' on channel {channel}")
        
        if hasattr(self.packet_engine, "_simulate_traffic"):
            # Simulation Mode: Inject fake network into MockPacketEngine
            self._simulate_evil_twin(ssid, channel)
        else:
            # Real Mode: Would start hostapd / airbase-ng
            logger.warning("Real Evil Twin requires hostapd (not implemented in python-only mode)")
            
    def _simulate_evil_twin(self, ssid, channel):
        """Inject a fake network into the mock engine"""
        fake_bssid = "DE:AD:BE:EF:CA:FE"
        
        # Access the networks dict directly on the mock engine
        if hasattr(self.packet_engine, "networks"):
            self.packet_engine.networks[fake_bssid] = {
                'ssid': ssid,
                'channel': channel,
                'crypto': {'OPN'},
                'bssid': fake_bssid,
                'signal': -30,  # Very strong signal
                'clients': set()
            }
            logger.info(f"[Simulation] Injected fake AP: {ssid} ({fake_bssid})")
            
            # Simulate a client connecting
            threading.Thread(target=self._simulate_victim, args=(fake_bssid,)).start()
            
    def _simulate_victim(self, bssid):
        """Simulate a victim connecting to the evil twin"""
        time.sleep(5)
        if hasattr(self.packet_engine, "clients"):
            victim_mac = "VI:CT:IM:00:11:22"
            self.packet_engine.clients[victim_mac] = {
                'mac': victim_mac,
                'bssid': bssid,
                'probed_ssids': set(),
                'packets': 0
            }
            self.packet_engine.networks[bssid]['clients'].add(victim_mac)
            logger.info(f"[Simulation] VICTIM CONNECTED: {victim_mac}")
            
    def stop(self):
        self.running = False
        logger.info("[Attack] Evil Twin stopped")
