
#pragma once

#include <string>
#include <memory>
#include <utility>
#include <cstdio>

template <typename... Args>
std::string sprintf(const char *fmt, Args... args)
{
    auto size = std::snprintf(nullptr, 0, fmt, args...);
    auto buf = std::make_unique<char[]>(size + 1);
    std::snprintf(buf.get(), size + 1, fmt, args...);
    // The string does not need to store the '\0' char
    return std::string{buf.get(), buf.get() + size};
}

