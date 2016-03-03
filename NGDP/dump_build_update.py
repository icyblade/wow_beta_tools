import re, os, glob
from NGDP import NGDP, Build

def main():
    ngdp = NGDP('wow_beta')
    ngdp.set_cdn('us')
    ngdp.set_version('us')
    cdn_config = ngdp.get_cdn_config()

    b = Build(ngdp.get_hash(cdn_config['builds'][1]))
    print(b.build_name[0])
    patch_config = ngdp.get_hash(b.patch_config[0])
    if not os.path.exists('./download/'): os.makedirs('./download')
    if not os.path.exists('./download/data/'): os.makedirs('./download/data/')
    if not os.path.exists('./download/config/'): os.makedirs('./download/config/')
    for i in re.findall('[0-9a-z]{32}',patch_config):
        print('Downloading %s...' % i)
        for path_type in ['config', 'data']:
            for index in [True, False]:
                filename = './download/%s/%s%s' % (
                    path_type,
                    i,
                    '.index' if index else ''
                )
                data = ngdp.get_hash(i, path_type, index)
                if data:
                    with open(filename, 'wb+') as output:
                        output.write(data)

if __name__ == '__main__':
    main()

