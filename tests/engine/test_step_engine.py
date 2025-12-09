import pytest
from src.engine.step_engine import StepEngine, Step

def test_identify_linear_first_order():
    # Input: y' + 2y = e^x
    # Should identify P(x) = 2 and Q(x) = e^x
    equation_str = "Derivative(y(x), x) + 2*y(x) - exp(x)"
    engine = StepEngine()
    
    # We expect the engine to identify this as a First Order Linear ODE
    ode_type = engine.identify_type(equation_str)
    assert ode_type == "First Order Linear"

def test_solve_linear_steps():
    # Test the step-by-step breakdown for y' + 2y = e^x
    equation_str = "Derivative(y(x), x) + 2*y(x) - exp(x)"
    engine = StepEngine()
    
    steps = engine.solve_steps(equation_str)
    
    assert len(steps) > 0
    assert isinstance(steps[0], Step)
    
    # Check for critical steps we outlined in the TDD
    # 1. Identify P(x)
    has_p_step = any("P(x)" in s.explanation for s in steps)
    assert has_p_step
    
    # 2. Integrating Factor
    has_mu_step = any("Factor Integrante" in s.explanation for s in steps)
    assert has_mu_step