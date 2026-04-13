---
name: grpc-protobuf
description: gRPC and Protocol Buffers for service-to-service communication. Use when user mentions "grpc", "protobuf", "protocol buffers", ".proto", "grpcurl", "service definition", "RPC", "streaming", "buf", "protoc", or building gRPC services.
---

# gRPC and Protocol Buffers

## Protobuf Basics

Protocol Buffers (protobuf) is a language-neutral binary serialization format. Define schemas in `.proto` files.

```protobuf
syntax = "proto3";
package myapp.v1;
option go_package = "github.com/myorg/myapp/gen/myappv1";

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
  repeated string roles = 5;       // ordered list
  Address address = 6;             // nested message
  UserStatus status = 7;           // enum
  map<string, string> metadata = 8; // key-value pairs
}

message Address {
  string street = 1;
  string city = 2;
  string country = 3;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;  // required zero value
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_INACTIVE = 2;
}
```

### Scalar Types

| Protobuf | Go      | Python | Node    | Java       |
|----------|---------|--------|---------|------------|
| double   | float64 | float  | number  | double     |
| float    | float32 | float  | number  | float      |
| int32    | int32   | int    | number  | int        |
| int64    | int64   | int    | number  | long       |
| bool     | bool    | bool   | boolean | boolean    |
| string   | string  | str    | string  | String     |
| bytes    | []byte  | bytes  | Buffer  | ByteString |

Field numbers 1-15 use one byte on the wire -- reserve them for frequent fields. Never reuse field numbers. Use wrapper types (`google.protobuf.StringValue`) to distinguish unset from default.

## Service Definitions

```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);           // unary
  rpc ListUsers(ListUsersRequest) returns (stream User);           // server streaming
  rpc UploadUsers(stream User) returns (UploadUsersResponse);      // client streaming
  rpc SyncUsers(stream SyncRequest) returns (stream SyncResponse); // bidirectional
}

message GetUserRequest { string id = 1; }
message GetUserResponse { User user = 1; }
message ListUsersRequest { int32 page_size = 1; string page_token = 2; }
```

## Code Generation with protoc

```bash
# Install: brew install protobuf (macOS) / apt install protobuf-compiler (Linux)

# Go
protoc --go_out=. --go-grpc_out=. proto/user.proto

# Python
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/user.proto

# Node.js
grpc_tools_node_protoc --js_out=import_style=commonjs:. --grpc_out=. proto/user.proto
```

## buf Tool (Modern protoc Replacement)

```yaml
# buf.yaml
version: v2
modules:
  - path: proto
lint:
  use: [STANDARD]
breaking:
  use: [FILE]
```

```yaml
# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/protocolbuffers/go
    out: gen/go
    opt: paths=source_relative
  - remote: buf.build/grpc/go
    out: gen/go
    opt: paths=source_relative
```

```bash
buf lint                                    # Lint proto files
buf breaking --against '.git#branch=main'   # Detect breaking changes
buf generate                                # Generate code
```

buf enforces style: package names match directories, enum zero values end in `_UNSPECIFIED`, service names end in `Service`.

## gRPC Patterns

- **Unary**: one request, one response. Use for CRUD, lookups.
- **Server streaming**: one request, stream of responses. Use for large result sets, feeds.
- **Client streaming**: stream of requests, one response. Use for uploads, batch ingestion.
- **Bidirectional**: both sides stream independently. Use for chat, real-time sync.

## gRPC in Node.js

```javascript
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const packageDef = protoLoader.loadSync("proto/user.proto", {
  keepCase: true, longs: String, enums: String, defaults: true, oneofs: true,
});
const proto = grpc.loadPackageDefinition(packageDef).myapp.v1;

// Server
function getUser(call, callback) {
  callback(null, { user: { id: call.request.id, name: "Alice" } });
}
function listUsers(call) {
  for (let i = 0; i < 10; i++) call.write({ id: String(i), name: `User ${i}` });
  call.end();
}
const server = new grpc.Server();
server.addService(proto.UserService.service, { getUser, listUsers });
server.bindAsync("0.0.0.0:50051", grpc.ServerCredentials.createInsecure(), () => {});

// Client
const client = new proto.UserService("localhost:50051", grpc.credentials.createInsecure());
client.getUser({ id: "123" }, (err, res) => {
  if (err) return console.error(`Code: ${err.code}, Message: ${err.details}`);
  console.log(res.user);
});
const stream = client.listUsers({ page_size: 10 });
stream.on("data", (user) => console.log(user));
stream.on("end", () => console.log("done"));
```

## gRPC in Python

```python
import grpc
from concurrent import futures
import user_pb2, user_pb2_grpc

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        if not request.id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "id required")
        return user_pb2.GetUserResponse(user=user_pb2.User(id=request.id, name="Alice"))

    def ListUsers(self, request, context):
        for i in range(10):
            yield user_pb2.User(id=str(i), name=f"User {i}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

# Client
channel = grpc.insecure_channel("localhost:50051")
stub = user_pb2_grpc.UserServiceStub(channel)
try:
    response = stub.GetUser(user_pb2.GetUserRequest(id="123"), timeout=5)
except grpc.RpcError as e:
    print(f"Code: {e.code()}, Details: {e.details()}")
for user in stub.ListUsers(user_pb2.ListUsersRequest(page_size=10)):
    print(user)
```

## gRPC in Go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "net"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    pb "github.com/myorg/myapp/gen/myappv1"
)

type server struct{ pb.UnimplementedUserServiceServer }

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "id required")
    }
    return &pb.GetUserResponse{User: &pb.User{Id: req.Id, Name: "Alice"}}, nil
}

func (s *server) ListUsers(req *pb.ListUsersRequest, stream pb.UserService_ListUsersServer) error {
    for i := 0; i < 10; i++ {
        if err := stream.Send(&pb.User{Id: fmt.Sprintf("%d", i)}); err != nil {
            return err
        }
    }
    return nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    pb.RegisterUserServiceServer(s, &server{})
    log.Fatal(s.Serve(lis))
}
```

Go client:

```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
defer conn.Close()
client := pb.NewUserServiceClient(conn)
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
resp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: "123"})
if err != nil {
    st, _ := status.FromError(err)
    log.Printf("Code: %s, Message: %s", st.Code(), st.Message())
}
```

## grpcurl for Testing

```bash
# Install: brew install grpcurl
# Server must have reflection enabled, or use -import-path/-proto flags

grpcurl -plaintext localhost:50051 list                              # list services
grpcurl -plaintext localhost:50051 describe myapp.v1.UserService     # describe service
grpcurl -plaintext -d '{"id":"123"}' localhost:50051 myapp.v1.UserService/GetUser
grpcurl -plaintext -H 'authorization: Bearer tok' -d '{"id":"123"}' \
  localhost:50051 myapp.v1.UserService/GetUser                       # with metadata
grpcurl -plaintext -import-path ./proto -proto user.proto \
  -d '{"page_size":10}' localhost:50051 myapp.v1.UserService/ListUsers
```

Enable reflection: Go `reflection.Register(s)`, Python `grpc_reflection.v1alpha.reflection.enable_server_reflection(names, server)`, Node `@grpc/reflection`.

## Error Handling: gRPC Status Codes

| Code                | Num | Use For                              |
|---------------------|-----|--------------------------------------|
| OK                  | 0   | Success                              |
| CANCELLED           | 1   | Client cancelled                     |
| INVALID_ARGUMENT    | 3   | Bad input                            |
| DEADLINE_EXCEEDED   | 4   | Timeout                              |
| NOT_FOUND           | 5   | Resource missing                     |
| ALREADY_EXISTS      | 6   | Conflict on create                   |
| PERMISSION_DENIED   | 7   | Lacks permission                     |
| RESOURCE_EXHAUSTED  | 8   | Rate limit / quota                   |
| FAILED_PRECONDITION | 9   | System not in required state         |
| UNIMPLEMENTED       | 12  | Method not implemented               |
| INTERNAL            | 13  | Unexpected server error              |
| UNAVAILABLE         | 14  | Transient -- client should retry     |
| UNAUTHENTICATED     | 16  | No valid credentials                 |

Do not use `UNKNOWN` as a catch-all. Return `UNAVAILABLE` for transient failures so clients retry.

## Metadata

Metadata is the gRPC equivalent of HTTP headers. Keys are strings; binary values use keys ending in `-bin`.

```go
// Go: read incoming metadata
md, _ := metadata.FromIncomingContext(ctx)
token := md.Get("authorization")
// Go: send outgoing metadata
ctx = metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer tok")
```

```python
# Python: read
token = context.invocation_metadata()  # list of (key, value) tuples
# Python: send
stub.GetUser(request, metadata=[("authorization", "Bearer tok")])
```

## Deadlines and Timeouts

Always set deadlines. A missing deadline holds resources indefinitely. Propagate the incoming context in chained calls so the overall deadline is respected.

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
```

```python
response = stub.GetUser(request, timeout=5)
```

```javascript
const deadline = new Date(Date.now() + 5000);
client.getUser({ id: "123" }, { deadline }, callback);
```

## Health Checking

Use the standard `grpc.health.v1.Health` protocol. Do not invent your own.

```go
import "google.golang.org/grpc/health"
import healthpb "google.golang.org/grpc/health/grpc_health_v1"
hs := health.NewServer()
healthpb.RegisterHealthServer(s, hs)
hs.SetServingStatus("myapp.v1.UserService", healthpb.HealthCheckResponse_SERVING)
```

```bash
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

## Common Patterns

### Microservice API Structure

```
proto/myapp/
  user/v1/user.proto
  user/v1/user_service.proto
  order/v1/order.proto
  order/v1/order_service.proto
```

Keep request/response messages with the service. Share domain messages via imports. Use `v1` package suffix for versioning.

### Streaming Data Feed

```protobuf
service PriceFeed {
  rpc Subscribe(SubscribeRequest) returns (stream PriceUpdate);
}
message SubscribeRequest { repeated string symbols = 1; }
message PriceUpdate { string symbol = 1; double price = 2; int64 timestamp = 3; }
```

Client reconnects on `UNAVAILABLE` with exponential backoff. Use keepalive settings to detect dead connections.

## gRPC vs REST

| Concern         | gRPC                           | REST                           |
|-----------------|--------------------------------|--------------------------------|
| Serialization   | Protobuf (binary, compact)     | JSON (text, readable)          |
| Schema          | Required (.proto)              | Optional (OpenAPI)             |
| Streaming       | Native (4 patterns)            | SSE / WebSocket workarounds    |
| Browser         | Needs grpc-web proxy           | Native                         |
| Tooling         | protoc/buf + plugins           | curl, any HTTP client          |
| Performance     | Lower latency, smaller payload | Higher latency, larger payload |
| Code gen        | Built-in, strongly typed       | Varies                         |
| Load balancing  | L7 HTTP/2-aware required       | Any HTTP LB                    |

Use gRPC for internal service-to-service calls where performance, type safety, and streaming matter. Use REST for public APIs and browser clients. Both coexist well -- REST at the edge, gRPC internally.
