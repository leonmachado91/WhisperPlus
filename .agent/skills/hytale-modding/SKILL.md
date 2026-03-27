---
name: hytale-modding
description: |
  Comprehensive Hytale modding guide covering all 4 official categories: Server Plugins (Java), Data Assets (JSON), Art Assets (Blockbench), and Save Files. Use when creating mods, plugins, packs, custom blocks, items, NPCs, world generation, or any Hytale game modification. Covers ECS architecture, Events, Commands, Registries, and content creation workflows. Essential for both no-code (Asset Editor) and programmer (Java 25 + IntelliJ) approaches.
---

# Hytale Modding

This skill provides comprehensive guidance for creating mods in Hytale, covering all official modding categories and community best practices.

## Quick Reference

| Modding Type | Files | Tools | Coding Required |
|--------------|-------|-------|-----------------|
| **Server Plugins** | `.jar` (Java) | IntelliJ IDEA, Gradle | Yes (Java 25) |
| **Data Assets** | `.json` | Asset Editor | No |
| **Art Assets** | `.bbmodel`, textures, sounds | Blockbench | No |
| **Save Files** | Worlds, prefabs | In-game tools | No |

## Technical Architecture

### Network & Infrastructure

| Aspect | Details |
|--------|---------|
| **Protocol** | QUIC (Quick UDP Internet Connections) - Fast like UDP, reliable like TCP |
| **Server Port** | UDP 5520 (default) |
| **Tick Rate** | 30 TPS (configurable via plugins) |
| **Rendering** | OpenGL 3.3 (Vulkan/Metal planned) |
| **Multi-core** | Yes - each world has main thread + parallel execution |

### Platform Support

- **Windows** (primary)
- **Linux** (actively supported)
- **macOS** (in development)
- Any OS with Java 25 runtime

### Server-Side Capabilities

Plugins have **full Java access**:
- Database connections (MySQL, PostgreSQL, MongoDB)
- Web requests (REST APIs, webhooks)
- Any Java library or framework
- Machine learning frameworks
- Scripting languages (Lua, JavaScript via Java)

### Hot Reload Support

- JSON data files ✓
- Models and textures ✓
- World generation assets ✓
- Some code changes require restart

## Core Architecture

### Entity-Component-System (ECS)

Hytale uses ECS architecture:
- **Entities**: Lightweight references (IDs)
- **Components**: Store data (position, health, inventory)
- **Systems**: Process logic based on component data

### Key Systems

1. **Registries**: Type-safe registration for components, commands, assets
2. **Events**: Sync/async event system with priority ordering
3. **Codecs**: Serialization system for config and data files
4. **Commands**: Argument parsing with permission support
5. **NoesisGUI**: Custom UI system (transitioning, allows custom menus/HUDs)

## Packs (No-Code Content)

Packs are the primary way to add content without programming.

### Pack Structure

```
%AppData%/Hytale/UserData/Packs/YourPackName/
├── manifest.json          # Required: Pack metadata
├── Common/                 # Visual assets (client-side)
│   ├── Models/
│   └── Textures/
└── Server/                 # Game logic (server-side)
    ├── Blocks/
    ├── Items/
    ├── Translations/
    └── Particles/
```

### Manifest Template

```json
{
  "Group": "your-group",
  "Name": "YourPackName",
  "Version": "1.0.0",
  "Description": "Pack description",
  "Authors": [{ "Name": "Your Name" }],
  "ServerVersion": "*",
  "Dependencies": [],
  "DisabledByDefault": false
}
```

### Creating Blocks

See [references/blocks-items.md](references/blocks-items.md) for complete block creation guide with:
- Block states (on/off, open/closed)
- Block animations (.blockyanim)
- Textures and models

### Activating Packs

1. Open Hytale → Worlds tab
2. Right-click target world
3. Toggle on your Pack
4. Enter world to test

## Plugins (Java Development)

Server plugins extend functionality programmatically.

### Requirements

- Java 25 (Adoptium/Temurin recommended)
- IntelliJ IDEA (or VSCode with Java extensions)
- Gradle build system

### Quick Start

1. Download [plugin template](https://github.com/realBritakee/hytale-template-plugin)
2. Configure `settings.gradle.kts` and `manifest.json`
3. Import into IntelliJ IDEA
4. Configure Java 25 SDK
5. Run HytaleServer configuration

### Plugin Structure

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
        // Called when plugin is loaded - register commands, events
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
        // Called on server stop - cleanup
        getLogger().at(Level.INFO).log("Plugin shutting down!");
    }
}
```

### Plugin Manifest

```json
{
  "Group": "com.yourgroup",
  "Name": "MyPlugin",
  "Version": "1.0.0",
  "Main": "com.yourgroup.myplugin.MyPlugin",
  "Description": "Plugin description",
  "Authors": [{ "Name": "Your Name" }],
  "ServerVersion": "*"
}
```

### Event System

```java
import com.hypixel.hytale.server.core.event.IEvent;
import com.hypixel.hytale.server.core.event.ICancellable;
import com.hypixel.hytale.server.core.event.priority.EventPriority;

// Subscribe to events in setup()
getEventRegistry().register(PlayerConnectEvent.class, this::onPlayerConnect);
getEventRegistry().register(PlaceBlockEvent.class, this::onBlockPlace, EventPriority.EARLY);

private void onPlayerConnect(PlayerConnectEvent event) {
    event.player().sendMessage(Message.raw("Welcome!"));
}

private void onBlockPlace(PlaceBlockEvent event) {
    if (event.isCancelled()) return; // ICancellable check
    // process block placement
}
```

#### Event Types

| Interface | Description |
|-----------|-------------|
| `IEvent<KeyType>` | Synchronous event with optional key |
| `IAsyncEvent<KeyType>` | Async event (use for I/O) |
| `ICancellable` | Can be cancelled (`setCancelled(true)`) |

### Commands

```java
import com.hypixel.hytale.server.core.command.system.AbstractCommand;
import com.hypixel.hytale.server.core.command.system.CommandContext;
import com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes;
import java.util.concurrent.CompletableFuture;

public class HelloCommand extends AbstractCommand {
    private final RequiredArg<String> targetArg;
    
    public HelloCommand() {
        super("hello", "Says hello to a player");
        targetArg = withRequiredArg("player", "Target player", ArgTypes.STRING);
    }
    
    @Override
    protected CompletableFuture<Void> execute(CommandContext context) {
        String target = targetArg.get(context);
        context.sender().sendMessage(Message.raw("Hello, " + target + "!"));
        return CompletableFuture.completedFuture(null);
    }
}

// Register in setup():
getCommandRegistry().registerCommand(new HelloCommand());
```

#### Argument Types

`ArgTypes.STRING`, `ArgTypes.INTEGER`, `ArgTypes.DOUBLE`, `ArgTypes.BOOLEAN`, `ArgTypes.LIST`

## Server Configuration

### Default Port

UDP 5520 (QUIC protocol)

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `mods/` | Plugin JARs |
| `Packs/` | Content packs |
| `worlds/` | World saves |
| `config/` | Server configuration |

## Tools & Resources

### Official Tools

- **Asset Editor**: In-game tool for creating/editing content (no coding)
- **Blockbench**: Official support for 3D model creation

### Community Resources

- [Hytale Modding Docs](https://hytale-docs.pages.dev/) - Server documentation
- [HytaleModding.dev](https://hytalemodding.dev/) - Community guides
- [Britakee Documentation](https://britakee-studios.gitbook.io/hytale-modding-documentation) - Comprehensive tutorials
- [Plugin Template](https://github.com/realBritakee/hytale-template-plugin) - Ready-to-use starter

### Discord Communities

- [Hytale Modding Discord](https://discord.gg/hytalemodding)
- [Vulpes Lab Discord](https://discord.gg/jshWA2kRmF)

## Common Patterns

### Config Files with Codecs

```java
public record MyConfig(String setting, int value) {
    public static final Codec<MyConfig> CODEC = RecordCodecBuilder.create(instance ->
        instance.group(
            Codec.STRING.fieldOf("setting").forGetter(MyConfig::setting),
            Codec.INT.fieldOf("value").forGetter(MyConfig::value)
        ).apply(instance, MyConfig::new)
    );
}
```

### Async Operations & Tasks

```java
import com.hypixel.hytale.server.HytaleServer;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

// Register tasks for automatic cleanup on plugin disable
CompletableFuture<Void> asyncTask = CompletableFuture.runAsync(() -> {
    // Long-running operation
});
getTaskRegistry().registerTask(asyncTask);

// Periodic task (e.g., auto-save every 5 minutes)
ScheduledFuture<?> periodic = HytaleServer.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(
    () -> { savePlayerData(); },
    5, 5, TimeUnit.MINUTES
);
getTaskRegistry().registerTask(periodic);
```

### Component Registration

```java
@Override
protected void setup() {
    ComponentRegistry.register(MyComponent.class, MyComponent.CODEC);
}
```

## Debugging

### Logging

```java
import java.util.logging.Level;

getLogger().at(Level.INFO).log("Info message");
getLogger().at(Level.WARNING).log("Warning: " + issue);
getLogger().at(Level.SEVERE).log("Error: " + error);
```

### Hot Reload

Some changes can be reloaded without restart via Asset Editor or server commands.

### Breakpoints

IntelliJ debugger works with the HytaleServer run configuration.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plugin doesn't load | Check manifest.json Main class path |
| Gradle sync fails | Verify Java 25 SDK configured |
| Pack not showing | Check manifest.json format and folder structure |
| Cannot connect | Verify port 5520 UDP is open |

## Best Practices

1. **Use semantic versioning** for plugins and packs
2. **Test locally** before deploying to production servers
3. **Bundle assets** with plugins when possible
4. **Use events** instead of polling for game state
5. **Prefer ECS patterns** for entity modifications
6. **Document your mods** for other developers and users
