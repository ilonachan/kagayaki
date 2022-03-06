import kagaconf

import logging.config
import yaml

# Read the logger configuration from a config file
with open('logging.yaml', 'r') as lf:
    log_cfg = yaml.safe_load(lf.read())
logging.config.dictConfig(log_cfg)

# top-level defaults
kagaconf.from_dict({
    'db': {
        'main': {
            'location': 'sqlite:///db/kagayaki.sqlite'
        },
        'playground': {
            'location': 'sqlite:///db/playground.sqlite'
        }
    }
})

# read user config directory
kagaconf.from_path('config', filter=r'[^_].*\.ya?ml')
kagaconf.from_path('config/deploy', filter=r'[^_].*\.ya?ml')
kagaconf.from_path('config/dialogue', filter=r'[^_].*\.ya?ml', recursive=True, prefix="humanize.dialogue",
                   dir_prefix=True)

# read environment variables
kagaconf.from_env_mapping({
    'discord': {
        'bot_token': 'BOT_TOKEN'
    },
    'db': {
        'main': {
            'location': 'DB_LOCATION'
        },
        'playground': {
            'location': 'DB_PLAYGROUND_LOCATION'
        }
    }
})
