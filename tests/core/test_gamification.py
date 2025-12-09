import pytest
from src.core.gamification import UserProgress

def test_user_initial_state():
    user = UserProgress()
    assert user.xp == 0
    assert user.current_streak == 0
    assert user.currency == 0
    assert user.level == 1

def test_add_xp():
    user = UserProgress()
    user.add_xp(50)
    assert user.xp == 50
    assert user.level == 1
    
    user.add_xp(60) # Total 110
    assert user.xp == 110
    assert user.level == 2 # Assuming 100 XP per level for simplicity initially

def test_update_streak():
    user = UserProgress()
    user.increment_streak()
    assert user.current_streak == 1
    
    user.reset_streak()
    assert user.current_streak == 0

def test_add_currency():
    user = UserProgress()
    user.add_currency(10)
    assert user.currency == 10
    
    user.spend_currency(5)
    assert user.currency == 5
    
    with pytest.raises(ValueError):
        user.spend_currency(10) # Should fail if not enough currency