#include "event_processor.hpp"
#include "models.hpp"

#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <thread>
#include <vector>

std::atomic<bool> keep_running{true};

void handle_signal(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        keep_running = false;
    }
}

int main() {
    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    const char* api_url = std::getenv("INGEST_API_URL");
    std::string target = api_url ? api_url : "http://python-api:8000/internal/events";

    const char* ingest_token = std::getenv("INGEST_TOKEN");
    std::string token = ingest_token ? ingest_token : "local-token";

    EventProcessor processor(512, 8, target, token, 3);
    processor.start();

    std::vector<std::thread> producers;
    for (int src = 1; src <= 7; ++src) {
        producers.emplace_back([src, &processor]() {
            int counter = 0;
            while (keep_running) {
                Event event{
                    random_uuid(),
                    "source-" + std::to_string(src),
                    now_iso8601(),
                    (counter % 5 == 0) ? "critical" : ((counter % 3 == 0) ? "high" : "medium"),
                    (counter % 2 == 0) ? "cpu_spike" : "latency_anomaly",
                    "{\"value\":" + std::to_string(50 + (counter % 50)) + ",\"unit\":\"percent\"}",
                    0,
                };
                processor.submit_event(event);
                counter++;
                std::this_thread::sleep_for(std::chrono::milliseconds(120 + src * 15));
            }
        });
    }

    while (keep_running) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    for (auto& thread : producers) {
        if (thread.joinable()) {
            thread.join();
        }
    }

    processor.stop();
    std::cout << "Shutdown complete. Dead letter events: " << processor.dead_letter_count() << std::endl;
    return 0;
}
