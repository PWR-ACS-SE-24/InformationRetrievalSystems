# Stage 4

## Starting up

Start analysis stack with `./docker_up.sh`. If `elasticsearch` container fails to start you might want to increase max amount of memory maps with `sudo sysctl -w vm.max_map_count=262144`. By default both containers use 6GB of memory and all available cores.

## Teardown

Use `./docker_destroy.sh` to destroy all containers and their data.

## Benchmarking
Before benchmarking you'll have to download arxiv dataset from [kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv) and extract it here. Running `prepare_typesense.py` and `prepare_elastic.py` will set up appropriate database.

## Analysis
todo(@mlodybercik and @jakubzehner)
