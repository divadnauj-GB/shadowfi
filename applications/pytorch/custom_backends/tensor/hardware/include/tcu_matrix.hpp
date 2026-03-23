#pragma once

#include <vector>
#include <stdexcept>
#include <cstddef>

class Matrixf {
public:
    Matrixf() = default;

    Matrixf(std::size_t rows, std::size_t cols, float value = 0.0f)
        : rows_(rows), cols_(cols), data_(rows * cols, value) {}

    std::size_t rows() const { return rows_; }
    std::size_t cols() const { return cols_; }

    float& operator()(std::size_t r, std::size_t c) {
        return data_.at(r * cols_ + c);
    }

    float operator()(std::size_t r, std::size_t c) const {
        return data_.at(r * cols_ + c);
    }

    const std::vector<float>& data() const { return data_; }
    std::vector<float>& data() { return data_; }

private:
    std::size_t rows_ = 0;
    std::size_t cols_ = 0;
    std::vector<float> data_;
};
