#!/bin/bash

docker run -d -p 8108:8108 --name typesense -m 6GB typesense/typesense:28.0 --data-dir / --api-key=test --enable-cors
docker run -d -p 9200:9200 --name elasticsearch -m 6GB -e xpack.security.enabled=false -e node.name=elasticsearch -e cluster.initial_master_nodes=elasticsearch docker.elastic.co/elasticsearch/elasticsearch:8.17.4