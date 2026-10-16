# Hero Types

## 1. McDonnell Douglas DC-10
In `raw_opensky_aircraft` the model is usually noted as `DC-10-XX`, for example, 'DC-10-40' sometimes also followed by an 'F'(freight) or 'I'(intercontinental). `typecode` is generally consistent as 'DC10'
## 2. Boeing 727
In `raw_opensky_aircraft` the model is usually noted as `727-2XX`, where XX is a customer code suffix added by Boeing. For example, '727-225' is a 727-200 made for Eastern Airlines. Customer code is generally followed by a feature modifier such as 'RE'(re-engined) or 'W'(winglets). `typecode` also consistent as 'B722'. Missing quite a few `built` values.
## 3. Airbus A310
Manufacturer ICAO is mostly consistent. In `raw_opensky_aircraft` the model is usually noted as `A310-XXX`. For example, 'A310-304'. Sometimes there is an 'Airbus' prefix included and a feature modifier suffix including 'MRTT', '24, 04', 'ET' or 'F'.
