#!/bin/bash

export IMAGE_TAG=$(cat VERSION)
export AARCH=`uname -m`
export DOCKER_CLI_EXPERIMENTAL=enabled

export IMAGE_NAMES=(
  'xos-base'
  'xos-core'
  'xos-libraries'
  'chameleon'
  'xos-client'
  'xos-synchronizer-base'
)

for IMAGE_NAME in ${IMAGE_NAMES[@]}; do
  docker manifest create --amend cachengo/$IMAGE_NAME:$IMAGE_TAG cachengo/$IMAGE_NAME-x86_64:$IMAGE_TAG cachengo/$IMAGE_NAME-aarch64:$IMAGE_TAG
  docker manifest push cachengo/$IMAGE_NAME:$IMAGE_TAG
done
