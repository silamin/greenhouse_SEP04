#include "thresholds.h"
#include "buzzer.h"
#include "leds.h"
#include "servo.h"        /* we use servo as valve */
#include "display.h"

void thresholds_apply(const SensorState *r,
                      const GreenhouseSettings *s)
{
    /* Temperature control */
    if (r->tmp_i > (int)s->temp_max) {
        leds_toggle(1); leds_toggle(1);
        buzzer_beep();
    } else if (r->tmp_i < (int)s->temp_min) {
        buzzer_beep();
    }

    /* Humidity */
    if (r->hum_i < (int)s->hum_min) {
        buzzer_beep();
        leds_turnOn(1);
    } else if (r->hum_i > (int)s->hum_max) {
        leds_toggle(1);
    }

    /* Soil moisture -> valve */
    if (r->soil < s->soil_min) {
        servo(0);        /* open valve */
    } else if (r->soil > s->soil_min + 100) {
        servo(90);       /* close valve */
    }

    /* Light */
    if (r->light < s->light_min) leds_turnOn(2);
    else if (r->light > s->light_max) leds_turnOff(2);

    /* Motion alarm */
    if (r->motion) {
        buzzer_beep();
        leds_toggle(3);
    }

    /* Always show current temp integer part */
    display_int((int16_t)r->tmp_i);
}
