#!/bin/bash

# setup
cd $(dirname $0)
NAME=$1
shift

# verify inputs
if [ "$NAME" == "" ] || [ "$NAME" == "-h" ] || [ "$NAME" == "--help" ]; then
    echo "Usage: $0 NAME [ ANSIBLE-GALAXY-ARGS ]"
    exit 1
fi

# create role
echo "Creating $NAME"
/usr/bin/ansible-galaxy init --offline --role-skeleton=.skel $@ "$NAME"
