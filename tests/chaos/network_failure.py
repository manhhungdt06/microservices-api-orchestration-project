import random
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class NetworkFailureTest:
    def __init__(self):
        config.load_kube_config()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        
    def simulate_network_partition(self, namespace, service_name, duration):
        try:
            # Get pods for the service
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={service_name}"
            )
            
            if not pods.items:
                print(f"No pods found for service {service_name}")
                return

            # Select random pod to isolate
            target_pod = random.choice(pods.items)
            print(f"Isolating pod {target_pod.metadata.name} from network")

            # Create network policy to block traffic
            policy = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": f"isolate-{target_pod.metadata.name}",
                    "namespace": namespace
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": {
                            "app": service_name
                        }
                    },
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": [],
                    "egress": []
                }
            }
            
            self.networking_v1.create_namespaced_network_policy(
                namespace=namespace,
                body=policy
            )

            # Wait for specified duration
            print(f"Network partition active for {duration} seconds")
            time.sleep(duration)

            # Clean up network policy
            self.networking_v1.delete_namespaced_network_policy(
                name=f"isolate-{target_pod.metadata.name}",
                namespace=namespace
            )
            print("Network partition removed")

        except ApiException as e:
            print(f"Error during network failure test: {e}")

if __name__ == "__main__":
    test = NetworkFailureTest()
    test.simulate_network_partition(
        namespace="default",
        service_name="auth-service",
        duration=60
    )
