"""Test the agent factory by running a simple query with all backends."""

from my_app.agent_factory import create_agent


def test_agent(agent_type: str, **kwargs):
    """Test a single agent type.
    
    Args:
        agent_type: Type of agent ("mock", "openai", "local")
        **kwargs: Additional agent configuration
    """
    print(f"\n{'='*60}")
    print(f"Testing {agent_type.upper()} Agent")
    print('='*60)
    
    try:
        # Create agent
        agent = create_agent(agent_type, **kwargs)
        print(f"✅ Agent created successfully")
        
        # Test query
        test_query = "How do I track my order?"
        print(f"\nQuery: {test_query}")
        
        response = agent.process_query(test_query)
        print(f"Response: {response}")
        print(f"✅ Agent processed query successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    results = {}
    
    # Test Mock Agent
    results["mock"] = test_agent("mock")
    
    # Test OpenAI Agent (skip if no API key)
    import os
    if os.getenv("OPENAI_API_KEY"):
        results["openai"] = test_agent(
            "openai",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200,
        )
    else:
        print("\n" + "="*60)
        print("Skipping OpenAI Agent (OPENAI_API_KEY not set)")
        print("="*60)
        results["openai"] = None
    
    # Test Local Agent (skip if model not found)
    from pathlib import Path
    model_path = Path("./models/Mistral-7B-Instruct-v0.1.Q4_K_M.gguf")
    if model_path.exists():
        results["local"] = test_agent(
            "local",
            model_path=str(model_path),
            n_ctx=512,
            n_threads=4,
        )
    else:
        print("\n" + "="*60)
        print(f"Skipping Local Agent (model not found at {model_path})")
        print("="*60)
        results["local"] = None
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for agent_type, success in results.items():
        if success is None:
            status = "⏭️  SKIPPED"
        elif success:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{agent_type:10} : {status}")
