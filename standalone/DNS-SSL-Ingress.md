# DNS, SSL, and Ingress for Kubernetes
This document contains instructions for configuring DNS, SSL, and Ingress for Kubernetes.


## DNS, SSL, and Ingress
While this guide will not cover all the different aspects of DNS, SSL, and Ingress configuations possible, we will cover a few senarios that will help you route and secure traffic to Atlas. The files referenced below are all in the `k8s` directory of this repo.

### Your company already has procedures in place to manage DNS, SSL Certificates, and a Ingress Service

1. Obtain a full chain SSL certificate that includes the root CA, intermidate cert, and the Atlas cert
2. Obtain the Atlas certificate key
3. Obtain a DNS record for Atlas. i.e. atlas.yourdomain.com
4. Configure the Ingress Service to route `https://atlas.yourdomain.com` traffic to the `atlas-service`

### Cloud hosted Kubernetes with a public certificate

1. Obtain a the full chain public SSL certificate i.e. atlas.yourdomain.com
    - Create a file called `atlas.crt` and copy the full chain certificate into the crt file, removing all text and any new line chars.  Do not remove the `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` lines

2. Obtain the public SSL certificate key
    - Create a file called `atlas.key` and copy the private key into key file

3. Convert the Atlas cert and key to base64:
    - Run the following commands:

        ```
        cat atlas.crt | base64
        cat atlas.key | base64
        ```

4. Deploy the atlas-tls-secret.yaml file to your Kubernetes cluster:

    ```
    kubectl apply -f atlas-tls-secret.yaml
    ```

5. Install Nginx-Ingress - We recommend installing using [Helm](#https://helm.sh/docs/intro/install/)
    - Set the Kubernetes context where you are installing atlas and run the following command:

        ```
        helm install nginx-ingress stable/nginx-ingress --namespace atlas --default-ssl-certificate=default/atlas-tls-secret --set controller.replicaCount=1 --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux
        ```

6. Wait for the LoadBalancer service to start and provide an external IP address

7. Configure DNS
    - <a href="https://docs.microsoft.com/en-us/azure/dns/dns-getstarted-portal">Azure</a>
    - <a href="https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html">AWS</a>

7. Update the atlas-ingress.yaml file
    - Replace `atlas.yourdomain.com` with your atlas URL

8. Deploy the atlas-ingress.yaml file to your Kubernetes cluster:

    ```
    kubectl apply -f atlas-ingress.yaml
    ```

9. If your domain name provider is different than your cloud provider, you will need to add the Name Servers from your cloud provider to your domain name provider.

### Cloud hosted Kubernetes with a self-signed certificate

By default, Nginx-Ingress includes a self-signed certificate called "Kubernetes Ingress Controller Fake Certificate". If you would like to replace the default self-signed certificate with your own self-signed certificate, follow the instructions below. NOTE: RegScale recommends the use of signed certificates from a trusted authority to verify authenticity and to reduce the number of browser security warnings encountered by end users.

1. Create a self-signed certificate

    ```
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout atlas.key -out atlas.crt -subj "/CN=yourdomain.com/O=yourdomain.com"
    ```

2. Upload certifcate to your cloud provider
    - <a href="https://docs.microsoft.com/en-us/rest/api/keyvault/importcertificate/importcertificate">Azure</a>
    - <a href="https://aws.amazon.com/premiumsupport/knowledge-center/import-ssl-certificate-to-iam/">AWS</a>

3. Convert the Atlas cert and key to base64:
    - Run the following commands:

        ```
        cat atlas.crt | base64
        cat atlas.key | base64
        ```

4. Copy the base64 results from step 3 and update the respective fields in the atlas-tls-secret.yaml file

5. Deploy the atlas-tls-secret.yaml file to your Kubernetes cluster:

    ```
    kubectl apply -f atlas-tls-secret.yaml
    ```

6. Deploy the atlas-ingress-cm.yaml file to your Kubernetes cluster:

    ```
    kubectl apply -f atlas-ingress-cm.yaml
    ```

7. Install Nginx-Ingress - We recommend installing using [Helm](#https://helm.sh/docs/intro/install/)
    - Set the Kubernetes context where you are installing atlas and run the following command:

        ```
        helm install nginx-ingress stable/nginx-ingress --namespace atlas --default-ssl-certificate=default/atlas-tls-secret --set controller.replicaCount=1 --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux
        ```

8. Wait for the LoadBalancer service to start and provide an external IP address

9. Configure DNS
    - <a href="https://docs.microsoft.com/en-us/azure/dns/dns-getstarted-portal">Azure</a>
    - <a href="https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html">AWS</a>

10. Update the atlas-ingress.yaml file
    - Replace `atlas.yourdomain.com` with your atlas URL

11. Deploy the atlas-ingress.yaml file to your Kubernetes cluster:

    ```
    kubectl apply -f atlas-ingress.yaml
    ```
  
12. If your domain name provider is different than your cloud provider, you will need to add the Name Servers from your cloud provider to your domain name provider.
