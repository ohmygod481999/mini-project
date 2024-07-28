import asyncio

import pytest

from chatserver.concurrency_control import ConcurrencyControl


@pytest.mark.asyncio
async def test_concurrency():
    test_cases = [
        {
            "max_connections": 4,
            "max_connection_per_client": 1,
            "client_ids": ["1", "2", "3", "4", "5"],
            "expected": 4,
        },
        {
            "max_connections": 4,
            "max_connection_per_client": 1,
            "client_ids": ["1", "2", "3"],
            "expected": 3,
        },
        {
            "max_connections": 4,
            "max_connection_per_client": 2,
            "client_ids": ["1", "1", "3", "4"],
            "expected": 4,
        },
        {
            "max_connections": 4,
            "max_connection_per_client": 1,
            "client_ids": ["1", "1", "3", "4"],
            "expected": 3,
        },
        {
            "max_connections": 5,
            "max_connection_per_client": 1,
            "client_ids": ["1", "2", "3", "2", "3"],
            "expected": 3,
        },
        {
            "max_connections": 5,
            "max_connection_per_client": 4,
            "client_ids": ["1", "1", "1", "2", "3"],
            "expected": 5,
        },
    ]
    for test_case in test_cases:
        concurrency_control = ConcurrencyControl(
            max_connections=test_case["max_connections"],
            max_connection_per_client=test_case["max_connection_per_client"],
        )
        await concurrency_control.clean_all_sessions()
        client_ids = test_case["client_ids"]
        result = await asyncio.gather(
            *[
                concurrency_control.acquire_connection(client_id)
                for client_id in client_ids
            ]
        )
        hash_map = await concurrency_control._get_hash_map()
        print("-----")
        print(test_case)
        print("result", result)
        print("hash_map", hash_map)
        connection_count = sum([int(hash_map[client_id]) for client_id in hash_map])
        assert connection_count == test_case["expected"]

    await concurrency_control.clean_all_sessions()
