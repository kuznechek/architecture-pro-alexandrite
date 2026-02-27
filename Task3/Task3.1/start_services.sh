cd ./Task3/Task3.1

minikube start --addons=ingress 

# cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

#jaeger
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability
kubectl apply -f jaeger-instance.yaml

# сборка сервисов и деплой
minikube image build -t requesting-service:latest requesting-service/
minikube image build -t calculating-service:latest calculating-service/

kubectl apply -f services.yaml
