#define DT_DRV_COMPAT qbf_lpm009m360a

#include <errno.h>
#include <string.h>
#include <zephyr/device.h>
#include <zephyr/drivers/display.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/spi.h>
#include <zephyr/kernel.h>

struct qbf_display_config {
    struct spi_dt_spec bus;
    struct gpio_dt_spec enable;
    struct gpio_dt_spec com;
};

struct qbf_display_data {
    struct k_mutex mutex;
    struct k_work_delayable flush;
    struct k_timer inversion;
    const struct device *device;
    uint8_t frame[144][9];
    bool dirty;
    bool enabled;
};

static int send(const struct device *device, uint8_t *bytes, size_t count) {
    const struct qbf_display_config *config = device->config;
    struct spi_buf buffer = {.buf = bytes, .len = count};
    struct spi_buf_set buffers = {.buffers = &buffer, .count = 1};
    return spi_write_dt(&config->bus, &buffers);
}

static void invert(struct k_timer *timer) {
    const struct device *device = k_timer_user_data_get(timer);
    const struct qbf_display_config *config = device->config;
    gpio_pin_set_dt(&config->com, 1);
    k_busy_wait(3);
    gpio_pin_set_dt(&config->com, 0);
}

static void flush(struct k_work *work) {
    struct qbf_display_data *data = CONTAINER_OF(k_work_delayable_from_work(work),
                                                 struct qbf_display_data, flush);
    k_mutex_lock(&data->mutex, K_FOREVER);
    if (data->dirty && data->enabled) {
        int error = 0;
        for (int row = 0; row < 144 && !error; row++) {
            uint8_t packet[13] = {0x88, row + 1};
            memcpy(packet + 2, data->frame[row], 9);
            error = send(data->device, packet, sizeof(packet));
        }
        data->dirty = error != 0;
    }
    bool retry = data->dirty && data->enabled;
    k_mutex_unlock(&data->mutex);
    if (retry) {
        k_work_schedule(&data->flush, K_SECONDS(1));
    }
}

static int blank_on(const struct device *device) {
    const struct qbf_display_config *config = device->config;
    struct qbf_display_data *data = device->data;
    k_mutex_lock(&data->mutex, K_FOREVER);
    data->enabled = false;
    data->dirty = true;
    k_timer_stop(&data->inversion);
    int error = gpio_pin_set_dt(&config->enable, 0);
    gpio_pin_set_dt(&config->com, 0);
    k_mutex_unlock(&data->mutex);
    return error;
}

static int blank_off(const struct device *device) {
    const struct qbf_display_config *config = device->config;
    struct qbf_display_data *data = device->data;
    k_mutex_lock(&data->mutex, K_FOREVER);
    if (data->enabled) {
        k_mutex_unlock(&data->mutex);
        return 0;
    }
    int error = gpio_pin_set_dt(&config->enable, 1);
    if (!error) {
        k_busy_wait(30);
        data->enabled = true;
        k_timer_start(&data->inversion, K_NO_WAIT, K_SECONDS(1));
        if (data->dirty) {
            k_work_schedule(&data->flush, K_NO_WAIT);
        }
    }
    k_mutex_unlock(&data->mutex);
    return error;
}

static int write_frame(const struct device *device, uint16_t x, uint16_t y,
                       const struct display_buffer_descriptor *descriptor, const void *buffer) {
    if (!buffer || !descriptor || descriptor->pitch < descriptor->width ||
        x + descriptor->width > 144 || y + descriptor->height > 72) {
        return -EINVAL;
    }
    size_t stride = DIV_ROUND_UP(descriptor->pitch, 8);
    if (descriptor->buf_size < stride * descriptor->height) {
        return -EINVAL;
    }
    struct qbf_display_data *data = device->data;
    const uint8_t *source = buffer;
    bool changed = false;
    k_mutex_lock(&data->mutex, K_FOREVER);
    for (int row = 0; row < descriptor->height; row++) {
        for (int column = 0; column < descriptor->width; column++) {
            int native_x = y + row;
            int native_y = 143 - x - column;
            uint8_t mask = 0x80 >> (native_x % 8);
            uint8_t *pixel = &data->frame[native_y][native_x / 8];
            bool white = (source[row * stride + column / 8] & (0x80 >> (column % 8))) != 0;
            uint8_t updated = white ? *pixel | mask : *pixel & ~mask;
            changed |= updated != *pixel;
            *pixel = updated;
        }
    }
    data->dirty |= changed;
    bool schedule = data->dirty && data->enabled;
    k_mutex_unlock(&data->mutex);
    if (schedule) {
        k_work_schedule(&data->flush, K_SECONDS(1));
    }
    return 0;
}

static void capabilities(const struct device *device, struct display_capabilities *caps) {
    memset(caps, 0, sizeof(*caps));
    caps->x_resolution = 144;
    caps->y_resolution = 72;
    caps->supported_pixel_formats = PIXEL_FORMAT_MONO01;
    caps->current_pixel_format = PIXEL_FORMAT_MONO01;
    caps->screen_info = SCREEN_INFO_MONO_MSB_FIRST;
}

static int pixel_format(const struct device *device, enum display_pixel_format format) {
    return format == PIXEL_FORMAT_MONO01 ? 0 : -ENOTSUP;
}

static int initialize(const struct device *device) {
    const struct qbf_display_config *config = device->config;
    struct qbf_display_data *data = device->data;
    if (!spi_is_ready_dt(&config->bus) || !gpio_is_ready_dt(&config->enable) ||
        !gpio_is_ready_dt(&config->com)) {
        return -ENODEV;
    }
    int error = gpio_pin_configure_dt(&config->enable, GPIO_OUTPUT_INACTIVE);
    if (error) {
        return error;
    }
    error = gpio_pin_configure_dt(&config->com, GPIO_OUTPUT_INACTIVE);
    if (error) {
        return error;
    }
    data->device = device;
    k_mutex_init(&data->mutex);
    k_work_init_delayable(&data->flush, flush);
    k_timer_init(&data->inversion, invert, NULL);
    k_timer_user_data_set(&data->inversion, (void *)device);
    uint8_t clear[] = {0x20, 0};
    error = send(device, clear, sizeof(clear));
    if (error) {
        return error;
    }
    k_msleep(1);
    memset(data->frame, 0, sizeof(data->frame));
    return blank_off(device);
}

static const struct display_driver_api api = {
    .blanking_on = blank_on,
    .blanking_off = blank_off,
    .write = write_frame,
    .get_capabilities = capabilities,
    .set_pixel_format = pixel_format,
};

static const struct qbf_display_config config = {
    .bus = SPI_DT_SPEC_INST_GET(0, SPI_OP_MODE_MASTER | SPI_WORD_SET(8) |
                                 SPI_TRANSFER_MSB | SPI_CS_ACTIVE_HIGH, 6),
    .enable = GPIO_DT_SPEC_INST_GET(0, disp_gpios),
    .com = GPIO_DT_SPEC_INST_GET(0, extcomin_gpios),
};
static struct qbf_display_data data;
DEVICE_DT_INST_DEFINE(0, initialize, NULL, &data, &config, POST_KERNEL,
                      CONFIG_DISPLAY_INIT_PRIORITY, &api);
