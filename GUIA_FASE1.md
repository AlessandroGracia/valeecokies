# 📚 GUÍA EDUCATIVA - FASE 1: Fundamentos del Backend

## 🎯 ¿Qué acabamos de construir?

Hemos creado la **arquitectura base** de tu sistema de facturación. Piensa en esto como los cimientos de una casa: no se ve bonito todavía, pero es lo más importante.

---

## 🏗️ Estructura del Proyecto Explicada

```
galletas-system/
├── backend/
│   ├── app/
│   │   ├── core/           ← Configuración central
│   │   ├── models/         ← Tablas de la base de datos
│   │   └── schemas/        ← Validación de datos
│   ├── requirements.txt    ← Librerías necesarias
│   ├── .env.example        ← Plantilla de configuración
│   └── main.py            ← Punto de entrada
└── README.md
```

---

## 📖 CONCEPTOS CLAVE - Explicados Simple

### 1️⃣ **FastAPI - El Framework Web**

**¿Qué es?**
FastAPI es como un "traductor" que permite que tu código Python hable con navegadores y aplicaciones. Cuando tu app de escritorio necesita datos, FastAPI los entrega.

**¿Por qué FastAPI y no Flask o Django?**
- ⚡ **Más rápido**: Procesa miles de peticiones por segundo
- 📝 **Auto-documenta**: Genera documentación automáticamente en `/docs`
- ✅ **Validación automática**: Pydantic revisa los datos antes de procesarlos
- 🔥 **Moderno**: Usa async/await (código asíncrono)

**Ejemplo práctico:**
```python
@app.get("/productos")
def obtener_productos():
    return {"productos": [...]}
```
Cuando alguien visita `http://localhost:8000/productos`, FastAPI ejecuta esta función.

---

### 2️⃣ **SQLAlchemy - El ORM**

**¿Qué es un ORM?**
Object-Relational Mapping = Mapeo Objeto-Relacional

En lugar de escribir SQL:
```sql
SELECT * FROM productos WHERE stock_quantity < 10;
```

Escribes Python:
```python
db.query(Product).filter(Product.stock_quantity < 10).all()
```

**Ventajas:**
- ✅ Código más legible y mantenible
- ✅ Evita errores de SQL
- ✅ Cambiar de base de datos es más fácil
- ✅ Validaciones automáticas

---

### 3️⃣ **Pydantic - Validación de Datos**

**Problema que resuelve:**
Sin validación, un usuario podría enviar:
```json
{
  "price": "abc",  ← Texto en vez de número
  "quantity": -5   ← Cantidad negativa
}
```

Con Pydantic:
```python
class ProductCreate(BaseModel):
    price: Decimal = Field(..., gt=0)  # Debe ser > 0
    quantity: int = Field(..., ge=0)    # Debe ser >= 0
```

Si los datos son inválidos, **Pydantic rechaza automáticamente** la petición.

---

### 4️⃣ **Modelos vs Schemas - ¿Cuál es la diferencia?**

Esta es una confusión común. Te lo explico con analogía:

**MODELO (SQLAlchemy)** = Plano de la casa (estructura en la base de datos)
```python
class Product(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

**SCHEMA (Pydantic)** = Formulario de solicitud (lo que el usuario envía/recibe)
```python
class ProductCreate(BaseModel):
    name: str
    # No incluye 'id' porque se genera automáticamente
```

**Flujo completo:**
1. Usuario envía JSON → Pydantic valida (Schema)
2. Datos válidos → Se guardan en DB (Modelo)
3. Se consulta DB → Se devuelve al usuario (Schema de respuesta)

---

## 🗂️ LOS MODELOS DE TU SISTEMA

### **User (Usuario)**
```
- Vendedores y administradores del sistema
- Roles: ADMIN o VENDEDOR
- Autenticación con contraseña encriptada
```

### **Product (Producto/Galleta)**
```
- Catálogo de galletas
- Precios, stock, código
- Propiedad calculada: needs_restock, profit_margin
```

### **Customer (Cliente)**
```
- Base de datos de clientes
- Información de contacto
- Opcional: no todas las ventas requieren cliente
```

### **Sale (Venta/Factura)**
```
- Cabecera de la factura
- Totales, método de pago
- Relación con User (quién vendió) y Customer
```

### **SaleItem (Items de Venta)**
```
- Detalle de cada producto vendido
- Cantidad, precio unitario, subtotal
- Relación con Sale y Product
```

**Relación entre modelos:**
```
Sale (1) ←→ (muchos) SaleItem
  ↓                      ↓
User                  Product
  ↓
Customer (opcional)
```

---

## 🔐 SEGURIDAD - Conceptos Básicos

### **Hashing de Contraseñas**
NUNCA guardes contraseñas en texto plano:
```python
# ❌ MAL
password = "123456"

# ✅ BIEN
hashed_password = "$2b$12$KIXx...." (hash bcrypt)
```

Usamos **bcrypt** porque:
- Es irreversible (no se puede "descifrar")
- Es lento (dificulta ataques de fuerza bruta)
- Incluye "salt" automático (evita rainbow tables)

### **JWT (JSON Web Tokens)**
Cuando un usuario inicia sesión:
1. Backend verifica usuario/contraseña
2. Genera un token JWT firmado
3. Cliente guarda el token
4. Cliente envía token en cada petición

El token contiene:
```json
{
  "user_id": 5,
  "role": "admin",
  "exp": 1234567890  // Fecha de expiración
}
```

---

## 🚀 PRÓXIMOS PASOS

En la siguiente sesión vamos a:
1. ✅ **Crear los endpoints de la API** (CRUD de productos)
2. ✅ **Configurar Supabase** (base de datos en la nube)
3. ✅ **Probar todo con Postman o Thunder Client**

---

## 💡 BUENAS PRÁCTICAS QUE ESTAMOS APLICANDO

### ✅ Separación de responsabilidades
- **models/**: Solo define estructura de datos
- **schemas/**: Solo valida entrada/salida
- **api/**: Solo maneja peticiones HTTP (lo crearemos después)
- **services/**: Lógica de negocio (lo crearemos después)

### ✅ Configuración centralizada
Todo en `config.py` y `.env`:
- Fácil de cambiar entre desarrollo/producción
- Secretos fuera del código
- Validación automática con Pydantic

### ✅ Tipos de datos correctos
- `Decimal` para dinero (no Float)
- `DateTime` con timezone
- `Enum` para valores fijos

### ✅ Relaciones bien definidas
- ForeignKey mantiene integridad
- Relaciones ORM facilitan consultas
- Cascade delete limpia automáticamente

---

## 🤔 PREGUNTAS FRECUENTES

**P: ¿Por qué Numeric en vez de Float para precios?**
R: Float tiene errores de redondeo: 0.1 + 0.2 = 0.30000000000000004
   Decimal es exacto: 0.1 + 0.2 = 0.3

**P: ¿Qué es "server_default=func.now()"?**
R: Le dice a PostgreSQL que genere automáticamente la fecha al insertar.

**P: ¿Para qué sirve "index=True"?**
R: Crea un índice en esa columna, haciendo las búsquedas mucho más rápidas.

**P: ¿Qué es "backref" en relationships?**
R: Crea una relación bidireccional automática:
   sale.customer → accede al cliente
   customer.sales → accede a todas sus ventas

---

## 📝 TAREA ANTES DE LA PRÓXIMA SESIÓN

1. **Instala Python 3.11+** si no lo tienes
2. **Lee este documento completo** y anota dudas
3. **Investiga qué es REST API** (10 minutos)
4. **Crea cuenta en Supabase** (https://supabase.com - es gratis)

---

¿Tienes dudas sobre algún concepto? ¡Pregúntame! 🚀
