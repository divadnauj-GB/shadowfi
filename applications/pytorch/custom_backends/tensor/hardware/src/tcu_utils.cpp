#include "tcu_utils.hpp"

#include <cstring>
#include <cmath>
#include <iomanip>
#include <iostream>

uint32_t float_to_u32(float x) {
    uint32_t out;
    std::memcpy(&out, &x, sizeof(uint32_t));
    return out;
}

float u32_to_float(uint32_t x) {
    float out;
    std::memcpy(&out, &x, sizeof(float));
    return out;
}

void pack4(WData* bus, const vec4f& v) {
    bus[0] = float_to_u32(v[0]);
    bus[1] = float_to_u32(v[1]);
    bus[2] = float_to_u32(v[2]);
    bus[3] = float_to_u32(v[3]);
}

vec4f unpack4(const WData* bus) {
    return {
        u32_to_float(bus[0]),
        u32_to_float(bus[1]),
        u32_to_float(bus[2]),
        u32_to_float(bus[3])
    };
}

void print_vec(const char* name, const vec4f& v) {
    std::cout << name << " = [ ";
    for (float x : v) {
        std::cout << std::fixed << std::setprecision(6) << x << " ";
    }
    std::cout << "]\n";
}

void print_mat(const char* name, const mat4f& m) {
    std::cout << name << "\n";
    for (const auto& row : m) {
        std::cout << "[ ";
        for (float x : row) {
            std::cout << std::fixed << std::setprecision(6) << x << " ";
        }
        std::cout << "]\n";
    }
    std::cout << "\n";
}

void print_abs_error(const char* name, const mat4f& got, const mat4f& exp) {
    std::cout << name << "\n";
    for (int i = 0; i < 4; ++i) {
        std::cout << "[ ";
        for (int j = 0; j < 4; ++j) {
            std::cout << std::fixed << std::setprecision(6)
                      << std::fabs(got[i][j] - exp[i][j]) << " ";
        }
        std::cout << "]\n";
    }
    std::cout << "\n";
}
