# Android Model Engine

**[Source Code on GitHub](https://github.com/the3deer/android-3D-engine)**

A standalone 3D rendering engine library for Android implementing a Scene Graph architecture and OpenGL ES 2.0/3.0 support.

## Overview

The engine is designed as a modular Android library (`:engine`) that can be easily integrated into any application. It provides a purely data-driven rendering pipeline, separating the complex 3D logic from the application's UI and state management.

## Features

*   **Scene Graph Architecture**: Manage complex scenes with parent-child object hierarchies and transformations.
*   **Multi-Format Parsers**: Built-in support for parsing GLTF and FBX model formats.
*   **Advanced Rendering**:
    *   Default and Anaglyph (Stereoscopic) renderers.
    *   Support for vertex, normals, colors, and textures.
*   **Animation**: Handles skeletal animations.
*   **Physics**: AABB-based collision detection and ray casting.
*   **CDI Framework**: A lightweight Contexts and Dependency Injection manager for building modular components.

## Architecture

#### Module Structure
- **`:app` (Android Application)**: The consumer of the engine. Handles UI, navigation, user preferences, and application state.
- **`:engine` (Android Library)**: A standalone 3D rendering engine. It implements a Scene Graph architecture, allowing for complex object hierarchies and transformations.

#### Design Principles
- **Scene Graph**: Instead of drawing flat lists of vertices, the engine manages a tree of `Node` objects. This allows for parent-child transformations (moving a group of objects together).
- **Separation of Concerns**: The `:engine` is purely data-driven. It doesn't know about ViewModels or SharedPreferences. It simply renders the `Model` data it is given.
- **MVP (Model-View-Projection)**: The engine uses standard 3D math matrices to handle object positions, camera views, and screen projections.

#### Application / Engine Integration
- **`GLSurfaceView`**: The engine provides a `org.the3deer.android.engine.renderer.GLSurfaceView` to be integrated into the application's layouts.
- **ViewModels (`SharedViewModel`, `ModelEngineViewModel`)**: The application uses ViewModels to manage state and push data into the engine for rendering.
- **CDI (`BeanFactory`)**: The engine's features can be configured and managed through a `BeanFactory` for dependency injection.

## Engine Sub-systems

### Renderer
The Renderer is responsible for handling the `onDrawFrame()` event from OpenGL.
*   **Default Renderer**: Holds a collection of `Drawer` objects that render various elements to the screen. It is linked to animation and world matrix updates.
*   **Anaglyph Renderer**: A specialized stereoscopic renderer capable of rendering for both left and right eyes to create a 3D effect.

### Collision Controller
The collision controller encapsulates the logic for collision detection using an Axis-Aligned Bounding Box (AABB) algorithm.
1.  2D screen coordinates are unprojected into a 3D ray.
2.  The ray is transformed into the object's local space.
3.  The ray is tested for intersection against the object's bounding box.
4.  If the bounding box is hit, an Octree is used to test the ray against individual triangles for a precise collision point.

### Model Parsers
The engine includes parsers to convert standard 3D file formats into its internal `Model` structure.

#### GLTF
The GLTF parser maps mesh primitives, skins, and nodes into the engine's `Object3D` and `Skin` structures. It handles unrolling vertex attributes like positions, normals, tangents, and texture coordinates.

```
- Mesh                  --------->  List<Object3D>
    |- Primitive            ----->      |- Object3D <fully assembled>
            |- POSITION                     |- Vertices
            |- NORMAL                       |- Normals
            |- INDICES                      |- Indices
            ...
```

#### FBX
A C-interface is used to parse `.fbx` files, exposing native methods to retrieve mesh data like vertices, normals, and indices via Java buffer objects.

```c
// FBXModel Java Class
# String native getName()
# int native getMeshCount()
# FBXMesh native getMesh(int index)

// FBXMesh Java Class
# Buffer native getVertexBuffer(int handler, int mesh)
# Buffer native getNormalsBuffer(int handler, int mesh)
# Buffer native getIndexBuffer(int handler, int mesh)
```

## CDI (Contexts and Dependency Injection) Manager

The engine includes a lightweight CDI manager to facilitate building modular, feature-based applications.

### Core Concepts
- **`@Feature`**: An annotation to group a set of related components.
- **`@Bean`**: An annotation to mark a class as a managed component.
- **`@BeanProperty`**: An annotation to expose a field or method as a configurable property.

### Preference Management
The CDI manager integrates with Android's `SharedPreferences`.
*   **Keys**: Preference keys are automatically generated as `<className>.<propertyName>`.
*   **Storage**: Property values are stored based on their type. `valueNames` in the annotation allows for string-based storage of complex types.

### Special Properties
*   **The `enabled` property**: A boolean property named `enabled` in a `@Bean` is treated as a master toggle. If set to `false`, all other properties in that bean are disabled in the UI.

```java
@Bean
public class MyComponent {
@BeanProperty
protected boolean enabled = true;

    @BeanProperty
    private float[] color; // Depends on 'enabled'
}
```

### Custom Property Values


    @BeanProperty(name = "Background Color", description = "Select the default color for 3D models", valueNames = {"White", "Gray", "Black"})
    private float[] backgroundColor = Constants.COLOR_GRAY;

    @BeanProperty(name = "backgroundColor", valueNames = {"White", "Gray", "Black"})
    public List<float[]> getBackgroundColorValues() {
        return Arrays.asList(Constants.COLOR_WHITE, Constants.COLOR_GRAY, Constants.COLOR_BLACK);
    }

### Delegated Property Values

    @BeanProperty(name = "Property X", description = "My delegated property X")
    public void setSomeFlag(boolean enabled){
        delegate.setSomeFlag(enabled);
    }

    @BeanProperty(description = "My delegated property X")
    public boolean isSomeFlag(){
        delegate.isSomeFlag();
        return false;
    }
