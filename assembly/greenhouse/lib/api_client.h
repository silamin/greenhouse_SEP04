#pragma once
#include <stdbool.h>
#include "sensor_state.h"
#include "greenhouse_settings.h"

/* 
   Existing calls:
   - api_authenticate()
   - api_send_reading()
   - api_get_settings()

   New:
   - api_predict(): calls POST /ml/predict with JSON {"soil":…, "hum":…, "temp":…, "light":…}
     Returns `true` if we got a valid “should_irrigate” value; else `false`. 
*/
bool api_authenticate(void);                       
bool api_send_reading(const SensorState *s);       
bool api_get_settings(GreenhouseSettings *dst);    

/* NEW: return true if successful and `*should_irrigate` is set; else false */
bool api_predict(const SensorState *s, bool *should_irrigate);
