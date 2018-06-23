# tf-ecosystem
A tool for handling terraform deployments in a modular way

[![Build Status](https://travis-ci.com/drewsonne/tf-ecosystem.svg?branch=master)](https://travis-ci.com/drewsonne/tf-ecosystem)
[![codecov](https://codecov.io/gh/drewsonne/tf-ecosystem/branch/master/graph/badge.svg)](https://codecov.io/gh/drewsonne/tf-ecosystem)

## Quickstart

    $ git clone https://github.com/drewsonne/tf-ecosystem.git
    $ cd tf-ecosystem
    $ pip install -e .
    $ tf-eco init-stack --region eu-central-1 --environment live --stack help
    $ cat ~/.config/tf-ecosystem/config.ini
    $ cat _eco_override.tf
