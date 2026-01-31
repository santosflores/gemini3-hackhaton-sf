
import logging
from agents.sub_agents.time.agent import get_current_time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_time_tool():
    print("Testing get_current_time function directly...")
    
    # Test case 1: Known city
    try:
        result = get_current_time("London")
        print(f"London Result: {result}")
        assert result['status'] == 'success'
    except Exception as e:
        print(f"FAILED London: {e}")

    # Test case 2: Unknown city
    try:
        result = get_current_time("Narnia")
        print(f"Narnia Result: {result}")
        assert result['status'] == 'error'
    except Exception as e:
        print(f"FAILED Narnia: {e}")
        
    # Test case 3: City with comma
    try:
        result = get_current_time("Monterrey, MX")
        print(f"Monterrey Result: {result}")
        assert result['status'] == 'success'
    except Exception as e:
        print(f"FAILED Monterrey: {e}")

if __name__ == "__main__":
    test_time_tool()
