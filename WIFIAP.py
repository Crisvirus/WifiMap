import jinja2
from datetime import datetime
import time

class WIFIAP:
    def __init__(self, NetType, ESSID, BSSID, Info, Channel, Cloaked, Encryption, Decrypted, MaxRate, MaxSeenRate,
     Beacon, LLC, Data, Crypt, Weak, Total, Carrier, Encoding, FirstTime, LastTime, BestQuality, BestSignal, BestNoise, GPSMinLat, GPSMinLon, 
     GPSMinAlt, GPSMinSpd, GPSMaxLat, GPSMaxLon, GPSMaxAlt, GPSMaxSpd, GPSBestLat, GPSBestLon, GPSBestAlt, DataSize, IPType, IP):
        self.NetType = NetType
        self.ESSID = ESSID
        self.BSSID = BSSID
        self.Info = Info
        self.Channel = Channel
        self.Cloaked = Cloaked
        self.Encryption = Encryption
        self.Decrypted = Decrypted
        self.MaxRate = MaxRate
        self.MaxSeenRate = MaxSeenRate
        self.Beacon = Beacon
        self.LLC = LLC
        self.Data = Data
        self.Crypt = Crypt
        self.Weak = Weak
        self.Total = Total
        self.Carrier = Carrier
        self.Encoding = Encoding
        self.FirstTime = FirstTime
        self.LastTime = LastTime
        self.BestQuality = BestQuality
        self.BestSignal = BestSignal
        self.BestNoise = BestNoise
        self.GPSMinLat = GPSMinLat
        self.GPSMinLon = GPSMinLon
        self.GPSMinAlt = GPSMinAlt
        self.GPSMinSpd = GPSMinSpd
        self.GPSMaxLat = GPSMaxLat
        self.GPSMaxLon = GPSMaxLon
        self.GPSMaxAlt = GPSMaxAlt
        self.GPSMaxSpd = GPSMaxSpd
        self.GPSBestLat = GPSBestLat
        self.GPSBestLon = GPSBestLon
        self.GPSBestAlt = GPSBestAlt
        self.DataSize = DataSize
        self.IPType = IPType
        self.IP = IP

    def getHTML(self):
        FirstTime = self.FirstTime.strftime("%d-%m-%y %H:%M:%S")
        LastTime = self.LastTime.strftime("%d-%m-%y %H:%M:%S")
        ESSID = self.ESSID
        BSSID = self.BSSID
        Lat = self.GPSBestLat
        Lon = self.GPSBestLon
        Link = "https://www.google.com/maps/search/?api=1&query="+str(Lat)+","+str(Lon)
        templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template('WIFIAP.html')
        return template.render(FirstTime = FirstTime,LastTime = LastTime, ESSID=ESSID,BSSID = BSSID,Lat=Lat,Lon=Lon,Link=Link)
