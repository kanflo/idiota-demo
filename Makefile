PROGRAM = idiota-test

# The baudrate used for serial communications, defaults to 115200
BAUDRATE ?= 115200

# Modify to your likings
IDIOTA_SERVER ?= 172.16.3.113
IDIOTA_PORT ?= 27532
IDIOTA_CHECK_INTERVAL ?= 1
NODE_ID ?= NULL
NODE_TYPE ?= esp32cam
HW_REV ?= NULL

OTA = 1
EXTRA_COMPONENTS = extras/rboot-ota extras/mbedtls extras/stdin_uart_interrupt
PROGRAM_INC_DIR = . idiota
PROGRAM_SRC_DIR = . idiota
PROGRAM_CFLAGS += -DCONFIG_BAUDRATE=$(BAUDRATE) -std=gnu99
PROGRAM_CFLAGS += -DCONFIG_IDIOTA_SERVER=\"$(IDIOTA_SERVER)\" -DCONFIG_IDIOTA_PORT=\"$(IDIOTA_PORT)\" -DCONFIG_IDIOTA_CHECK_INTERVAL=$(IDIOTA_CHECK_INTERVAL) -DCONFIG_NODE_ID=\"$(NODE_ID)\" -DCONFIG_NODE_TYPE=\"$(NODE_TYPE)\" -DCONFIG_HW_REVISION=\"$(HW_REV)\"

include esp-open-rtos/common.mk
