## Contents
- [Images](#Images)
- [Containers](#Containers)
- [Volume Management](#Volume+Management)
 
### Images
#### List the images
```
> docker images
REPOSITORY                                     TAG            IMAGE ID       CREATED         SIZE
postgres                                       latest         9181f7259a3d   5 days ago      425MB
postgres                                       14-alpine      4b4eb045a965   5 days ago      241MB
adminer                                        latest         b5cec1739340   2 weeks ago     250MB
confluentinc/cp-kafka                          7.3.0          b526943eeea4   13 months ago   828MB
confluentinc/cp-schema-registry                7.3.0          6d6a26f0e871   13 months ago   1.86GB
confluentinc/cp-zookeeper                      7.3.0          b3ebff3db01d   13 months ago   828MB
confluentinc/cp-kafka-connect                  7.1.1-1-ubi8   cd3ed71b7af7   19 months ago   1.45GB
confluentinc/cp-schema-registry                7.1.1-1-ubi8   9ab24d8f0028   19 months ago   1.81GB
confluentinc/cp-server                         7.1.1-1-ubi8   7fb33afb1b34   19 months ago   1.66GB
confluentinc/cp-zookeeper                      7.1.1-1-ubi8   534c2e2cfdbc   19 months ago   783MB
confluentinc/cp-enterprise-control-center      7.1.1-1-ubi8   086c4b9aa76e   19 months ago   1.21GB
hello-world                                    latest         feb5d9fea6a5   2 years ago     13.3kB
grafana/grafana                                8.1.3          e9eea6656cd9   2 years ago     213MB
prom/prometheus                                v2.29.2        a40ec91685b3   2 years ago     196MB
```
#### Remove a image
```
> docker image rm 7b1ecd0403a6
Error response from daemon: conflict: unable to delete 7b1ecd0403a6 (must be forced) - image is being used by stopped container 09e9ae5a5845
 
> docker rm 09e9ae5a5845
09e9ae5a5845
> docker image rm 7b1ecd0403a6
Error response from daemon: conflict: unable to delete 7b1ecd0403a6 (must be forced) - image is being used by stopped container cc5f9e4275d3
 
> docker rm cc5f9e4275d3
cc5f9e4275d3
 
> docker image rm 7b1ecd0403a6
Deleted: sha256:7b1ecd0403a6fd527e086c14c5bc6ad34209ad4542c8000741fdd895354867c7
```
### Containers
#### Get the latest image of a container from docker repo
```
> docker pull victoriametrics/victoria-metrics:latest
latest: Pulling from victoriametrics/victoria-metrics
4abcf2066143: Pull complete
b7492ce4cbe0: Pull complete
f3886e6bdc05: Pull complete
Digest: sha256:e25167523fc1788daaa73944c141cc8fcf80ccc77c6527c3d722d50eb4cb7757
Status: Downloaded newer image for victoriametrics/victoria-metrics:latest
docker.io/victoriametrics/victoria-metrics:latest
```
#### Run a container
```
> docker run -d -it --rm -v `pwd`/victoria-metrics-data:/victoria-metrics-data -p 8428:8428 victoriametrics/victoria-metrics:latest
2e619b91b349cff7101187fc81caec58242bd0ce8f4539a9df507f0a85e12c02
```
#### List the running containers
```
> docker ps
CONTAINER ID   IMAGE      COMMAND                  CREATED        STATUS        PORTS                                       NAMES
0263650b5b0f   postgres   "docker-entrypoint.s…"   10 hours ago   Up 10 hours   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   postgres_db_1
0c52dc10145f   adminer    "entrypoint.sh php -…"   10 hours ago   Up 10 hours   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   postgres_adminer_1
```
#### List all containers ( running + stopped )
```
> docker ps -a
CONTAINER ID   IMAGE                                     COMMAND                  CREATED         STATUS                      PORTS                                       NAMES
6fd06589f62f   victoriametrics/victoria-metrics:latest   "/victoria-metrics-p…"   4 minutes ago   Up 4 minutes                0.0.0.0:8428->8428/tcp, :::8428->8428/tcp   blissful_hoover
8e51fe95ce86   postgres                                  "docker-entrypoint.s…"   8 weeks ago     Created                                                                 pg-container-name
7900e71b49cb   consumer                                  "bash"                   3 months ago    Exited (0) 3 months ago                                                 great_volhard
c0950eeb1504   consumer                                  "bash"                   3 months ago    Exited (0) 3 months ago                                                 interesting_benz
60cb139bc9ba   consumer                                  "bash"                   3 months ago    Exited (0) 3 months ago                                                 loving_golick
6e0bb4d2634b   consumer                                  "bash -c 'python -m …"   3 months ago    Exited (0) 3 months ago                                                 nifty_lichterman
09e9ae5a5845   7b1ecd0403a6                              "bash -c 'python -m …"   3 months ago    Exited (1) 3 months ago                                                 suspicious_lewin
cc5f9e4275d3   7b1ecd0403a6                              "bash -c 'python -m …"   3 months ago    Exited (1) 3 months ago                                                 wizardly_yalow
d095ac84af76   4f0b571b2ce4                              "bash"                   3 months ago    Exited (129) 3 months ago                                               funny_napier
8abd54b560b6   4f0b571b2ce4                              "bash -c 'python -m …"   3 months ago    Exited (1) 3 months ago                                                 musing_neumann
```
#### Locate the compose file of a running container
```
> docker inspect 0263650b5b0f | grep working_dir
                "com.docker.compose.project.working_dir": "/home/ubuntu/customer/suncor/postgres",
```
#### Stop a running container ( SIGTERM first, then, after a grace period, SIGKILL - commits the state to a new image)
```
> docker stop cbc3b64bbd01
cbc3b64bbd01
```
#### Remove a container (force) ( SIGKILL )
```
> docker ps
CONTAINER ID   IMAGE                                     COMMAND                  CREATED         STATUS        PORTS                                       NAMES
8388c9862453   victoriametrics/victoria-metrics:latest   "/victoria-metrics-p…"   2 seconds ago   Up 1 second   0.0.0.0:8428->8428/tcp, :::8428->8428/tcp   fervent_joliot

> docker rm fervent_joliot
Error response from daemon: You cannot remove a running container 8388c9862453ef839e15e541bb85697befdcc3ee13e531d4a29688ce879b3454. Stop the container before attempting removal or force remove

> docker rm --force fervent_joliot
fervent_joliot
```
### Volume Management

#### List the volumes used by docker
```
[ubuntu@awst2x ~]# docker volume ls
DRIVER    VOLUME NAME
local     7e2a133e5f95b2c0a4075ccea0386358b332295e7110e6e278b279829eddbfd5
local     176dcf8e4cdedb2a2d2854800c8f82e3d66da563f5a5e33e9b718386b6e4db21
local     d98c8b13385cf865cf8d384a6becbcae3dd91ca22278dd874eadea552d9b89a0
```
#### Clean up the unused volume.
```
[ubuntu@awst2x ~]# docker volume prune
WARNING! This will remove all local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
d0b84377afa496b216a314ee0a7c8e1014596ef535307581fdcbd99ab624eb37
. . .
b4c0f09395a345440664050055f0deb6c66b6ca25518b18273dd066d88e1d9c8

Total reclaimed space: 11.18GB
```
