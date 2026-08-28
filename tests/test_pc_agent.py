from aioffice_modules.pc_agent import HeartbeatRequest, health, heartbeat, next_tasks


def test_pc_agent_health_and_heartbeat() -> None:
    health_response = health()
    assert health_response.status == "healthy"

    heartbeat_response = heartbeat(
        HeartbeatRequest(agent_id="local-pc-agent", running_task_ids=[], capacity=1)
    )
    assert heartbeat_response["accepted"] is True
    assert heartbeat_response["agentId"] == "local-pc-agent"
    assert heartbeat_response["runningTaskIds"] == []
    assert heartbeat_response["capacity"] == 1
    assert "seenAt" in heartbeat_response


def test_task_poll_interface_returns_list() -> None:
    assert next_tasks() == []


def test_pc_agent_rejects_invalid_capacity() -> None:
    try:
        HeartbeatRequest(agent_id="local-pc-agent", running_task_ids=[], capacity=-1)
    except ValueError:
        return
    raise AssertionError("negative capacity should be rejected")
