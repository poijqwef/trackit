#!/bin/bash
cat input.cfg |sed 's/=.*$/=/g' > input.cfg.template
gpg -c input.cfg
