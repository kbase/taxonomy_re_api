# Tools for developing alongside kbase-ui

Since the Taxonomy API is utilized by front end tools, it is useful to be able to make changes to the API while also making changes to front end tools.

It is possible with kbase-ui to run tools hosted in kbase-ui against locally-hosted dynamic and core services.

The basic mechanism to enable this is that during development kbase-ui runs behind a local docker-hosted proxy, operating on a docker network named `kbase-dev`. Command line options to start kbase-ui flow through to the proxy, which can create routes to services running on the same kbase-dev internal network with the following rules:
    - the service is available at a known host name (preferably the module name)
    - and on port 5000
    - the service must be started before kbase-ui (nginx restriction)

This directory contains support for this type of workflow.

Specifically:

- `docker-compose.yaml` - a docker-compose designed to operate on the kbase-dev network, use google DNS.


## Instructions

### Start the Relation Engine

In the RE repo:

```bash
make start-ui-dev
```

### Start the Taxonomy API

In the Taxonomy API Repo

```bash
make start-ui-dev
```

### Start kbase-ui

First, map ci.kbase.ui to localhost. In your `/etc/hosts` (or wherever your hosts file is), add this entry

```hosts
127.0.0.1      ci.kbase.us
```

In the kbase-ui repo:

```bash
make start dynamic-services="taxonomy-re-api" 
```

(some details omitted here, consult the kbase-ui docs for: kbase-ui setup, installing dev ssl cert, )

This causes the kbase-ui proxy to intercept calls to the api dynamic service and route them on the `kbase-dev` docker network to service running at `taxonomy-re-api`.

> Note that the dynamic service name is "taxonomy-re-api" not the module name "taxonomy_re_api"; this is because the url path to the api is not the same as the module name. (There must be a transformation in by the service wizard from _ to -. Most dynamic services use ProperCase module naming, so the issue does not come up.)

You can now access the local kbase-ui at `https://ci.kbase.us`, with routing for all Taxonomy API dynamic service calls to the local instance.

## Local kbase-ui Plugin Development

The kbase-ui Taxonomy Landing Page (LP) plugin is developed as a standalone Create React App, not hosted within kbase-ui as plain javascript plugins are.

With kbase-ui configured as above, the Taxonomy LP will utilize the local Taxonomy API instance, since it those calls will be intercepted by the kbase-ui proxy.

