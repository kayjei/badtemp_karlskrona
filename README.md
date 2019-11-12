Home assistant integration to read and display temperatures for swimareas in Karlskrona, Sweden.

1. Download the folder badtemp_karlskrona into $CONFIG/custom_components/
2. Add configuration to your ```configuration.yaml```
```
sensor:
    - platform: badtemp_karlskrona
```

Sensors will be available as sensor.badtemp_xxxxxxx and positioned at your map in HA.
