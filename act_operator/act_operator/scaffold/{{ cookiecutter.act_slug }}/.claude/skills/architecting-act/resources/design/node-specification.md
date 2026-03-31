# Node Specification Guide

## Core Principle

**Single Responsibility:** Each node does ONE thing.

**Test:** If you use "and" to describe it, split it.

## Design Process

1. Break workflow into discrete operations
2. Each LLM/API/DB call = separate node
3. Apply granularity check

**Too coarse (split):** Does multiple operations, hard to describe in one sentence.

**Too fine (merge):** Always runs together, trivial operation.

## Node Types

### Flat Node
A regular function that reads/writes state. Single deterministic operation.

### Agent Subgraph Node (`create_agent`)
A `create_agent` compiled graph added as a node. Has its own tool set and reasoning loop. Use when the node needs tools + autonomous reasoning.

### DeepAgent Subgraph Node (`create_deep_agent`)
A `create_deep_agent` compiled graph. Has subagent delegation, backends, memory. Use when the node needs multi-step planning, sandbox, or subagent spawning.

### Orchestrator Node (internally invokes subgraphs)
A flat node function that internally invokes one or more agent subgraphs. Use when custom pre/post-processing or dynamic agent selection is needed.

## Output Format

**IMPORTANT: Describe node structure only. Do NOT write other modules(tool, middleware etc.) or implementation code (def functions, classes etc.).**

For **flat nodes**:
```
Nodes:
- NodeName - Single responsibility description
```

For **agent subgraph nodes**:
```
Nodes:
- AgentName (create_agent subgraph) - Agent responsibility description
  - Tools: [tool names]
```

For **deep agent subgraph nodes**:
```
Nodes:
- AgentName (create_deep_agent) - Agent responsibility description
  - Tools: [tool names]
```

For **orchestrator nodes** (internally invoking subgraphs):
```
Nodes:
- OrchestratorName - Orchestration responsibility description
  - Invokes: [agent subgraph names]
```

## Naming Convention

**REQUIRED: CamelCase format** (not lowercase or snake_case)
- ✅ Good: `InspectorAgent`, `ResponseGenerater`
- ❌ Bad: `inspect_agent`, `generate_response`

## Checklist

- [ ] Each node has single responsibility
- [ ] Names are clear (VerbNoun format)
- [ ] LLM calls are separated