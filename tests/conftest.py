"""Shared fixtures for all tests."""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.fixture
def sample_source_text():
    """A simple C#-like source text for testing."""
    return """public class MGMultiGateSolver
{
    private NativeArray<ActorData> m_ActorData;

    public void Initialize()
    {
        m_ActorData = new NativeArray<ActorData>(100, Allocator.Persistent);
    }

    public void AddCommand(CreateActorCommand cmd)
    {
        // Process command
        if (cmd == null) { Debug.LogError("cmd is null"); return; }
        m_CommandQueue.Enqueue(cmd);
    }

    public void Update()
    {
        foreach (var cmd in m_CommandQueue)
        {
            ProcessCommand(cmd);
        }
    }
}"""


@pytest.fixture
def sample_extractions():
    """Sample extractions for pipeline testing."""
    return [
        {
            "type": "entity",
            "text": "public class MGMultiGateSolver",
            "summary_cn": "倍增门解算器核心类",
        },
        {
            "type": "rule",
            "text": "if (cmd == null) { Debug.LogError(\"cmd is null\"); return; }",
            "summary_cn": "命令空检查规则",
            "condition": "cmd == null",
            "action": "LogError + return",
        },
        {
            "type": "constraint",
            "text": "NativeArray<ActorData>",
            "summary_cn": "Actor数据使用NativeArray存储",
            "check_type": "type_constraint",
            "condition_cn": "必须使用NativeArray存储Actor数据",
        },
        {
            "type": "event",
            "text": "m_CommandQueue.Enqueue(cmd)",
            "summary_cn": "命令入队事件",
        },
    ]


@pytest.fixture
def grounded_extractions(sample_source_text, sample_extractions):
    """Extractions that have been through source grounding."""
    from source_grounding import SourceGrounder

    grounder = SourceGrounder(sample_source_text)
    return grounder.process(sample_extractions)
