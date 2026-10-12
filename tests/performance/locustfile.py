import random

from locust import HttpUser, between, task

from tests.performance.payloads import USER_PROFILES


class PulsoUser(HttpUser):
    wait_time = between(1, 2)

    @task(4)
    def analyze(self):
        profile = random.choice(USER_PROFILES)

        with self.client.post(
            "/api/analyze",
            json=profile,
            name="/api/analyze",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}: "
                    f"{response.text[:200]}"
                )

    @task(1)
    def simulate(self):
        profile = random.choice(USER_PROFILES)

        payload = {
            "original": profile,
            "changes": {
                "weight": max(30, profile["weight"] - 5),
                "ap_hi": max(70, profile["ap_hi"] - 10),
            },
        }

        with self.client.post(
            "/api/simulate",
            json=payload,
            name="/api/simulate",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}: "
                    f"{response.text[:200]}"
                )