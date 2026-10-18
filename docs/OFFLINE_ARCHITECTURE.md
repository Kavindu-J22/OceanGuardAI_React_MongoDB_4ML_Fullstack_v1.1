# OceanGuard AI — Offline-First Architecture & Synchronization Engine

## 1. Maritime Connectivity Context

Artisanal, day-boat, and multi-day fishing craft operating in Sri Lanka experience severe telecommunication constraints:
1. **Cellular Drop-Off:** High-speed 4G LTE terrestrial mobile connectivity degrades and terminates approximately 12 to 18 nautical miles (NM) from the coast.
2. **Economic Prohibitions:** Satellite data transceivers (e.g., Inmarsat FleetBroadband, Iridium Certus) carry capital and bandwidth costs far exceeding the operating budget of small-scale fisheries.
3. **Operational Necessity:** Critical safety advisories, catch logging, and voyage monitoring must function continuously throughout multi-day voyages that can extend up to 100-200 NM offshore for 5 to 15 days.

OceanGuard AI is fundamentally designed as an **offline-first progressive web platform (PWA)** that operates autonomously offshore and performs seamless bi-directional synchronization upon returning to shore cellular or harbour Wi-Fi coverage.

---

## 2. Local Storage Architecture (IndexedDB)

The client application leverages native browser IndexedDB managed via the typed `idb` abstraction layer.

### 2.1 Object Stores & Schema

```typescript
interface OceanGuardDBSchema extends DBSchema {
  // Vessel profiles, stability constants, and hydrostatic curves
  vessels: {
    key: string;              // vessel_id (e.g. 'V038')
    value: VesselRecord;
  };
  
  // Historical and in-progress voyage plans
  trips: {
    key: string;              // trip_id (e.g. 'TRIP_2026_001')
    value: TripRecord;
  };

  // Locally cached ML inference results and spatio-temporal grids
  cachedPredictions: {
    key: string;              // Composite key: `${component}_${date}_${target}`
    value: {
      key: string;
      component: 'C1' | 'C2' | 'C3' | 'C4' | 'INTEGRATED';
      data: any;
      cachedAt: string;       // ISO 8601 timestamp
    };
  };

  // Chronological queue of mutations executed while disconnected
  offlineSyncQueue: {
    key: number;              // Auto-incrementing transaction ID
    value: {
      id?: number;
      endpoint: string;       // API endpoint (e.g., '/api/v1/trips')
      method: string;         // HTTP method (POST, PATCH, PUT)
      payload: any;           // Request body payload
      createdAt: string;      // Timestamp of skipper action
      retryCount: number;     // Transmission retry counter
    };
    indexes: { 'by-endpoint': string };
  };
}
```

---

## 3. Offline Mutation & Interception Lifecycle

```
  [User Action in React UI] (e.g., Log Catch / Update Trip State)
                 |
                 v
  [Axios HTTP Client Interceptor]
                 |
        Is navigator.onLine?
        /                  \
      YES                   NO (or Network Failure ERR_NETWORK)
      /                      \
  [Dispatch HTTP to Backend]  [Intercept Request & Prevent Error Screen]
                              |
                              +--> Add payload to 'offlineSyncQueue' in IndexedDB
                              |
                              +--> Update local optimistic UI state
                              |
                              +--> Display Status: "Queued for shore synchronization"
```

### 3.1 Transparent Interceptor Logic
When an outgoing mutation (`POST` or `PATCH`) encounters an offline state or network drop:
1. The Axios response interceptor intercepts the failure.
2. The endpoint, method, and JSON body are written into `offlineSyncQueue`.
3. An optimistic response payload is constructed and returned to the caller, preventing UI crash or blocking dialogs.
4. The global Zustand store increments `pendingSyncCount` and displays an amber notification badge in the application navbar.

---

## 4. Reconnection & Synchronization Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Skipper as Vessel Skipper
    participant Browser as Browser Event Loop
    participant Store as Zustand App Store
    participant IDB as Local IndexedDB
    participant API as FastAPI Cloud Backend
    participant DB as Central MongoDB

    Note over Skipper,Browser: Vessel returns to harbour; Cellular 4G signal restored
    Browser->>Browser: Emit 'online' event (navigator.onLine = true)
    Browser->>Store: Trigger setOnlineStatus(true)
    Store->>Store: Invoke syncOfflineQueue()
    Store->>IDB: getPendingSyncQueue()
    IDB-->>Store: Return N pending queue items (FIFO order)
    
    loop For each queued item in chronological order
        Store->>API: HTTP POST/PATCH (Payload with original client timestamp)
        alt Success (HTTP 200/201)
            API->>DB: Upsert / Insert document
            DB-->>API: Acknowledged
            API-->>Store: 200 OK
            Store->>IDB: removeQueueItem(item.id)
        else Server Error / Conflict
            Store->>Store: Increment retryCount; preserve in queue
        end
    end

    Store->>IDB: refreshPendingSyncCount()
    Store->>Skipper: Display Green Toast: "Successfully synchronized N actions to shore server"
```

---

## 5. Conflict Resolution & Idempotency

To prevent race conditions, duplication, and stale overrides during batch replay:
1. **Client-Assigned Unique Identifiers:** All operational entities (Trips, Observations, Emergency Events) generate universally unique identifiers (`trip_id`, `observation_id`, `event_id`) on the client prior to enqueueing.
2. **Backend Upsert Semantics:** MongoDB mutation endpoints utilize `$set` and upsert operations keyed on entity IDs rather than blind incremental inserts:
   ```python
   db.trips.update_one(
       {"trip_id": payload["trip_id"]},
       {"$set": payload},
       upsert=True
   )
   ```
3. **Temporal Ordering:** Every payload retains its original `client_created_at` timestamp so that server-side time is not falsely attributed to an event logged 4 days earlier while offshore.

---

## 6. Offline Model Operational Modes

When disconnected from the FastAPI server, the frontend offers graceful degradation:
- **Cached Spatial Charts:** The ST-GCN marine fishing suitability zones and sea surface temperature fronts remain interactive via Leaflet offline tile cache.
- **Static Vessel Hydrostatic Guidelines:** Vessel stability criteria, maximum recommended wave height limits, and Beaufort scale roll advisories are evaluated locally using JavaScript naval architecture equations.
- **Emergency Distress Buffering:** Emergency distress records are persisted to IndexedDB immediately, ensuring that as soon as any ephemeral radio or cellular packet is transmitted, the full distress payload is broadcast.
