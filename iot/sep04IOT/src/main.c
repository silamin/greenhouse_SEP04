#include "adxl345.h"
#include "buttons.h"
#include "buzzer.h"
#include "dht11.h"
#include "display.h"
#include "hc_sr04.h"
#include "leds.h"
#include "light.h"
#include "pc_comm.h"
#include "periodic_task.h"
#include "pir.h"
#include "servo.h"
#include "soil.h"
#include "tone.h"
#include "uart.h"
#include "wifi.h"

#include "sensor_state.h"
#include "thresholds.h"
#include "api_client.h"

#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

/* Wi-Fi credentials & API host are in api_client.c                      */
#define WIFI_SSID "H158-381_5B79"
#define WIFI_PASS "MGNn93gDda5"

/* ------------------------------------------------------------------ */
/* Buffers & globals                                                  */
/* ------------------------------------------------------------------ */
static char debug_buf[128];
static volatile SensorState g_state = {0};
static volatile bool send_flag = false;

/* ------------------------------------------------------------------ */
/* Sensor read callbacks                                              */
/* ------------------------------------------------------------------ */
static void read_sensors_A(void)     /* every 2 s */
{
    if (dht11_get(&g_state.hum_i,&g_state.hum_d,
                  &g_state.tmp_i,&g_state.tmp_d) != DHT11_OK)
        g_state.hum_i = g_state.tmp_i = 255;

    g_state.soil  = soil_read();
    g_state.light = light_read();
    g_state.dist  = hc_sr04_takeMeasurement();
}

static void read_sensors_B(void)     /* every 5 s */
{
    adxl345_read_xyz(&g_state.acc_x,&g_state.acc_y,&g_state.acc_z);
}

static void buttons_demo(void)       /* every 300 ms */
{
    if (buttons_1_pressed()) servo(0);
    if (buttons_2_pressed()) servo(90);
    if (buttons_3_pressed()) servo(180);
}

static void mark_send(void)          /* every 10 s */
{
    send_flag = true;
}

static void pir_cb(void)
{
    g_state.motion = true;
}

/* ------------------------------------------------------------------ */
static bool wifi_ok(WIFI_ERROR_MESSAGE_t e, const char *ctx)
/* ------------------------------------------------------------------ */
{
    if (e != WIFI_OK) {
        snprintf(debug_buf,sizeof(debug_buf),
                 "[WIFI ERR] %s:%d\r\n", ctx, e);
        uart_send_string_blocking(USART_0, debug_buf);
        return false;
    }
    return true;
}

/* ------------------------------------------------------------------ */
int main(void)
/* ------------------------------------------------------------------ */
{
    /* UARTs */
    uart_init(USART_0,115200,NULL);          /* PC console */
    pc_comm_init(115200,NULL);

    uart_send_string_blocking(USART_0,"\r\nBooting greenhouse...\r\n");

    /* Drivers */
    dht11_init(); soil_init(); light_init(); hc_sr04_init();
    adxl345_init(); buttons_init(); display_init(); leds_init();
    tone_init(); pir_init(pir_cb); servo(90); display_int(0);

    /* Wi-Fi */
    wifi_init(); _delay_ms(2000);
    wifi_ok(wifi_command_AT(), "AT");
    wifi_ok(wifi_command_disable_echo(),"ECHO");
    wifi_ok(wifi_command_set_mode_to_1(),"MODE1");
    wifi_ok(wifi_command_join_AP((char*)WIFI_SSID,(char*)WIFI_PASS),"JOIN");
    uart_send_string_blocking(USART_0,"Wi-Fi ready\r\n");

    /* Timers */
    sei();
    periodic_task_init_a(read_sensors_A,2000);
    periodic_task_init_b(read_sensors_B,5000);
    periodic_task_init_c(buttons_demo,300);
    periodic_task_init_b(mark_send,10000);

    /* Main loop */
    while (1) {
        if (send_flag) {
            /* 1. Push reading */
            api_send_reading((SensorState*)&g_state);

            /* 2. Pull thresholds & apply */
            GreenhouseSettings gh;
            if (api_get_settings(&gh))
                thresholds_apply((SensorState*)&g_state,&gh);

            /* housekeeping */
            g_state.motion = false;
            send_flag = false;
        }
    }
}
