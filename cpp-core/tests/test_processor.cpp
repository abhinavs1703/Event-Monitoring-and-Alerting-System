#include "event_processor.hpp"

#include <cassert>
#include <chrono>
#include <thread>

int main() {
    EventProcessor processor(8, 2, "http://localhost:9999/not-running", "token", 1);
    processor.start();

    Event invalid{"", "source-1", "2025-01-01T00:00:00Z", "high", "cpu", "{}", 0};
    processor.submit_event(invalid);

    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    processor.stop();

    assert(processor.dead_letter_count() >= 1);
    return 0;
}
