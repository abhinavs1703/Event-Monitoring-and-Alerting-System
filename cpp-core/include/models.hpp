#pragma once

#include <chrono>
#include <optional>
#include <random>
#include <sstream>
#include <string>

struct Event {
    std::string event_id;
    std::string source_id;
    std::string timestamp;
    std::string severity;
    std::string event_type;
    std::string payload;
    int retry_count{0};
};

inline std::string now_iso8601() {
    auto now = std::chrono::system_clock::now();
    std::time_t time = std::chrono::system_clock::to_time_t(now);
    char buffer[32];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&time));
    return std::string(buffer);
}

inline std::string random_uuid() {
    static thread_local std::mt19937 gen(std::random_device{}());
    static thread_local std::uniform_int_distribution<int> dis(0, 15);
    static const char *hex = "0123456789abcdef";
    std::stringstream ss;
    int groups[] = {8, 4, 4, 4, 12};
    for (size_t g = 0; g < 5; ++g) {
        if (g > 0) ss << '-';
        for (int i = 0; i < groups[g]; ++i) ss << hex[dis(gen)];
    }
    return ss.str();
}
