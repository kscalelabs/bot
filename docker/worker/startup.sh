#!/bin/bash

# Downloads the model, if it doesn't exist.
python3.11 -m bot.worker.download

# Start the worker.
python3.11 -m bot.worker.server
