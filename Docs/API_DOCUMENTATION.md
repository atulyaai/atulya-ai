# Atulya AI API Documentation

## Overview

Atulya AI provides a comprehensive REST API for interacting with the dynamic intelligence system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for local development.

## Endpoints

### Health Check

**GET** `/health`

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "agent_available": true,
  "uptime": "2024-01-01T12:00:00"
}
```

### Root

**GET** `/`

Returns system information.

**Response:**
```json
{
  "service": "Atulya AI - Dynamic Intelligence",
  "version": "0.1.0",
  "status": "active",
  "agent_available": true,
  "main_brain": "DeepSeek R1",
  "capabilities": [
    "text", "vision", "speech", "document", 
    "embedding", "tools", "admin"
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### Chat

**POST** `/chat`

Send a message to the AI agent.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "user_id": "user123",
  "context": {},
  "stream": false
}
```

**Response:**
```json
{
  "success": true,
  "response": "Hello! I'm doing well, thank you for asking.",
  "model_used": "DeepSeek R1",
  "processing_time": 1.2,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Admin

**POST** `/admin`

Admin operations for system management.

**Request Body:**
```json
{
  "action": "status",
  "parameters": {},
  "user_id": "admin"
}
```

**Response:**
```json
{
  "success": true,
  "system_status": {
    "status": "operational",
    "models_loaded": 3,
    "memory_usage": "2.1GB"
  },
  "metrics": {
    "requests_processed": 150,
    "errors_count": 2
  },
  "active_sessions": 5
}
```

### Status

**GET** `/status`

Get detailed system status.

**Response:**
```json
{
  "status": "operational",
  "agent_available": true,
  "metrics": {
    "requests_processed": 150,
    "models_loaded": 3,
    "errors_count": 2,
    "start_time": "2024-01-01T10:00:00"
  },
  "active_sessions": 5,
  "timestamp": "2024-01-01T12:00:00"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Rate Limiting

Currently, no rate limiting is implemented for local development.

## WebSocket Support

WebSocket support for real-time chat is planned for future releases. 