
# Podcast RSS Feed Processor

This project fetches podcast episodes from an RSS feed, enqueues metadata processing tasks using Redis Queue (RQ), and processes these tasks asynchronously. The setup involves two main services: `rss-feed-parser` and `message-processor`, along with a Redis service for task queuing. The app also splits downloaded audio files into smaller fragments of configurable length.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Optional Parameters](#optional-parameters)
- [Capabilities](#capabilities)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Docker and Docker Compose installed on your machine.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/podcast-rss-feed-processor.git
    cd podcast-rss-feed-processor
    ```

2. Build the Docker containers:

    ```sh
    docker-compose build
    ```

## Usage

1. Start the services:

    ```sh
    docker-compose up
    ```

2. Exec into the `rss-feed-parser` container to run the `fetch.py` script:

    ```sh
    docker-compose exec rss-feed-parser /bin/sh
    python fetch.py <RSS_FEED_URL>
    ```

    Replace `<RSS_FEED_URL>` with the actual URL of the RSS feed you want to fetch. For example:

    ```sh
    python fetch.py https://feeds.captivate.fm/the-game-alex-hormozi/
    ```

3. Tail the logs of the `message-processor` to see the processing logs:

    ```sh
    docker-compose logs -f message-processor
    ```

## Optional Parameters

The `fetch.py` script supports an optional parameter to specify the episode number you want to fetch:

- `--episode`: Fetches a specific episode by its number.

### Example:

To fetch episode number 10 from the RSS feed:

```sh
python fetch.py https://feeds.captivate.fm/the-game-alex-hormozi/ --episode 744
```

### Default Behavior:

If the `--episode` parameter is not provided, the script will fetch the latest episode (the first item in the RSS feed).

## Capabilities

- **Fetch Episodes**: The app fetches podcast episodes from a provided RSS feed URL.
- **Download Audio Files**: It downloads the full-length audio file of the specified or latest episode.
- **Process Metadata**: The app processes metadata of the episodes and updates the RSS feed item XML.
- **Split Audio Files**: The downloaded audio file is split into smaller fragments of a configurable length.
- **Store Files**: The full-length audio file and its fragments are stored in the `data` directory, which is shared between the host machine and the Docker containers.

## Directory Structure

```plaintext
.
├── data                       # This will be shared between host and containers
├── docker-compose.yml
├── rss-feed-parser
│   ├── Dockerfile
│   ├── requirements.txt
│   └── fetch.py
├── message-processor
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── tasks.py
│   ├── worker.py
│   └── config.yaml
```

- **rss-feed-parser**: Contains the script to fetch podcast episodes and enqueue tasks.
- **message-processor**: Contains the worker that processes the tasks and downloads the audio files, as well as splitting them into fragments.
- **docker-compose.yml**: Docker Compose configuration file to set up the services.
- **data**: Shared directory between the host machine and Docker containers for storing audio files.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
