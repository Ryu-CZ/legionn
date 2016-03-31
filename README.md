# Legionn

* maintainer: [Ryu-CZ](https://github.com/Ryu-CZ)

## Description

Legionn is platform hosting other subroutines in form of modules. It consists of Cores and Units.
* **Core** represent one SI implementation and holds data shared by all its Units
* **Unit** is worker produced by Core. Unit handles incoming communicator messages and http requests
Curretly I oplan to implement Core for jabber client with cleverbot intelligence.
Suggested port of Legionn server is 5009.

## Goals
There are important abilities of Leggion which raises from its design:
* **modularity** - you can simply wrap any of you favourite python scripts or projects into Core interface (if it makes sense to pack them) and add them into your Leggion.
* **transferability** - Legionn server class inherits from Core also. This could be use for Legionn server cloning/migration in running state. Your Legionn can pack itself with python object serialisation and transfer into 'other Legionn server.' So in final Your Legionn is able to run nested in 'other Legionn server' and operate form there.
* **uniqueness**(singularity) - thanks to transferability & modularity your Leggion could be mobile persona. It is free to move between other Legionn nodes. So with some empty Legionn nodes on your devices, your personalised Leggion instance is able to follow you and assist you everywhere.

### Manual installation 
Manual installation Dependencies:
```bash
pip install -r requirements.txt
```

###Swagger api interface
You can test http requests in swagger interaface on path `host:port/`
