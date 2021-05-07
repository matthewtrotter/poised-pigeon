import time
import tests.messages.lnsalerts_pb2 as la


def rand_alert(num_alerts: int = 10, seed: int = 1234):
    """Yield a random alert on every call
    """
    for i in range(num_alerts):
        # Create a random alert
        alert = la.Alert()
        alert.ownerid = 1
        alert.code = 1000
        alert.subcode = 13
        alert.message = f"Generic alert occured at time {time.time()}"
        
        # Yield to test function
        yield alert