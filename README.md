# NetGear Pro Safe Plus Web to mqtt

Compatible:
- JGS516PE 2.6.0.48

Usage:

```./netgear.py <ip> <password> <mqtt-ip> <mqtt-topic> <delay-stats> <delay-config>```

Or with docker-compose:

```
version: "3.9"
services:
  netgear:
    image: fensoft/netgear_prosafeplus_web2mqtt:latest
    environment:
    - SWITCH_IP=
    - SWITCH_PASSWORD=
    - MQTT_IP=
    - MQTT_TOPIC=
    - DELAY_STATS=15
    - DELAY_CONFIG=120
```
