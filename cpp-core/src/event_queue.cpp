#include "event_queue.hpp"

EventQueue::EventQueue(size_t capacity) : capacity_(capacity) {}

bool EventQueue::push(const Event& event) {
    std::unique_lock<std::mutex> lock(mutex_);
    cv_not_full_.wait(lock, [this]() { return closed_ || queue_.size() < capacity_; });
    if (closed_) {
        return false;
    }
    queue_.push(event);
    cv_not_empty_.notify_one();
    return true;
}

std::optional<Event> EventQueue::pop() {
    std::unique_lock<std::mutex> lock(mutex_);
    cv_not_empty_.wait(lock, [this]() { return closed_ || !queue_.empty(); });
    if (queue_.empty()) {
        return std::nullopt;
    }

    Event event = queue_.front();
    queue_.pop();
    cv_not_full_.notify_one();
    return event;
}

void EventQueue::close() {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        closed_ = true;
    }
    cv_not_empty_.notify_all();
    cv_not_full_.notify_all();
}
