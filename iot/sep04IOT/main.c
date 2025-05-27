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

#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

/* Config */
#define WIFI_SSID "H158-381_5B79"
#define WIFI_PASS "MGNn93gDda5"
#define SERVER_IP "192.168.1.42"  // your laptop's IP
#define SERVER_PORT 9000          // backend TCP port

/* Buffers */
static char json_buf[256];
static char cmd_buf[64];
static uint8_t cmd_i = 0;

/* Latest sensor state */
volatile struct {
	int16_t acc_x, acc_y, acc_z;
	uint8_t hum_i, hum_d, tmp_i, tmp_d;
	uint16_t soil, light, dist;
	bool motion;
	} state = {0};

	/* Flags */
	volatile bool send_flag = false;

	/*--- Forward declarations ---*/
	void read_sensors_a(void);
	void read_sensors_b(void);
	void read_sensors_c(void);
	void prepare_send(void);
	void pir_cb(void);
	void pc_command_cb(char c);
	bool check_wifi(WIFI_ERROR_MESSAGE_t e, const char* ctx);

	/*--- Implementations ---*/

	// Read DHT11 + soil + light + distance + PIR/motion
	void read_sensors_a(void) {
		if (dht11_get(&state.hum_i, &state.hum_d, &state.tmp_i, &state.tmp_d) != DHT11_OK) {
			state.hum_i = state.hum_d = 0xFF;
			state.tmp_i = state.tmp_d = 0xFF;
		}
		state.soil  = soil_read();
		state.light = light_read();
		state.dist  = hc_sr04_takeMeasurement();
	}

	// Read accelerometer
	void read_sensors_b(void) {
		adxl345_read_xyz(&state.acc_x, &state.acc_y, &state.acc_z);
	}

	// Demo: button?driven servo control
	void read_sensors_c(void) {
		if (buttons_1_pressed()) servo(0);
		if (buttons_2_pressed()) servo(90);
		if (buttons_3_pressed()) servo(180);
	}

	// Mark data for send
	void prepare_send(void) {
		send_flag = true;
	}

	// PIR motion interrupt
	void pir_cb(void) {
		state.motion = true;
	}

	// PC or WiFi UART command handler
	void pc_command_cb(char c) {
		if (c == '\r' || c == '\n') {
			cmd_buf[cmd_i] = 0;
			// Example command: "LED 2 ON"
			char dev[8], act[16];
			if (sscanf(cmd_buf, "%7s %15[^\n]", dev, act) == 2) {
				if (strcasecmp(dev,"LED")==0) {
					if (strcasecmp(act,"ON")==0)  leds_turnOn(2);
					if (strcasecmp(act,"OFF")==0) leds_turnOff(2);
					if (strcasecmp(act,"TOGGLE")==0) leds_toggle(2);
				}
				else if (strcasecmp(dev,"BUZZER")==0) buzzer_beep();
				else if (strcasecmp(dev,"TONE")==0) tone_play(1000,200);
				else if (strcasecmp(dev,"SERVO")==0) {
					int a = atoi(act);
					if (a>=0 && a<=180) servo((uint8_t)a);
				}
				else if (strcasecmp(dev,"DISPLAY")==0) {
					// act = an integer string
					display_int((int16_t)atoi(act));
				}
			}
			cmd_i = 0;
			} else if (cmd_i < sizeof(cmd_buf)-1) {
			cmd_buf[cmd_i++] = c;
		}
	}

	// WiFi error helper
	bool check_wifi(WIFI_ERROR_MESSAGE_t e, const char* ctx) {
		if (e != WIFI_OK) {
			char tmp[64];
			snprintf(tmp, sizeof(tmp), "[WIFI ERR] %s: %d\n", ctx, e);
			uart_send_string_blocking(USART_0, tmp);
			return false;
		}
		return true;
	}

	int main(void) {
		// --- Init UARTs ---
		uart_init(USART_0, 115200, pc_command_cb);
		pc_comm_init(115200, pc_comm_callback_t(pc_command_cb));
		uart_send_string_blocking(USART_0, "Booting SEP4 MCU...\n");

		// --- Init Drivers ---
		dht11_init();
		soil_init();
		light_init();
		hc_sr04_init();
		adxl345_init();
		buttons_init();
		display_init();
		leds_init();
		tone_init();
		buzzer_beep();          // sanity beep
		pir_init(pir_cb);
		servo(90);              // center
		display_int(0);         // clear

		// --- WiFi & TCP setup ---
		wifi_init();
		_delay_ms(2000);
		check_wifi(wifi_command_AT(), "AT");
		check_wifi(wifi_command_disable_echo(), "ECHO OFF");
		check_wifi(wifi_command_set_mode_to_1(), "MODE 1");
		check_wifi(wifi_command_join_AP((char*)WIFI_SSID,(char*)WIFI_PASS),"JOIN AP");
		static char wifi_rx[128];
		check_wifi(
		wifi_command_create_TCP_connection((char*)SERVER_IP, SERVER_PORT, NULL, wifi_rx),
		"TCP CONNECT"
		);
		uart_send_string_blocking(USART_0, "WiFi Ready\n");

		// --- Periodic sensor reads ---
		sei();
		periodic_task_init_a(read_sensors_a, 2000);  // every 2s
		periodic_task_init_b(read_sensors_b, 5000);  // every 5s
		periodic_task_init_c(read_sensors_c, 300);   // button check

		periodic_task_init_b(prepare_send, 10000);   // send every 10s

		while (1) {
			if (send_flag) {
				// build JSON
				int wrote = snprintf(json_buf,sizeof(json_buf),
				"{\"temp\":%u.%u,\"hum\":%u.%u,\"soil\":%u,\"light\":%u,"
				"\"dist\":%u,\"motion\":%s,\"acc\":[%d,%d,%d]}\n",
				state.tmp_i, state.tmp_d,
				state.hum_i, state.hum_d,
				state.soil, state.light,
				state.dist,
				state.motion?"true":"false",
				state.acc_x, state.acc_y, state.acc_z
				);
				// send and log
				if (!check_wifi(wifi_command_TCP_transmit((uint8_t*)json_buf, wrote),"TX"))
				wifi_command_close_TCP_connection();
				uart_send_string_blocking(USART_0, json_buf);

				// display temperature
				display_int((int16_t)state.tmp_i);

				// reset
				send_flag = false;
				state.motion = false;
			}
			// idle loop — all work in interrupts
		}
	}
