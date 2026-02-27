#include "event_processor.hpp"

#include <curl/curl.h>

#include <chrono>
#include <iostream>
#include <thread>

EventProcessor::EventProcessor(size_t queue_capacity, size_t worker_count, std::string api_url, std::string ingest_token, int max_retries)
    : queue_(queue_capacity), pool_(worker_count), api_url_(std::move(api_url)), ingest_token_(std::move(ingest_token)), max_retries_(max_retries) {
    curl_global_init(CURL_GLOBAL_ALL);
}

void EventProcessor::start() {
    running_ = true;
    for (size_t i = 0; i < 4; ++i) {
        pool_.enqueue([this]() {
            while (running_) {
                auto maybe_event = queue_.pop();
                if (!maybe_event.has_value()) {
                    return;
                }
                Event event = maybe_event.value();
                if (!validate_event(event)) {
                    std::lock_guard<std::mutex> lock(dlq_mutex_);
                    dead_letter_queue_.push_back(event);
                    continue;
                }

                bool success = dispatch_event(event);
                while (!success && event.retry_count < max_retries_) {
                    event.retry_count += 1;
                    std::this_thread::sleep_for(std::chrono::milliseconds(100 * event.retry_count));
                    success = dispatch_event(event);
                }

                if (!success) {
                    std::lock_guard<std::mutex> lock(dlq_mutex_);
                    dead_letter_queue_.push_back(event);
                }
            }
        });
    }
}

void EventProcessor::stop() {
    running_ = false;
    queue_.close();
    pool_.shutdown();
    curl_global_cleanup();
}

void EventProcessor::submit_event(const Event& event) {
    if (!queue_.push(event)) {
        std::cerr << "Queue closed; event dropped: " << event.event_id << std::endl;
    }
}

size_t EventProcessor::dead_letter_count() const {
    std::lock_guard<std::mutex> lock(dlq_mutex_);
    return dead_letter_queue_.size();
}

bool EventProcessor::validate_event(const Event& event) const {
    return !event.event_id.empty() && !event.source_id.empty() && !event.timestamp.empty() && !event.severity.empty() &&
           !event.event_type.empty() && !event.payload.empty();
}

bool EventProcessor::dispatch_event(const Event& event) const {
    CURL* curl = curl_easy_init();
    if (!curl) {
        return false;
    }

    std::string body =
        "{\"event_id\":\"" + event.event_id + "\",\"source_id\":\"" + event.source_id + "\",\"timestamp\":\"" +
        event.timestamp + "\",\"severity\":\"" + event.severity + "\",\"event_type\":\"" + event.event_type +
        "\",\"payload\":" + event.payload + "}";

    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    std::string token_header = "x-ingest-token: " + ingest_token_;
    headers = curl_slist_append(headers, token_header.c_str());

    curl_easy_setopt(curl, CURLOPT_URL, api_url_.c_str());
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 1500L);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    CURLcode result = curl_easy_perform(curl);
    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    return result == CURLE_OK && status >= 200 && status < 300;
}
