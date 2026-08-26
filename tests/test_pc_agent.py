from aioffice_modules.pc_agent import HeartbeatRequest, health, heartbeat, next_tasks


def test_pc_agent_health_and_heartbeat() -> None:
    health_response = health()
    assert health_response.status == "healthy"

    heartbeat_response = heartbeat(
        HeartbeatRequest(agent_id="local-pc-agent", running_task_ids=[], capacity=1)
    )
    assert heartbeat_response["accepted"] is True


def test_task_poll_interface_returns_list() -> None:
    assert next_tasks() == []
