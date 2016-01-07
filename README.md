# mobile-push
A mobile-push microservice (APNS, GCM)

## Usage

### Environment
The process will see `MOBILE_PUSH_ENV` environment variable to decide what configuration file to use.
The environment variable is mandatory.

-----

### bin/competing_consumer.py

```
MOBILE_PUSH_ENV=production python competing_consumer.py
```

A script to poll SQS and perform actions.
The SQS message is basically a JSON array.
Each element inside the array is an action and its arguments.
See the following actions.

#### Create topic
Create a topic in SNS.

```json
{
    "action": "create_topic",
    "args": {
        "topic": "topic-name"
    }
}
```

#### Create APNS token
Create a APNS token attached to a SNS APNS application.

```json
{
    "action": "create_apns_token",
    "args": {
        "token": "a valid APNS token",
        "user_data": "a json serializeable object"
    }
}
```

#### Create GCM token
Create a GCM token attached to a SNS GCM application.

```json
{
    "action": "create_gcm_token",
    "args": {
        "token": "a valid GCM token",
        "user_data": "a json serializeable object"
    }
}
```

#### Subscribe a topic
Subscribe a APNS token or GCM token to a topic.

```json
{
    "action": "subscribe_topic",
    "args": {
        "token": "a APNS or GCM token",
        "topic": "a topic name"
    }
}
```

#### Unsubscribe a topic
Unsubscribe a APNS or GCM token from a topic.

```json
{
    "action": "unsubscribe_topic",
    "args": {
        "token": "a APNS or GCM token",
        "topic": "a topic name"
    }
}
```

#### Publish to a topic
Publish a message to a topic. The message should conform to SNS format.

```json
{
    "action": "publish_to_topic",
    "args": {
        "topic": "a topic name",
        "message": "{\"default\":\"hello world\",\"APNS\":\"{\\\"aps\\\":{\\\"alert\\\": \\\"hello world\\\"} }\",\"GCM\":\"{ \\\"data\\\": { \\\"message\\\": \\\"hello world\\\" } }\"}"
    }
}
```

#### Direct publish to a device
Publish a message to a device. The message should conform to SNS format.

```json
{
    "action": "direct_publish",
    "args": {
        "tokens": [
            "a valid APNS or GCM token"
        ],
        "message": "{\"default\":\"hello world\",\"APNS\":\"{\\\"aps\\\":{\\\"alert\\\": \\\"hello world\\\"} }\",\"GCM\":\"{ \\\"data\\\": { \\\"message\\\": \\\"hello world\\\" } }\"}"
    }
}
```
