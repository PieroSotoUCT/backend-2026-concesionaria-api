# Diagramas del sistema

## Diagrama de clases del dominio

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
    }

    class Reserva {
        +int id
        +date fecha_reserva
        +date fecha_vencimiento
        +int monto_reserva
        +str estado
    }

    Sucursal "1" --> "0..*" Vehiculo : tiene
    Cliente "1" --> "0..*" Reserva : realiza
    Vehiculo "1" --> "0..*" Reserva : recibe
```

## Diagrama de datos

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

## Dominio y persistencia

El diagrama de clases representa las entidades del dominio y sus relaciones. El diagrama de datos representa las tablas persistidas, sus claves primarias (PK), claves foráneas (FK) y la restricción de unicidad del RUT.