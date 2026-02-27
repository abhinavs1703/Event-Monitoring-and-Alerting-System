#pragma once

#include <atomic>
#include <string>
#include <vector>

#include "event_queue.hpp"
#include "thread_pool.hpp"

class EventProcessor {
public:
    EventProcessor(size_t queue_capacity, size_t worker_count, std::string api_url, std::string ingest_token, int max_retries);

    void start();
    void stop();
    void submit_event(const Event& event);

    [[nodiscard]] size_t dead_letter_count() const;

private:
    bool validate_event(const Event& event) const;
    bool dispatch_event(const Event& event) const;

    EventQueue queue_;
    ThreadPool pool_;
    std::string api_url_;
    std::string ingest_token_;
    int max_retries_;
    std::atomic<bool> running_{false};

    mutable std::mutex dlq_mutex_;
    std::vector<Event> dead_letter_queue_;
};
