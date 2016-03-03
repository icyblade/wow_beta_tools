import urllib, urllib2, re, logging
from config import DEBUG_LEVEL, NGDP_HOST

class NGDP:
    def __init__(self, program_code):
        self.program_code = program_code
        self.ngdp_host = NGDP_HOST
        self.opener = urllib2.build_opener()
        self.logger = self.configure_logger()
        self.cdn = None
        self.version = None
        
    def configure_logger(self, file=False, stdout=True):
        logger = logging.getLogger(__name__)
        logger.setLevel(DEBUG_LEVEL)
        if file:
            if not os.path.exists('./log/'):
                os.mkdir('./log/')
            file_handler = logging.FileHandler(
                'log/%s.log' % os.path.basename(__file__)
            )
            file_handler.setLevel(DEBUG_LEVEL)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(processName)s: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(file_handler)

        if stdout:
            stdout_handler = logging.StreamHandler()
            stdout_handler.setLevel(DEBUG_LEVEL)
            stdout_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(processName)s: %(message)s',
                '%H:%M:%S'
            ))
            logger.addHandler(stdout_handler)
        return logger
        
    def set_cdn(self, region):
        try:
            self.cdn = self.get_cdns()[region]
        except KeyError:
            print('Invalid region')
        
    def get_cdns(self, raw=False):
        url = '{self.ngdp_host}/{self.program_code}/cdns'.format(
            self = self,
        )
        self.logger.debug(url)
        r = self.opener.open(url)
        html = r.read()
        if raw: return html
        cdns = {}
        for line in html.split('\r\n')[1:]:
            if line:
                lst = line.split('|')
                cdns[lst[0]] = CDN(line)
        return cdns
    
    def set_version(self, region):
        try:
            self.version = self.get_versions()[region]
        except KeyError:
            print('Invalid region')

    def get_versions(self, raw=False):
        url = '{self.ngdp_host}/{self.program_code}/versions'.format(
            self = self,
        )
        self.logger.debug(url)
        r = self.opener.open(url)
        html = r.read()
        if raw: return html
        versions = {}
        for line in html.split('\n')[1:]:
            if line:
                lst = line.split('|')
                versions[lst[0]] = Versions(line)
        return versions

    def get_build_config(self):
        hash = self.version.build_config
        url = 'http://{self.cdn.host}/{self.cdn.path}/config/\
{first_two_hex}/{second_two_hex}/{hash}'.format(
            self = self,
            first_two_hex = hash[0:2],
            second_two_hex = hash[2:4],
            hash = hash,
        )
        self.logger.debug(url)
        r = self.opener.open(url)
        return Build(r.read())
        
    def get_hash(self, hash, path_type='config', index=False):
        url = 'http://{self.cdn.host}/{self.cdn.path}/\
{path_type}/{first_two_hex}/{second_two_hex}/{hash}{index}'.format(
            self = self,
            path_type = path_type,
            first_two_hex = hash[0:2],
            second_two_hex = hash[2:4],
            hash = hash,
            index = '.index' if index else ''
        )
        self.logger.debug(url)
        try:
            r = self.opener.open(url)
            data = r.read()
            return data
        except urllib2.HTTPError as e:
            self.logger.warning('HTTPError %s' % e.code)  
            return None

    def get_hash_bruteforce(self, hash):
        ret = {}
        for path_type in ['config', 'data']:
            for index in [True, False]:
                data = self.get_hash(hash, path_type, index)
                if data != None:
                    try:
                        ret[path_type][index]
                    except ValueError:
                        ret[path_type] = {}
                    ret[path_type][index] = data
        return ret
    
    def get_cdn_config(self, raw=False):
        hash = self.version.cdn_config
        url = 'http://{self.cdn.host}/{self.cdn.path}/config/\
{first_two_hex}/{second_two_hex}/{hash}'.format(
            self = self,
            first_two_hex = hash[0:2],
            second_two_hex = hash[2:4],
            hash = hash,
        )
        self.logger.debug(url)
        r = self.opener.open(url)
        html = r.read()
        if raw: return html
        result = {}
        for i in html.split('\n'):
            if i != '' and not i.startswith('#'):
                tmp = i.split(' = ')
                result[tmp[0]] = tmp[1].split(' ')
        return result
        
class Build:
    """Build config
    Something like this:
    # Build Configuration

    root = 72868c732efa9d779bb8b4a741066626
    download = 1891eb50ad0dbdb674408e771691b9ad
    install = 1c8c727ccb75b2bf5da5bd9c986a81fe
    encoding = 727ad3e4889a7904feb6d3c45499d65f b13b9c416f6296a0eb21289825d085b
    d
    encoding-size = 57424269 57401741
    build-name = WOW-21021patch7.0.1_Beta
    build-playbuild-installer = ngdptool_casc2
    build-product = WoW
    build-uid = wow_beta
    patch = c082f088758f98f9056a5a5c1e127055
    patch-size = 962433
    patch-config = 96b6fabbb9d599d78f9ad24f04adf8c1
    """
    def __init__(self, s):
        self.raw = s
        for row in s.split('\n'):
            if row != '' and not row.startswith('#'):
                tmp = row.split(' = ')
                setattr(self, tmp[0].replace('-', '_'), tmp[1].split(' '))
   
class Patch:
    """Patch Configuration
    Something like this:
    # Patch Configuration

    patch-entry = encoding 
    727ad3e4889a7904feb6d3c45499d65f 57424269 
    b13b9c416f6296a0eb21289825d085bd 57401741
    b:{22=n,36731=z,268512=n,34369536=n,176352=n,22573056=n,*=z} 
    63bb28b648996c73a8f9bf2c0d1040f6 57149541 
    b3375039b22ec41fce9d505fc4dedccc 1995099 
    171673fb92bc8734213e7a04fa5af682 57426117
    5e89a734f3c878c2146f3785b800e577 511980
    e6aa3fd868c5d0db2c4297006cf98e11 57426117 
    dd4579b5982eb82a61ca3445b018a940 499210
    patch-entry = install 
    1c8c727ccb75b2bf5da5bd9c986a81fe 22365 
    43f8c39b9fb26f4a54436e1ccca724a2 21796 
    b:{818=z,21547=n} 
    09b834877afd0ff8eee05bf48d7843cb 22365 
    db8446e7e6808abab4a672be60cfd028 455 
    46ab9d10f08e0f48ed57c6d4d472ca6c 22365 
    b52c52d5cac3046c52d74be4690c64a1 420 
    2ed87af5044ed167e1fbc9d888ad3fdb 22365 
    af3e92148b32b2efba711743c4af6aac 420
    patch-entry = download 
    1891eb50ad0dbdb674408e771691b9ad 25923662 
    4bdda50b0b3c7f0dcc2f2ff00375b744 23352044 
    b:{11=n,23342358=n,2581293=z} 
    8c1954fd6333e56374878a658223a7c2 25797793 
    f46d278bd5bd61918d55a5343e1337c3 574176 
    4d180dac5472ba0fc22f706f8f763b75 25923662 
    3c92b78781d9aba50fa9516fc2f90e6c 28693 
    f2a360c8fca66047c8c2721be5e0bc8c 25923662 
    d570386a25689068dedb1fa9b44d8bf5 26585
    patch = c082f088758f98f9056a5a5c1e127055
    """
    def __init__(self, s):
        self.raw = s
   
class CDN:
    """
    Something like this:
    cn|tpr/wow|client01.pdl.wow.battlenet.com.cn client02.pdl.wow.battlenet.com.cn client03.pdl.wow.battlenet.com.cn client04.pdl.wow.battlenet.com.cn blzddist1-a.akamaihd.net'
    """
    def __init__(self, s):
        self.raw = s
        lst = s.split('|')
        self.name = lst[0]
        self.path = lst[1]
        self.cdns = lst[2].split(' ')
        self.host = self.cdns[0]

class Versions:
    """
    Something like this:
    cn|d420d22fc20ff97128c56620532b4628|46b8e1bcb8549101a27df62f74db70cd|21021|7.0.1.21021
    """
    def __init__(self, s):
        self.raw = s
        self.region, self.build_config, self.cdn_config, self.build_id, self.versions_name = s.split('|')
