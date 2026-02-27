#pragma once

#include <condition_variable>
#include <mutex>
#include <optional>
#include <queue>

#include "models.hpp"

class EventQueue {
public:
    explicit EventQueue(size_t capacity);

    bool push(const Event& event);
    std::optional<Event> pop();
    void close();

private:
    size_t capacity_;
    std::queue<Event> queue_;
    std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    bool closed_{false};
};
