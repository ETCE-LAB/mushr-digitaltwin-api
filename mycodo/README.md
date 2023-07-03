
# Table of Contents

1.  [Pre-requisites](#org0703cf8)
2.  [Installation](#orgdfcc0ee)
    1.  [Install Dependencies](#org2fcbc9a)
        1.  [Install Mycodo](#org132c00a)
    2.  [Install DigitalTwin dependencies](#org0c73bd3)
    3.  [Clone MushR](#orgce8fc8c)
    4.  [Configure DigitalTwin neo4j database connection](#org602d656)
    5.  [Install MushR DigitalTwin implementation to mycodo](#orge433a3b)
    6.  [Import MushR Widgets](#org9ec8ef4)

Documentation for using MushR digital twin mycodo widgets on a
Raspberry Pi 4 B.

This Documentation was last tested on <span class="timestamp-wrapper"><span class="timestamp">&lt;2023-03-01 Wed&gt;</span></span>

**IMPORTANT**: The documentation for this setup has not been formally
audited for security holes. You probably do not want to use this as a
guide for setting up a production-ready setup (Unless you know what
you are doing). I reccommend keeping your raspberry pi behind a strong
firewall.


<a id="org0703cf8"></a>

# Pre-requisites

Make sure the following pre-requisites are fulfilled:

1.  A Raspberry Pi 4 B with a 32-bits installation of [Raspberry Pi OS](https://www.raspberrypi.com/software/)

2.  The ability to aquire a TLS Certificate for mycodo, including a
    web-domain associated with the raspberry pi (Since modern browsers
    [block mixed content](https://support.mozilla.org/en-US/kb/mixed-content-blocking-firefox)).

3.  A working installation of neo4j **[With SSL Enabled (at least for the
    bolt interface)](https://neo4j.com/docs/operations-manual/4.4/security/ssl-framework/)** (Also since modern browsers [block mixed content](https://support.mozilla.org/en-US/kb/mixed-content-blocking-firefox)).


<a id="orgdfcc0ee"></a>

# Installation


<a id="org2fcbc9a"></a>

## Install Dependencies


<a id="org132c00a"></a>

### Install Mycodo

You can use the official [quick-install script](https://github.com/kizniche/Mycodo#install-command) (and follow the
on-screen instructions):

Side-note: At the time of writing this documentation, you must install
Influxdb1.x when prompted by the Mycodo install.sh script (even if you
do not require the raspberry pi to run this server during production).

    curl -L https://kizniche.github.io/Mycodo/install | bash

1.  Install TLS Certificate

    Once you have acquired a TLS Certificate, install them for mycodo to
    use. If you used the [quick-install script](https://github.com/kizniche/Mycodo#install-command), the folder is
    `~/Mycodo/mycodo/mycodo_flask/ssl_certs`.
    
        ls -l


<a id="org0c73bd3"></a>

## Install DigitalTwin dependencies

The python dependencies must be installed inside the virtualenv that
mycodo uses (You probably have to use `sudo`):

    /home/pi/Mycodo/env/bin/python3 -m pip install neomodel


<a id="orgce8fc8c"></a>

## Clone This repository

    git clone https://github.com/ETCE-LAB/mushr-digitaltwin-api.git


<a id="org602d656"></a>

## Configure DigitalTwin neo4j database connection

Edit the neo4j database connection configuration file. This must be
done in two places:

1.  `<path to mushr-digitaltwin-api>/mycodo/mycodo_plugins/mushr-neomodel.conf` (You
    might have to create this file if it does not already exist)
    
        [neo4j]
        database_url = bolt://<username>:<password>@<domain>:<port, e.g. 7687>/<database-name>
2.  In `~/mushr/digitaltwins/mycodo_plugins/mushr_neomodel.py` , edit the following line:
    
        neo4jconfig.DATABASE_URL = mushr_neomodel_config.get(
            "neo4j",
            "DATABASE_URL",
            fallback="bolt://<username>:<password>@<domain>:<port, e.g. 7687>/<database-name>")


<a id="orge433a3b"></a>

## Install MushR DigitalTwin implementation to mycodo

1.  Copy files to `user_python_code`:
    
        sudo su mycodo
        cp <path to mushr-digitaltwin-api>/mycodo/mycodo_plugins/mushr_neomodel.py /home/pi/Mycodo/mycodo/user_python_code/
        cp <path to mushr-digitaltwin-api>/mycodo/mycodo_plugins/mushr-neomodel.conf /home/pi/Mycodo/mycodo/user_python_code/

2.  Restart Mycodo frontend and backend (just in case).


<a id="org9ec8ef4"></a>

## Import MushR Widgets

1. To
   [import](https://kizniche.github.io/Mycodo/Configuration-Settings/#widget-settings)
   a widget, upload the required widget file, e.g., [to create new
   substrate](widgets/substrate/mushr_substrate_create.py)
2. Add the widget to a dashboard.
3. Widgets that end with *_view.py will additionally require you to
   enter the neo4j database url, username and password in the widget
   settings menu.
