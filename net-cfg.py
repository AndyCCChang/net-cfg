import shlex,os,json,subprocess

OS_RELEASE_PATH = "/etc/os-release"
NETWORK_JSON_PATH = "/root/network.json"
VERSION = 1.1
class OS_RELEASE:
    def __init__(self):
        self.vars = {}
        if os.path.isfile(OS_RELEASE_PATH):
            with open(OS_RELEASE_PATH) as inf:
                for line in inf:
                    name, var = line.partition("=")[::2]
                    self.vars[name.strip()] = var
        return
    def name(self):
        if self.vars.has_key('NAME'):
            return self.vars['NAME']
        else:
            return None

    def version(self):
        if self.vars.has_key('VERSION'):
            return self.vars['VERSION']
        else:
            return ''

    def id(self):
        if self.vars.has_key('ID'):
            return self.vars['ID']
        else:
            return ''
    def isUbuntu(self):
        if self.id().lower().strip()=='ubuntu':
            return True
        return False
    def isRedhat(self):
        if self.id().lower().strip()=='"centos"':
            return True
        return False

    def get(self,key):
        if self.vars.has_key(key):
            return self.vars[key]
        else:
            return ''

class NET:
    def __init__(self,cfg):
        self.cfg = cfg
        self.__name = ''
        self.__iname = ''

        return
    def filename(self):
        if self.name() == '':
            return ''
        ret = 'ifcfg-'+self.name()
        if self.cfg['type'] == 'vlan':
            ret += '.'+self.cfg['vlan_id']
        return ret

    def name(self):
        if self.__name == '':
            if self.cfg.has_key('name'):
                self.__name = self.cfg['name']
            elif self.cfg.has_key('mac'):
                self.__name = get_iface_name(self.cfg['mac'])
            else:
                self.__name = ''
        return self.__name

    def iname(self):
        if self.__iname == '':
            if self.cfg['type'] == 'eth':
                self.__iname = self.name()
            elif self.cfg['type'] == 'vlan':
                self.__iname = self.name()+'.'+self.cfg['vlan_id']
            elif self.cfg['type'] == 'bond':
                self.__iname = self.name()
            else:
                self.__iname = self.name()
        return self.__iname

    def get_script(self):
        ret = ''
        cfg = self.cfg
        if cfg['type'] == 'eth':
#        if 'eth' in self.name():
            ret += 'DEVICE='+self.name()+'\n'
            if cfg['mode'].lower().strip() == 'static':
                ret += 'BOOTPROTO=none'+'\n'
                if cfg.has_key('address'):
                    ret += 'IPADDR='+cfg['address']+'\n'
                if cfg.has_key('netmask'):
                    ret += 'NETMASK='+cfg['netmask']+'\n'
                if cfg.has_key('gateway'):
                    ret += 'GATEWAY '+cfg['gateway']+'\n'                    
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                                    
                if cfg.has_key('dns1'):
                    ret += 'DNS1 '+cfg['dns1']+'\n'                
                if cfg.has_key('dns2'):
                    ret += 'DNS2 '+cfg['dns2']+'\n'                
                if cfg.has_key('dns3'):
                    ret += 'DNS3 '+cfg['dns3']+'\n'                                
                    
                ret += 'USERCTL=no'+'\n'
            elif cfg['mode'].lower().strip() == 'dhcp':
                ret += 'BOOTPROTO=dhcp'+'\n'
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                                    
            ret += 'ONBOOT=yes'+'\n'
        elif cfg['type'] == 'vlan':
#        elif 'vlan' in self.name():
            ret += 'DEVICE='+self.name()+'.'+self.cfg['vlan_id']+'\n'
            if cfg['mode'].lower().strip() == 'static':
                ret += 'BOOTPROTO=none'+'\n'
                if cfg.has_key('address'):
                    ret += 'IPADDR='+cfg['address']+'\n'
                if cfg.has_key('netmask'):
                    ret += 'NETMASK='+cfg['netmask']+'\n'
                if cfg.has_key('gateway'):
                    ret += 'GATEWAY '+cfg['gateway']+'\n'                    
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                                    
                ret += 'USERCTL=no'+'\n'
            elif cfg['mode'].lower().strip() == 'dhcp':
                ret += 'BOOTPROTO=dhcp'+'\n'
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                
            ret += 'ONBOOT=yes'+'\n'
            ret += 'VLAN=yes'+'\n'
        elif cfg['type'] == 'bond':
#        elif 'bond' in self.name():
            ret += 'DEVICE='+self.name()+'\n'
            ret += 'TYPE=Bond'+'\n'
            ret += 'BONDING_MASTER=yes'+'\n'
            if cfg['mode'].lower().strip() == 'static':
                ret += 'BOOTPROTO=none'+'\n'
                if cfg.has_key('address'):
                    ret += 'IPADDR='+cfg['address']+'\n'
                if cfg.has_key('netmask'):
                    ret += 'NETMASK='+cfg['netmask']+'\n'
                if cfg.has_key('gateway'):
                    ret += 'GATEWAY '+cfg['gateway']+'\n'                    
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                                    
                ret += 'USERCTL=no'+'\n'
            elif cfg['mode'].lower().strip() == 'dhcp':
                ret += 'BOOTPROTO=dhcp'+'\n'
                if cfg.has_key('metric'):
                    ret += 'METRIC '+cfg['metric']+'\n'                                    
            ret += 'ONBOOT=yes'+'\n'
            ret += 'BONDING_OPTS=""'+'\n'
            ret += 'NM_CONTROLLED="no"'+'\n'
        return ret
    def get_iface(self):
        ret = ''
        cfg = self.cfg
#        if cfg['type'] == 'eth':
        if 'eth' in self.name():
            self.cfg['type'] = 'eth'
            ret += 'auto '+self.name()+'\n'
            ret += 'iface '+self.name()+' inet '+cfg['mode']+'\n'
            if cfg.has_key('address'):
                ret += 'address '+cfg['address']+'\n'
            if cfg.has_key('netmask'):
                ret += 'netmask '+cfg['netmask']+'\n'
            if cfg.has_key('gateway'):
                ret += 'gateway '+cfg['gateway']+'\n'                
            if cfg.has_key('metric'):
                ret += 'metric '+cfg['metric']+'\n'                
            if cfg.has_key('dns1'):
                ret += 'dns-nameserver '+cfg['dns1']+'\n'                
            if cfg.has_key('dns2'):
                ret += 'dns-nameserver '+cfg['dns2']+'\n'                
            if cfg.has_key('dns3'):
                ret += 'dns-nameserver '+cfg['dns3']+'\n'                                
            if cfg.has_key('bond-master'):
                ret += 'bond-master '+cfg['bond-master']+'\n'                
#        elif cfg['type'] == 'vlan':
        if 'vlan' in self.name():
            self.cfg['type'] = 'vlan'
            ifname =self.name()+'.'+cfg['vlan_id']
            ret += 'auto '+ifname+'\n'
            ret += 'iface '+ifname+' inet '+cfg['mode']+'\n'
            if cfg.has_key('address'):
                ret += 'address '+cfg['address']+'\n'
            if cfg.has_key('netmask'):
                ret += 'netmask '+cfg['netmask']+'\n'
            if cfg.has_key('gateway'):
                ret += 'gateway '+cfg['gateway']+'\n'
            if cfg.has_key('metric'):
                ret += 'metric '+cfg['metric']+'\n'                
            ret += 'vlan-raw-device '+self.name()+'\n'
#        elif cfg['type'] == 'bond':
        if 'bond' in self.name():
            self.cfg['type'] = 'bond'
            ret += 'auto '+self.name()+'\n'
            ret += 'iface '+self.name()+' inet '+cfg['mode']+'\n'
            if cfg.has_key('address'):
                ret += 'address '+cfg['address']+'\n'
            if cfg.has_key('netmask'):
                ret += 'netmask '+cfg['netmask']+'\n'
            if cfg.has_key('gateway'):
                ret += 'gateway '+cfg['gateway']+'\n'
            if cfg.has_key('metric'):
                ret += 'metric '+cfg['metric']+'\n'                                
            if cfg.has_key('bond-mode'):
                ret += 'bond-mode '+cfg['bond-mode']+'\n'
            if cfg.has_key('bond-miimon'):
                ret += 'bond-miimon '+cfg['bond-miimon']+'\n'
            if cfg.has_key('bond-slaves'):
                ret += 'bond-slaves '+cfg['bond-slaves']+'\n'
        else:
            self.cfg['type'] = 'eno'
            ret += 'auto '+self.name()+'\n'
            ret += 'iface '+self.name()+' inet '+cfg['mode']+'\n'
            if cfg.has_key('address'):
                ret += 'address '+cfg['address']+'\n'
            if cfg.has_key('netmask'):
                ret += 'netmask '+cfg['netmask']+'\n'
            if cfg.has_key('gateway'):
                ret += 'gateway '+cfg['gateway']+'\n'
            if cfg.has_key('metric'):
                ret += 'metric '+cfg['metric']+'\n'
            if cfg.has_key('dns1'):
                ret += 'dns-nameserver '+cfg['dns1']+'\n'
            if cfg.has_key('dns2'):
                ret += 'dns-nameserver '+cfg['dns2']+'\n'
            if cfg.has_key('dns3'):
                ret += 'dns-nameserver '+cfg['dns3']+'\n'
            if cfg.has_key('bond-master'):
                ret += 'bond-master '+cfg['bond-master']+'\n'

        return ret


class NET_CFG:
    def __init__(self,cfgfile):
        self.cfgfile = cfgfile
        self.osr = OS_RELEASE()
        return
    def backup(self):
        os.system('mkdir -p ./backup')
        if self.osr.isUbuntu():
            if os.path.isfile('/etc/network/interfaces'):
                os.system('rm -f ./backup/interfaces')
                os.system('cp -f /etc/network/interfaces ./backup/')
        elif self.osr.isRedhat():
            if os.path.isdir('/etc/sysconfig/network-scripts'):
                os.system('rm -fr ./backup/network-scripts')
                os.system('cp -fr /etc/sysconfig/network-scripts/ ./backup/')
        return
    def apply(self):
        if self.osr.isUbuntu():
            intfs,cfgfiles = self.toInterfaces()
        elif self.osr.isRedhat():
            intfs,cfgfiles = self.toScripts()

        for cfgfile in cfgfiles:
            print cfgfile['filename']+'\n'
            print cfgfile['path']+'\n'
            print cfgfile['data']+'\n'
            os.system('mkdir -p '+cfgfile['path'])
            with open(cfgfile['path']+cfgfile['filename'], "wb") as outf:
                outf.write(cfgfile['data'])

        if self.osr.isUbuntu():
            os.system('modprobe 8021q')
            for intf in intfs:
                os.system('ifdown '+intf)
                os.system('ifup '+intf)
        elif self.osr.isRedhat():
            for intf in intfs:
                os.system('ifdown '+intf)
                os.system('ifup '+intf)
        return

    def parse(self):
        self.configures = {}
        try:
            if os.path.isfile(self.cfgfile):
                with open(self.cfgfile, 'r') as inf:
                    self.configures = json.load(inf)['network']
            else:
                return False
        except Exception as e:
            return False
        return True
    def toInterfaces(self):
        ret = []
        networks = []
        intfs = []
        for cfg in self.configures:
            net = NET(cfg)
            networks.append(net)
        data = ''
        for net in networks:
            data += net.get_iface()+'\n'
            intfs.append(net.iname())
        ret.append({'filename':'interfaces','path':'/etc/network/','data':data})
        return intfs,ret

    def toScripts(self):
        ret = []
        networks = []
        intfs = []
        for cfg in self.configures:
            net = NET(cfg)
            networks.append(net)
        for net in networks:
            ret.append({'filename':net.filename(),'path':'/etc/sysconfig/network-scripts/','data':net.get_script()})
            intfs.append(net.iname())
            print net.filename()
            print net.get_script()
        return intfs,ret

    def show(self):
        return

def get_iface_name(mac):
    cmd = shlex.split('find /sys/class/net -mindepth 1 -maxdepth 1 ! -name lo -printf "%P= " -execdir cat {}/address \;')
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    for line in out.splitlines():
        name, addr = line.partition("=")[::2]
        if mac.lower() == addr.lower().strip():
            return name.lower().strip()
    return ''




if __name__ == "__main__":
    netcfg = NET_CFG(NETWORK_JSON_PATH)
    if netcfg.parse():
        netcfg.backup()
        netcfg.apply()

