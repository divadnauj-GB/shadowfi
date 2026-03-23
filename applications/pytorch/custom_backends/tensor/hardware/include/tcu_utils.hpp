#pragma once

#include "tcu_types.hpp"
#include <cstdint>

using WData = uint32_t;

uint32_t float_to_u32(float x);
float u32_to_float(uint32_t x);

void pack4(WData* bus, const vec4f& v);
vec4f unpack4(const WData* bus);

void print_vec(const char* name, const vec4f& v);
void print_mat(const char* name, const mat4f& m);
void print_abs_error(const char* name, const mat4f& got, const mat4f& exp);
