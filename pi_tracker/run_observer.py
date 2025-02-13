import json
import logging
from observer import ArtObserver

def main():
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.error("config.json not found. Please create it with your settings.")
        return
    except json.JSONDecodeError:
        logging.error("Invalid JSON in config.json")
        return

    # Create and start observer
    observer = ArtObserver(
        camera_id=config['camera_id'],
        artwork_id=config['artwork_id'],
        lambda_url=config['lambda_url']
    )
    
    observer.start(video_source=config.get('video_source', 0))

if __name__ == '__main__':
    main()
