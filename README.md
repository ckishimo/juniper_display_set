# Juniper display set

This script converts standard Juniper config into a list of 'set' commands which you can use 
to configure a Juniper device

Usage
-----
The input is a standard Juniper configuration file like:

```
/* my configuration */
version 14.1R1.10;
system {
    host-name myrouter;
    root-authentication {
        encrypted-password "$11111$VrloaKaj0$OwnE4.pHqnEGigmuLZQkZ/"; ## SECRET-DATA
    }
    login {
        user ckishimo {
            uid 2000;
            class super-user;
            authentication {
                encrypted-password "$1$YJ7i717qVpo8$myuAjTW/tkWlm6EudqcL4/"; ## SECRET-DATA
            }
        }
    }
    protect: services {
        ftp;
        ssh;
        telnet;
        netconf {
            ssh;
        }
    }
    inactive: syslog {
        user * {
            any emergency;
        }
        file messages {
            any notice;
            authorization info;
        }
        file interactive-commands {
            interactive-commands any;
        }
    }
}
interfaces {
    ge-0/0/1 {
        vlan-tagging;
    }
    ge-0/0/2 {
        vlan-tagging;
    }
}
```

The output will be a list of set commands you can paste into your router

```
$ $ python junos_converter.py
usage: junos_converter.py [-h] [--ignore-annotations] --input INPUT
junos_converter.py: error: the following arguments are required: --input

$ python junos_converter.py --input example.conf
set version 14.1R1.10
set system host-name myrouter
set system root-authentication encrypted-password "$11111$VrloaKaj0$OwnE4.pHqnEGigmuLZQkZ/"
set system login user ckishimo uid 2000
set system login user ckishimo class super-user
set system login user ckishimo authentication encrypted-password "$1$YJ7i717qVpo8$myuAjTW/tkWlm6EudqcL4/"
protect system services
set system services ftp
set system services ssh
set system services telnet
set system services netconf ssh
deactivate system syslog
set system syslog user * any emergency
set system syslog file messages any notice
set system syslog file messages authorization info
set system syslog file interactive-commands interactive-commands any
set interfaces ge-0/0/1 vlan-tagging
set interfaces ge-0/0/2 vlan-tagging
top
annotate version "my configuration"
```

Or you can upload the output file to the Juniper device and use the 'load merge' command 

```
$ python junos_converter.py --input example.conf > example.set
$ scp example.set ckishimo@10.1.1.1:

[edit]
ckishimo@juniper-mx# load merge example.set    
```

Or you better use [napalm](https://github.com/napalm-automation/napalm)
```
$ cl_napalm_configure --strategy merge --user ckishimo --vendor junos 10.1.1.1 example.set
```

Notes
-----
- Annotations are supported. They will be listed at the end
   - Note "annotations" are not supported by Junos (ie: they will be lost when `show | display set`)
- Inactive blocks are supported (like "system syslog" in the example)
- Protect blocks are supported as well (like "system services" in the example)

Limitations
-----------
As we cannot distinguish a JUNOS keyword from a configuration value we cannot convert the other way around

