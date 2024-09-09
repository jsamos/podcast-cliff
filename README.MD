
# Podcast Cliff RSS

This project is capable of fetching and transcribing media files, usually from a podcast RSS feed. It leverages Redis Queue (RQ) to process tasks asynchronously, and optimizes transription by splitting the audio into chunks allowing for the processing each chunk in parallel.

Transcription is handled by Vosk API.

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
    git clone https://github.com/jsamos/podcast-cliff.git
    cd podcast-cliff
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

### RSS Feeds

1. Exec into the `message-processor` container to run the `fetch_rss.py` script:

    ```sh
    docker compose exec message-processor bash
    python fetch_rss.py <RSS_FEED_URL> [--title "<EPISODE_TITLE>"]
    ```

    Replace `<RSS_FEED_URL>` with the actual URL of the RSS feed you want to fetch. For example:

    ```sh
    python fetch_rss.py https://feeds.captivate.fm/the-game-alex-hormozi/
    ```

2. Tail the logs of the `message-processor` to see the processing logs:

    ```sh
    docker compose logs -f message-processor
    ```

#### Optional Parameters

The `fetch_rss.py` script supports an optional parameter to specify the episode you want to fetch:

- `--title`: Fetches a specific episode by its title. It will use "fuzzy" matching to find the episode, incase you copy pasta badly

#### Example:

To fetch episode by title from the RSS feed:

```sh
python fetch_rss.py https://feeds.captivate.fm/the-game-alex-hormozi/ --title 'Why Branding Makes You Money'
```

#### Default Behavior:

If the `--title` parameter is not provided, the script will fetch the latest episode (the first item in the RSS feed).

### Local files:

The app also supports transcribing local files using the run_stored.py script:

```sh
python run_stored.py <PATH_TO_FILE>
```

it currently supports mp3 and wav files.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
