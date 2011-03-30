WIKI_NAME = 'qwapp Wiki'
REPOSITORY_PATH = './wiki'
DEBUG = True
SECRET_KEY = 'development key'

# use password.py to generate
PASSWORD_HASH = '06ab2f79d3fb9d86c75f0bb981c95f5d68497b311bdb1ed32918717547b4a6c31017a7a04908c6d39a93c8f748e312d5bfd255cbfbf15530cf374c1861dc73a7' # "devpass"

CACHE_TYPE = 'simple' # set this to 'null' to disable or use memcached, or others
#CACHE_MEMCACHED_SERVERS = ['localhost:11211']
CACHE_THRESHOLD = 200
CACHE_DEFAULT_TIMEOUT = 50 # 50 seconds default cache timeout
CACHE_KEY_PREFIX = PASSWORD_HASH[:10]

# no plugins loaded by default
PLUGINS = []
