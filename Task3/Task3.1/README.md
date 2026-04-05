# Задание 3.1 Трейсинг с OpenTelemetry и Jaege

### Скрипт инициализации и запуска сервисов

```
sh Task3/Task3.1/start_services.sh
```

[start_services.sh](https://github.com/kuznechek/architecture-pro-alexandrite/blob/feature/Task3/Task3.1/start_services.sh)

### Тестирование

```
kubectl port-forward svc/simplest-query 16686:16686
```
[http://localhost:16686](http://localhost:16686)

```
kubectl exec -it $(kubectl get pods -l app=requesting-service -o jsonpath='{.items[0].metadata.name}') -- wget -qO- http://requesting-service:8080
```
