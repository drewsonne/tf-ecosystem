# tf-ecosystem
A tool for handling terraform deployments in a modular way

[![Build Status](https://travis-ci.com/drewsonne/tf-ecosystem.svg?branch=master)](https://travis-ci.com/drewsonne/tf-ecosystem)
[![codecov](https://codecov.io/gh/drewsonne/tf-ecosystem/branch/master/graph/badge.svg)](https://codecov.io/gh/drewsonne/tf-ecosystem)

## Quickstart

    $ pip install tf-ecosystem
    $ tf-eco init-stack --region eu-central-1 --environment live --stack help
    $ cat ~/.config/tf-ecosystem/config.ini
    $ cat _eco_override.tf

## Configuration Reference

### `facets`

Facets are variables used as required arguments and to describe the state path in an s3 backend.

#### `facets.state`
A list of facets strings

#### `facets.optional`
A subset of `facets.state` marking those facets as optional.

#### `facets.composite`

### `backend`

### `providers`

### `mappings`

A dictionary of dictionaries where each 
