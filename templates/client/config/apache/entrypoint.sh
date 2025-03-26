#!/bin/bash

bash /usr/local/bin/change-uid-gid.sh $@
bash /usr/local/bin/docker-entrypoint.sh $@

exec "$@"