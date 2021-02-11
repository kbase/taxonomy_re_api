# Testing local API against a local RE instance

Sometimes, as one is adding new functionality to the Taxonomy API, concurrent changes are also required in the Relation Engine (RE).

At such times, you will need to run RE locally, and populate it with your changes. E.g. this may require creating a new collection and importing data.

However, existing integration tests will fail, as they by and large require a well-populated RE, including at least two taxonomies (NCBI, RDP) and related workspaces. As of this writing, RE does not have direct support for importing test data required by the Taxonomy API.

Thus the integration tests are split into two parts - those that must or can run against CI, and those which can't.

This document describes the process of testing those which can't.

## Overview

- run RE in ui mode
- run `make local-test`

## Running RE in ui mode

RE supports a local development workflow in which the runtime can be started in a docker container, running in a docker network named `kbase-dev`, utilizing a local Arango database which can be populated with data. At the moment, the only built-in test data support is for `data_sources`, although the Jacobson project codebase is also available.

When started in this mode, the RE api is available at `http://relation-engine-api:5000` on the docker network `kbase-dev`.

The name choice for the RE api host name is due to the fact that this is the registered service module name for the RE api.

This can be easily over-ridden by defining the environment variable `RE_API_URL` before running `make local-test`.

## Instructions

- start relation engine
- populate with data
  
- run local tests


### Start Relation Engine

- Clone the relation engine from `https://github.com/kbase/relation_engine`
- Start a local instance with `make start-ui-dev`
- In another terminal, load your test data.
  - See RE documentation

You should now have an instance of RE running, on the docker network `kbase-dev` with the hostname `relation-engine-api`.

### Run Tests

- In this repo, simply run `make local-test`.

If you started a local RE by some other means, you may need to set the environment variable `RE_API_URL`.
