# Plugin Development Reference

Advanced patterns and detailed API reference for Hytale plugin development.

## Project Setup

### Gradle Configuration

`settings.gradle.kts`:
```kotlin
rootProject.name = "my-plugin"

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}
```

`build.gradle.kts`:
```kotlin
plugins {
    java
}

group = "com.yourgroup"
version = "1.0.0"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(25))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    compileOnly(files("libs/HytaleServer.jar"))
}

tasks.jar {
    archiveBaseName.set("MyPlugin")
    
    // Include resources
    from("src/main/resources")
}
```

### Manifest Schema

`manifest.json`:
```json
{
  "Group": "com.yourgroup",
  "Name": "MyPlugin",
  "Version": "1.0.0",
  "Main": "com.yourgroup.myplugin.MyPlugin",
  "Description": "Description of your plugin",
  "Authors": [
    { "Name": "Your Name", "Role": "Developer" }
  ],
  "Website": "https://yourwebsite.com",
  "ServerVersion": "*",
  "Dependencies": [],
  "OptionalDependencies": [],
  "LoadOrder": "NORMAL"
}
```

### Load Order Options

| Value | Description |
|-------|-------------|
| `EARLIEST` | Load first (bootstrap plugins) |
| `EARLY` | Load before normal plugins |
| `NORMAL` | Default load order |
| `LATE` | Load after normal plugins |
| `LATEST` | Load last |

## Plugin Lifecycle

```java
import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;
import java.util.logging.Level;

public class MyPlugin extends JavaPlugin {
    private static MyPlugin instance;
    
    public MyPlugin(JavaPluginInit init) {
        super(init);
    }
    
    public static MyPlugin get() { return instance; }
    
    @Override
    protected void setup() {
        // Called when plugin is loading - register events, commands
        instance = this;
        getEventRegistry().register(BootEvent.class, this::onBoot);
        getCommandRegistry().registerCommand(new MyCommand());
    }
    
    @Override
    protected void start() {
        // Called when server is ready
        getLogger().at(Level.INFO).log("Plugin started!");
    }
    
    @Override
    protected void shutdown() {
        // Called on server stop - cleanup resources
        getLogger().at(Level.INFO).log("Plugin shutting down!");
    }
}
```

## Event System

### Event Priorities

| Priority | Description |
|----------|-------------|
| `EARLY` | Called first |
| `NORMAL` | Default |
| `LATE` | Called last |

### Subscribing to Events

```java
import com.hypixel.hytale.server.core.event.IEvent;
import com.hypixel.hytale.server.core.event.ICancellable;
import com.hypixel.hytale.server.core.event.priority.EventPriority;

// In setup() method:
getEventRegistry().register(PlayerConnectEvent.class, this::onConnect);
getEventRegistry().register(PlaceBlockEvent.class, this::onBlockPlace, EventPriority.EARLY);

private void onConnect(PlayerConnectEvent event) {
    event.player().sendMessage(Message.raw("Welcome!"));
}

private void onBlockPlace(PlaceBlockEvent event) {
    if (event.isCancelled()) return;
    // process placement
}
```

### Cancellable Events

```java
private void onBlockBreak(BreakBlockEvent event) {
    if (isProtectedBlock(event.block())) {
        event.setCancelled(true);
        event.player().sendMessage(Message.raw("Protected!"));
    }
}
```

### Async Events

```java
// IAsyncEvent runs on async thread - safe for I/O
getEventRegistry().register(PlayerChatAsyncEvent.class, this::onChat);

private void onChat(PlayerChatAsyncEvent event) {
    String filtered = filterMessage(event.message());
    event.setMessage(filtered);
}
```

### Common Events

| Event | Trigger |
|-------|---------|
| `PlayerJoinEvent` | Player connects |
| `PlayerQuitEvent` | Player disconnects |
| `PlayerChatEvent` | Chat message sent |
| `BlockBreakEvent` | Block destroyed |
| `BlockPlaceEvent` | Block placed |
| `EntityDamageEvent` | Entity takes damage |
| `EntityDeathEvent` | Entity dies |
| `InventoryClickEvent` | Inventory interaction |

### Custom Events

### Custom Events

```java
import com.hypixel.hytale.server.core.event.IEvent;
import com.hypixel.hytale.server.core.event.ICancellable;

public class CustomEvent implements IEvent<Void>, ICancellable {
    private final Player player;
    private boolean cancelled = false;
    
    public CustomEvent(Player player) {
        this.player = player;
    }
    
    public Player player() { return player; }
    
    @Override
    public boolean isCancelled() { return cancelled; }
    
    @Override
    public void setCancelled(boolean cancelled) { 
        this.cancelled = cancelled; 
    }
}

// Firing the event from your plugin
CustomEvent event = new CustomEvent(player);
// dispatchFor(EventClass, Key) or dispathFor(EventClass) if key is Void
MyPlugin.get().getEventRegistry().dispatchFor(CustomEvent.class, event);

if (!event.isCancelled()) {
    // Proceed
}
```

## Command System

### Basic Command

### Basic Command

```java
import com.hypixel.hytale.server.core.command.system.AbstractCommand;
import com.hypixel.hytale.server.core.command.system.CommandContext;
import com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg;
import com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes;
import java.util.concurrent.CompletableFuture;

public class GreetCommand extends AbstractCommand {
    private final RequiredArg<String> targetArg;
    
    public GreetCommand() {
        super("greet", "Greet a player");
        // Arguments are registered in constructor
        targetArg = withRequiredArg("player", "Player to greet", ArgTypes.STRING);
    }
    
    @Override
    protected CompletableFuture<Void> execute(CommandContext context) {
        String targetName = targetArg.get(context);
        context.sender().sendMessage(Message.raw("Hello, " + targetName + "!"));
        return CompletableFuture.completedFuture(null);
    }
}
```

### Command Arguments

```java
// String argument
RequiredArg<String> strArg = withRequiredArg("text", "desc", ArgTypes.STRING);

// Integer argument
RequiredArg<Integer> intArg = withRequiredArg("number", "desc", ArgTypes.INTEGER);

// Double argument
RequiredArg<Double> doubleArg = withRequiredArg("val", "desc", ArgTypes.DOUBLE);

// Boolean argument
RequiredArg<Boolean> boolArg = withRequiredArg("flag", "desc", ArgTypes.BOOLEAN);

// List argument
RequiredArg<List> listArg = withRequiredArg("items", "desc", ArgTypes.LIST);
```

### Argument Types

- `ArgTypes.STRING`
- `ArgTypes.INTEGER` 
- `ArgTypes.DOUBLE`
- `ArgTypes.BOOLEAN`
- `ArgTypes.LIST`

### Tab Completion

// Tab completion logic can be customized by overriding methods in AbstractCommand
```

## Components (ECS)

### Accessing Components

```java
Entity entity = ...;

// Get component
HealthComponent health = entity.getComponent(HealthComponent.class);
if (health != null) {
    health.setHealth(health.getHealth() + 10);
}

// Check for component
if (entity.hasComponent(FlyingComponent.class)) {
    // Entity can fly
}
```

### Custom Components

```java
public class CustomComponent implements Component {
    private int customValue;
    
    public static final Codec<CustomComponent> CODEC = 
        RecordCodecBuilder.create(instance ->
            instance.group(
                Codec.INT.fieldOf("customValue")
                    .forGetter(c -> c.customValue)
            ).apply(instance, CustomComponent::new)
        );
    
    public CustomComponent(int customValue) {
        this.customValue = customValue;
    }
    
    // Getters and setters
}

// Register in setup()
@Override
protected void setup() {
    ComponentRegistry.register(CustomComponent.class, CustomComponent.CODEC);
}
```

## Scheduler & Tasks

### Delayed Tasks

```java
import com.hypixel.hytale.server.HytaleServer;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ScheduledFuture;

// Run after 1 second
ScheduledFuture<?> task = HytaleServer.SCHEDULED_EXECUTOR.schedule(
    () -> { player.sendMessage(Message.raw("Delayed message!")); },
    1, TimeUnit.SECONDS
);
getTaskRegistry().registerTask(task);
```

### Repeating Tasks

```java
// Run every 5 seconds
ScheduledFuture<?> repeatingTask = HytaleServer.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(
    () -> { broadcastMessage("Keepalive signal"); },
    0, 5, TimeUnit.SECONDS
);
getTaskRegistry().registerTask(repeatingTask);

// Tasks registered in TaskRegistry are automatically cancelled on plugin disable
```

### Async operations

```java
import java.util.concurrent.CompletableFuture;

// Using CompletableFuture for async/sync workflow
CompletableFuture.runAsync(() -> {
    // Async thread: Heavy I/O
    String data = fetchFromDatabase();
    return data;
}).thenAccept(data -> {
    // Sync thread (if configured) or handle safely
    processData(data);
});
```

## Configuration

### Using Codecs

```java
public record PluginConfig(
    String welcomeMessage,
    int maxPlayers,
    List<String> bannedWords
) {
    public static final Codec<PluginConfig> CODEC = RecordCodecBuilder.create(i ->
        i.group(
            Codec.STRING.fieldOf("welcomeMessage")
                .forGetter(PluginConfig::welcomeMessage),
            Codec.INT.fieldOf("maxPlayers")
                .forGetter(PluginConfig::maxPlayers),
            Codec.STRING.listOf().fieldOf("bannedWords")
                .forGetter(PluginConfig::bannedWords)
        ).apply(i, PluginConfig::new)
    );
    
    public static final PluginConfig DEFAULT = new PluginConfig(
        "Welcome to the server!",
        100,
        List.of()
    );
}
```

### Loading Config

```java
private PluginConfig config;

private PluginConfig config;

@Override
protected void setup() {
    config = loadConfig("config.json", PluginConfig.CODEC, PluginConfig.DEFAULT);
}
```

## Database Patterns

### Service-Storage Pattern

Separates business logic (Service) from data persistence (Storage):

```java
// Storage Interface - Handles data persistence
public interface PlayerStorage {
    PlayerData load(UUID uuid);
    void save(PlayerData data);
    List<PlayerData> loadAll();
}

// Service Layer - Business logic and caching
public class PlayerService {
    private final PlayerStorage storage;
    private final Map<UUID, PlayerData> cache = new ConcurrentHashMap<>();
    
    public PlayerService(PlayerStorage storage) {
        this.storage = storage;
    }
    
    public PlayerData getPlayer(UUID uuid) {
        return cache.computeIfAbsent(uuid, id -> {
            PlayerData data = storage.load(id);
            return data != null ? data : new PlayerData(id);
        });
    }
    
    public void savePlayer(PlayerData data) {
        cache.put(data.getUuid(), data);
        storage.save(data);
    }
}
```

**Benefits**:
- Clean separation of concerns
- Easy to swap storage backends (JSON → Database)
- Testable business logic
- In-memory caching layer

### Thread Pool Management

```java
public class MyPlugin extends JavaPlugin {
    private ScheduledExecutorService executor;
    
    @Override
    protected void setup() {
        executor = Executors.newScheduledThreadPool(4);
        
        // Schedule periodic tasks
        executor.scheduleAtFixedRate(this::saveAllData, 5, 5, TimeUnit.MINUTES);
    }
    
    @Override
    protected void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
    }
}
```

**Benefits**:
- Reuses threads instead of creating new ones
- Limits concurrent threads (resource management)
- Built-in support for delayed/periodic tasks

### Singleton Pattern for Plugin Access

```java
public class MyPlugin extends JavaPlugin {
    private static MyPlugin instance;
    
    @Override
    public void onEnable() {
        instance = this;
    }
    
    public static MyPlugin getInstance() {
        return instance;
    }
}
```

## Codec Types Reference

| Java Type | Codec | Example Value |
|-----------|-------|---------------|
| `Double` | `Codec.DOUBLE` | `0.40` |
| `Integer` | `Codec.INT` | `100` |
| `String` | `Codec.STRING` | `"Hello"` |
| `Boolean` | `Codec.BOOL` | `true` |
| `Long` | `Codec.LONG` | `1000000L` |
| `Float` | `Codec.FLOAT` | `1.5f` |
| `List<T>` | `Codec.STRING.listOf()` | `["a", "b"]` |

## Networking

### Custom Packets

```java
public class MyPacket implements Packet {
    private final String data;
    
    public MyPacket(String data) {
        this.data = data;
    }
    
    @Override
    public void write(PacketBuffer buffer) {
        buffer.writeString(data);
    }
    
    public static MyPacket read(PacketBuffer buffer) {
        return new MyPacket(buffer.readString());
    }
}

// Register
PacketRegistry.register(MyPacket.class, MyPacket::read);

// Send
player.sendPacket(new MyPacket("Hello!"));
```

## Testing

### Gradle Test Task

```kotlin
dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

tasks.test {
    useJUnitPlatform()
}
```

### Unit Test Example

```java
class MyPluginTest {
    
    @Test
    void testPlayerDataSerialization() {
        PlayerData original = new PlayerData(UUID.randomUUID(), 100, 50);
        
        String json = serialize(original);
        PlayerData deserialized = deserialize(json, PlayerData.class);
        
        assertEquals(original.health(), deserialized.health());
        assertEquals(original.coins(), deserialized.coins());
    }
}
```

## Performance Tips

1. **Cache frequently accessed data**
2. **Use async for I/O operations**
3. **Batch database writes**
4. **Avoid heavy computations in event handlers**
5. **Use object pooling for frequent allocations**
6. **Profile with IntelliJ profiler**

## Debugging

### Log Levels

```java
getLogger().fine("Debug info");      // FINE
getLogger().info("Information");     // INFO
getLogger().warning("Warning!");     // WARNING
getLogger().severe("Error!");        // SEVERE
```

### Debug Mode

Enable in server config:
```json
{
  "debug": true,
  "logLevel": "FINE"
}
```
