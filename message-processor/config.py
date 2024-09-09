import yaml

def load_config():
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
    return config

# Load the configuration once when the module is imported
config = load_config()

# Define constants
AUDIO_FRAGMENT_LENGTH = config['audio_fragment_length']
TRANSCRIPTION_CHECK_INTERVAL = config['transcription_check_interval']
TRANSCRIPTION_MAX_WAIT_TIME = config['transcription_max_wait_time']