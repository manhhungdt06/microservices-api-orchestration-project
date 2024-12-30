import random
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class PodFailureTest:
    def __init__(self):
        config.load_kube_config()
        self.core_v1 = client.CoreV1Api()
        
    def simulate_pod_failure(self, namespace, service_name):
        try:
            # Get pods for the service
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={service_name}"
            )
            
            if not pods.items:
                print(f"No pods found for service {service_name}")
                return

            # Select random pod to delete
            target_pod = random.choice(pods.items)
            print(f"Deleting pod {target_pod.metadata.name}")

            # Delete the pod
            self.core_v1.delete_namespaced_pod(
                name=target_pod.metadata.name,
                namespace=namespace
            )

            # Monitor pod recovery
            print("Monitoring pod recovery...")
            start_time = time.time()
            while True:
                new_pods = self.core_v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=f"app={service_name}"
                )
                
                # Check if new pod is running
                for pod in new_pods.items:
                    if pod.metadata.uid != target_pod.metadata.uid and \
                       pod.status.phase == "Running":
                        recovery_time = time.time() - start_time
                        print(f"Pod recovered in {recovery_time:.2f} seconds")
                        return
                
                time.sleep(1)

        except ApiException as e:
            print(f"Error during pod failure test: {e}")

if __name__ == "__main__":
    test = PodFailureTest()
    test.simulate_pod_failure(
        namespace="default",
        service_name="auth-service"
    )
