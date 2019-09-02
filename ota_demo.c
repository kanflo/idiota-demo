/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Johan Kanflo (github.com/kanflo)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <espressif/esp_common.h>
#include <esp/uart.h>
#include <string.h>
#include <FreeRTOS.h>
#include <task.h>
#include <sysparam.h>
#include <idiota.h>
#include "ssid_config.h"


#ifdef CONFIG_IDIOTA_SERVER
 #define IDIOTA_SERVER       CONFIG_IDIOTA_SERVER
#else
 #define IDIOTA_SERVER       "172.16.3.113"
#endif // CONFIG_IDIOTA_SERVER

#ifdef CONFIG_IDIOTA_PORT
 #define IDIOTA_PORT       CONFIG_IDIOTA_PORT
#else
 #define IDIOTA_PORT       "27532"
#endif // CONFIG_IDIOTA_PORT

#ifdef CONFIG_IDIOTA_CHECK_INTERVAL
 #define IDIOTA_CHECK_INTERVAL       CONFIG_IDIOTA_CHECK_INTERVAL
#else
 #define IDIOTA_CHECK_INTERVAL       1
#endif // CONFIG_IDIOTA_PORT

#ifdef CONFIG_NODE_ID
 #define NODE_ID       CONFIG_NODE_ID
#else
 #define NODE_ID       NULL
#endif // CONFIG_IDIOTA_PORT

#ifdef CONFIG_NODE_TYPE
 #define NODE_TYPE       CONFIG_NODE_TYPE
#else
 #define NODE_TYPE       NULL
#endif // CONFIG_IDIOTA_PORT

#ifdef CONFIG_HW_REVISION
 #define HW_REV       CONFIG_HW_REVISION
#else
 #define HW_REV       NULL
#endif // CONFIG_HW_REVISION


static void ota_status_cb(ota_status_t status)
{
    switch(status) {
        case OTA_DNS_LOOKUP_FAILED:
            printf("Error: DNS lookup has failed\n");
            break;
        case OTA_SOCKET_ALLOCATION_FAILED:
            printf("Error: could not allocate OTA socket\n");
            break;
        case OTA_SOCKET_CONNECTION_FAILED:
            printf("Error: failed to connect to server %s:%s\n", IDIOTA_SERVER, IDIOTA_PORT);
            break;
        case OTA_SHA256_MISMATCH:
            printf("Error: downloaded SHA256 does not match downloaded binary\n");
            break;
        case OTA_REQUEST_SEND_FAILED:
            printf("Error: could not send OTA HTTP request\n");
            break;
        case OTA_DOWNLOAD_SIZE_MISMATCH:
            printf("Error: OTA download failed\n");
            break;
        case OTA_ONE_SLOT_ONLY:
            printf("Error: rboot has only one slot configured, cannot run OTA\n");
            break;
        case OTA_FAIL_SET_NEW_SLOT:
            printf("Error: rboot failed to switch\n");
            break;
        case OTA_IMAGE_VERIFY_FAILED:
            printf("Error: rboot verification failed\n");
            break;
        case OTA_START:
            printf("OTA started\n");
            break;
        case OTA_RUNNING:
            //printf("OTA running\n");
            break;
        case OTA_COMPLETED:
            printf("OTA successful\n");
            break;
    }
}

static ota_info info = {
    .server         = IDIOTA_SERVER,
    .port           = IDIOTA_PORT,
    .check_interval = IDIOTA_CHECK_INTERVAL,
    .node_id        = NODE_ID,
    .node_type      = NODE_TYPE,
    .hw_rev         = HW_REV,
    .ota_cb         = ota_status_cb
};

void user_init(void)
{
    uart_set_baud(0, 115200);
    printf("SDK version : %s\n", sdk_system_get_sdk_version());

    printf("OTA settings:\n");
    printf(" server         : %s\n", info.server);
    printf(" port           : %s\n", info.port);
    printf(" check_interval : %d\n", info.check_interval);

    printf("Node settings:\n");
    printf(" node_id        : %s\n", info.node_id);
    printf(" node_type      : %s\n", info.node_type);
    printf(" hw_rev         : %s\n", info.hw_rev);

    struct sdk_station_config config = {
        .ssid     = WIFI_SSID,
        .password = WIFI_PASS,
    };

    /** Must call wifi_set_opmode before station_set_config */
    sdk_wifi_set_opmode(STATION_MODE);
    sdk_wifi_station_set_config(&config);
    if (!ota_init(&info)) {
        printf("Failed to start OTA\n");
    }
}
