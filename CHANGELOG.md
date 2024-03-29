# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.9.1] - 2022-05-14
 - Bumped kbase.yml in order to register to beta/release

## [3.9.0] - 2022-04-18
### Changed
 - Removed un-needed GHA actions
 - Upgraded sanic: 19.3.1 -> 20.12.6
 - Upgraded pyyaml: 5.1 -> 5.4

## [3.7.2] - 2022-03-02

### Added

- `get_data_sources` method which returns taxonomy data sources with optional filtering
- `github actions` Docker Image Builds at ghcr.io

### Changed

- extended jsonrpc exceptions to be comprehensive; utilized in main file; extended integration tests to cover.
- `search_species` method now calls the `taxonomy_search_species_strain` and `taxonomy_search_species_strain_no_sort` stored queries in the RE API

## [3.7.1] - 2020-04-14

### Changed

- Use a special RE API URL environment variable if we are in the appdev server environment

## [3.5.0] - 2020-04-02

### Added

- Added the `search_species` method which calls the `taxonomy_search_species` query in the RE API
