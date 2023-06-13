#!/bin/bash -e

cd sdk

PYTHONPATH=$(pwd):$(pwd)/tests python -m unittest discover -v