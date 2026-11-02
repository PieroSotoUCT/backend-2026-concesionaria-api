# Diagramas del sistema

## 1. Diagrama de clases del dominio

El siguiente diagrama representa las entidades principales del sistema de concesionaria, sus atributos y las relaciones entre ellas.

```mermaid
classDiagram
    class Cliente {
        +int id
        +str rut
        +str nombre
        +str correo
        +str telefono
        +str direccion
    }

    class Sucursal {
        +int id
        +str nombre
        +str direccion
        +str ciudad
        +str telefono
        +str horario_atencion
    }

    class Vehiculo {
        +int id
        +str marca
        +str modelo
        +int anio
        +int precio
        +int kilometraje
        +str transmision
        +str condicion
        +str estado
        +int sucursal_id
    }

    class Reserva {
        +int id
        +date fecha_reserva
        +date fecha_vencimiento
        +int monto_reserva
        +str estado
        +int cliente_id
        +int vehiculo_id
    }

    Sucursal "1" --> "0..*" Vehiculo : tiene
    Cliente "1" --> "0..*" Reserva : realiza
    Vehiculo "1" --> "0..*" Reserva : recibe
```

## 2. Diagrama de datos

El siguiente diagrama representa la estructura de las tablas persistidas mediante SQLAlchemy ORM, incluyendo sus claves primarias, claves foráneas y restricciones de unicidad.

```mermaid
erDiagram
    SUCURSAL ||--o{ VEHICULO : tiene
    CLIENTE ||--o{ RESERVA : realiza
    VEHICULO ||--o{ RESERVA : recibe

    SUCURSAL {
        int id PK
        string nombre
        string direccion
        string ciudad
        string telefono
        string horario_atencion
    }

    CLIENTE {
        int id PK
        string rut UK
        string nombre
        string correo
        string telefono
        string direccion
    }

    VEHICULO {
        int id PK
        string marca
        string modelo
        int anio
        int precio
        int kilometraje
        string transmision
        string condicion
        string estado
        int sucursal_id FK
    }

    RESERVA {
        int id PK
        date fecha_reserva
        date fecha_vencimiento
        int monto_reserva
        string estado
        int cliente_id FK
        int vehiculo_id FK
    }
```

## 3. Relaciones entre entidades

### Sucursal y vehículo

Una sucursal puede tener asociados varios vehículos.

Cada vehículo pertenece a una sucursal mediante el atributo `sucursal_id`, que actúa como clave foránea.

Cardinalidad:

- Una sucursal puede tener cero o muchos vehículos.
- Cada vehículo pertenece a una sucursal.

### Cliente y reserva

Un cliente puede realizar distintas reservas a lo largo del tiempo.

Cada reserva referencia a un cliente mediante `cliente_id`.

Cardinalidad:

- Un cliente puede tener cero o muchas reservas.
- Cada reserva pertenece a un cliente.

### Vehículo y reserva

Un vehículo puede aparecer en diferentes registros de reserva a lo largo del historial del sistema.

Cada reserva referencia a un vehículo mediante `vehiculo_id`.

Cardinalidad:

- Un vehículo puede tener cero o muchas reservas históricas.
- Cada reserva referencia a un vehículo.

Las reglas del servicio de reservas controlan la disponibilidad y evitan reservas activas incompatibles para un mismo vehículo.

## 4. Dominio y persistencia

El diagrama de clases representa las entidades principales del dominio y sus relaciones conceptuales.

El diagrama de datos representa las tablas persistidas en la base de datos y permite identificar:

- **PK (Primary Key):** identificador principal de cada registro.
- **FK (Foreign Key):** referencia a otra tabla mediante una clave foránea.
- **UK (Unique Key):** restricción de unicidad aplicada al RUT del cliente.

Los modelos ORM implementan las relaciones entre sucursales, vehículos, clientes y reservas mediante SQLAlchemy.

La persistencia permite mantener la integridad referencial de los registros y representar las asociaciones entre las entidades del sistema.