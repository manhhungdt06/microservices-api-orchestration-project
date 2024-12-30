# Application Flow

## System Flow Overview

The application follows a microservices architecture with API orchestration through a central gateway. The flow begins with client requests entering through the API Gateway, which then routes them to the appropriate microservices. The services communicate with each other through synchronous REST APIs and asynchronous message queues.

## Architecture Diagram

```
                                     │
                                     ▼
                            [API Gateway (Kong)]
                                     │
                    ┌────────┬──────┴───────┬────────┐
                    ▼        ▼              ▼        ▼
              [User Service] [Product Service] [Order Service] [Payment Service]
                    │        │              │        │
                    ▼        ▼              ▼        ▼
             [PostgreSQL] [MongoDB]    [PostgreSQL] [PostgreSQL]
                    │        │              │        │
                    └────────┴──────┬───────┴────────┘
                                   ▼
                            [Message Broker]
                          (RabbitMQ/Kafka)
```

## Flow Description

1. **Client Request**: All external requests first hit the API Gateway
2. **Routing**: The gateway routes requests to appropriate services based on the endpoint
3. **Service Processing**: Each service handles its specific business logic
4. **Database Interaction**: Services interact with their dedicated databases
5. **Inter-service Communication**: Services communicate through REST APIs or message queues
6. **Response**: The gateway aggregates responses and returns them to the client

## Key Components

- **API Gateway**: Central entry point for all requests, handles routing, authentication, and rate limiting
- **Microservices**: Independent services handling specific business capabilities
- **Databases**: Dedicated databases for each service's data storage needs
- **Message Broker**: Facilitates asynchronous communication between services
