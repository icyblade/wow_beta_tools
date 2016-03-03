import re, os, glob
from NGDP import NGDP, Build

ngdp = NGDP('wow_beta')
ngdp.set_cdn('us')
ngdp.set_version('us')
print('Current version: {ngdp.version.versions_name}'.format(ngdp=ngdp))
cdn_config = ngdp.get_cdn_config()

for i, hash in enumerate(cdn_config['builds']):
    if i >= 5:
        break
    b = Build(ngdp.get_hash(hash))
    print('%50s %10s' % (b.build_name[0], b.patch_size[0]))
